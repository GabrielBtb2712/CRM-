from django.db import models
from django.contrib.auth.models import User


class TipoUsuario(models.Model):
    tipo_usuario_id = models.AutoField(primary_key=True)
    tipo_usuario = models.CharField(max_length=255)

    class Meta:
        db_table = "tipo_usuario"

class Usuarios(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)  # Relación uno a uno con el modelo User de Django
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE)

    class Meta:
        db_table = "usuarios"
        
class Pacientes(models.Model):
    paciente_id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuarios, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField(default='1900-01-01')  # Valor predeterminado
    direccion = models.CharField(max_length=255, default='')  # Valor predeterminado vacío

    class Meta:
        db_table = "pacientes"


class Especialidad(models.Model):
    especialidad_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)  # Nombre de la especialidad

    class Meta:
        db_table = "especialidades"




class Doctores(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuarios, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)  # Clave foránea a `Especialidad`

    class Meta:
        db_table = "doctores"

        
class TipoTratamiento(models.Model):
    tipo_tratamiento_id = models.AutoField(primary_key=True)
    tipo_tratamiento = models.CharField(max_length=255)

    class Meta:
        db_table = "tipo_tratamiento"


class Tratamientos(models.Model):
    tratamiento_id = models.AutoField(primary_key=True)
    tipo_tratamiento = models.ForeignKey(
        TipoTratamiento, 
        on_delete=models.CASCADE, 
        default=1 
    ) 
    descripcion = models.TextField(default='')
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fecha_inicio = models.DateField(default='1900-01-01')
    fecha_fin = models.DateField(default='1900-01-01')

    class Meta:
        db_table = "tratamientos"



class Citas(models.Model):
    SERVICIOS = [
        ('Consulta médica', 'Consulta médica'),
        ('Asesoría', 'Asesoría'),
        ('Revisión', 'Revisión'),
        ('Otro', 'Otro'),
    ]
    
    cita_id = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctores, on_delete=models.CASCADE)
    tratamiento = models.ForeignKey(Tratamientos, on_delete=models.SET_NULL, null=True, blank=True)
    
    servicio = models.CharField(max_length=50, choices=SERVICIOS, default='Consulta médica')
    fecha = models.DateField()
    hora = models.TimeField()
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('realizada', 'Realizada'),
            ('cancelada', 'Cancelada')
        ],
        default='pendiente'
    )
    comentarios = models.TextField(blank=True, null=True)


    class Meta:
        db_table = "citas"


class Pagos(models.Model):
    pago_id = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    fecha = models.DateField(default='1900-01-01')  # Valor predeterminado
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Valor predeterminado
    metodo_pago = models.CharField(
        max_length=20,
        choices=[
            ('efectivo', 'Efectivo'),
            ('tarjeta', 'Tarjeta'),
            ('transferencia', 'Transferencia')
        ],
        default='efectivo'  # Valor predeterminado
    )
    descripcion = models.CharField(max_length=255, default='')  # Valor predeterminado vacío
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pagado', 'Pagado'),
            ('pendiente', 'Pendiente'),
            ('no pagado', 'No Pagado')
        ],
        default='pendiente'  # Valor predeterminado
    )

    class Meta:
        db_table = "pagos"

class HistorialMedico(models.Model):
    historial_id = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctores, on_delete=models.CASCADE)
    fecha = models.DateField(default='1900-01-01')  # Valor predeterminado
    descripcion = models.TextField(default='')  # Valor predeterminado vacío
    tratamientos = models.ManyToManyField(Tratamientos)

    class Meta:
        db_table = "historial_medico"
