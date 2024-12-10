from turtle import pd
from django.contrib import messages
from django.shortcuts import render, redirect
from api.models import Citas, Doctores, TipoTratamiento,Tratamientos
import plotly.express as px
import plotly.io as pio
from django.db import models
from django.db.models import Q,Count
import pandas as pd  # Asegúrate de importar pandas


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





# Vista para tipos de tratamientos más solicitados
def tipos_tratamientos_mas_solicitados(request):
    
    # Consulta para contar los tratamientos más solicitados
    tipos_tratamientos = Tratamientos.objects.annotate(
        count_solicitudes=Count('citas', filter=Q(citas__isnull=False))  # Usamos Count para contar citas
    ).order_by('-count_solicitudes')[:10]  # Tomar los 10 más solicitados

    # Si no hay datos, mostrar mensaje
    if not tipos_tratamientos.exists():
        return render(request, "sg_paciente/sg_citas.html", {
            "plot_html": None,
            "message": "No hay datos disponibles para mostrar."
        })

    # Convertir los datos en un formato adecuado para Plotly
    data = {
        "Tipo de Tratamiento": [tipo.tipo_tratamiento.tipo_tratamiento for tipo in tipos_tratamientos],
        "Solicitudes": [tipo.count_solicitudes for tipo in tipos_tratamientos],
    }
    df = pd.DataFrame(data)

    # Crear la gráfica con Plotly
    fig = px.bar(
        df,
        x="Tipo de Tratamiento",
        y="Solicitudes",
        title="Tipos de Tratamientos más solicitados",
        labels={"Tipo de Tratamiento": "Tipo de Tratamiento", "Solicitudes": "Número de Solicitudes"},
    )
    fig.update_layout(xaxis=dict(tickangle=-45))  # Inclinar etiquetas si son largas

    # Convertir la gráfica a HTML
    plot_html = fig.to_html(full_html=False)

    # Renderizar la plantilla con la gráfica
    return render(request, "sg_paciente/sg_tratamientos_demandados.html", {
        "plot_html": plot_html,
        "message": None
    })
