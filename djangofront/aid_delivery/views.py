from django.shortcuts import redirect, render

# Create your views here.

def index(request):
    if not request.session.get('is_authenticated'):
        return redirect('login')
    context = {}
    return render(request, 'home.html', context)
	
# Function: login_view
#  Show login form
def login_view(request):
	'''Show login form'''
	context =  {'message':'Welcome, login to access 445 aid delivery system.'}
	return render(request, 'login.html', context)

# Function: login_post
#  Login to system
def login_post(request):
    '''Login to system'''
    username = request.POST['username']
    password = request.POST['password']
    # check for authentication from backend
    user = authenticate(username=username, password=password)
    if user["success"]:
        # create login session 
        response = redirect("/")
        response.set_cookie("auth_token", user["token"])
        return response
    else:
        # Return an 'invalid login' error message.
        return render(request, 'login.html', {'message': 'Invalid username or password'})

# Function: logout_view
# logout from movie
def logout_view(request):
	'''Simply logout'''
	# logout here from backend
	return redirect("/").set_cookie("auth_token", "")
