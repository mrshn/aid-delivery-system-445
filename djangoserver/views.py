from django.shortcuts import render


def index(request):
    return render(request, 'forms_app/index.html')


def submit_form(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        # Process the form data as needed
        return render(request, 'forms_app/success.html', {'name': name})
    else:
        return render(request, 'forms_app/index.html')