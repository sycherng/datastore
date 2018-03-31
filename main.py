import sys
import entry, datastore_utils

DATASTORE_HEADING = 'STB|TITLE|DATE|PROVIDER|REV|VIEW_TIME' #sic
DATASTORE_NAME = 'datastore.txt'
TEMPFILE_NAME = 'tempstore.txt'

def main():
#    initializeDatastore()
    print("Program started.")
    while True:
        message = sys.stdin.readline()[:-1] #strip /n 
        if message == "quit":
            sys.exit()
        elif message.startswith("./import "):
            datastore_utils.Importer().importFile(message[9:])
        elif message.startswith("./query "):
            parser(message[8:])
        else:
            print("Invalid command.")


#def initializeDatestore():
#    """(None) -> None | if datastore.txt does not exist, create it and write 0\n to first line"""
#    with open(DATASTORE_NAME, 'r+') as ds:
#        line1 = ds.readline()
#        if line1 == '':
#            ds.write("0\n")

def parser(query):
    pass

if __name__ == '__main__':
    main()
  
