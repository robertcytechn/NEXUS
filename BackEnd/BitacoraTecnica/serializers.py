from rest_framework import serializers
from .models import BitacoraTecnica

class BitacoraTecnicaSerializer(serializers.ModelSerializer):
    tecnico_nombre = serializers.CharField(
        source='usuario_tecnico.username', 
        read_only=True
    )
    
    fecha_registro = serializers.DateTimeField(
        source='creado_en', 
        format="%Y-%m-%d %H:%M:%S", 
        read_only=True
    )

    class Meta:
        model = BitacoraTecnica
        fields = [
            'id', 
            'ticket', 
            'tecnico_nombre', 
            'usuario_tecnico', 
            'tipo_intervencion', 
            'descripcion_trabajo', 
            'resultado_intervencion', 
            'estado_maquina_resultante', 
            'finaliza_ticket', 
            'fecha_registro'
        ]
        read_only_fields = ['id', 'tecnico_nombre', 'creado_en', 'modificado_en', 'creado_por', 'modificado_por']