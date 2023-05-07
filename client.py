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
        command = {"command": "login", "username": username, "password": password}
        self.send_command(command)
        response = self.receive_response()
        print("Client recieved in login" , response)
        if response.get("success"):
            self.authenticated = True
        return response
    
    def register(self, username, password):
        command = {"command": "register", "username": username, "password": password}
        self.send_command(command)
        print("Client send_command in register")
        response = self.receive_response()
        print("Client recieved in register" , response)
        if response.get("success"):
            self.authenticated = True
        return response

    def send_command(self, command):
        if not self.authenticated and command.get("command") not in ["authenticate", "login"]:
            return {"success": False, "error": "Not authenticated"}
        message = json.dumps(command).encode()
        self.socket.send(message)

    def receive_response(self):
        response = []
        req = self.socket.recv(1024)
        while req and req != '':
            # remove trailing newline and blanks
            response.append(json.loads(req.decode()))
        result = "".join(response)
        return result


