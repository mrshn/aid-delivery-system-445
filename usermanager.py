

from inspect import getfullargspec

import hashlib
import uuid
import json


# Decorator to check if user is admin
def admin(func):
    # TODO: implement
    def wrapper(self, user, *args, **kwargs):
        if user.username=="admin" and user.logged_in:
            return func(self, user, *args, **kwargs)
        raise Exception("Unaouthorized admin access")
    return wrapper #this is the fun_obj mentioned in the above content


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


class User:
    __global_id_counter = 0
    __readable_fields = ["id", "username", "email", "fullname"]
    __writeable_fields = ["username", "email", "fullname", "passwd"]
    
    def __init__(self, username, email, fullname, passwd):
        self.username = username
        self.email = email
        self.fullname = fullname
        self.passwd = hashlib.sha256(f"{passwd}".encode())
        self.logged_in = False
        self.session_token = None
        self.id = User.__global_id_counter
        User.__global_id_counter += 1

    def get(self):
        result = {}
        for f in User.__readable_fields:
            result[f] = getattr(self, f)
        return json.dumps(result, indent=4)

    # return json string representation
    @validate(fields=__writeable_fields)
    def update(self, user, values: dict[str,any]):
        for k,v in values.items():
            if k in User.__writeable_fields:
                setattr(self, k, v)

    def auth(self, plainpass):
        # Check if the supplied password matches the user password
        return hashlib.sha256(f"{plainpass}".encode()).hexdigest() == self.passwd.hexdigest()

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


class UserManager:
    admin = User("admin", "admin_email", "admin_name", "123")
    __all_users = { admin.id : admin }

    @staticmethod
    def search_user( username: str):
        for id, user in UserManager.__all_users.items():
            if user.username == username:
                return user
        return None

    @staticmethod
    def add_user(username, password):
        if UserManager.search_user(username):
            return None
        new_user = User(username, "default_email", "default_name", password)
        UserManager.__all_users[new_user.id] = new_user
        return new_user

    @staticmethod
    def login( username, password ):
        user = UserManager.search_user(username)
        if user:
            if user.auth(password):
                return user.login()
        return None
    
    @staticmethod
    def validate_token( username, token ):
        user = UserManager.search_user(username)
        if user and user.is_valid_token(token):
            return True
        return False

    @staticmethod
    def logout(username):
        user = UserManager.search_user(username)
        if user:
            user.logout()
        return None

    @staticmethod
    def remove_user(username):
        user = UserManager.search_user(username)
        if user and user.logged_in:
            del UserManager.__all_users[user.id]

    @staticmethod
    def get_all_users():
        return list(UserManager.__all_users.values())
