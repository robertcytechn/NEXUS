from rest_framework import serializers
from .models import Denominacion

class DenominacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Denominacion
        fields = '__all__'