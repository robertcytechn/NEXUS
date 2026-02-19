from rest_framework import viewsets
from .models import AuditoriaServicioExterno
from .serializers import AuditoriaServicioExternoSerializer

class AuditoriaServicioExternoViewSet(viewsets.ModelViewSet):
    """
    Controlador para supervisar y auditar el acceso de terceros a áreas críticas.
    """
    queryset = AuditoriaServicioExterno.objects.all().select_related(
        'casino', 
        'empresa_proveedora', 
        'supervisor_interno'
    )
    serializer_class = AuditoriaServicioExternoSerializer

    def get_queryset(self):
        # Permite filtrar por casino o por proveedor: ?casino=1&proveedor=2
        queryset = self.queryset
        casino_id = self.request.query_params.get('casino')
        proveedor_id = self.request.query_params.get('proveedor')
        
        if casino_id:
            queryset = queryset.filter(casino_id=casino_id)
        if proveedor_id:
            queryset = queryset.filter(empresa_proveedora_id=proveedor_id)
            
        return queryset

    def perform_create(self, serializer):
        # Auditoría automática de Sakai
        serializer.save(
            creado_por=self.request.user.username
        )