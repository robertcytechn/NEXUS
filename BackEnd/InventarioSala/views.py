from rest_framework import viewsets
from .models import InventarioSala
from .serializers import InventarioSalaSerializer

class InventarioSalaViewSet(viewsets.ModelViewSet):
    """
    Controlador para el inventario simplificado de herramientas y consumibles.
    """
    queryset = InventarioSala.objects.all().select_related('casino')
    serializer_class = InventarioSalaSerializer

    def get_queryset(self):
        # Filtro opcional por casino en la URL: ?casino={id}
        queryset = self.queryset
        casino_id = self.request.query_params.get('casino')
        if casino_id:
            queryset = queryset.filter(casino_id=casino_id)
        return queryset

    def perform_create(self, serializer):
        # El sistema registra quién dio de alta el artículo automáticamente
        serializer.save(
            creado_por=self.request.user.username
        )