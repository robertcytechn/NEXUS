from rest_framework import viewsets
from .models import Denominacion
from .serializers import DenominacionSerializer

class DenominacionViewSet(viewsets.ModelViewSet):
    queryset = Denominacion.objects.all().order_by('valor')
    serializer_class = DenominacionSerializer