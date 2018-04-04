DATASTORE_HEADING = 'STB|TITLE|DATE|PROVIDER|REV|VIEW_TIME' #sic
DATASTORE_NAME = 'datastore.txt'
TEMPFILE_NAME = 'tempstore.txt'
VALID_KEYS = DATASTORE_HEADING.split("|")
VALID_FLAGS = ['-f', '-g', '-s', '-o']
VALID_AGGREGATE_OPTIONS = ['max', 'min', 'sum', 'count', 'collect']
