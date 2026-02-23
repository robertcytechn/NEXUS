from rest_framework import viewsets, permissions
from .models import EvolucionNexus
from .serializers import EvolucionNexusSerializer
from Gamificacion.signals_gamificacion import get_puntos_context, limpiar_puntos_context

class EvolucionNexusViewSet(viewsets.ModelViewSet):
    serializer_class = EvolucionNexusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Lógica de visibilidad
        # Roles permitidos para ver todo: administrador, dba
        # Aseguramos manejo insensible a mayúsculas/minúsculas
        if not user.rol:
             return EvolucionNexus.objects.none()

        rol_nombre = user.rol.nombre.lower()
        
        if rol_nombre in ['administrador', 'dba', 'sistemas']: # Agregado sistemas por si acaso
            return EvolucionNexus.objects.all()
        
        # Otros roles solo ven lo que crearon
        return EvolucionNexus.objects.filter(usuario=user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def create(self, request, *args, **kwargs):
        limpiar_puntos_context()
        response = super().create(request, *args, **kwargs)
        puntos = get_puntos_context()
        if puntos:
            response.data['puntos_nexus'] = puntos
            limpiar_puntos_context()
        return response
