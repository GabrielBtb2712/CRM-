from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout  # Importa la función logout de Django
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from api.models import Usuarios, TipoUsuario, Doctores, Especialidad



def cliente_login_view(request):
    template_name = 'cliente/login_cliente.html'
    
    # Verifica si el usuario ya está autenticado
    if request.user.is_authenticated:
        return redirect('cliente/home')

    # Verifica si el método de solicitud es POST
    if request.method == 'POST':
        # Obtén el correo electrónico y la contraseña del formulario
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Busca el usuario en la base de datos usando el correo
            user = User.objects.get(email=email)

            # Obtén el objeto de la relación `Usuarios` para verificar el tipo de usuario
            usuario = Usuarios.objects.get(usuario=user)

            # Verifica si el usuario tiene el tipo de usuario permitido
            tipo_usuario_cliente = TipoUsuario.objects.get(tipo_usuario_id=1)
            if usuario.tipo_usuario == tipo_usuario_cliente:  # Verifica el tipo de usuario

                # Autentica al usuario con su username y contraseña
                user = authenticate(request, username=user.username, password=password)

                if user is not None:
                    login(request, user)
                    messages.success(request, 'Inicio de sesión exitoso.')
                    return redirect('cliente/home')
                else:
                    messages.error(request, 'Credenciales de inicio de sesión inválidas')
            else:
                messages.error(request, 'No tienes permiso para iniciar sesión')

        except User.DoesNotExist:
            messages.error(request, 'No existe un usuario con ese correo electrónico')
        except Usuarios.DoesNotExist:
            messages.error(request, 'No se encontró un perfil asociado al usuario')
        except TipoUsuario.DoesNotExist:
            messages.error(request, 'Tipo de usuario no encontrado')

    return render(request, template_name)
# Registro de cliente

def cliente_register_view(request):
    template_name = 'cliente/register_cliente.html'

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password') 
        confirm_password = request.POST.get('confirm_password')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        telefono = request.POST.get('telefono')

        # Validar que las contraseñas coinciden
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, template_name)

        # Validar que el correo electrónico no esté registrado en el modelo `User`
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Ya hay una cuenta con este correo electrónico.')
            return render(request, template_name)

        try:
            # Crear el usuario de Django
            user = User.objects.create_user(
                username=email,  # Puedes usar el correo como nombre de usuario
                password=password,
                email=email,
                first_name=nombre,
                last_name=apellido
            )

            # Crear una instancia de `Usuarios` y asociarla al `User` recién creado
            tipo_usuario = TipoUsuario.objects.get(tipo_usuario_id=1)  # Asumiendo tipo de usuario con ID 1
            usuario_personalizado = Usuarios.objects.create(
                usuario=user,
                nombre=nombre,
                apellido=apellido,
                email=email,
                telefono=telefono,
                tipo_usuario=tipo_usuario
            )

           
            messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
            return redirect('login_cliente')  # Redirige a la vista de inicio de sesión

        except Exception as e:
            messages.error(request, f'Error al registrar el usuario: {e}')
            return render(request, template_name)

    return render(request, template_name)

# Login de Doctor

def login_view(request):
    template_name = 'login.html'
    
    # Verifica si el usuario ya está autenticado
    if request.user.is_authenticated:
        return redirect('index')

    # Verifica si el método de solicitud es POST
    if request.method == 'POST':
        # Obtén el correo electrónico y la contraseña del formulario
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Busca el usuario en la base de datos usando el correo
            user = User.objects.get(email=email)

            # Obtén el objeto de la relación `Usuarios` para verificar el tipo de usuario
            usuario = Usuarios.objects.get(usuario=user)

            # Verifica si el usuario tiene el tipo de usuario permitido
            tipo_usuario_cliente = TipoUsuario.objects.get(tipo_usuario_id=0)
            if usuario.tipo_usuario == tipo_usuario_cliente:  # Verifica el tipo de usuario

                # Autentica al usuario con su username y contraseña
                user = authenticate(request, username=user.username, password=password)

                if user is not None:
                    login(request, user)
                    messages.success(request, 'Inicio de sesión exitoso.')
                    return redirect('index')
                else:
                    messages.error(request, 'Credenciales de inicio de sesión inválidas')
            else:
                messages.error(request, 'No tienes permiso para iniciar sesión')

        except User.DoesNotExist:
            messages.error(request, 'No existe un usuario con ese correo electrónico')
        except Usuarios.DoesNotExist:
            messages.error(request, 'No se encontró un perfil asociado al usuario')
        except TipoUsuario.DoesNotExist:
            messages.error(request, 'Tipo de usuario no encontrado')

    return render(request, template_name)

def register_view(request):
    template_name = 'register.html'

    # Obtener todas las especialidades para el formulario
    especialidades = Especialidad.objects.all()

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password') 
        confirm_password = request.POST.get('confirm_password')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        telefono = request.POST.get('telefono')
        especialidad_id = request.POST.get('especialidad')  # Obtener el ID de especialidad seleccionada

        # Validaciones...
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, template_name, {'especialidades': especialidades})

        # Comprobación de email duplicado...
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Ya hay una cuenta con este correo electrónico.')
            return render(request, template_name, {'especialidades': especialidades})

        try:
            # Crear usuario y objeto Usuarios
            user = User.objects.create_user(
                username=email,
                password=password,
                email=email,
                first_name=nombre,
                last_name=apellido
            )
            tipo_usuario = TipoUsuario.objects.get(tipo_usuario_id=0)
            usuario_personalizado = Usuarios.objects.create(
                usuario=user,
                nombre=nombre,
                apellido=apellido,
                email=email,
                telefono=telefono,
                tipo_usuario=tipo_usuario
            )

            # Crear doctor con especialidad seleccionada
            especialidad = Especialidad.objects.get(especialidad_id=especialidad_id)
            Doctores.objects.create(
                usuario=usuario_personalizado,
                especialidad=especialidad
            )

            messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Error al registrar el usuario: {e}')
            return render(request, template_name, {'especialidades': especialidades})

    return render(request, template_name, {'especialidades': especialidades})

# Forget password ?

def forget_passsword(request):
    template_name = 'forget_password.html'  
    return render(request, template_name)


def logout_view(request):
    logout(request)
    
    # Verifica el origen de la solicitud para determinar la redirección
    referer = request.META.get('HTTP_REFERER', '')
    
    if 'index' in referer:
        # Si la URL de referencia contiene 'index', redirige a 'login'
        return redirect('login')
    elif 'home' in referer:
        # Si la URL de referencia contiene 'home', redirige a 'login_cliente'
        return redirect('login_cliente')
    else:
        # Redirección predeterminada en caso de que no coincida ninguna condición
        return redirect('login')    
