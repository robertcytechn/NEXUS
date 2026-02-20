from rest_framework import serializers
from .models import MenuConfig

class MenuConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuConfig
        fields = ['configuracion', 'actualizado_en']
