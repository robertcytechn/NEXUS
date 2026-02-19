from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import TareaEspecial
from .serializers import TareaEspecialSerializer

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