from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import TareaEspecial
from .serializers import TareaEspecialSerializer
from Gamificacion.signals_gamificacion import get_puntos_context, limpiar_puntos_context

class TareaEspecialViewSet(viewsets.ModelViewSet):
    """
    Controlador para tareas de infraestructura ajenas a máquinas.
    """
    queryset = TareaEspecial.objects.all().select_related(
        'creado_por_usuario', 
        'asignado_a', 
        'casino'
    )
    serializer_class = TareaEspecialSerializer

    def perform_create(self, serializer):
        # Registramos quién da de alta la tarea
        serializer.save(
            creado_por_usuario=self.request.user,
            creado_por=self.request.user.username
        )

    def perform_update(self, serializer):
        # Lógica de Auto-Asignación
        instance = self.get_object()
        # Si la tarea no tiene técnico y se está cambiando el estatus
        if not instance.asignado_a:
            serializer.save(
                asignado_a=self.request.user,
                modificado_por=self.request.user.username
            )
        else:
            serializer.save(
                modificado_por=self.request.user.username
            )

    def _update_con_puntos(self, request, *args, **kwargs):
        """Helper compartido por update() y partial_update()."""
        limpiar_puntos_context()
        kwargs['partial'] = kwargs.get('partial', False)
        response = super().update(request, *args, **kwargs)
        puntos = get_puntos_context()
        if puntos:
            response.data['puntos_nexus'] = puntos
            limpiar_puntos_context()
        return response

    def update(self, request, *args, **kwargs):
        return self._update_con_puntos(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self._update_con_puntos(request, *args, **kwargs)