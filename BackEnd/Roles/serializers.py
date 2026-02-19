from rest_framework import serializers
from .models import Rol

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = [
            'id', 'nombre', 'descripcion', 
            'esta_activo', 'creado_en', 'modificado_en', 'creado_por', 'modificado_por', 'notas_internas'
        ]
        read_only_fields = ['creado_en', 'modificado_en', 'creado_por', 'modificado_por']