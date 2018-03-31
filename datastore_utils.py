import os
import main, entry

def lineToEntry(line, fields=main.HEADING, delimiter="|"):
    """(str, str, str) -> Entry | instantiate an Entry object given a line in a file, fields, and delimiter"""
    line = line[:-1] #remove /n
    line_dict = dict(zip(fields.split(delimiter), (value for value in line.split(delimiter))))
    return Entry(line_dict)

def importFile(file_name):
    new_entries = geitEntriesFromFile(file_name)
    removeDuplicates(new_entries)
    Entry.sortEntries(new_entries)
    insertEntries(new_entries, datastore) #binary search insert into datastore, includes duplicate key overrides

def getEntriesFromFile(file_name):
    """(str) -> list of Entry | instantiate an Entry object for each line in this file, overwrite each subsequent Entry with the same logical record, return in a list."""
    new_entries = {}
    with open(file_name, 'r') as f:
        heading = f.readline()[:-1] #remove /n
        line = f.readline()
        while line:
            entry = lineToEntry(line, heading)
            key = f"{entry.stb}|{entry.title}|{entry.provider}"
            new_entries[key] = entry
            line = f.readline()
    return list(new_entries.values())

def insertEntries(new_entries, datastore):
    """(list of Entry) -> None | binary search insert into datastore, overriding duplicates by primary keys"""
    if os.path.isfile(main.TEMPFILE_NAME):
        raise RuntimeError(f"Previous file import may have failed. Check {main.DATASTORE_NAME}, delete {main.TEMPFILE_NAME}, and reattempt import as needed.")
    with open(main.DATASTORE_NAME, 'r') as ds:
        with open(main.TEMPFILE_NAME, 'w') as tf:

            def _nextDataStoreRecord(ds):
                stored_line = ds.readline()
                if stored_line == "":
                    stored_entry = None
                else:
                    stored_entry = lineToEntry(stored_line)
                return stored_line, stored_entry

            def _nextNewEntry(index, new_entries):
                index += 1
                if index == len(new_entries) - 1:
                    new_entry = None
                else:
                    new_entry = new_entries[index]
                return index, new_entry

            index, new_entry = _nextNewEntry(0, new_entries)
            stored_line, stored_entry = _nextDataStoreRecord(ds)

            while True:
                if new_entry > stored_entry:
                    tf.write(stored_line)
                    stored_line, stored_entry = _nextDataStoreRecord(ds)
                else if new_entry == stored_entry:
                    tf.write(new_entry.toStorageString))
                    stored_line, stred_entry = _nextDataStoreRecord(ds)
                    index, new_entry = _nextNewEntry(index, new_entries)
                else if new_entry < stored_entry:
                    tf.write(new_entry.toStorageString))
                    index, new_entry = _nextNewEntry
                else if new_entry == None:
                    while stored_line:
                        tf.write(stored_line)
                        stored_line = ds.readline()
                    break
                else if stored_entry == None:
                    while new_entry:
                        tf.write(new_entry.toStorageString())
                    break
            os.rename(main.TEMPFILE_NAME, main.DATASTORE_NAME) 
