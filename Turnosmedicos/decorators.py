from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def es_recepcionista(user):
    if user.is_authenticated and user.groups.filter(name='Recepcionista').exists():
        return True
    raise PermissionDenied