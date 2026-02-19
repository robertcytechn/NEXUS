from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import BitacoraTecnica
from .serializers import BitacoraTecnicaSerializer
from Usuarios.models import Usuarios

class BitacoraTecnicaViewSet(viewsets.ModelViewSet):
    """
    Controlador verticalizado para las entradas de bitácora técnica.
    """
    queryset = BitacoraTecnica.objects.all().select_related(
        'ticket', 
        'usuario_tecnico'
    )
    serializer_class = BitacoraTecnicaSerializer

    def perform_create(self, serializer):
        # Obtener el ID del usuario desde el payload (localStorage del frontend)
        usuario_tecnico_id = self.request.data.get('usuario_tecnico')
        
        if usuario_tecnico_id:
            try:
                # Buscar el usuario por ID
                usuario = Usuarios.objects.get(id=usuario_tecnico_id, esta_activo=True)
                # Guardar con el usuario del localStorage
                serializer.save(
                    usuario_tecnico=usuario,
                    creado_por=usuario.username
                )
            except Usuarios.DoesNotExist:
                # Si no existe el usuario, intentar usar el autenticado o crear sin usuario
                if self.request.user.is_authenticated and hasattr(self.request.user, 'username'):
                    serializer.save(creado_por=self.request.user.username)
                else:
                    serializer.save(creado_por='sistema')
        else:
            # Fallback: usar el usuario autenticado si existe
            if self.request.user.is_authenticated and hasattr(self.request.user, 'id'):
                serializer.save(
                    usuario_tecnico=self.request.user,
                    creado_por=self.request.user.username
                )
            else:
                serializer.save(creado_por='sistema')

    def list(self, request, *args, **kwargs):
        # Filtro rápido por ticket en URL: ?ticket={id}
        ticket_id = self.request.query_params.get('ticket')
        if ticket_id:
            self.queryset = self.queryset.filter(ticket_id=ticket_id)
        return super().list(request, *args, **kwargs)