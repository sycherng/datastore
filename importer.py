import os
import values
import entry

class Importer:

    def __init__(self, file_name):
        """
        Initializes Importer object with file name as attribute.
        """
        self.file_name = file_name


    def importFile(self, file_name):
        """(self, str) -> None
        Obtains entries from file to be imported, overwriting with newer entry if same logical record,
        sorts the list of entries by primary keys,
        inserts entry to datastore, overwriting with newer entry if same logical record.
        """
        self.new_entries = self.getEntriesFromFile()
        entry.Entry.sortEntries(self.new_entries) #sorts by primary keys
        self.insertEntries()


    def getEntriesFromFile(self):
        """(str) -> list<Entry>
        Instantiates an Entry object for each line in the provided file, 
        overwrites each subsequent Entry with the same logical record (primary keys),
        returns in a list of Entry objects."""
        new_entries = {}
        with open(self.file_name, 'r') as f:
            heading = f.readline()[:-1] #remove /n
            line = f.readline()
            while line:
                entry = Entry.lineToEntry(line, heading)
                key = f"{entry.stb}|{entry.title}|{entry.date}" #primary keys
                new_entries[key] = entry
                line = f.readline()
        return list(new_entries.values())


    def insertEntries(self):
        """(self, list<Entry>) -> None
        Converts each Entry to a storable string format,
        both the list of new entries and all stored entries are already sorted by primary keys,
        therefore uses modified merge join algorithm to insert into datastore,
        overriding duplicates with the same logical record (primary keys)."""

        #if tempfile exists, a previous import may have aborted midway, raise an error
        if os.path.isfile(values.TEMPFILE_NAME):
            raise RuntimeError(f"Previous file import may have failed. Check {values.DATASTORE_NAME}, delete {values.TEMPFILE_NAME}, and reattempt import as needed.")

        #otherwise proceed with import
        with open(values.DATASTORE_NAME, 'w+') as ds: #only need 'r' privileges to read, but 'w+' allows creation of a new datastore file if one doesn't exist.
            with open(values.TEMPFILE_NAME, 'w') as tf:
                self.number_of_new_entries = len(self.new_entries)
                self.new_entries_index = 0

                # Current new entry we want to insert
                self.new_entry = self.new_entries[self.new_entries_index] #Entry object
                self.new_line = self.new_entry.toStorageString() #storeable formatted string

                # Current stored entry being compared with
                self.stored_line = ds.readline() #storeable formatted string
                self.stored_entry = Entry.lineToEntry(self.stored_line) #Entry object

                while True:
                    if self.new_entry is None:
                        while self.stored_entry:
                            tf.write(self.stored_line)
                            _getNextStoredRecord()
                        break
                    elif self.stored_entry is None:
                        while self.new_entry:
                            tf.write(self.new_line)
                            _getNextNewEntry()
                        break
                    elif self.new_entry > self.stored_entry:
                        tf.write(self.stored_line)
                        self.getNextStoredRecord()
                    elif self.new_entry == self.stored_entry:
                        tf.write(self.new_line)
                        self.getNextStoredRecord()
                        self.getNextNewEntry()
                    else: # self.new_entry < self.stored_entry
                        tf.write(self.new_line)
                        self.getNextNewEntry()

                os.rename(values.TEMPFILE_NAME, values.DATASTORE_NAME)
                print(f"\"{self.file_name}\" successfully imported.")


    def getNextStoredRecord(self):
        self.stored_line = ds.readline()
        if not self.stored_line or self.stored_line.isspace():
            self.stored_entry = None
        else:
            self.stored_entry = Entry.lineToEntry(self.stored_line)


    def getNextNewEntry(self):
        self.new_entries_index += 1
        if self.new_entries_index >= self.number_of_new_entries:
            self.new_entry = None
        else:
            self.new_entry = self.new_entries[self.new_entries_index]
            self.new_line = self.new_entry.toStorageString()
