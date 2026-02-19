from rest_framework import serializers
from .models import EvolucionNexus

class EvolucionNexusSerializer(serializers.ModelSerializer):
    nombre_usuario = serializers.CharField(source='usuario.username', read_only=True)
    nombre_rol = serializers.CharField(source='usuario.rol.nombre', read_only=True)

    class Meta:
        model = EvolucionNexus
        fields = '__all__'
        read_only_fields = ('usuario', 'fecha_creacion', 'fecha_actualizacion')
