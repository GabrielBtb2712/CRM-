from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

def login_view(request):
    template_name = 'login.html'
    if request.method == 'POST':
        # Obtén el correo electrónico del formulario (nombre del campo 'username' en el formulario)
        email = request.POST['username']  
        password = request.POST['password']

        try:
            # Busca el usuario en la base de datos usando el correo
            user = User.objects.get(email=email)
            # Autentica al usuario con su username y contraseña
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Inicio de sesión exitoso.')
                return redirect('index')
            else:
                messages.error(request, 'Contraseña incorrecta.')
        except User.DoesNotExist:
            messages.error(request, 'No existe un usuario con ese correo electrónico.')
    
    return render(request, template_name)

# Registrarse 

def register_view(request):
    template_name = 'register.html'  
    return render(request, template_name)

# Forget password ?

def forget_passsword(request):
    template_name = 'forget_password.html'  
    return render(request, template_name)

def log_out(request):
    template_name =''




