import socket
import threading
import json
import struct

from lib import Campaign, WatchQueue, CampaignsManager

class Agent(threading.Thread):
    def __init__(self, conn, campaign):
        threading.Thread.__init__(self)
        self.conn = conn
        self.authenticated = False
        self.instance = None
        self.user = None
        self.campaign = campaign 
        self.requests = {
            "authenticate": self.handle_authenticate,
            "login": self.handle_login,
            "new": self.handle_new_instance,
            "list": self.handle_list_instances,
            "open": self.handle_open_instance,
            "close": self.handle_close_instance,
            "additem": self.handle_add_item
        }

    def run(self):
        while True:
            try:
                data = self.read_message()
                if not data:
                    break
                cmd = data[0]
                args = data[1:]
                if cmd in self.requests:
                    if cmd in ["authenticate", "login", "new", "list"]:
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

    def handle_authenticate(self, user, password):
        if self.campaign.authenticate(user, password):
            self.user = user
            self.authenticated = True
            self.send_message("Authentication successful.")
        else:
            self.user = None
            self.authenticated = False
            self.send_message("Authentication was not successful.")

    def handle_login(self, user, password):
        return self.authenticate(user, password)

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
            self.instance = instance
            self.send_message(f"Instance with id '{instance_id}' opened.")


    def handle_close_instance(self):
        self.instance = None

        self.send_message("Instance closed.")

    def handle_add_item(self, obj_id, item_name, quantity, price):
        self.campaign.find(obj_id).addrequest(item_name, quantity, price)
        self.send_message(f"Item {item_name} added to object {obj_id}.")


