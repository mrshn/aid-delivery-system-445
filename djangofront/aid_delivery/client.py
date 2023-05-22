import socket
import json
import threading
from typing import Tuple, List

class Client:
    def __init__(self, host, port, name=""):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.supply_id = None
        self.name = name

    def call_login(self, username, password):
        command = {"command": "login",
                   "args": [username, password] }
        
        if self.send_command(command,islogin=True):
            print(self.name, ": Client send_command in call_login")

        response = self.receive_response()
        print(self.name, ": Client recieved in call_login" , response)
        if response["success"]:
            self.token = response["data"]
        return response
    
    def call_logout(self, username, token):
        command = {"command": "logout",
                    "args" : []
                   }
        
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_logout")

        response = self.receive_response()
        return response

    
    def call_register(self, username, password):
        command = {"command": "register", 
                    "args" : [username,password] }
        
        if self.send_command(command,islogin=True):
            print(self.name, ": Client send_command in call_register")

        response = self.receive_response()
        print(self.name, ": Client recieved in call_register" , response)

        return response
    
    def call_add_request(self, username, token, items: List[Tuple[str,int]], geoloc: Tuple[float,float],  urgency: str):

        command = {
            "command" : "addrequest",
            "args": [items,geoloc,urgency]
        }
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_add_request")
        
        response = self.receive_response()
        return response
        
    
    def call_update_request(self, username, token, reqId,items: List[Tuple[str,int]], geoloc: Tuple[float,float],  urgency: str):

        command = {
            "command" : "updaterequest",
            "args": [reqId,items,geoloc,urgency]
        }
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_update_request")
        
        response = self.receive_response()
        return response
    
    def call_delete_request(self, username, token, request_id):

        command = {
            "command" : "deleterequest",
            "args": [request_id]
        }
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_delete_request")
        
        response = self.receive_response()
        return response
        

    def call_list(self, username, token):

        command = {
            "command" : "list",
            "args" : []
        }
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_list")

        response = self.receive_response()
        return response

    
    def call_add_catalog_item(self, username, token, name,synonyms):

        command = {
            "command" : "addcatalogitem",
            "args" : [name,synonyms]
        }
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_add_catalog_item")
        
        response = self.receive_response()
        return response
        

    def call_update_catalog_item(self,username, token, old_name,name,synonyms):

        command = {
            "command" : "updatecatalogitem",
            "args" : [old_name,name,synonyms]
        }
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_update_catalog_item")
        
        response = self.receive_response()
        return response
        
    
    def call_search_catalog_item(self,username, token, name):

        command = {
            "command" : "searchcatalogitem",
            "args" : [name]
        }
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_search_catalog_item")

        response = self.receive_response()
        return response


    def call_new_instance(self, username, token, name, description):

        command = {
            "command" : "new",
            "args": [name, description]
        }
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_new_instance")

        response = self.receive_response()
        return response

    
    def call_open(self, username, token, campaign_id):
        command = {
            "command" : "open",
            "args": [campaign_id]
        }
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_open")

        response = self.receive_response()
        return response
  
    
    def call_close(self, username, token):
        command = {
            "command" : "close",
            "args": []
        }
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_close")

        response = self.receive_response()
        return response
    
    
    def call_watch(self, username, token, item, loc):
        command = {
            "command" : "watch",
            "args": [item, loc]
        }
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_watch")

        response = self.receive_response()
        return response
      

    def call_mark_available_request(self, username, token, requestid, items, expire, geoloc, comments):
        command = {
            "command" : "markavilable",
            "args": [requestid, items, expire, geoloc, comments]
        }
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_mark_available_request")

        response = self.receive_response()
        return response

        
    # TODO: implement
    def call_get_supply_ids(self, username, token):
        # For now no req for this
        # But when call_mark_available_request returns there is a supply_id there usign that one
        return self.supply_id
    
    # TODO: test
    def call_pick_request(self, username, token, requestid, supply_id):
        command = {
            "command" : "pick",
            "args": [requestid,supply_id]
        }
        if self.send_command(command, username, token):
            print("Client send_command in call_pick_request")

        response = self.receive_response()
        return response
        
    
    # TODO: test
    def call_arrived_request(self, username, token, requestid, supply_id):
        command = {
            "command" : "arrived",
            "args": [requestid,supply_id]
        }
        if self.send_command(command, username, token):
            print(self.name, ": Client send_command in call_arrived_request")

        response = self.receive_response()
        return response
        

    def send_command(self, json_command, username=None, token=None, islogin=False):
        json_command["token"] = token 
        json_command["username"] = username 
        message = json.dumps(json_command).encode()
        self.socket.sendall(message)
        return True

    def receive_response(self):
        data = b""
        while True:
            chunk = self.socket.recv(1024)
            data += chunk
            try:
                msg = json.loads(data.decode())
                if not msg["success"]:
                    print(self.name, ": Your request failed to be executed")
                return msg
            except ValueError:
                continue




