import socket
import json
import threading
from typing import Tuple, List

class Client:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.authenticated = False
        self.token = None
        self.response_receiver = False
        # start this after login & register
    def start_response_receiver(self):
        if self.response_receiver:
            self.cond.wait()
        def response_handler() :
            self.response_receiver = True
            while self.response_receiver:
                response = self.receive_response()
                print(f"RESPONSE EVENT : {response}")
        thread = threading.Thread(target=response_handler, args=())
        thread.start()

    def stop_response_receiver(self):
        self.response_receiver = False

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
            self.start_response_receiver()

        return response
    
    def call_logout(self ):
        self.stop_response_receiver
        command = {"command": "logout",
                    "args" : []
                   }
        
        self.send_command(command)
        print("Client send_command in call_logout")
    
    def call_register(self, username, password):
        command = {"command": "register", 
                    "args" : [username,password] }
        
        self.send_command(command)
        print("Client send_command in call_register")
        response = self.receive_response()
        print("Client recieved in call_register" , response)

        return response
    
    def call_add_request(self, items: List[Tuple[str,int]], geoloc: Tuple[float,float],  urgency: str):

        command = {
            "command" : "addrequest",
            "args": [items,geoloc,urgency]
        }
        self.send_command(command)
        print("Client send_command in call_add_request")
    
    def call_update_request(self, reqId,items: List[Tuple[str,int]], geoloc: Tuple[float,float],  urgency: str):

        command = {
            "command" : "updaterequest",
            "args": [reqId,items,geoloc,urgency]
        }
        self.send_command(command)
        print("Client send_command in call_update_request")
    
    def handle_delete_request(self, request_id):

        command = {
            "command" : "deleterequest",
            "args": [request_id]
        }
        self.send_command(command)
        print("Client send_command in handle_delete_request")

    def call_list(self):

        command = {
            "command" : "list",
            "args" : []
        }
        self.send_command(command)
        print("Client send_command in call_list")
    
    def call_add_catalog_item(self,name,synonyms):

        command = {
            "command" : "addcatalogitem",
            "args" : [name,synonyms]
        }
        self.send_command(command)
        print("Client send_command in call_add_catalog_item")

    def call_update_catalog_item(self,old_name,name,synonyms):

        command = {
            "command" : "updatecatalogitem",
            "args" : [old_name,name,synonyms]
        }
        self.send_command(command)
        print("Client send_command in call_update_catalog_item")
    
    def call_search_catalog_item(self,name):

        command = {
            "command" : "searchcatalogitem",
            "args" : [name]
        }
        self.send_command(command)
        print("Client send_command in call_search_catalog_item")

    def call_new_instance(self, name, description):

        command = {
            "command" : "new",
            "args": [name, description]
        }
        self.send_command(command)
        print("Client send_command in call_new_instance")
    
    def call_open(self, campaign_id):

        command = {
            "command" : "open",
            "args": [campaign_id]
        }
        self.send_command(command)
        print("Client send_command in call_open")
    
    def call_close(self):
        command = {
            "command" : "open",
            "args": []
        }
        self.send_command(command)
        print("Client send_command in call_close")
    
    def call_watch(self, item, loc):
        command = {
            "command" : "watch",
            "args": [item, loc]
        }
        self.send_command(command)
        print("Client send_command in call_watch")

    def call_mark_available(self, requestid, items, expire, geoloc, comments):
        command = {
            "command" : "markavilable",
            "args": [requestid, items, expire, geoloc, comments]
        }
        self.send_command(command)
        print("Client send_command in call_mark_available")

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
       


