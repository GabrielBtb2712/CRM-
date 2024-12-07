from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from api.home.value_const import LOGIN_URL
from api.models import Doctores,TipoTratamiento, Citas
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
    doctores = Doctores.objects.all()
    tratamiento = TipoTratamiento.objects.all()
    servicios = Citas.SERVICIOS  # Obtener la lista de servicios definida en el modelo
    template_name = 'cliente/citas.html'
    
    context = {
        'doctores': doctores,
        'tratamiento': tratamiento,
        'servicios': servicios  # Aquí cambiamos de 'citas' a 'servicios'
    }
    
    return render(request, template_name, context)

def proximas_citas_views(request):
    # Obtener el médico logueado (supongamos que el usuario tiene un perfil relacionado)
    medico = request.user.doctor

    # Obtener las citas asignadas a este médico, ordenadas por fecha
    proximas_citas = Citas.objects.filter(doctor=medico).order_by('fecha', 'hora')

    # Filtrar solo las citas futuras
    from datetime import date
    proximas_citas = proximas_citas.filter(fecha__gte=date.today())

    context = {
        'proximas_citas': proximas_citas
    }

    return render(request, 'medico/registro_citas.html', context)
