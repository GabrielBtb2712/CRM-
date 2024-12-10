import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from api.home.value_const import LOGIN_URL
from api.models import Doctores,TipoTratamiento, Citas,Pacientes,Usuarios,Pagos,RegistrosClinicos
from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied


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


def detalle_paciente(request, id):
    template_name = 'sg_paciente/detalles.html'

    
    # Obtener el objeto Usuarios asociado al usuario autenticado
    usuario_logueado = get_object_or_404(Usuarios, usuario=request.user)
    # Verificar si el usuario es médico (tipo_usuario = 0)
    if usuario_logueado.tipo_usuario.tipo_usuario_id != 0:  # 0 = Médico
        raise PermissionDenied("Solo los médicos pueden acceder a esta sección.")

    # Obtener el paciente
    paciente = get_object_or_404(Pacientes, paciente_id=id)
    # Si ya existe un registro clínico para este paciente, obtén el primero
    registro_clinico = RegistrosClinicos.objects.filter(paciente=paciente).first()

    if request.method == 'POST':
        # Recuperar los datos del formulario
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        peso = request.POST.get('peso')
        estatura = request.POST.get('estatura')
        presion_sistolica = request.POST.get('presion_sistolica')
        presion_diastolica = request.POST.get('presion_diastolica')
        frecuencia_cardiaca = request.POST.get('frecuencia_cardiaca')
        temperatura = request.POST.get('temperatura', None)
        saturacion_oxigeno = request.POST.get('saturacion_oxigeno', None)

        # Si existe un registro clínico, actualízalo; de lo contrario, crea uno nuevo
        if registro_clinico:
            registro_clinico.fecha = fecha
            registro_clinico.hora = hora
            registro_clinico.peso = peso
            registro_clinico.estatura = estatura
            registro_clinico.presion_sistolica = presion_sistolica
            registro_clinico.presion_diastolica = presion_diastolica
            registro_clinico.frecuencia_cardiaca = frecuencia_cardiaca
            registro_clinico.temperatura = temperatura
            registro_clinico.saturacion_oxigeno = saturacion_oxigeno
            registro_clinico.save()
        else:
            registro_clinico = RegistrosClinicos.objects.create(
                paciente=paciente,
                fecha=fecha,
                hora=hora,
                peso=peso,
                estatura=estatura,
                presion_sistolica=presion_sistolica,
                presion_diastolica=presion_diastolica,
                frecuencia_cardiaca=frecuencia_cardiaca,
                temperatura=temperatura,
                saturacion_oxigeno=saturacion_oxigeno,
                registrado_por=usuario_logueado  # Asignar la instancia de Usuarios
            )

        return redirect('seguimientoP')  # Redirige a la lista de pacientes

    return render(request, template_name, {
        'paciente': paciente,
        'registro_clinico': registro_clinico
    })












def metricas(request):
    # Número total de clientes
    num_clientes = Usuarios.objects.count()
    
    # Total de pacientes atendidos
    num_pacientes = Pacientes.objects.count()
    
    # Total de citas programadas
    num_citas = Citas.objects.count()

    # Total de pagos realizados
    num_pagos = Pagos.objects.filter(estado='pagado').count()

    # Obtener las fechas para los últimos 30 días
    hace_30_dias = datetime.datetime.now() - datetime.timedelta(days=30)

    # Citas en los últimos 30 días
    citas_30_dias = Citas.objects.filter(fecha__gte=hace_30_dias).count()

    # Pagos realizados en los últimos 30 días
    pagos_30_dias = Pagos.objects.filter(fecha__gte=hace_30_dias, estado='pagado').count()

    context = {
        'num_clientes': num_clientes,
        'num_pacientes': num_pacientes,
        'num_citas': num_citas,
        'num_pagos': num_pagos,
        'citas_30_dias': citas_30_dias,  # Añadir las citas en los últimos 30 días
        'pagos_30_dias': pagos_30_dias,  # Añadir los pagos en los últimos 30 días
    }

    return render(request, 'index.html', context)