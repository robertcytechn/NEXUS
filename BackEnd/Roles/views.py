from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Rol
from .serializers import RolSerializer

class RolViewSet(viewsets.ModelViewSet):
    """
    API para gestión de roles con soporte de auditoría y borrado lógico.
    """
    serializer_class = RolSerializer
    
    def get_queryset(self):
        return Rol.objects.filter(esta_activo=True).order_by('nombre')
    
    @action(detail=False, methods=['get'], url_path='lista')
    def lista_roles(self, request):
        """Devuelve todos los roles, incluyendo inactivos."""
        roles = Rol.objects.all().order_by('nombre')
        serializer = self.get_serializer(roles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='switch-estado')
    def switch_estado(self, request, pk=None):
        """Cambia el estado activo/inactivo de un rol."""
        from django.shortcuts import get_object_or_404
        
        # Obtenemos el modelo dinámicamente desde el serializer
        ModeloRol = self.get_serializer().Meta.model
        
        # IMPORTANTE: Buscamos en .all() para encontrar el rol aunque esté inactivo
        # Esto evita el error 404 cuando get_queryset filtra por esta_activo=True
        rol = get_object_or_404(ModeloRol.objects.all(), pk=pk)
        
        rol.esta_activo = not rol.esta_activo
        rol.modificado_por = request.user.username if request.user.is_authenticated else 'Anónimo'
        rol.save()
        
        serializer = self.get_serializer(rol)
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
            {"message": "El rol ha sido desactivado correctamente (Borrado Lógico)."},
            status=status.HTTP_204_NO_CONTENT
        )