from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Casino
from .serializers import CasinoSerializer

class CasinoViewSet(viewsets.ModelViewSet):
    """
    API para gestión de casinos con soporte de auditoría y borrado lógico.
    """
    serializer_class = CasinoSerializer

    def get_queryset(self):
        return Casino.objects.filter(esta_activo=True).order_by('nombre')
    
    @action(detail=False, methods=['get'], url_path='lista')
    def lista_casinos(self, request):
        """Devuelve todos los casinos, incluyendo inactivos."""
        casinos = Casino.objects.all().order_by('nombre')
        serializer = self.get_serializer(casinos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], url_path='switch-estado')
    def switch_estado(self, request, pk=None):
        """Cambia el estado activo/inactivo de un casino."""
        from django.shortcuts import get_object_or_404
        
        # Obtenemos el modelo dinámicamente desde el serializer
        ModeloCasino = self.get_serializer().Meta.model
        
        # IMPORTANTE: Buscamos en .all() para encontrar el casino aunque esté inactivo
        # Esto evita el error 404 cuando get_queryset filtra por esta_activo=True
        casino = get_object_or_404(ModeloCasino.objects.all(), pk=pk)
        
        casino.esta_activo = not casino.esta_activo
        casino.modificado_por = request.user.username if request.user.is_authenticated else 'Anónimo'
        casino.save()
        
        serializer = self.get_serializer(casino)
        return Response(serializer.data)

    def perform_create(self, serializer):
        usuario = self.request.user.username if self.request.user.is_authenticated else 'Anónimo'
        serializer.save(creado_por=usuario)

    def perform_update(self, serializer):
        usuario = self.request.user.username if self.request.user.is_authenticated else 'Anónimo'
        serializer.save(modificado_por=usuario)

    def destroy(self, request, *args, **kwargs):
        """Implementa borrado lógico en lugar de eliminación física."""
        instance = self.get_object()
        instance.esta_activo = False
        instance.modificado_por = request.user.username if request.user.is_authenticated else 'Anónimo'
        instance.save()
        return Response(
            {"message": "El casino ha sido desactivado correctamente (Borrado Lógico)."},
            status=status.HTTP_204_NO_CONTENT
        )
        
