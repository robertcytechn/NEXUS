from rest_framework import viewsets
from .models import RelevoTurno
from .serializers import RelevoTurnoSerializer

class RelevoTurnoViewSet(viewsets.ModelViewSet):
    """
    Controlador para documentar el traspaso de responsabilidades entre técnicos.
    """
    queryset = RelevoTurno.objects.all().select_related(
        'casino', 
        'tecnico_saliente', 
        'tecnico_entrante'
    )
    serializer_class = RelevoTurnoSerializer

    def get_queryset(self):
        # Filtro por casino para auditorías rápidas por sala
        queryset = self.queryset.order_by('-hora_salida_real')
        casino_id = self.request.query_params.get('casino')
        if casino_id:
            queryset = queryset.filter(casino_id=casino_id)
        return queryset

    def perform_create(self, serializer):
        # El sistema registra automáticamente quién está realizando el relevo en el sistema
        serializer.save(
            creado_por=self.request.user.username
        )