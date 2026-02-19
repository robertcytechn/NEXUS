from rest_framework import viewsets
from .models import MantenimientoPreventivo
from .serializers import MantenimientoPreventivoSerializer

class MantenimientoPreventivoViewSet(viewsets.ModelViewSet):
    """
    Controlador para gestionar el calendario y registro de preventivos.
    """
    queryset = MantenimientoPreventivo.objects.all().select_related(
        'maquina', 
        'tecnico_responsable',
        'maquina__casino'
    )
    serializer_class = MantenimientoPreventivoSerializer

    def perform_create(self, serializer):
        # Auditoría automática de quién registra en el sistema
        serializer.save(
            creado_por=self.request.user.username
        )

    def get_queryset(self):
        """
        Filtros soportados:
        - ?maquina={id}: Preventivos de una máquina específica.
        - ?casino={id}: Preventivos de todas las máquinas de un casino.
        """
        queryset = self.queryset
        
        maquina_id = self.request.query_params.get('maquina')
        if maquina_id:
            queryset = queryset.filter(maquina_id=maquina_id)
            
        casino_id = self.request.query_params.get('casino')
        if casino_id:
            queryset = queryset.filter(maquina__casino_id=casino_id)
            
        return queryset