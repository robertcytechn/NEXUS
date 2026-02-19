from rest_framework import serializers
from .models import Casino

class CasinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Casino
        fields = [
            'id', 'nombre', 'identificador', 'direccion', 'telefono', 'ciudad', 'encargado', 'esta_activo',
            'creado_en', 'modificado_en', 'creado_por', 'modificado_por', 'notas_internas', 'horario_apertura', 'horario_cierre',
            'grid_width', 'grid_height'
        ]
        read_only_fields = ['creado_en', 'modificado_en', 'creado_por', 'modificado_por']
