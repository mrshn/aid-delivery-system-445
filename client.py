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
        self.supply_id = None

    # started after login 
    # closed after logout 
    def start_response_receiver(self):
        self.response_receiver = True
        def response_handler() :
            while self.response_receiver:
                response = self.receive_response()
                print(f"RESPONSE EVENT : {response}")
                if response is not None  and response["response"] =="Items marked available":
                    self.supply_id = response["data"]
            print("Client is logged out")
        thread = threading.Thread(target=response_handler, args=())
        thread.start()

    def stop_response_receiver(self):
        self.response_receiver = False

    def call_login(self, username, password):
        command = {"command": "login",
                   "args": [username, password] }
        
        if self.send_command(command,islogin=True):
            print("Client send_command in call_login")
        if not self.response_receiver:
            response = self.receive_response()
            print("Client recieved in call_login" , response)
            if response["success"]:
                self.token = response["data"]
                self.authenticated = True
                self.start_response_receiver()
    
    def call_logout(self ):
        command = {"command": "logout",
                    "args" : []
                   }
        
        self.stop_response_receiver()
        if self.send_command(command):
            print("Client send_command in call_logout")

    
    def call_register(self, username, password):
        command = {"command": "register", 
                    "args" : [username,password] }
        
        if self.send_command(command,islogin=True):
            print("Client send_command in call_register")

        if not self.response_receiver:
            response = self.receive_response()
            print("Client recieved in call_register" , response)

        return response
    
    def call_add_request(self, items: List[Tuple[str,int]], geoloc: Tuple[float,float],  urgency: str):

        command = {
            "command" : "addrequest",
            "args": [items,geoloc,urgency]
        }
        if self.send_command(command):
            print("Client send_command in call_add_request")
        
    
    def call_update_request(self, reqId,items: List[Tuple[str,int]], geoloc: Tuple[float,float],  urgency: str):

        command = {
            "command" : "updaterequest",
            "args": [reqId,items,geoloc,urgency]
        }
        if self.send_command(command):
            print("Client send_command in call_update_request")
        
    
    def call_delete_request(self, request_id):

        command = {
            "command" : "deleterequest",
            "args": [request_id]
        }
        if self.send_command(command):
            print("Client send_command in call_delete_request")
        

    def call_list(self):

        command = {
            "command" : "list",
            "args" : []
        }
        if self.send_command(command):
            print("Client send_command in call_list")
        

    
    def call_add_catalog_item(self,name,synonyms):

        command = {
            "command" : "addcatalogitem",
            "args" : [name,synonyms]
        }
        if self.send_command(command):
            print("Client send_command in call_add_catalog_item")
        

    def call_update_catalog_item(self,old_name,name,synonyms):

        command = {
            "command" : "updatecatalogitem",
            "args" : [old_name,name,synonyms]
        }
        if self.send_command(command):
            print("Client send_command in call_update_catalog_item")
        
    
    def call_search_catalog_item(self,name):

        command = {
            "command" : "searchcatalogitem",
            "args" : [name]
        }
        if self.send_command(command):
            print("Client send_command in call_search_catalog_item")


    def call_new_instance(self, name, description):

        command = {
            "command" : "new",
            "args": [name, description]
        }
        if self.send_command(command):
            print("Client send_command in call_new_instance")

    
    def call_open(self, campaign_id):

        command = {
            "command" : "open",
            "args": [campaign_id]
        }
        if self.send_command(command):
            print("Client send_command in call_open")
  
    
    def call_close(self):
        command = {
            "command" : "open",
            "args": []
        }
        if self.send_command(command):
            print("Client send_command in call_close")
    
    
    def call_watch(self, item, loc):
        command = {
            "command" : "watch",
            "args": [item, loc]
        }
        if self.send_command(command):
            print("Client send_command in call_watch")
      

    # TODO: test
    def call_mark_available_request(self, requestid, items, expire, geoloc, comments):
        command = {
            "command" : "markavilable",
            "args": [requestid, items, expire, geoloc, comments]
        }
        if self.send_command(command):
            print("Client send_command in call_mark_available_request")
        
    # TODO: implement
    def call_get_supply_ids(self):
        # For now no req for this
        # But when call_mark_available_request returns there is a supply_id there usign that one
        return self.supply_id
    
    # TODO: test
    def call_pick_request(self, requestid, supply_id):


        command = {
            "command" : "pick",
            "args": [requestid,supply_id]
        }
        if self.send_command(command):
            print("Client send_command in call_pick_request")
        
    
    # TODO: test
    def call_arrived_request(self, requestid, supply_id):
        command = {
            "command" : "arrived",
            "args": [requestid,supply_id]
        }
        if self.send_command(command):
            print("Client send_command in call_arrived_request")
        

    def send_command(self, json_command,islogin=False):

        if self.authenticated or islogin :
            json_command["token"] = self.token 

            message = json.dumps(json_command).encode()
            self.socket.sendall(message)
            return True
        else:
            print("From Client:  Please login first")
            return False

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
       


