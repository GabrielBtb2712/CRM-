from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from api.home.value_const import LOGIN_URL
# Create your views here.
@login_required(login_url=LOGIN_URL)
def home_views(request):
    template_name = 'index.html'
    return render(request, template_name)


def cliente_home_view(request):
    template_name = 'cliente/home.html'
    nombre_completo = f"{request.user.first_name} {request.user.last_name}"
    context = {
                'nombre_usuario': nombre_completo
    }
    return render(request, template_name, context)



def citas_views(request):
    template_name = 'cliente/citas.html'
    return render(request, template_name)
