from rest_framework import serializers
from .models import ModeloMaquina

class ModeloMaquinaSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para el frontend
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre', 
        read_only=True
    )
    casino_nombre = serializers.CharField(
        source='proveedor.casino.nombre', 
        read_only=True
    )
    total_maquinas = serializers.SerializerMethodField()

    class Meta:
        model = ModeloMaquina
        fields = [
            'id', 'proveedor', 'proveedor_nombre', 'casino_nombre',
            'nombre_modelo', 'nombre_producto', 'descripcion',
            'total_maquinas', 'esta_activo',
            'creado_en', 'modificado_en', 
            'creado_por', 'modificado_por'
        ]
        read_only_fields = ['creado_por', 'modificado_por', 'creado_en', 'modificado_en']

    def get_total_maquinas(self, obj):
        return obj.maquinas.filter(esta_activo=True).count()