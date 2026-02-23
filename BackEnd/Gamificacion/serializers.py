from rest_framework import serializers
from .models import RecompensaGamificacion, CanjeRecompensa


# ──────────────────────────────────────────────────────────────────────────────
# RECOMPENSAS
# ──────────────────────────────────────────────────────────────────────────────
class RecompensaGamificacionSerializer(serializers.ModelSerializer):
    """Serializer completo para GERENCIA (crear / editar / listar todo)."""

    casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)

    class Meta:
        model = RecompensaGamificacion
        fields = '__all__'
        read_only_fields = ['creado_en', 'modificado_en', 'creado_por', 'modificado_por']


class RecompensaPublicaSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura para técnicos en la tienda.
    Muestra solo las recompensas activas con la información necesaria para el canje.
    """

    casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)

    class Meta:
        model = RecompensaGamificacion
        fields = [
            'id',
            'titulo',
            'descripcion',
            'costo_puntos',
            'casino_nombre',
            'stock',
            'activo',
        ]
        read_only_fields = fields


# ──────────────────────────────────────────────────────────────────────────────
# CANJES
# ──────────────────────────────────────────────────────────────────────────────
class CanjeRecompensaSerializer(serializers.ModelSerializer):
    """Serializer de lectura para historial de canjes."""

    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    recompensa_titulo = serializers.CharField(source='recompensa.titulo', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = CanjeRecompensa
        fields = '__all__'
        read_only_fields = [
            'usuario',
            'puntos_descontados',
            'creado_en',
            'modificado_en',
            'creado_por',
            'modificado_por',
        ]
