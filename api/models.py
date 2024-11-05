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

class Doctores(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuarios, on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=255, default='')  # Valor predeterminado vacío

    class Meta:
        db_table = "doctores"

class Tratamientos(models.Model):
    tratamiento_id = models.AutoField(primary_key=True)
    descripcion = models.TextField(default='')  # Valor predeterminado vacío
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Valor predeterminado
    fecha_inicio = models.DateField(default='1900-01-01')  # Valor predeterminado
    fecha_fin = models.DateField(default='1900-01-01')  # Valor predeterminado

    class Meta:
        db_table = "tratamientos"

class Citas(models.Model):
    cita_id = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctores, on_delete=models.CASCADE)
    fecha = models.DateField(default='1900-01-01')  # Valor predeterminado
    hora = models.TimeField(default='00:00')  # Valor predeterminado
    descripcion = models.CharField(max_length=255, default='')  # Valor predeterminado vacío
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('realizada', 'Realizada'),
            ('cancelada', 'Cancelada')
        ],
        default='pendiente'  # Valor predeterminado
    )

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
