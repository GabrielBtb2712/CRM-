from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout  # Importa la función logout de Django
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password

def login_view(request):
    template_name = 'login.html'

    # Verifica si el usuario ya estácd autenticado
    if request.user.is_authenticated:
        return redirect('index')

    # Verifica si el método de solicitud es POST
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
                messages.error(request, 'Credenciales de inicio de sesión inválidas')
        except User.DoesNotExist:
            messages.error(request, 'No existe un usuario con ese correo electrónico')

    return render(request, template_name)


def register_view(request):
    template_name = "register.html"

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validar que las contraseñas coinciden
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, template_name)

        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return render(request, template_name)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Ya hay una cuenta con este correo electrónico.')
            return render(request, template_name)

        # Crear el nuevo usuario con contraseña hasheada
        try:
            user = User(
                username=username, 
                email=email, 
                password=make_password(password),
                is_active=0  # Desactivar el usuario después de registrarlo
            )
            user.save()
            messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
            return redirect('login')  # Redirige a la página de inicio de sesión
        except Exception as e:
            messages.error(request, f'Error al registrar el usuario: {e}')
            return render(request, template_name)

    return render(request, template_name)

# Forget password ?

def forget_passsword(request):
    template_name = 'forget_password.html'  
    return render(request, template_name)


def logout_view(request):
    logout(request)  # Esto cierra la sesión del usuario actual
    return redirect('login') 


