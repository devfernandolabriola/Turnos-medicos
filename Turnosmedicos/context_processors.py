from .models import Paciente

def paciente_context(request):
    paciente_id = request.session.get("paciente_id")

    if paciente_id:
        try:
            paciente = Paciente.objects.get(id=paciente_id)
            return {"paciente_logueado": paciente}
        except Paciente.DoesNotExist:
            pass
    
    return {"paciente_logueado": None}