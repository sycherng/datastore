import sys
import entry, importer, query_processor

DATASTORE_HEADING = 'STB|TITLE|DATE|PROVIDER|REV|VIEW_TIME' #sic
DATASTORE_NAME = 'datastore.txt'
TEMPFILE_NAME = 'tempstore.txt'
VALID_KEYS = DATASTORE_HEADING.split("|")
VALID_FLAGS = ['f', 'g', 's', 'o']
VALID_AGGREGATE_OPTIONS = ['max', 'min', 'sum', 'count', 'collect']


def main():
#    initializeDatastore()
    print("Program started.")
    while True:
        message = sys.stdin.readline()[:-1] #strip /n 
        if message == "quit":
            sys.exit()
        elif message.startswith("./import "):
            importer.Importer().importFile(message[9:])
        elif message.startswith("./query "):
            query_processor.QueryProcessor(message[8:]).process()
        else:
            print("Invalid command.")

if __name__ == '__main__':
    main()
  
