import socket
import json

class Client:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.authenticated = False
        self.token = None

    def call_login(self, username, password):
        command = {"command": "login",
                   "args": [username, password] }
        
        self.send_command(command)
        print("Client send_command in call_login")
        response = self.receive_response()
        print("Client recieved in call_login" , response)

        if response["success"]:
            self.token = response["data"]
            self.authenticated = True

        return response
    
    def call_logout(self ):
        command = {"command": "logout"}
        
        self.send_command(command)
        print("Client send_command in call_logout")
        response = self.receive_response()
        print("Client recieved in call_logout" , response)
 
        return response
    
    def call_register(self, username, password):
        command = {"command": "register", 
                    "args" : [username,password] }
        
        self.send_command(command)
        print("Client send_command in call_register")
        response = self.receive_response()
        print("Client recieved in call_register" , response)

        return response

    def call_list(self):

        command = {
            "command" : "list",
            "args" : []
        }
        self.send_command(command)
        print("Client send_command in call_list")
        response = self.receive_response()
        print("Client recieved in call_list" , response)

        return response
        
    def call_new_instance(self, name, description):

        command = {
            "command" : "new",
            "args": [name, description]
        }
        self.send_command(command)
        print("Client send_command in call_new_instance")
        response = self.receive_response()
        print("Client recieved in call_new_instance" , response)

        return response


    def send_command(self, json_command):
        json_command["token"] = self.token 

        message = json.dumps(json_command).encode()
        self.socket.sendall(message)

    def receive_response(self):
        data = b""
        while True:
            chunk = self.socket.recv(1024)
            data += chunk
            try:
                msg = json.loads(data.decode())
                if not msg["success"]:
                    print("Your request failed to be executed")
                return msg
            except ValueError:
                continue
       


