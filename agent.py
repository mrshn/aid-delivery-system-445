import socket
import threading
import json
import struct

from lib import Campaign

class Agent(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn
        self.authenticated = False
        self.instance = None
        self.user = None
        self.requests = {
            # add commands for instance editing such as additem
            "authenticate": self.handle_authenticate,
            "login": self.handle_authenticate,
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
        # do authentication logic here, for example check user credentials
        # against a database or a file
        self.user = user
        self.authenticated = True
        self.send_message("Authentication successful.")

    def handle_new_instance(self, *args):
        # create new instance logic goes here
        self.instance = None  # set instance to None for now
        self.send_message("Instance created successfully.")

    def handle_list_instances(self):
        # list instances logic goes here
        self.send_message("List of instances goes here.")

    def handle_open_instance(self, instance_id):
        # open instance logic goes here
        self.instance = instance_id
        # close if open instance
        # activate condition in for instance in msg queue
        self.send_message(f"Instance {instance_id} opened.")

    def handle_close_instance(self):
        # close instance logic goes here
        self.instance = None
        self.send_message("Instance closed.")

    def handle_add_item(self, obj_id, item_name, quantity, price):
        # add item logic goes here
        self.send_message(f"Item {item_name} added to object {obj_id}.")


