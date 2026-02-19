"""
Clase de autenticación personalizada para Django REST Framework
que usa session_token desde localStorage en lugar de JWT o sesiones.
"""

from rest_framework import authentication
from rest_framework import exceptions
from Usuarios.models import Usuarios


class SessionTokenAuthentication(authentication.BaseAuthentication):
    """
    Autenticación personalizada que lee el session_token del header Authorization.
    Formato esperado: Authorization: Bearer {session_token}
    
    Esta clase permite que DRF reconozca la autenticación y desactive
    automáticamente la verificación CSRF para endpoints autenticados.
    """
    
    def authenticate(self, request):
        # Obtener el header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None  # No hay autenticación
        
        # Formato esperado: "Bearer {token}"
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise exceptions.AuthenticationFailed('Formato de token inválido')
        
        token = parts[1]
        
        try:
            # Buscar usuario por session_token
            user = Usuarios.objects.select_related('casino', 'rol').get(
                session_token=token,
                esta_activo=True
            )
            
            # Retornar tupla (user, auth) donde auth puede ser None o el token
            return (user, token)
            
        except Usuarios.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token inválido o usuario no activo')
    
    def authenticate_header(self, request):
        """
        Retorna el string que se usa en el header WWW-Authenticate
        cuando falla la autenticación (HTTP 401).
        """
        return 'Bearer realm="api"'
