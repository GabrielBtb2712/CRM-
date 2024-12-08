import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from api.home.value_const import LOGIN_URL
from api.models import Doctores,TipoTratamiento, Citas,Pacientes,Usuarios,Tratamientos
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

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



def lista_pacientes(request):
    template_name = 'sg_paciente/seguimiento.html'

    # Filtrar usuarios por tipo de usuario = 1 (clientes)
    usuarios = Usuarios.objects.filter(tipo_usuario=1)

    # Obtener el término de búsqueda desde la URL
    query = request.GET.get('search', '')
    if query:
        if query.isdigit():  # Si el query es un número, buscar por ID
            usuarios = usuarios.filter(usuario__id=query)
        else:  # Si el query no es un número, buscar en nombre, email o teléfono
            usuarios = usuarios.filter(
                Q(nombre__icontains=query) |  # Buscar por nombre
                Q(email__icontains=query) |  # Buscar por email
                Q(telefono__icontains=query)  # Buscar por teléfono
            )

    return render(request, template_name, {'usuarios': usuarios, 'search_query': query})



def detalle_paciente(request):
    template_name = 'sg_paciente/detalles.html'
    return render(request, template_name)
