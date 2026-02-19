from rest_framework import serializers
from .models import TareaEspecial

class TareaEspecialSerializer(serializers.ModelSerializer):
    creador_nombre = serializers.CharField(
        source='creado_por_usuario.username', 
        read_only=True
    )
    
    tecnico_nombre = serializers.CharField(
        source='asignado_a.username', 
        read_only=True, 
        default="Pendiente"
    )
    
    casino_nombre = serializers.CharField(
        source='casino.nombre', 
        read_only=True
    )

    class Meta:
        model = TareaEspecial
        fields = '__all__'
        read_only_fields = ['creado_en', 'modificado_en', 'creado_por', 'modificado_por']