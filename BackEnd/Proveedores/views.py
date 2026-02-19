from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Proveedor
from .serializers import ProveedorSerializer, ProveedorGestionSerializer, ProveedorVerificacionSerializer

import logging
logger = logging.getLogger(__name__)

class ProveedorViewSet(viewsets.ModelViewSet):
    """
    API para gestión de proveedores con autenticación simple.
    """
    serializer_class = ProveedorSerializer
    queryset = Proveedor.objects.all()

    def get_queryset(self):
        """
        Filtros soportados:
        - ?search=termino: Busca en nombre y RFC
        """
        from django.db.models import Q
        
        queryset = Proveedor.objects.filter(esta_activo=True).select_related('casino')
        
        # Filtro de búsqueda
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(rfc__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='lista')
    def lista_proveedores(self, request):
        """Devuelve todos los proveedores, incluyendo inactivos."""
        proveedores = Proveedor.objects.all().order_by('-id')
        serializer = self.get_serializer(proveedores, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='lista-por-casino/(?P<casino_id>[^/.]+)')
    def lista_por_casino(self, request, casino_id=None):
        """
        Devuelve todos los proveedores de un casino específico con estadísticas.
        Endpoint: /proveedores/lista-por-casino/{casino_id}/
        """
        if not casino_id:
            return Response(
                {'error': 'Se requiere el ID del casino'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            queryset = Proveedor.objects.filter(
                casino_id=casino_id,
                esta_activo=True
            ).select_related('casino').prefetch_related('modelos_maquinas').order_by('nombre')

            serializer = ProveedorGestionSerializer(queryset, many=True)

            total = queryset.count()

            return Response({
                'proveedores': serializer.data,
                'estadisticas': {
                    'total': total
                }
            })
        except Exception as e:
            logger.error(f"Error al obtener proveedores del casino {casino_id}: {str(e)}")
            return Response(
                {'error': 'Error al obtener los proveedores del casino'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['patch'], url_path='switch-estado')
    def switch_estado(self, request, pk=None):
        """Cambia el estado activo/inactivo de un proveedor."""
        from django.shortcuts import get_object_or_404
        
        # Obtenemos el modelo dinámicamente desde el serializer
        ModeloProveedor = self.get_serializer().Meta.model
        
        # IMPORTANTE: Buscamos en .all() para encontrar el proveedor aunque esté inactivo
        # Esto evita el error 404 cuando get_queryset filtra por esta_activo=True
        proveedor = get_object_or_404(ModeloProveedor.objects.all(), pk=pk)
        
        proveedor.esta_activo = not proveedor.esta_activo
        proveedor.modificado_por = request.user.username if request.user.is_authenticated else 'Anónimo'
        proveedor.save()
        
        serializer = self.get_serializer(proveedor)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='verificar-acceso', serializer_class=ProveedorVerificacionSerializer)
    def verificar_acceso(self, request):
        """Valida credenciales de proveedor sin generar tokens de sesión."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        casino_id = serializer.validated_data.get('casino_id')

        filtros = {'username': username}
        if casino_id:
            filtros['casino_id'] = casino_id

        candidatos = Proveedor.objects.filter(**filtros)

        if not candidatos.exists():
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

        proveedor_valido = None
        for proveedor in candidatos:
            if proveedor.password == password:
                if not proveedor.esta_activo:
                    return Response({"error": "Cuenta desactivada."}, status=status.HTTP_403_FORBIDDEN)
                proveedor_valido = proveedor
                break
        
        if proveedor_valido:
            data = ProveedorSerializer(proveedor_valido).data
            return Response({"mensaje": "Acceso correcto", "proveedor": data}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)
