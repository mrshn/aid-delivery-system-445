import socket
import threading
import json
from typing import Tuple, List
import time

from lib import CampaignsManager, Request, Item
from usermanager import UserManager

class Agent(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn
        self.authenticated = False
        self.username = None

        self.instance = None # This will be a Campaign instance
        self.requests = {
            "login": self.handle_login,
            "register": self.handle_register,
            "logout": self.handle_logout,
            "new": self.handle_new_instance,
            "list": self.handle_list_instances,
            "open": self.handle_open_instance,
            "close": self.handle_close_instance,
            "watch": self.handle_watch,
            "addcatalogitem": self.handle_add_catalog_item,
            "updatecatalogitem": self.handle_update_catalog_item,
            "searchcatalogitem": self.handle_search_catalog_item,
            "addrequest": self.handle_add_request,
            "updaterequest": self.handle_update_request,
            "deleterequest": self.handle_delete_request,
            "markavilable": self.handle_mark_available,
            "pick": self.handle_pick,
            "arrived": self.handle_arrived,

        }

        self._watches = []

    def run(self):
        while True:
            try:
                print("Agent is running ")
                data = self.read_message()
                print("data is read at Agent" , data)
                if not data:
                    break
                cmd = data["command"]
                args = data["args"]
                token = data["token"]
                
                print(f"Agent recieved {cmd} and {args}")

                if cmd in self.requests:
                    if cmd in ["login", "register"]:
                        self.requests[cmd](*args)
                    else:
                        self.authenticated = UserManager.validate_token(self.username,token)
                        if self.authenticated :
                            self.requests[cmd](*args)
                        else:
                            self.send_message("Please authenticate first",success=False)
                else:
                    self.send_message("Invalid command.",success=False)

            except Exception as e:
                print(f"Error handling request: {str(e)}")

        self.conn.close()

    def read_message(self):
        data = b""
        while True:
            time.sleep(0.00001)
            chunk = self.conn.recv(1024)
            data += chunk
            try:
                msg = json.loads(data.decode())
                return msg
            except ValueError:
                continue

    def handle_register(self, username, password):
        if UserManager.add_user(username, password):
            return self.send_message("Register is successful. Please login ")
        else:
            return self.send_message("Register was not successful", success=False)

    def handle_login(self, username, password):
        if self.authenticated:
            return self.send_message("You are already logged in , logout first please",success=False)
        token =  UserManager.login(username, password)
        if token:
            self.username = username
            self.authenticated = True
            return self.send_message("Authentication successful.",token)
        else:
            self.username = None
            self.authenticated = False
            return self.send_message("Authentication was not successful.",success=False)

    def handle_logout(self):
        if self.authenticated and UserManager.logout(self.username):
            self.username = None
            self.authenticated = False
            return self.send_message("Logout successful.")
        else:
            return self.send_message("Logout was not successful.",success=False)

    def handle_new_instance(self, *args):
        # *args are  [name, description]
        self.instance = None 
        instance_name = args[0] if len(args) > 0 else None
        instance_description = args[1] if len(args) > 1 else None
        if not instance_name  or not instance_description:
            return self.send_message("instance_name or instance_description can not be empty.",success=False)
        instance = CampaignsManager.addCampaign(instance_name,instance_description)
        return self.send_message("New instance created ", data= f"id={instance.id}, name={instance_name}, description={instance_description}")


    def handle_list_instances(self):
        data = "\n".join([f"{i.id}: {i.name or ''}" for i in CampaignsManager.listCampaigns()])
        return self.send_message("Here is the list of instances",data=data)

    def handle_open_instance(self, instance_id):
        if not self.authenticated:
            return self.send_message("Authentication required.",success=False)
        if self.instance:
            self.handle_close_instance()

        instance = CampaignsManager.getCampaign(instance_id)
        if not instance:
            return self.send_message(f"Instance with id '{instance_id}' not found.",success=False)
        else:
            self.instance = instance
            return self.send_message(f"Instance with id '{instance_id}' opened.")
    
    def handle_watch(self, item, loc):
        if not self.authenticated:
            self.send_message("Authentication required.", success=False)
        if not self.instance:
            self.send_message(f"First open an instance.", success=False)
        else :
            def callback(request):
                    self.send_message(f"NOTIFICATION : Watch notifications : Request with id {request.id} added.")
            watch_id = self.instance.watch(callback, item=item, loc=loc)
            self._watches.append(watch_id)
            self.send_message(f"New watcher registered with id : {watch_id}")

    def handle_close_instance(self):
        if not self.authenticated:
            return self.send_message("Authentication required.",success=False)
        if self.instance:
            instanceid = self.instance.id
            for watch_id in self._watches:
                self.instance.unwatch(watch_id)
            self._watches = []
            self.instance = None
            return self.send_message(f"Instance with id {instanceid} closed.")

    def handle_add_request(self, items: List[Tuple[str,int]], geoloc: Tuple[float,float],  urgency: str):
        def supplyNotificationCallback(message):
            self.send_message(f"NOTIFICATION : Request {r.id} supply update : ", message)
        r = Request( items, geoloc, urgency, supplyNotificationCB=supplyNotificationCallback)
        self.instance.addrequest(r)
        return self.send_message(f"New request with id {r.id} added to campaign with id {self.instance.id}. \n Request info : \n {r.get()}")

    def handle_update_request(self, request_id, *args, **kwargs):
        if (self.instance.updaterequest(request_id, *args, **kwargs)):
            return self.send_message(f"Request with id {request_id} is updated. \n Request info : \n {self.instance.getrequest(request_id).get()}")
        else :
            self.send_message(f"Request with id {request_id} update rejected. Request has active delivery.")

    def handle_delete_request(self, request_id):
        if (self.instance.removerequest(request_id)):
            return self.send_message(f"Request with id {request_id} is deleted")
        else :
            return self.send_message(f"Request with id {request_id} delete rejected. Request has active delivery.")

    def handle_add_catalog_item(self, name, synonyms):
        Item(name, synonyms)
        self.send_message(f"Catalog item '{name}' is created")
    
    def handle_update_catalog_item(self, old_name, new_name, synonyms):
        
        item = Item.search(old_name)
        if item:
            # item.update(new_name, synonyms)
            return self.send_message(f"Catalog item is updated")
        return self.send_message(f"Catalog item is not updated", success=False)

    def handle_search_catalog_item(self, name):

        item = Item.search(name)
        if item:
            return self.send_message(f"Item id : {item.id} \n Item name : {item.name} \n Item synonyms : {item.synonyms}")
        self.send_message("Item not found", success=False)

    def handle_mark_available(self, requestid: int, items: List[Tuple[str,int]], expire: int, geoloc: Tuple[float,float], comments: str):
        supply_id =  self.instance.findrequest(requestid).markavailable(UserManager.search_user(username=self.username),
                                                           items, expire, geoloc, comments)
        self.send_message("Items marked available",data=supply_id)
    
    def handle_pick(self, requestid, supply_id):
        self.instance.findrequest(requestid).pick(supply_id)
        self.send_message("Items picked")

    def handle_arrived(self, requestid, supply_id):
        self.instance.findrequest(requestid).arrived(supply_id)
        self.send_message("Items arrived")

    def send_message(self, message, data = "No data", success = True):
        response = {"response": message,
                    "data": data,
                    "success": success}
        message = json.dumps(response).encode()
        self.conn.sendall(message)
