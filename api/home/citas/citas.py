from django.contrib import messages
from django.shortcuts import render, redirect
from api.models import Citas, Doctores, TipoTratamiento,Pacientes,Tratamientos
import plotly.express as px
import plotly.io as pio
from django.db import models


def agendar_cita(request):
    if request.method == 'POST':
        # Obtener los valores del formulario
        servicio = request.POST.get('servicio')
        doctor_id = request.POST.get('doctor')
        tratamiento_id = request.POST.get('tratamiento')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        comentarios = request.POST.get('comentarios')

        # Asegúrate de que los campos no estén vacíos
        if not servicio or not doctor_id or not tratamiento_id or not fecha or not hora:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('agendar_cita')  # Redirigir al mismo formulario en caso de error

        # Obtener el paciente (suponiendo que ya está logueado)
        try:
            paciente = Pacientes.objects.get(user=request.user)
        except Pacientes.DoesNotExist:
            messages.error(request, "Paciente no encontrado.")
            return redirect('agendar_cita')

        # Obtener el doctor y el tratamiento
        try:
            doctor = Doctores.objects.get(doctor_id=doctor_id)
            tratamiento = Tratamientos.objects.get(tratamiento_id=tratamiento_id)
        except (Doctores.DoesNotExist, Tratamientos.DoesNotExist):
            messages.error(request, "El doctor o tratamiento no existen.")
            return redirect('agendar_cita')

        # Crear y guardar la cita
        nueva_cita = Citas(
            paciente=paciente,
            doctor=doctor,
            tratamiento=tratamiento,
            servicio=servicio,
            fecha=fecha,
            hora=hora,
            comentarios=comentarios,
        )
        nueva_cita.save()

        # Mostrar mensaje de éxito
        messages.success(request, "Cita agendada exitosamente.")
        return redirect('nombre_de_la_vista')  # Redirige a una vista de éxito o a la lista de citas

    # Si el formulario es GET, pasar las opciones al formulario
    servicios = Citas.SERVICIOS
    doctores = Doctores.objects.all()
    tratamientos = Tratamientos.objects.all()

    return render(request, 'agendar_cita.html', {
        'servicios': servicios,
        'doctores': doctores,
        'tratamientos': tratamientos,
    })

def citas(request):
    doctores = Doctores.objects.all()
    tratamiento = TipoTratamiento.objects.all()
    servicios = Citas.SERVICIOS  # Obtener la lista de servicios definida en el modelo

    # Verificar si la solicitud es POST
    if request.method == 'POST':
        # Capturar los datos del formulario
        doctor_id = request.POST.get('doctor')
        servicio = request.POST.get('servicio')
        tratamiento_id = request.POST.get('tratamiento')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        comentarios = request.POST.get('comentarios')

        # Obtener el doctor y tratamiento desde la base de datos
        doctor = Doctores.objects.get(doctor_id=doctor_id)
        tratamiento = TipoTratamiento.objects.get(tratamiento_id=tratamiento_id) if tratamiento_id else None

        # Crear la nueva cita
        nueva_cita = Citas(
            paciente=request.user.paciente,  # Asegúrate de obtener el paciente correctamente
            doctor=doctor,
            servicio=servicio,
            tratamiento=tratamiento,
            fecha=fecha,
            hora=hora,
            comentarios=comentarios
        )

        # Guardar la cita en la base de datos
        nueva_cita.save()

        # Enviar el mensaje de éxito
        messages.success(request, '¡Cita creada con éxito!')

        # Redirigir de nuevo a la misma página o a una página de confirmación
        return redirect('citas')

    context = {
        'doctores': doctores,
        'tratamiento': tratamiento,
        'servicios': servicios
    }

    return render(request, 'cliente/citas.html', context)



def citas_por_estado(request):
    # Obtener las citas y agrupar por el estado
    estado_citas = Citas.objects.values('estado').annotate(count=models.Count('estado'))

    # Extraer los datos para la gráfica
    estados = [estado['estado'] for estado in estado_citas]
    counts = [estado['count'] for estado in estado_citas]

    # Crear la gráfica circular
    fig = px.pie(names=estados, values=counts, title="Citas por Estado")

    # Convertir la gráfica a HTML
    graph_html = pio.to_html(fig, full_html=False)

    # Renderizar la página con la gráfica
    return render(request, 'sg_paciente/sg_citas.html', {'graph_html': graph_html})