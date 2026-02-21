import threading
from django.utils.deprecation import MiddlewareMixin

# Usamos ThreadLocal para guardar atributos por cada request
_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

def get_current_casino():
    return getattr(_thread_locals, 'casino', None)

class AuditMiddleware(MiddlewareMixin):
    """
    Este Middleware guarda al usuario actual en una variable de hilo local.
    Al usarse REST Framework y SessionTokenMiddleware (Bearer), 
    request.user no siempre se setea a nivel middleware tradicional.
    Aquí interceptamos `process_view` que ocurre DESPUÉS de Authentication, o en su defecto extraemos manualmente.
    """
    
    def process_request(self, request):
        # Limpiar al entrar a un nuevo request
        _thread_locals.user = None
        _thread_locals.casino = None

    def process_view(self, request, view_func, view_args, view_kwargs):
        # En DRF, request.user a veces solo está disponible dentro de la vista
        # Tratamos de obtenerlo si algún middleware anterior lo puso:
        user = getattr(request, 'user', None)
        
        if user and user.is_authenticated:
            _thread_locals.user = user
            # Si el usuario tiene casino
            if hasattr(user, 'casino'):
                _thread_locals.casino = user.casino

    def process_response(self, request, response):
        # Limpiar al salir para evitar cruce de hilos
        _thread_locals.user = None
        _thread_locals.casino = None
        return response

    def process_exception(self, request, exception):
        _thread_locals.user = None
        _thread_locals.casino = None
