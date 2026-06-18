from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from .models import Especialidad
from .models import Medico
from .models import Turno
from .models import DisponibilidadMedico
from .models import Paciente, Consultorio
from .serializers import MedicoSerializer
from .serializers import EspecialidadSerializer
from .serializers import TurnoSerializer
from .serializers import DisponibilidadMedicoSerializer
from .serializers import PacienteSerializer
from rest_framework import viewsets
from .forms import LoginForm, RegisterForm, SeleccionTurnoForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .decorators import es_recepcionista
from datetime import datetime, timedelta
import locale
from django.db.models import Q
from django.utils import timezone



class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer

class DisponibilidadMedicoViewSet(viewsets.ModelViewSet):
    queryset = DisponibilidadMedico.objects.all()
    serializer_class = DisponibilidadMedicoSerializer

class TurnoViewSet(viewsets.ModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer

def index(request):
    paciente_id = request.session.get("paciente_id")
    if not paciente_id:
        return redirect('http://127.0.0.1:8000/login/')

    try:
        usuario_actual = Paciente.objects.get(id=paciente_id)
    except Paciente.DoesNotExist:
        request.session.flush()
        return redirect('http://127.0.0.1:8000/login/')

    if usuario_actual.es_recepcionista:
        return render(request, 'Turnosmedicos/index_recepcionista.html')
    
    return render(request, 'Turnosmedicos/index.html')

@api_view(['POST'])

def login(request):
    dni = request.data.get("dni")
    password = request.data.get("password")

    if not dni or not password:
        return Response({"error": "Debes enviar un DNI"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        paciente = Paciente.objects.get(dni=dni)
    except Paciente.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    if not check_password(password, paciente.password):
        return Response({"error": "Contraseña incorrecta"}, status=status.HTTP_400_BAD_REQUEST)
    
    request.session["paciente_id"] = paciente.id
    return Response({"mensaje": "Login correcto", "paciente_id": paciente.id})

def register(request):
    serializer = PacienteSerializer(data=request.data)
    if serializer.is_valid():
        paciente = serializer.save()
        return Response({"mensaje": "Paciente registrado", "paciente_id": paciente.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni']
            password = form.cleaned_data['password']

            try:
                paciente = Paciente.objects.get(dni=dni)
                if check_password(password, paciente.password):
                    request.session['paciente_id'] = paciente.id
                    messages.success(request, f"¡Bienvenido {paciente.nombre} {paciente.apellido}!")
                    return redirect('index') 
                else:
                    messages.error(request, "Contraseña incorrecta")
            except Paciente.DoesNotExist:
                messages.error(request, "Paciente no encontrado")
        
        return render(request, 'Turnosmedicos/login.html', {'form': form})
        
    else:
        form = LoginForm()
        
    return render(request, 'Turnosmedicos/login.html', {'form': form})

    return render(request, "Turnosmedicos/login.html", {"form": form})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            serializer = PacienteSerializer(data=form.cleaned_data)
            if serializer.is_valid():
                dni = serializer.validated_data['dni']
                if Paciente.objects.filter(dni=dni).exists():
                    messages.error(request, "DNI ya registrado")
                else:
                    serializer.save() 
                    messages.success(request, "Paciente registrado con exito.")
                    return redirect('index')
            else:
                messages.error(request, serializer.errors)
    else:
        form = RegisterForm()

    return render(request, "Turnosmedicos/register.html", {"form": form})

def logout_view(request):
    request.session.flush()
    return redirect('index')

def tomar_turno(request):
    # Verificar paciente logueado
    paciente_id = request.session.get('paciente_id')
    if not paciente_id:
        return redirect('login')
    paciente = Paciente.objects.get(id=paciente_id)

    # Traer todas las especialidades para el dropdown
    especialidades = Especialidad.objects.all()

    if request.method == 'POST':
        medico_id = request.POST.get('medico')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')

        if not (medico_id and fecha_str and hora_str):
            messages.error(request, "Debe seleccionar especialidad, médico, fecha y horario.")
            return redirect('tomar_turno')

        # Obtener objeto medico, fecha y hora
        medico = Medico.objects.get(id=medico_id)
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hora = datetime.strptime(hora_str, "%H:%M").time()

        # Crear el turno en la DB
        turno = Turno.objects.create(
            medico=medico,
            paciente=paciente,
            fecha=fecha,
            hora=hora,
            disponible=False
        )

        # Mensaje de éxito con detalle
        messages.success(request, f"✅ Turno confirmado con {medico.nombre} {medico.apellido} el {fecha} a las {hora.strftime('%H:%M')}.")

        return redirect('mis_turnos')

    # GET → renderizar formulario
    return render(request, 'Turnosmedicos/tomar_turno.html', {
        'especialidades': especialidades,
        'paciente_logueado': paciente  # Por si lo querés usar en el template
    })


def mis_turnos(request):
    paciente_id = request.session.get('paciente_id')
    if not paciente_id:
        return redirect('login')

    paciente = Paciente.objects.get(id=paciente_id)

    if request.method == 'POST':
        turno_id = request.POST.get('turno_id')
        try:
            turno = Turno.objects.get(id=turno_id, paciente=paciente)
            turno.delete()
            messages.success(request, '✅ El turno fue cancelado correctamente.')
        except Turno.DoesNotExist:
            messages.error(request, '❌ No se pudo cancelar el turno.')

        return redirect('mis_turnos')

    turnos = Turno.objects.filter(paciente=paciente).order_by('fecha', 'hora')

    return render(request, 'Turnosmedicos/mis_turnos.html', {
        'turnos': turnos,
        'paciente_logueado': paciente
    })


def ajax_medicos(request):
    especialidad_id = request.GET.get('especialidad')
    medicos = Medico.objects.filter(especialidad_id=especialidad_id).values('id', 'nombre', 'apellido')
    # Retornar nombre completo
    medicos_list = [{'id': m['id'], 'nombre': f"{m['apellido']}, {m['nombre']}"} for m in medicos]
    return JsonResponse(medicos_list, safe=False)


def ajax_turnos(request):
    medico_id = request.GET.get('medico')
    fecha_str = request.GET.get('fecha')

    if not medico_id or not fecha_str:
        return JsonResponse([], safe=False)

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    dia_semana = fecha.weekday()

    medico = Medico.objects.get(id=medico_id)

    try:
        # Traemos al médico e indicamos que traiga también su especialidad relacionada
        medico = Medico.objects.select_related('especialidad').get(id=medico_id)
    except Medico.DoesNotExist:
        return JsonResponse([], safe=False)

    try:
        disponibilidad = DisponibilidadMedico.objects.get(
            medico=medico, 
            dia_semana=dia_semana
        )
    except DisponibilidadMedico.DoesNotExist:
        return JsonResponse([], safe=False) 

  
    turnos_ocupados = Turno.objects.filter(
        medico=medico,
        fecha=fecha,
        disponible=False
    ).values_list('hora', flat=True)


    hora = datetime.combine(fecha, disponibilidad.hora_inicio)
    fin = datetime.combine(fecha, disponibilidad.hora_fin)

    minutos_duracion = medico.especialidad.duracion_turno if medico.especialidad.duracion_turno else 15

    turnos = []
    while hora <= fin:
        if hora.time() not in turnos_ocupados:
            turnos.append({
                'id': hora.strftime("%H:%M"),
                'hora': hora.strftime("%H:%M")
            })
        hora += timedelta(minutes=minutos_duracion)

    return JsonResponse(turnos, safe=False)

import locale
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8") 

import locale
from datetime import datetime, timedelta


locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

def ajax_fechas(request):
    medico_id = request.GET.get('medico')
    medico = Medico.objects.get(id=medico_id)


    disponibilidades = DisponibilidadMedico.objects.filter(medico=medico)
    dias_validos = [d.dia_semana for d in disponibilidades]

    fechas = []
    hoy = datetime.today().date()

    for i in range(60):
        fecha = hoy + timedelta(days=i)
        if fecha.weekday() in dias_validos:

            texto = fecha.strftime("%A %d de %B").capitalize()

            fechas.append({
                "valor": fecha.strftime("%Y-%m-%d"),
                "texto": texto
            })

    return JsonResponse(fechas, safe=False)


def tomar_turno_recepcionista(request):
    # Traemos todos los pacientes de la base de datos
    pacientes = Paciente.objects.all().order_by('apellido', 'nombre')
    
    # Traemos las especialidades (que ya tenías en tu lógica)
    especialidades = Especialidad.objects.all()
    
    context = {
        'pacientes': pacientes,
        'especialidades': especialidades,
    }
    
    return render(request, "Turnosmedicos/tomar_turno_recepcionista.html", context)


def tomar_turno_recepcionista(request):
    
    # Traer todas las especialidades para el dropdown
    especialidades = Especialidad.objects.all()
    pacientes = Paciente.objects.all().order_by('apellido', 'nombre')

    if request.method == 'POST':
        paciente_id = request.POST.get('paciente')
        medico_id = request.POST.get('medico')
        consultorio_id = request.POST.get('consultorio_codigo')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')

        if not (paciente_id and medico_id and consultorio_id and fecha_str and hora_str):
            messages.error(request, "Debe seleccionar Paciente, especialidad, médico, consultorio, fecha y horario.")
            return redirect('turno_recepcionista')

        # Obtener objeto paciente, medico, fecha y hora
        paciente = Paciente.objects.get(id=paciente_id)
        medico = Medico.objects.get(id=medico_id)
        consultorio = Consultorio.objects.get(codigo=consultorio_id)
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hora = datetime.strptime(hora_str, "%H:%M").time()

        # Crear el turno en la DB
        turno = Turno.objects.create(
            medico=medico,
            paciente=paciente,
            consultorio_codigo=consultorio,
            fecha=fecha,
            hora=hora,
            disponible=False,
            estado=1
        )

        # Mensaje de éxito con detalle
        messages.success(request, f"✅ Turno confirmado con {medico.nombre} {medico.apellido} el {fecha} a las {hora.strftime('%H:%M')}.")

        return redirect('index')

    # GET → renderizar formulario
    return render(request, 'Turnosmedicos/tomar_turno_recepcionista.html', {
        'especialidades': especialidades,
        'pacientes': pacientes  # Por si lo querés usar en el template
    })

def ajax_consultorios(request):
    especialidad_id = request.GET.get('especialidad')
    
    # 🛠️ CORRECCIÓN: Filtramos usando el nombre del atributo 'especialidad' 
    # que definiste en la ForeignKey del modelo Consultorio
    consultorios = Consultorio.objects.filter(especialidad=especialidad_id)
    
    # Armamos la lista para mandar a JS
    data = []
    for c in consultorios:
        data.append({
            'codigo': c.codigo,
            'observaciones': c.observaciones
        })
        
    return JsonResponse(data, safe=False)

def buscar_pacientes_ajax(request):
    term = request.GET.get('q', '') # Captura lo que el usuario escribe
    pacientes = Paciente.objects.all()
    
    if term:
        # Busca por coincidencia parcial en nombre, apellido o DNI
        pacientes = pacientes.filter(
            Q(nombre__icontains=term) | 
            Q(apellido__icontains=term) | 
            Q(dni__icontains=term)
        )[:10] # Limitamos a 10 resultados por rendimiento
    
    # Select2 requiere estrictamente un diccionario con la clave 'results' 
    # y que cada objeto tenga 'id' y 'text'.
    results = [
        {
            'id': p.id, 
            'text': f"{p.apellido}, {p.nombre} (DNI: {p.dni})"
        } for p in pacientes
    ]
    
    return JsonResponse({'results': results})

def panel_turnos_recepcionista(request):
    fecha_filtro_str = request.GET.get('fecha')
    
    if fecha_filtro_str:
        fecha_filtro = datetime.strptime(fecha_filtro_str, "%Y-%m-%d").date()
    else:
        fecha_filtro = timezone.now().date()

    turnos = Turno.objects.filter(fecha=fecha_filtro).select_related('medico', 'paciente', 'consultorio_codigo').order_by('hora', 'medico__apellido')

    MAPEO_CONSULTORIOS = {
        'CA-01': 'Consultorio 1',
        'CM-01': 'Consultorio 2',
        'CM-02': 'Consultorio 3',
        'DE-01': 'Consultorio 4',
        'GI-01': 'Consultorio 5',
        'PE-01': 'Consultorio 6',
        'TR-01': 'Consultorio 7',
    }

    ESTADOS = {
        1: "Reservado",
        2: "Asistió",
        3: "Cancelado",
    }

    for t in turnos:
        t.estado_texto = ESTADOS.get(t.estado, "Desconocido")
        codigo_real = t.consultorio_codigo.codigo if t.consultorio_codigo else ""
        t.consultorio_nombre_lindo = MAPEO_CONSULTORIOS.get(codigo_real, f"Consultorio {codigo_real}")

    return render(request, 'Turnosmedicos/panel_turnos.html', {
        'turnos': turnos,
        'fecha_filtro': fecha_filtro.strftime("%Y-%m-%d"), # Lo mandamos formateado para el input date
        'hoy': timezone.now().date()
    })


def cancelar_turno_recepcionista(request, turno_id):
    if request.method == 'POST':
        turno = get_object_or_404(Turno, id=turno_id)
        
        # Cambiamos el estado a 3 (Cancelado) y lo liberamos para que se pueda volver a tomar si se quiere
        turno.estado = 3
        turno.disponible = True  
        turno.save()
        
        messages.warning(request, f"❌ El turno de las {turno.hora.strftime('%H:%M')} fue cancelado correctamente.")
        
        # Redirigimos manteniendo la fecha en la que estaba parada la recepcionista
        return redirect(f"/api/panel-recepcionista/?fecha={turno.fecha}")
        
    return redirect('panel_turnos_recepcionista')

def asistio_turno_recepcionista(request, turno_id):
    if request.method == 'POST':
        turno = get_object_or_404(Turno, id=turno_id)
        
        # Estado 2 = Asistió. Mantenemos disponible = False porque el turno ya se usó.
        turno.estado = 2
        turno.save()
        
        messages.success(request, f"¡Asistencia confirmada para el turno de las {turno.hora.strftime('%H:%M')}!")
        return redirect(f"/api/panel-recepcionista/?fecha={turno.fecha}")
        
    return redirect('panel_turnos_recepcionista')