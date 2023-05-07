import socket
import threading
import json
import struct

from lib import Campaign, WatchQueue, CampaignsManager
from usermanager import UserManager

class Agent(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn
        self.authenticated = False
        self.user = None

        self.campaign_instance = None # This will be a Campaign instance
        self.requests = {
            "login": self.handle_login,
            "register": self.handle_register,
            "logout": self.handle_logout,
            "new": self.handle_new_instance,
            "list": self.handle_list_instances,
            "open": self.handle_open_instance,
            "close": self.handle_close_instance,
            "additem": self.handle_add_item,
            "watch": self.handle_watch
        }

        self._watches = []

    def run(self):
        while True:
            try:
                print("Agent is running ")
                data = self.read_message()
                if not data:
                    break
                cmd = data[0]
                args = data[1:]
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
        try:
            size = struct.unpack("!I", self.conn.recv(4))[0]
            data = bytearray()
            while len(data) < size:
                packet = self.conn.recv(size - len(data))
                if not packet:
                    return None
                data.extend(packet)
            return json.loads(data)
        except:
            return None
        
    def handle_register(self, user, password):
        if UserManager.add_user(user, password):
            self.send_message("Register is successful. Please login ")
        else:
            self.send_message("User already exists.")

    def handle_login(self, user, password):
        if UserManager.login(user, password):
            self.user = user
            self.authenticated = True
            self.send_message("Authentication successful.")
        else:
            self.user = None
            self.authenticated = False
            self.send_message("Authentication was not successful.")

    def handle_logout(self, user, password):
        if self.authenticated and UserManager.logout(user, password):
            self.user = None
            self.authenticated = False
            self.send_message("Logout successful.")
        else:
            self.send_message("Logout was not successful.")

    def handle_new_instance(self, *args):
        if not self.authenticated:
            return "Authentication required."
        self.instance = None 
        instance_name = args[0] if len(args) > 0 else None
        self.instance = self.campaign.new(*args)
        self.send_message(f"New instance created with id '{self.current_instance.id}' and name '{instance_name or ''}'.")

    def handle_list_instances(self):
        self.send_message("\n".join([f"{i.id}: {i.name or ''}" for i in self.campaign.instances]))

    def handle_open_instance(self, instance_id):
        if not self.authenticated:
            self.send_message("Authentication required.")

        instance = self.campaign.getrequest(instance_id)
        if not instance:
            self.send_message(f"Instance with id '{instance_id}' not found.")
        else:
            self.instance = CampaignsManager.getCampaign(instance_id)
            self.send_message(f"Instance with id '{instance_id}' opened.")
    
    def handle_watch(self, item, loc, urgency):
        if not self.instance:
            self.send_message(f"First open an instance.")
        else :
            def callback(request):
                    self.send_message(f"Request with id : {request.id} added.")
            watch_id = self.instance.watch(callback, item=item, loc=loc, urgency=urgency)
            self._watches.append(watch_id)
            self.send_message(f"New watcher registered with id : {watch_id}")

    def handle_close_instance(self):
        self.instance = None
        for watch_id in self._watches:
            self.instance.unwatch(watch_id)
        self._watches = []
        self.send_message("Instance closed.")

    def handle_add_item(self, obj_id, item_name, quantity, price):
        self.campaign.find(obj_id).addrequest(item_name, quantity, price)
        self.send_message(f"Item {item_name} added to object {obj_id}.")

    def send_message(self, message):
        self.conn.sendall(message.encode() + b"\n")


