import socket
import threading
import json
from typing import Tuple, List

from lib import CampaignsManager, Request
from usermanager import UserManager

class Agent(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn
        self.authenticated = False
        self.user = None

        self.instance = None # This will be a Campaign instance
        self.requests = {
            "login": self.handle_login,
            "register": self.handle_register,
            "logout": self.handle_logout,
            "new": self.handle_new_instance,
            "list": self.handle_list_instances,
            "open": self.handle_open_instance,
            "close": self.handle_close_instance,
            "addrequest": self.handle_add_request,
            "updaterequest": self.handle_update_request,
            "deleterequest": self.handle_delete_request,
            "watch": self.handle_watch
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
                
                print(f"Agent recieved {cmd} and {args}")

                if cmd in self.requests:
                    if cmd in ["login", "register", "new", "list"]:
                        self.requests[cmd](*args)
                    else:
                        if self.authenticated and self.instance:
                            self.requests[cmd](*args)
                        else:
                            self.send_message("Please authenticate and open an instance first.")
                else:
                    self.send_message("Invalid command.")

            except Exception as e:
                print(f"Error handling request: {str(e)}")

        self.conn.close()

    def read_message(self):
        data = b""
        while True:
            chunk = self.conn.recv(1024)
            data += chunk
            try:
                msg = json.loads(data.decode())
                return msg
            except ValueError:
                continue

    def handle_register(self, user, password):
        if UserManager.add_user(user, password):
            return self.send_message("Register is successful. Please login ")
        else:
            return self.send_message("Register was not successful",success=False)

    def handle_login(self, user, password):
        token =  UserManager.login(user, password)
        if token:
            self.user = user
            self.authenticated = True
            return self.send_message("Authentication successful.",token)
        else:
            self.user = None
            self.authenticated = False
            return self.send_message("Authentication was not successful.",success=False)

    def handle_logout(self, user, password):
        if self.authenticated and UserManager.logout(user, password):
            self.user = None
            self.authenticated = False
            return self.send_message("Logout successful.")
        else:
            return self.send_message("Logout was not successful.",success=False)

    def handle_add_item(self, user, password):
        return

    def handle_new_instance(self, *args):
        # *args are  [name, description]
        if not self.authenticated:
            return self.send_message("Authentication required.",success=False)
        self.instance = None 
        instance_name = args[0] if len(args) > 0 else None
        instance_description = args[1] if len(args) > 1 else None
        if not instance_name  or not instance_description:
            return self.send_message("instance_name or instance_description can not be empty.",success=False)
        self.instance = CampaignsManager.addCampaign(instance_name,instance_description)
        self.send_message("New instance created ", data= f"id={self.instance.id}, name={instance_name}, description={instance_description}")


    def handle_list_instances(self):
        self.send_message("\n".join([f"{i.id}: {i.name or ''}" for i in CampaignsManager.listCampaigns()]))

    def handle_open_instance(self, instance_id):
        if not self.authenticated:
            self.send_message("Authentication required.")
        if self.instance:
            self.handle_close_instance()
        else:
            instance = self.campaign.getrequest(instance_id)
            if not instance:
                self.send_message(f"Instance with id '{instance_id}' not found.")
            else:
                self.instance = CampaignsManager.getCampaign(instance_id)
                self.send_message(f"Instance with id '{instance_id}' opened.")
    
    def handle_watch(self, item, loc, urgency):
        if not self.authenticated:
            self.send_message("Authentication required.")
        if not self.instance:
            self.send_message(f"First open an instance.")
        else :
            def callback(request):
                    self.send_message(f"Request with id : {request.id} added.")
            watch_id = self.instance.watch(callback, item=item, loc=loc, urgency=urgency)
            self._watches.append(watch_id)
            self.send_message(f"New watcher registered with id : {watch_id}")

    def handle_close_instance(self):
        if not self.authenticated:
            self.send_message("Authentication required.")
        if self.isinstance:
            instanceid = self.instance.id
            self.instance = None
            for watch_id in self._watches:
                self.instance.unwatch(watch_id)
            self._watches = []
            self.send_message(f"Instance with id {instanceid} closed.")

    def handle_add_request(self, items: List[Tuple[str,int]], geoloc: Tuple[float,float],  urgency: str):
        if not self.authenticated:
            self.send_message("Authentication required.")
        def supplyNotificationCallback(message):
            self.send_message(f"New request with id {r.id} update : ", message)
        r = Request(self.user.id, items, geoloc, urgency, notificationCallBack=supplyNotificationCallback)
        self.instance.addrequest(r)
        self.send_message(f"New request with id {r.id} added to campaign with id {self.instance.id}. \n Request info : \n {r.get()}")
        return r.id

    def handle_update_request(self, request_id, *args, **kwargs):
        if not self.authenticated:
            self.send_message("Authentication required.")
        if (self.instance.updaterequest(request_id, *args, **kwargs)):
            self.send_message(f"Request with id {request_id} is updated. \n Request info : \n {self.instance.getrequest(request_id).get()}")
            return request_id
        else :
            self.send_message(f"Request with id {request_id} update rejected. Request has active delivery.")

    def handle_delete_request(self, request_id):
        if not self.authenticated:
            self.send_message("Authentication required.")
        if (self.instance.removerequest(request_id)):
            self.send_message(f"Request with id {request_id} is deleted")
            return request_id
        else :
            self.send_message(f"Request with id {request_id} delete rejected. Request has active delivery.")

    def send_message(self, message, data = "No data", success = True):
        response = {"response": message,
                    "data": data,
                    "success": success}
        message = json.dumps(response).encode()
        self.conn.sendall(message)


