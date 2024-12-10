from django.shortcuts import render
from django.db.models import Sum
from api.models import Pagos

def pagos_view(request):
    # Obtener los totales de pagos por método de pago
    pagos_por_metodo = Pagos.objects.values('metodo_pago').annotate(total=Sum('monto'))

    # Obtener los totales de pagos por estado (si es necesario)
    pagos_estado = Pagos.objects.values('estado').annotate(total=Sum('monto'))

    # Crear listas para los datos del gráfico
    metodos = [pago['metodo_pago'] for pago in pagos_por_metodo]
    totales_metodos = [pago['total'] for pago in pagos_por_metodo]

    # Pasar los datos a la plantilla
    context = {
        'metodos': metodos,
        'totales_metodos': totales_metodos,
        'pagos_estado': pagos_estado,  # Para mostrar los pagos por estado
    }
    return render(request, 'sg_pagos/pagos.html', context)
