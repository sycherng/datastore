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
            importer.Importer(message[9:]).importFile()
        elif message.startswith("./query "):
            query_processor.QueryProcessor(message[8:]).processQuery()
        else:
            print("Invalid command. Try:\n./import <filename>\n./query <query>")

if __name__ == '__main__':
    start() 
