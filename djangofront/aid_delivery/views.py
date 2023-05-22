import json
from django.shortcuts import redirect, render
from aid_delivery.client import Client

c = Client("localhost", 1423, "LOGGER 1")

_urgency_values = {"urgent": 1,
    "soon": 2,
    "days": 3,
    "weeks": 4, 
    "optional": 5}

# Create your views here.

def index(request):
    '''Main Page'''
    if not request.session.get('is_authenticated'):
        return redirect('/login')
    context = {"form" : request.GET.get("form", None),
               "response_message" : request.session.get('response_message', '')}
    return render(request, 'home.html', context)
	
# Function: login_view
#  Show login form
def login_view(request):
    '''Show login form'''
    context =  {'message':'Welcome, login to access 445 aid delivery system.'}
    response = render(request, 'login.html', context)
    return response

# Function: login_post
#  Login to system
def login_post(request):
    '''Login to system'''
    username = request.POST['username']
    password = request.POST['password']
    # check for authentication from backend
    login = c.call_login(username, password)
    print("anan 501 : login : ", login)
    if login["success"]:
        # create login session 
        request.session['is_authenticated'] = True
        response = redirect("/")
        response.set_cookie("auth_token", login["data"])
        response.set_cookie("username", username)
        return response
    else:
        # Return an 'invalid login' error message.
        return render(request, 'login.html', {'message': 'Invalid username or password'})

# Function: logout_view
# logout from movie
def logout_get(request):
    '''Simply logout'''
    # logout here from backend
    logout = c.call_logout(request.COOKIES.get('username'), request.COOKIES.get('auth_token'))
    print("anan650 : logout : ", logout)
    if logout["success"]:
        request.session['is_authenticated'] = False
        response = redirect("/")
        response.delete_cookie("auth_token")
        response.delete_cookie("username")
        return response
        
    return redirect("/")

# Function: login_view
#  Show login form
def register_view(request):
	'''Show register form'''
	context =  {'message':'Registration to aid delivery 445 system.'}
	return render(request, 'register.html', context)

# Function: login_post
#  Login to system
def register_post(request):
    '''Login to system'''
    username = request.POST['username']
    password = request.POST['password']
    # check for authentication from backend
    register = c.call_register(username=username, password=password)
    if register["success"]:
        # create login session 
        return redirect("/login")
    else:
        return render(request, 'register.html', {'message': 'Unsuccessful registration'})
    
def add_request(request):
    '''add_request Request'''
    items = request.POST['items']
    geoloc = request.POST['geoloc']
    urgency = request.POST['urgency']
    # parse
    items = [(t.split(':')[0].strip(), int(t.split(':')[1])) for t in  items.split(',')]
    geoloc = (float(geoloc.split(',')[0]),float(geoloc.split(',')[1]))
    urgency = _urgency_values.get(urgency, 5)

    result = c.call_add_request(request.COOKIES.get('username'), 
                                request.COOKIES.get('auth_token'), 
                                items, geoloc, urgency)

    request.session['response_message'] = result

    print("result : ", result)
        
    return redirect("/")

def update_request(request):
    '''add_request Request'''
    id = int(request.POST["id"])
    items = request.POST['items']
    geoloc = request.POST['geoloc']
    urgency = request.POST['urgency']
    # parse
    items = [(t.split(':')[0].strip(), int(t.split(':')[1])) for t in  items.split(',')]
    geoloc = (float(geoloc.split(',')[0]),float(geoloc.split(',')[1]))
    urgency = _urgency_values.get(urgency, 5)

    result = c.call_update_request(request.COOKIES.get('username'), 
                                request.COOKIES.get('auth_token'), 
                                id, items, geoloc, urgency)

    request.session['response_message'] = result

    print("result : ", result)
        
    return redirect("/")

def delete_request(request):
    '''add_request Request'''
    id = int(request.POST["id"])

    result = c.call_update_request(request.COOKIES.get('username'), 
                                request.COOKIES.get('auth_token'), 
                                id)

    request.session['response_message'] = result

    print("result : ", result)
        
    return redirect("/")

def mark_available_request(request):
    '''add_request Request'''
    id = int(request.POST["id"])
    expire = int(request.POST["expire"])
    items = request.POST['items']
    geoloc = request.POST['geoloc']
    comments = request.POST["comments"]
    # parse
    items = [(t.split(':')[0].strip(), int(t.split(':')[1])) for t in  items.split(',')]
    geoloc = (float(geoloc.split(',')[0]),float(geoloc.split(',')[1]))

    result = c.call_mark_available_request(request.COOKIES.get('username'), 
                                request.COOKIES.get('auth_token'), 
                                id, items, expire, geoloc, comments)

    request.session['response_message'] = result

    print("result : ", result)
        
    return redirect("/")

def pick_request(request):
    '''add_request Request'''
    id = int(request.POST["id"])
    supplyid = int(request.POST["supplyid"])

    result = c.call_pick_request(request.COOKIES.get('username'), 
                                request.COOKIES.get('auth_token'), 
                                id, supplyid)

    request.session['response_message'] = result

    print("result : ", result)
        
    return redirect("/")

def arrived_request(request):
    '''add_request Request'''
    id = int(request.POST["id"])
    supplyid = int(request.POST["supplyid"])

    result = c.call_arrived_request(request.COOKIES.get('username'), 
                                request.COOKIES.get('auth_token'), 
                                id, supplyid)

    request.session['response_message'] = result

    print("result : ", result)
        
    return redirect("/")

def new_campaign(request):
    '''new_instance Request'''
    name = request.POST['name']
    description = request.POST['description']

    result = c.call_new_instance(request.COOKIES.get('username'), 
                                request.COOKIES.get('auth_token'), 
                                name, description)
    
    result["data"] = json.loads(result.get("data", ""))

    response = redirect("/")

    if result["success"]:
        request.session['response_message'] = json.dumps(result, indent=4)
        #response.set_cookie("campaign", int(result["data"]["id"]))

    return response

def open_campaign(request):
    '''open_instance Request'''
    id = request.POST['id']

    result = c.call_open(request.COOKIES.get('username'), 
                                request.COOKIES.get('auth_token'), 
                                int(id))
    
    if result.get("data", None):
        result["data"] = json.loads(result["data"])

    response = redirect("/")
    if result["success"]:
        request.session['response_message'] = json.dumps(result, indent=4)
        response.set_cookie("campaign_id", id)

    return response

def list_campaign(request):
    '''open_instance Request'''
    result = c.call_list(request.COOKIES.get('username'), 
                                request.COOKIES.get('auth_token'))
    
    if result.get("data", None):
        result["data"] = json.loads(result["data"])

    response = redirect("/")
    if result["success"]:
        request.session['response_message'] = json.dumps(result, indent=4)
        response.set_cookie("campaign_id", id)
    return response

def close_campaign(request):
    '''open_instance Request'''
    result = c.call_close(request.COOKIES.get('username'), 
                                request.COOKIES.get('auth_token'))
    
    if result.get("data", None):
        result["data"] = json.loads(result["data"])

    response = redirect("/")
    if result["success"]:
        request.session['response_message'] = json.dumps(result, indent=4)
        response.set_cookie("campaign_id", id)

    return response

def add_catalog_item(request):
    '''open_instance Request'''
    name = request.POST['name']
    synonyms = request.POST['synonyms']

    synonyms = [s.strip() for s in synonyms.split(",")]

    result = c.call_add_catalog_item(request.COOKIES.get('username'), 
                                request.COOKIES.get('auth_token'),
                                name, synonyms)
    
    print("anan33 : ", result.get("data", None))
    if result.get("data", None):
        result["data"] = json.loads(result["data"])

    response = redirect("/")
    if result["success"]:
        request.session['response_message'] = json.dumps(result, indent=4)
        response.set_cookie("campaign_id", id)

    return response


def update_catalog_item(request):
    '''open_instance Request'''
    name = request.POST['name']
    newname = request.POST['newname']
    synonyms = request.POST['synonyms']

    synonyms = [s.strip() for s in synonyms.split(",")]

    result = c.call_update_catalog_item(request.COOKIES.get('username'), 
                                request.COOKIES.get('auth_token'),
                                name, newname, synonyms)
    
    if result.get("data", None):
        result["data"] = json.loads(result["data"])

    response = redirect("/")
    if result["success"]:
        request.session['response_message'] = json.dumps(result, indent=4)
        response.set_cookie("campaign_id", id)

    return response


def search_catalog_item(request):
    '''open_instance Request'''
    name = request.POST['name']

    result = c.call_search_catalog_item(request.COOKIES.get('username'), 
                                request.COOKIES.get('auth_token'),
                                name)
    
    if result.get("data", None):
        result["data"] = json.loads(result["data"])

    response = redirect("/")
    if result["success"]:
        request.session['response_message'] = json.dumps(result, indent=4)
        response.set_cookie("campaign_id", id)

    return response
