from rest_framework import serializers
from .models import InventarioSala

class InventarioSalaSerializer(serializers.ModelSerializer):
    # Datos de lectura para la interfaz de Vue
    casino_nombre = serializers.CharField(
        source='casino.nombre', 
        read_only=True
    )

    class Meta:
        model = InventarioSala
        fields = '__all__'
        
        # Blindaje de campos de auditoría solicitado
        read_only_fields = [
            'creado_en',
            'modificado_en',
            'creado_por',
            'modificado_por'
        ]