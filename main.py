import sys


def main():
    print("Program started.")
    while True:
        message = sys.stdin.readline()[:-1] #strip /n 
        if message == "quit":
            sys.exit()
        if message.startswith("./query "):
            parser(message[8:])
        else:
            print("Invalid command.")

def parser(message):
    index = 0
    for  



if __name__ == '__main__':
    main()
  
