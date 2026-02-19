"""
Middleware personalizado para autenticación basada en session_token
sin usar sesiones de Django. Lee el token del header Authorization
y asigna el usuario correspondiente a request.user.
"""

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from Usuarios.models import Usuarios


class SessionTokenMiddleware(MiddlewareMixin):
    """
    Middleware que valida el session_token del header Authorization
    y asigna el usuario autenticado a request.user.
    """
    
    def process_request(self, request):
        # Obtener el token del header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            request.user = AnonymousUser()
            return None
        
        # Formato esperado: "Bearer {token}"
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            request.user = AnonymousUser()
            return None
        
        token = parts[1]
        
        try:
            # Buscar usuario por session_token
            user = Usuarios.objects.select_related('casino', 'rol').get(
                session_token=token,
                esta_activo=True
            )
            request.user = user
        except Usuarios.DoesNotExist:
            request.user = AnonymousUser()
        
        return None
