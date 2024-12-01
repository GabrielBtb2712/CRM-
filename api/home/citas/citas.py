from django.contrib import messages
from django.shortcuts import render, redirect
from api.models import Citas, Doctores, TipoTratamiento

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
