#!usr/bin/python3

from src.networking import TServer, TClient

def main():
	for i in range(int(input("How many clients? "))): TClient()
	server = TServer()
	server.startBroadcasting()

if __name__ == "__main__": main()
