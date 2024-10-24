from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from api.home.value_const import LOGIN_URL
# Create your views here.
@login_required(login_url=LOGIN_URL)
def home_views(request):
    template_name = 'index.html'
    return render(request, template_name)

