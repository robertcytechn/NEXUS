from rest_framework import viewsets
from .models import IncidenciaInfraestructura
from .serializers import IncidenciaInfraestructuraSerializer
from Usuarios.models import Usuarios

class IncidenciaInfraestructuraViewSet(viewsets.ModelViewSet):
    """
    Controlador para documentar eventos externos que afectan la infraestructura.
    """
    serializer_class = IncidenciaInfraestructuraSerializer

    def get_queryset(self):
        # Traer todas las incidencias con sus relaciones
        queryset = IncidenciaInfraestructura.objects.all().select_related('casino').order_by('-creado_en')

        usuario = self.request.user

        # Filtrado opcional por casino: ?casino={id}
        casino_id = self.request.query_params.get('casino')
        if casino_id:
            queryset = queryset.filter(casino_id=casino_id)
        else:
            # Usuarios sin nivel de mando central solo ven su propio casino.
            # nivel_jerarquia >= 19 corresponde a roles privilegiados (ADMINISTRADOR, DB ADMIN, etc.)
            rol_nivel = getattr(getattr(usuario, 'rol', None), 'nivel_jerarquia', 0)
            if rol_nivel < 19 and getattr(usuario, 'casino_id', None):
                queryset = queryset.filter(casino=usuario.casino)

        return queryset

    def perform_create(self, serializer):
        # Capturar usuario desde localStorage si viene en el payload
        usuario_id = self.request.data.get('creado_por_id')
        if usuario_id:
            try:
                usuario = Usuarios.objects.get(id=usuario_id)
                serializer.save(creado_por=usuario.username)
            except Usuarios.DoesNotExist:
                serializer.save(creado_por='Sistema')
        else:
            serializer.save(creado_por='Sistema')
    
    def perform_update(self, serializer):
        # Capturar usuario modificador desde localStorage si viene en el payload
        usuario_id = self.request.data.get('modificado_por_id')
        if usuario_id:
            try:
                usuario = Usuarios.objects.get(id=usuario_id)
                serializer.save(modificado_por=usuario.username)
            except Usuarios.DoesNotExist:
                serializer.save(modificado_por='Sistema')
        else:
            serializer.save(modificado_por='Sistema')