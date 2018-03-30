import main

def importFile(file_name):
    new_entries = getEntriesFromFile(file_name)
    Entry.sortEntries(new_entries)
    insertEntries(new_entries, datastore) #binary search insert into datastore, includes duplicate key overrides

def getEntriesFromFile(file_name):
    """(str) -> list of Entry | instantiate an Entry object for each line in this file, return them in a list"""
    new_entries = []
    with open(file_name, 'r') as f:
        heading = f.readline()[:-1].split("|")
        line = f.readline()[:-1]
        while line:
            line = line.split("|")
            line_dict = dict(zip(heading, (field for field in line)))
            e = entry.Entry(line_dict)
            new_entries.append(e)
            line = f.readline()[:-1]
    return new_entries

def insertEntries(new_entries, datastore):
    """(list of Entry) -> None | binary search insert into datastore, overriding duplicates by primary keys"""
    #duplicate_found = None
    #position_to_insert = None
    with open(main.DATASTORE_NAME, 'r+') as ds:
        num_stored = int(ds.readline())
        for new_entry in new_entries:
            new_entry_string = new_entry.toStorageString()
            #binary search
            start_line_no, end_line_no = 0, num_stored + 1
            entry_at_line = None
            while entry_at_line != new_entry and start_line_no <= end_line_no:
                mid_line_no = (start_line_no + end_line_no) // 2
                position = mid_line_no * main.DATASTORE_WIDTH
                ds.seek(position) #jump to start of middle line
                line = ds.readline()
                line_dict = dict(zip(main.DATASTORE_HEADING, field for field in line))
                entry_at_line = entry.Entry(line_dict)
                if entry_at_line < new_entry:
                    start_line_no = mid_line_no + 1
                else:
                    end_line_no = mid_line_no - 1
            ds.seek(position)
            if entry_at_line != new_entry:
                ds.write(new_entry_string)
            else:
                ds.
     
         
         
