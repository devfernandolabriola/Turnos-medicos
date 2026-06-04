from django.db import models
from django.contrib.auth.models import User

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)
    duracion_turno = models.IntegerField(default=15)

    def __str__(self):
        return self.nombre
    

class ObraSocial(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class Consultorio(models.Model):
    codigo = models.CharField(max_length=100,primary_key=True,db_column='Codigo')
    observaciones = models.TextField(max_length=400, null=True,blank=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE,db_column='especialidadid')

    def __str__(self):
        return f"Consultorio {self.codigo} - {self.especialidad.nombre}"

class Medico(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.IntegerField()
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"


class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)
    es_recepcionista = models.BooleanField(default=False)
    obrasocial = models.ForeignKey(ObraSocial, on_delete=models.CASCADE)
    correo = models.EmailField(max_length=100, null=True, blank=True)
    telefono = models.BigIntegerField(null=True, blank=True)
    numero_asociado = models.CharField(max_length=200, null=True, blank=True)


    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

class DisponibilidadMedico(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    dia_semana = models.IntegerField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

class Turno(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    paciente = models.ForeignKey(Paciente, null=True, blank=True, on_delete=models.SET_NULL)
    disponible = models.BooleanField(default=True)
    consultorio_codigo = models.ForeignKey(Consultorio, on_delete=models.CASCADE, db_column='Consultorio_codigo')
    estado = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = ('medico', 'fecha', 'hora')

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.medico}"

class Licencia(models.Model):
    motivo = models.CharField(max_length=200)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    medicoid = models.ForeignKey('Turnosmedicos.Medico', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'turnosmedicos_licencia'


