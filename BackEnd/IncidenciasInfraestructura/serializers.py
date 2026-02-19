from rest_framework import serializers
from .models import IncidenciaInfraestructura

class IncidenciaInfraestructuraSerializer(serializers.ModelSerializer):
    casino_nombre = serializers.CharField(
        source='casino.nombre', 
        read_only=True
    )

    class Meta:
        model = IncidenciaInfraestructura
        fields = [
            'id',
            'casino',
            'casino_nombre',
            'titulo',
            'categoria',
            'descripcion',
            'severidad',
            'afecta_operacion',
            'hora_inicio',
            'hora_fin',
            'esta_activo',
            'creado_en',
            'modificado_en',
            'creado_por',
            'modificado_por',
            'notas_internas'
        ]
        
        # Blindaje de campos de auditoría solicitado
        read_only_fields = [
            'creado_en',
            'modificado_en',
            'creado_por',
            'modificado_por'
        ]