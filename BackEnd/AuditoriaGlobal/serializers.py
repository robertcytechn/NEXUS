from rest_framework import serializers
from .models import LogAuditoria

class LogAuditoriaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)

    class Meta:
        model = LogAuditoria
        fields = [
            'id', 'tabla', 'registro_id', 'accion', 
            'datos_anteriores', 'datos_nuevos', 'fecha',
            'usuario', 'usuario_nombre', 'casino', 'casino_nombre'
        ]
