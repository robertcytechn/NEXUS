from rest_framework import serializers
from .models import MantenimientoPreventivo

class MantenimientoPreventivoSerializer(serializers.ModelSerializer):
    tecnico_nombre = serializers.CharField(
        source='tecnico_responsable.username', 
        read_only=True
    )
    
    maquina_uid = serializers.CharField(
        source='maquina.uid_sala', 
        read_only=True
    )
    
    casino_nombre = serializers.CharField(
        source='maquina.casino.nombre',
        read_only=True
    )

    class Meta:
        model = MantenimientoPreventivo
        fields = [
            'id',
            'maquina',
            'maquina_uid',
            'casino_nombre',
            'tecnico_responsable',
            'tecnico_nombre',
            'fecha_mantenimiento',
            'estado_final_maquina',
            'observaciones',
            'creado_en'
        ]
        read_only_fields = ['creado_en', 'modificado_en', 'creado_por', 'modificado_por']