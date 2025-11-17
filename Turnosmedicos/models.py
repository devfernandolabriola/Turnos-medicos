from django.db import models
from django.contrib.auth.models import User

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

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

    class Meta:
        unique_together = ('medico', 'fecha', 'hora')

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.medico}"
