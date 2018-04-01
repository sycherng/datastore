import os
import main, entry

class Importer:

    def importFile(self, file_name):
        self.file_name = file_name
        new_entries = Importer.getEntriesFromFile(file_name)
        entry.Entry.sortEntries(new_entries)
        self.insertEntries(new_entries)

    @classmethod
    def getEntriesFromFile(cls, file_name):
        """(str) -> list of Entry | instantiate an Entry object for each line in this file, overwrite each subsequent Entry with the same logical record, return in a list."""
        new_entries = {}
        with open(file_name, 'r') as f:
            heading = f.readline()[:-1] #remove /n
            line = f.readline()
            while line:
                entry = Entry.lineToEntry(line, heading)
                key = f"{entry.stb}|{entry.title}|{entry.date}"
                new_entries[key] = entry
                line = f.readline()
        return list(new_entries.values())

    def insertEntries(self, new_entries):
        """(list of Entry) -> None | binary search insert into datastore, overriding duplicates by primary keys"""

        #if tempfile exists, a previous import may have aborted midway, raise an error
        if os.path.isfile(main.TEMPFILE_NAME):
            raise RuntimeError(f"Previous file import may have failed. Check {main.DATASTORE_NAME}, delete {main.TEMPFILE_NAME}, and reattempt import as needed.")


        #otherwise proceed with import
        with open(main.DATASTORE_NAME, 'w+') as ds:
            with open(main.TEMPFILE_NAME, 'w') as tf:
                self.number_of_new_entries = len(new_entries)
                self.new_entries_index = 0

                # Current new entry we want to insert
                self.new_entry = new_entries[self.new_entries_index] #Entry object
                self.new_line = self.new_entry.toStorageString() #storeable formatted string

                # Current stored entry being examined
                self.stored_line = ds.readline() #storeable formatted string
                self.stored_entry = Entry.lineToEntry(self.stored_line) #Entry object

                def _getNextStoredRecord():
                    self.stored_line = ds.readline()
                    if not self.stored_line or self.stored_line.isspace():
                        self.stored_entry = None
                    else:
                        self.stored_entry = Entry.lineToEntry(self.stored_line)

                def _getNextNewEntry():
                    self.new_entries_index += 1
                    if self.new_entries_index >= self.number_of_new_entries:
                        self.new_entry = None
                    else:
                        self.new_entry = new_entries[self.new_entries_index]
                        self.new_line = self.new_entry.toStorageString()

                while True:
                    print(f"new_entry {self.new_entry}\nnew_line {self.new_line}stored_entry {self.stored_entry}\nstored_line {self.stored_line}\n")
                    if self.new_entry is None:
                        print(1)
                        while self.stored_entry:
                            tf.write(self.stored_line)
                            _getNextStoredRecord()
                        break
                    elif self.stored_entry is None:
                        print(2)
                        while self.new_entry:
                            tf.write(self.new_line)
                            _getNextNewEntry()
                            print("next new entry is" + str(self.new_entry))
                        break
                    elif self.new_entry > self.stored_entry:
                        print(3)
                        tf.write(self.stored_line)
                        _getNextStoredRecord()
                    elif self.new_entry == self.stored_entry:
                        print(4)
                        tf.write(self.new_line)
                        _getNextStoredRecord()
                        _getNextNewEntry()
                    else: # self.new_entry < self.stored_entry
                        print(5)
                        tf.write(self.new_line)
                        _getNextNewEntry()

                os.rename(main.TEMPFILE_NAME, main.DATASTORE_NAME)
                print(f"\"{self.file_name}\" successfully imported.")
