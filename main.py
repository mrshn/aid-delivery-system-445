from math import radians, sin, cos, sqrt
import random
import string
import uuid


class UserManager:
    """
    This class will manage all the users on the platform. 
    It will have methods to create, delete, and get users. It will also have a list of all the users.
    """
    def __init__(self):
        self.users = []

    def create_user(self, username: str, password: str, contact: str) -> User:
        user = User(username, password, contact)
        self.users.append(user)
        return user

    def delete_user(self, user: User):
        self.users.remove(user)

    def get_user(self, username: str) -> User:
        for user in self.users:
            if user.username == username:
                return user
        return None


class User:
    def __init__(self, username, email, fullname, passwd):
        self.username = username
        self.email = email
        self.fullname = fullname
        self.passwd = passwd
        self.logged_in = False
        self.session_token = None

    def read(self):
        # TODO: implement read operation
        pass

    def auth(self, plainpass):
        # Check if the supplied password matches the user password
        return plainpass == self.passwd

    def generate_random_token(self):
        return str(uuid.uuid4())
    
    def is_valid_token(self, token):
        return token == self.session_token
    
    def end_session(self):
        self.session_token = None

    def start_session(self):
        if self.session_token is not None:
            self.end_session()
        self.session_token = self.generate_random_token()
        return self.session_token

    def login(self):
        # Start a session for the user
        if not self.logged_in:
            self.logged_in = True
            self.start_session()
            return self.session_token

    def checksession(self, token):
        # Check if the token is valid, returned by the last login
        return self.logged_in and token == self.session_token

    def logout(self):
        # End the session invalidating the token
        if self.logged_in:
            self.logged_in = False
            self.end_session()




class Item:
    def __init__(self, name, synonyms):
        self.name = name
        self.synonyms = synonyms

    def update(self, name=None, synonyms=None):
        if name is not None:
            self.name = name
        if synonyms is not None:
            self.synonyms = synonyms

    def search(self, name):
        return name in [self.name] + self.synonyms


from enum import Enum
class Urgency(Enum):
    URGENT = 1
    SOON = 2
    DAYS = 3
    WEEKS = 4
    OPTIONAL = 5

class Location:
    """
    This class will represent a location on the map. It will have a longitude and latitude.
    """
    def __init__(self, longitude: float, latitude: float):
        self.longitude = longitude
        self.latitude = latitude

import threading
import time
from typing import List, Tuple

class Item:
    """Class representing an item"""
    all_items = {}
    
    def __init__(self, name: str, synonyms: List[str]) -> None:
        self.name = name
        self.synonyms = synonyms
        Item.all_items[name] = self
        
    @staticmethod
    def search(self, name: str) -> Item:
        """Searches for an item by name or synonym"""
        for item in Item.all_items.values():
            if name == item.name or name in item.synonyms:
                return self
        return False

class Request:
    """Class representing a request for supplies"""
    def __init__(self, owner: str, items: List[Tuple[str,int]], geoloc: Tuple[float,float], urgency: str, comments: str) -> None:
        self.owner = owner
        self.items = items
        self.geoloc = geoloc
        self.urgency = urgency
        self.comments = comments
        self.status = "OPEN" # initial status is OPEN
        
        self.available_suppliers = {} # available suppliers and their supplies
        self.selected_supplies = {} # selected supplies from different suppliers
        self.reserved_supplies = {} # reserved supplies by suppliers
        self.delivery_info = {} # delivery information
        
        self.id_counter = 0 # counter for unique ids
        
    def markavailable(self, user: str, items: List[Tuple[str,int]], expire: int, geoloc: Tuple[float,float], comments: str) -> int:
        """Marks some of the requested items as available by a supplier"""
        available_items = {}
        for item, count in items:
            if Item.search(item):
                available_items[item] = count
            else:
                Item(item, [item]) # create a new item with the same name and synonym
        
        # TODO:  Not sure if I need to remove the reserved items from self.items
        # self.items = [(item, count) for item, count in self.items if (item, count) not in items]
        """
        for i, (name, count) in enumerate(self.items):
            if name in available_items:
                if available_items[name] >= count:
                    available_items[name] -= count
                    self.items.pop(i)
                else:
                    self.items[i] = (name, count - available_items[name])
                    available_items[name] = 0
        """

        supply_id = self.id_counter
        self.id_counter += 1 # So it is unique
        
        self.available_suppliers[supply_id] = (user, geoloc, comments, available_items)
        self.reserved_supplies[supply_id] = available_items
        
        # set a timer to remove the reserved supplies after the expire time has elapsed 
        # TODO: change this to callback
        def remove_reserved_supplies():
            # Add the reserved items back to self.items
            del self.reserved_supplies[supply_id]
            del self.available_suppliers[supply_id]
        timer = threading.Timer(expire*3600, remove_reserved_supplies)
        timer.start()
        return supply_id

    
    def pick(self, item_id: int, items: List[Tuple[str,int]]) -> None:
        """Selects supplies from a supplier and starts delivery"""
        supplier, geoloc, comments, available_items = self.available_suppliers[item_id]
        selected_items = {}
        for item, count in items:
            if item in available_items and available_items[item] >= count:
                selected_items[item] = count
                available_items[item] -= count
            elif item in available_items and available_items[item] < count:
                # return as much as possible
                selected_items[item] = available_items[item]
                available_items[item] = 0
        if selected_items:
            self.selected_supplies[supplier] = selected_items
            self.delivery_info[supplier] = (geoloc, comments)
            if available_items:
                self.reserved_supplies[item_id] = available_items
            else:
                del self.reserved_supplies[item_id]
                
    def arrived(self, item_id: int) -> None:
        """Marks the selected supplies as arrived"""
        supplier = list(self.selected_supplies.keys())[item_id]
        delivered_items = self.selected_supplies[supplier]
        for item, count in delivered_items.items():
            for i in range(len(self.items)):
                if self.items[i][0] == item:
                    self.items[i] = (item, self.items[i][1] - count)
                    if self.items[i][1] == 0:
                        self.items.pop(i)
                    break
        del self.selected_supplies[supplier]
        del self.delivery_info[supplier]
        if not self.items and not self.selected_supplies:
            self.status = "CLOSED"



class CampaignManager:
    """
    This class will manage all the campaigns on the platform. 
    It will have methods to create, delete, and get campaigns. 
    It will also have a list of all the campaigns.
    """
    def __init__(self):
        self.campaigns = []

    def create_campaign(self, name: str, description: str) -> 'Campaign':
        campaign = Campaign(name, description)
        self.campaigns.append(campaign)
        return campaign

    def delete_campaign(self, campaign: 'Campaign'):
        self.campaigns.remove(campaign)

    def get_campaign(self, name: str) -> 'Campaign':
        for campaign in self.campaigns:
            if campaign.name == name:
                return campaign
        return None

class Campaign:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.requests = []
        self.watch_callbacks = []
        self.next_request_id = 1
        
    def addrequest(self, request):
        request_id = self.next_request_id
        self.next_request_id += 1
        request.set_id(request_id)
        self.requests.append(request)
        for callback in self.watch_callbacks:
            if callback.matches_query(request):
                callback.notify(request)
        return request_id
    
    def removerequest(self, request_id):
        for request in self.requests:
            if request.get_id() == request_id:
                if request.is_deletable():
                    self.requests.remove(request)
                    return True
                else:
                    return False
        return False
    
    def updaterequest(self, request_id, *args, **kwargs):
        for request in self.requests:
            if request.get_id() == request_id:
                return request.update(*args, **kwargs)
        return False
    
    def getrequest(self, request_id):
        for request in self.requests:
            if request.get_id() == request_id:
                return request.read()
        return None
    
    def query(self, item=None, loc=None, urgency=None):
        matching_requests = []
        for request in self.requests:
            if item is not None and item.lower() not in [i.lower() for i in request.items]:
                continue
            if loc is not None and not request.location_within(loc):
                continue
            if urgency is not None and request.urgency < urgency:
                continue
            matching_requests.append(request.read())
        return matching_requests
    
    def watch(self, callback, item=None, loc=None, urgency=None):
        watch_id = uuid.uuid4().hex
        self.watch_callbacks.append(WatchCallback(watch_id, callback, item, loc, urgency))
        return watch_id
    
    def unwatch(self, watch_id):
        for callback in self.watch_callbacks:
            if callback.id == watch_id:
                self.watch_callbacks.remove(callback)
                return True
        return False

class Notification:
    """
    This class will represent a notification that is sent to a user when an event occurs. 
    Each notification will have a message, timestamp, and associated user.
    """
    def __init__(self, message: str, timestamp: str, user: User):
        self.message = message
        self.timestamp = timestamp
        self.user = user


class WatchCallback:
    def __init__(self, id, callback, item=None, loc=None, urgency=None):
        self.id = id
        self.callback = callback
        self.item = item.lower() if item is not None else None
        self.loc = loc
        self.urgency = urgency
    
    def matches_query(self, request):
        if self.item is not None and self.item not in [i.lower() for i in request.items]:
            return False
        if self.loc is not None and not request.location_within(self.loc):
            return False
        if self.urgency is not None and request.urgency < self.urgency:
            return False
        return True
    
    def notify(self, request):
        self.callback(request.read())









