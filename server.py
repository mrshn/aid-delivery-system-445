import socket
import threading
import json
import struct

from agent import Agent

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        print(f"Starting server on {self.host}:{self.port}...")
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print("Server is now listening for incoming connections...")

        while True:
            client_socket, client_address = self.socket.accept()
            print(f"New connection from {client_address}")

            agent = Agent(client_socket)
            agent.start()

