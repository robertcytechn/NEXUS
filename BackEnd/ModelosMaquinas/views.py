from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ModeloMaquina
from .serializers import ModeloMaquinaSerializer

import logging
logger = logging.getLogger(__name__)

class ModeloMaquinaViewSet(viewsets.ModelViewSet):
    """
    Controlador para gestionar los modelos de máquinas por proveedor.
    """
    serializer_class = ModeloMaquinaSerializer

    def get_queryset(self):
        # Por defecto, solo modelos activos y traemos al proveedor de una vez (Optimización) y su casino relacionado
        return ModeloMaquina.objects.filter(esta_activo=True).select_related('proveedor', 'proveedor__casino')

    @action(detail=False, methods=['get'], url_path='lista')
    def lista_todos(self, request):
        """Muestra todos los modelos (incluyendo inactivos) para administración."""
        queryset = ModeloMaquina.objects.all().select_related('proveedor', 'proveedor__casino').order_by('nombre_modelo')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='lista-por-casino/(?P<casino_id>[^/.]+)')
    def lista_por_casino(self, request, casino_id=None):
        """
        Devuelve todos los modelos de máquina de un casino específico con estadísticas.
        Filtra por proveedor.casino_id y solo activos.
        Endpoint: /modelos/lista-por-casino/{casino_id}/
        """
        if not casino_id:
            return Response(
                {'error': 'Se requiere el ID del casino'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            queryset = ModeloMaquina.objects.filter(
                proveedor__casino_id=casino_id,
                esta_activo=True
            ).select_related('proveedor', 'proveedor__casino').order_by('nombre_modelo')

            serializer = self.get_serializer(queryset, many=True)

            total = queryset.count()

            return Response({
                'modelos': serializer.data,
                'estadisticas': {
                    'total': total
                }
            })
        except Exception as e:
            logger.error(f"Error al obtener modelos del casino {casino_id}: {str(e)}")
            return Response(
                {'error': 'Error al obtener los modelos del casino'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'], url_path='switch-estado')
    def switch_estado(self, request, pk=None):
        """Cambia el estado activo/inactivo de un modelo de máquina."""
        from django.shortcuts import get_object_or_404
        
        # Obtenemos el modelo dinámicamente desde el serializer
        ModeloMaquina = self.get_serializer().Meta.model
        
        # IMPORTANTE: Buscamos en .all() para encontrar el modelo aunque esté inactivo
        # Esto evita el error 404 cuando get_queryset filtra por esta_activo=True
        modelo = get_object_or_404(ModeloMaquina.objects.all(), pk=pk)
        
        modelo.esta_activo = not modelo.esta_activo
        modelo.modificado_por = request.user.username if request.user.is_authenticated else 'Anónimo'
        modelo.save()
        
        serializer = self.get_serializer(modelo)
        return Response(serializer.data)

    def perform_create(self, serializer):
        creado_por = self.request.user.username if self.request.user.is_authenticated else 'system'
        serializer.save(creado_por=creado_por)

    def perform_update(self, serializer):
        modificado_por = self.request.user.username if self.request.user.is_authenticated else 'system'
        serializer.save(modificado_por=modificado_por)