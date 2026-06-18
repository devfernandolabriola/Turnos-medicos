from rest_framework import routers
from django.urls import path
from . import views

from .views import (
    EspecialidadViewSet,
    MedicoViewSet,
    PacienteViewSet,
    DisponibilidadMedicoViewSet,
    TurnoViewSet
)

router = routers.DefaultRouter()
router.register(r'especialidades', EspecialidadViewSet)
router.register(r'medicos', MedicoViewSet)
router.register(r'pacientes', PacienteViewSet)
router.register(r'disponibilidades', DisponibilidadMedicoViewSet)
router.register(r'turnos', TurnoViewSet)

urlpatterns = router.urls
print("Cargando URLs OK")

urlpatterns = [
    path('tomar-turno/', views.tomar_turno, name='tomar_turno'),
    path('ajax/medicos/', views.ajax_medicos, name='ajax_medicos'),
    path('ajax/turnos/', views.ajax_turnos, name='ajax_turnos'),
    path('mis-turnos/', views.mis_turnos, name='mis_turnos'),
    path('ajax/fechas/', views.ajax_fechas, name='ajax_fechas'),
    path('tomar_turno_recepcionista/', views.tomar_turno_recepcionista, name='turno_recepcionista'),
    path('ajax/consultorios/', views.ajax_consultorios, name='ajax_consultorios'),
    path('ajax/buscar-pacientes/', views.buscar_pacientes_ajax, name='buscar_pacientes_ajax'),
    path('panel-recepcionista/', views.panel_turnos_recepcionista, name='panel_turnos_recepcionista'),
    path('panel-recepcionista/cancelar/<int:turno_id>/', views.cancelar_turno_recepcionista, name='cancelar_turno_recepcionista'),
    path('panel-recepcionista/asistio/<int:turno_id>/', views.asistio_turno_recepcionista, name='asistio_turno_recepcionista'),
]

