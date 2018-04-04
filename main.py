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
            p = query_processor.QueryProcessor(message[8:])
            print(p.orders)
            print(p.selects)
            print(p.groups)
            print(p.filter)
            p.process()
        else:
            print("Invalid command.")

if __name__ == '__main__':
    start() 
