import socket
import json

class Client:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.authenticated = False

    def login(self, username, password):
        command = {"command": "login",
                   "args": [username, password] }
        
        self.send_command(command)
        response = self.receive_response()
        print("Client recieved in login" , response)
        if response.get("success"):
            self.authenticated = True
        return response
    
    def register(self, username, password):
        command = {"command": "register", 
                    "args" : [username,password] }
        
        self.send_command(command)
        print("Client send_command in register")
        response = self.receive_response()
        print("Client recieved in register" , response)
        if response.get("success"):
            self.authenticated = True
        return response

    def send_command(self, json_command):
        message = json.dumps(json_command).encode()
        self.socket.sendall(message)

    def receive_response(self):
        data = b""
        while True:
            chunk = self.socket.recv(1024)
            data += chunk
            try:
                msg = json.loads(data.decode())
                return msg
            except ValueError:
                continue
       


