from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import WikiTecnica
from .serializers import WikiTecnicaSerializer

class WikiTecnicaViewSet(viewsets.ModelViewSet):
    """
    Controlador de la base de conocimientos con sistema de premios.
    """
    queryset = WikiTecnica.objects.all().select_related(
        'autor', 
        'casino_origen', 
        'modelo_relacionado'
    )
    serializer_class = WikiTecnicaSerializer

    def perform_create(self, serializer):
        # El sistema vincula automáticamente al técnico logueado como autor
        serializer.save(
            autor=self.request.user,
            creado_por=self.request.user.username
        )

    @action(detail=True, methods=['post'], url_path='premiar')
    def premiar_guia(self, request, pk=None):
        """
        Incrementa los puntos de reconocimiento del técnico autor.
        URL: /api/wiki/{id}/premiar/
        """
        guia = self.get_object()
        guia.puntos_reconocimiento += 10 # Se otorgan 10 puntos por cada voto útil
        guia.save()
        return Response(
            {'message': f'¡Has premiado a {guia.autor.username} por su excelente guía!'}, 
            status=status.HTTP_200_OK
        )