import sys
import importer
import query_processor

def start():
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
    start()
  
