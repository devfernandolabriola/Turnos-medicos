from django.contrib import admin
from .models import Especialidad, Medico, Paciente, DisponibilidadMedico, Turno

admin.site.register(Especialidad)
admin.site.register(Medico)
admin.site.register(Paciente)
admin.site.register(DisponibilidadMedico)
admin.site.register(Turno)