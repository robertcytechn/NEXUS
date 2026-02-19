from rest_framework import serializers
from .models import Proveedor

class ProveedorSerializer(serializers.ModelSerializer):
    """Serializer para proveedores con nombre de casino incluido."""
    casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)

    class Meta:
        model = Proveedor
        fields = [
            'id', 'casino', 'casino_nombre', 'nombre', 'rfc', 'email_corporativo',
            'telefono_soporte', 'email_soporte', 'nombre_contacto_tecnico',
            'username', 'password', 'esta_activo',
            'creado_en', 'modificado_en', 'creado_por', 'modificado_por'
        ]
        
        extra_kwargs = {
            'password': {'write_only': True},
            'creado_en': {'read_only': True},
            'modificado_en': {'read_only': True},
            'creado_por': {'read_only': True},
            'modificado_por': {'read_only': True},
        }

class ProveedorGestionSerializer(serializers.ModelSerializer):
    """Serializer para gestión que incluye password en lectura."""
    casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)
    total_modelos = serializers.SerializerMethodField()

    class Meta:
        model = Proveedor
        fields = [
            'id', 'casino', 'casino_nombre', 'nombre', 'rfc', 'email_corporativo',
            'telefono_soporte', 'email_soporte', 'nombre_contacto_tecnico',
            'username', 'password', 'esta_activo',
            'total_modelos',
            'creado_en', 'modificado_en', 'creado_por', 'modificado_por'
        ]
        extra_kwargs = {
            'creado_en': {'read_only': True},
            'modificado_en': {'read_only': True},
            'creado_por': {'read_only': True},
            'modificado_por': {'read_only': True},
        }

    def get_total_modelos(self, obj):
        return obj.modelos_maquinas.filter(esta_activo=True).count()


class ProveedorVerificacionSerializer(serializers.Serializer):
    """Serializer para validación de credenciales de proveedor."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    casino_id = serializers.IntegerField(required=False)