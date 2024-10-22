from django.shortcuts import render

def login_view(request):
    template_name = 'login.html'  
    return render(request, template_name)
