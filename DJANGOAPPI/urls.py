"""
URL configuration for DJANGOAPPI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api.home.home_view import home_views,cliente_home_view, citas_views,lista_pacientes,detalle_paciente,metricas,agregar_medicamento_views,proximas_citas_views
from api.login.login_view import (
    login_view,
    register_view,
    cliente_register_view,
    forget_passsword, 
    logout_view, 
    cliente_login_view)
from api.home.pagos.pagos import pagos_view
from api.home.citas.citas import citas_por_estado
#from api.home.citas.citas import citas_por_fecha


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('forget_password/', forget_passsword, name='forget_password'),
    path('', home_views, name='index'),
    path('', metricas, name='index'),
    path('agregar_medicamento/', agregar_medicamento_views, name='agregar_medicamento_views'),
    path('proximas_citas/', proximas_citas_views, name='proximas_citas_views'),
    
    #Registro de cliente 
    path('login_cliente/', cliente_login_view, name='login_cliente'),
    path('cliente/home/', cliente_home_view, name='cliente/home'),
    path('cliente/register_cliente/', cliente_register_view, name='register_cliente'),  # Corrige aquí
    path('cliente/citas/', citas_views, name='citas_cliente'),  
    
    # Seguimiento medico del paciente 
    path('sg_paciente/seguimiento/', lista_pacientes, name='seguimientoP'),  

    #Pagos 
    
    path('sg_pagos/pagos/', pagos_view, name='pagos'),
    path('sg_paciente/sg_citas/', citas_por_estado, name='sg_citas'),
    #  path('sg_paciente/sg_citas/', citas_por_fecha, name='sg_citas'),
    path('sg_paciente/detalles<int:id>/', detalle_paciente, name='detalle_paciente'),





    

]
