import uuid
import json
from enum import Enum
import time
import hashlib
import threading
from typing import List, Tuple
from inspect import getfullargspec


# Decorator to check writeable fields
# Throws exception
def validate(fields:list[str]):
    def _validate(func):
        def wrapper(*args, **kwargs):
            argspec = getfullargspec(func)
            argument_index = argspec.args.index("values")
            values = args[argument_index]
            for k in values:
                if k not in fields:
                    raise Exception("Unwriteable field write is attempted")
            return func(*args, **kwargs)
        return wrapper #this is the fun_obj mentioned in the above content
    return _validate

# Decorator to check authorization
# Authorize the user "admin" to everything
# user should be the first parameter
# put it as outermost decorator
# Throws permission exception
def authorize(func):
    # TODO: implement
    def wrapper(self, user, *args, **kwargs):
        if user.username=="admin" and user.logged_in:
            return func(self, user, *args, **kwargs)
        elif self.owner != user.username or not user.logged_in:
            raise Exception("Unaouthorized access")
        return func(self, user, *args, **kwargs)
    return wrapper #this is the fun_obj mentioned in the above content

# Decorator to check if user is admin
def admin(func):
    # TODO: implement
    def wrapper(self, user, *args, **kwargs):
        if user.username=="admin" and user.logged_in:
            return func(self, user, *args, **kwargs)
        raise Exception("Unaouthorized admin access")
    return wrapper #this is the fun_obj mentioned in the above content

class User:
    __global_id_counter = 0
    __readable_fields = ["id", "username", "email", "fullname"]
    __writeable_fields = ["username", "email", "fullname", "passwd"]
    __all_users = {}
    
    def __init__(self, username, email, fullname, passwd):
        self.username = username
        self.email = email
        self.fullname = fullname
        self.passwd = hashlib.sha256(passwd.encode())
        self.logged_in = False
        self.session_token = None
        self.id = User.__global_id_counter
        User.__global_id_counter+=1
        self.__all_users[self.id] = self

    def get(self):
        result = {}
        for f in User.__readable_fields:
            result[f] = getattr(self, f)
        return json.dumps(result, indent=4)

    # return json string representation
    @authorize
    @validate(fields=__writeable_fields)
    def update(self, user, values: dict[str,any]):
        for k,v in values.items():
            if k in User.__writeable_fields:
                setattr(self, k, v)

    @authorize
    def delete(self, user):
        # delete from db
        del self.__all_users[self.id]

    def auth(self, plainpass):
        # Check if the supplied password matches the user password
        return hashlib.sha256(plainpass.encode()).hexdigest() == self.passwd.hexdigest()

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

    def __str__(self):
        str(self.get())

    # for managing users
    @classmethod
    def search_user(cls, username: str):
        for id, user in cls.__all_users.items():
            if user.username == username:
                return user
        return None

class Urgency(Enum):
    URGENT = 1
    SOON = 2
    DAYS = 3
    WEEKS = 4
    OPTIONAL = 5

    def get(self):
        return self.name

class Item:
    """Class representing an item"""
    __all_items = {}
    __global_id_counter = 0
    __readable_fields = ["id", "name", "synonyms"]
    __writeable_fields = ["name", "synonyms"]
    
    def __init__(self, name: str, synonyms: List[str] = None) -> None:
        self.name = name
        self.synonyms = synonyms
        self.id = Item.__global_id_counter
        Item.__global_id_counter+=1

        Item.__all_items[self.id] = self

    # return json string representation
    def get(self):
        result = {}
        for f in Item.__readable_fields:
            result[f] = getattr(self, f)
        return json.dumps(result, indent=4)

    # return json string representation
    @validate(fields=__writeable_fields)
    def update(self, values: dict[str,any]):
        for k,v in values.items():
            if k in self.__writeable_fields:
                setattr(self, k, v)
        # update in db
    
    def delete(self):
        # delete from db
        del Item.__all_items[self.id]
        
    @classmethod
    def search(cls, name: str):
        """Searches for an item by name or synonym"""
        for _id, v in cls.__all_items.items():
            if name == v.name or (v.synonyms and name in v.synonyms):
                return cls.__all_items[_id]
        return False

class Request:
    """Class representing a request for supplies"""
    __global_id_counter = 0
    __readable_fields = ["id", "owner", "items", "geoloc", "urgency", "status"]
    __custom_fields = ["urgency"]
    __writeable_fields = ["owner", "items", "geoloc", "urgency", "status"]
    __all_requests = {}

    def __init__(self, owner: str, items: List[Tuple[str,int]], geoloc: Tuple[float,float], urgency: str, comments: str=None) -> None:
        self.owner = owner
        self._init_items(items) 
        self.geoloc = geoloc
        self.urgency = urgency
        self.comments = comments
        self.status = "OPEN" # initial status is OPEN
        
        self._available_suppliers = {} # available suppliers and their supplies
        self._reserved_supplies = {} # reserved supplies by suppliers
        self._delivery_info = {} # delivery information
        self._selected_supplies = {}
        
        self.id = Request.__global_id_counter # counter for unique ids
        Request.__global_id_counter += 1

        self.__all_requests[self.id] = self
    
    def _init_items(self, items):
        self.items = {}
        for item_name, count in items:
            item = Item.search(item_name)
            if not item:
                item = Item(item, [item]) # create a new item with the same name and synonym
            self.items[item.name] = (count)


    # return json string representation
    def get(self):
        result = {}
        for f in Request.__readable_fields:
            if f in Request.__custom_fields:
                result[f] = getattr(self, f).get()
            else:
                result[f] = getattr(self, f)

        for f in result:
            print(f"type of {f} is {type(result[f])}")

        return json.dumps(result)

    # return json string representation
    @authorize
    @validate(fields=__writeable_fields)
    def update(self, user: User, values: dict[str,any]):
        for k,v in values.items():
            if k in Request.__writeable_fields:
                setattr(self, k, v)
        # update in db

    @authorize
    def delete(self, user: User):
        # delete from db
        del self.__all_requests[self.id]
        
    def markavailable(self, user: User, items: List[Tuple[str,int]], expire: int, geoloc: Tuple[float,float], comments: str) -> int:
        """Marks some of the requested items as available by a supplier"""
        available_items = {}
        for item_name, count in self.items.items():
            if not Item.search(item_name):
                Item(item_name, [item_name]) # create a new item with the same name and synonym
            available_items[item_name] = (count)
        
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

        supply_id = str(uuid.uuid4())
        
        self._available_suppliers[supply_id] = (user, geoloc, comments, available_items)
        self._reserved_supplies[supply_id] = available_items
        
        def remove_reserved_supplies():
            del self._reserved_supplies[supply_id]
            del self._available_suppliers[supply_id]

        timer = threading.Timer(expire*3600, remove_reserved_supplies)
        timer.start()

        return supply_id

    
    def pick(self, supply_id: str, items: List[Tuple[str,int]]) -> None:
        """Selects supplies from a supplier and starts delivery"""
        supplier, geoloc, comments, available_items = self._available_suppliers[supply_id]
        selected_items = {}
        for item, count in self.items.items():
            if item in available_items and available_items[item] >= count:
                selected_items[item] = count
                available_items[item] -= count
            elif item in available_items and available_items[item] < count:
                # return as much as possible
                selected_items[item] = available_items[item]
                available_items[item] = 0
        if selected_items:
            self._selected_supplies[supplier] = selected_items
            self._delivery_info[supplier] = (geoloc, comments)
            if available_items[item]:
                self._reserved_supplies[supply_id] = available_items
            else:
                del self._reserved_supplies[supply_id]
                
    def arrived(self, supply_id: int) -> None:
        """Marks the selected supplies as arrived"""
        supplier = list(self._selected_supplies.keys())[supply_id]
        delivered_items = self._selected_supplies[supplier]
        for item, count in delivered_items.items():
            self.items[item] = self.items[item] - count
            if self.items[item] == 0:
                del self.items[item]
        del self._selected_supplies[supplier]
        del self._delivery_info[supplier]
        if not self.items and not self._selected_supplies:
            self.status = "CLOSED"

class Campaign:
    __global_id_counter = 0
    _campaigns = {}

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.requests = []
        self.watch_callbacks = []

        self.id = Campaign.__global_id_counter
        Campaign.__global_id_counter+=1

        self._campaigns[self.id] = (self)

    @classmethod
    def getCampaigns(cls):
        return cls._campaigns

    def delete(self):
        # delete from db
        del self._campaigns[self.id]
        
    def addrequest(self, request: Request):
        self.requests.append(request)
        for callback in self.watch_callbacks:
            if callback.matches_query(request):
                callback.notify(self.id, request)
        return request.id
    
    def removerequest(self, user, request_id):
        for request in self.requests:
            if request.id == request_id:
                if not len(request._delivery_info):
                    self.requests.remove(request)
                    request.delete(user)
                    return True
                else:
                    return False
        return False

    def updaterequest(self, user, request_id, *args, **kwargs):
        for request in self.requests:
            if request.id == request_id:
                return request.update(user, *args, **kwargs)
        return False
    
    def getrequest(self, request_id):
        for request in self.requests:
            if request.id == request_id:
                return request.get()
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
            matching_requests.append(request)
        return matching_requests
    
    def watch(self, callback, item=None, loc=None, urgency=None):
        watch_id = str(uuid.uuid4())
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
    
    def notify(self, campaign_id, request):
        #messagequeue 
        WatchQueue.notifyCampaign(campaign_id, request)
        
# tested    
class WatchQueue:
    _is_notified = {c.id : threading.Condition(threading.Lock()) for c in Campaign.getCampaigns()}
    _active_requests = {}
    _mutex = threading.Lock()

    # one instance can only watch single campaign object
    def __init__(self, campaign_id):
        self.campaign_id = campaign_id
        self.is_watching = False

    @staticmethod
    def notifyCampaign(campaign_id, request):
        with WatchQueue._mutex:
            WatchQueue._active_requests[campaign_id] = request
            cond = WatchQueue._is_notified[campaign_id]
            with cond:
                cond.notify_all()

    def watch(self, callback, campaign_id):
        cond = WatchQueue._is_notified[campaign_id]
        self.is_watching = True
        with cond:
            while True:
                self.cond.wait()
                with cond:
                    if not self.is_watching:
                        break
                    callback(WatchQueue._active_requests[campaign_id])

    def handleClose(self):
        self.is_watching = False




