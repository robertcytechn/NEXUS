from rest_framework import serializers
from .models import RecompensaGamificacion, CanjeRecompensa
from Usuarios.models import Usuarios


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

# ──────────────────────────────────────────────────────────────────────────────
# SALÓN DE LA FAMA
# ──────────────────────────────────────────────────────────────────────────────
class TecnicoSalonFamaSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura para la vista pública del Salón de la Fama.
    Expone todos los datos necesarios para las 'Cartas de Héroe' incluyendo
    métricas completas de actividad anotadas en el queryset (0 queries extra).
    """
    casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)
    rol_nombre    = serializers.CharField(source='rol.nombre',    read_only=True)
    rango         = serializers.DictField(source='rango_gamificacion', read_only=True)

    # ── Tickets ──────────────────────────────────────────────────────────────
    tickets_totales     = serializers.IntegerField(read_only=True, default=0)
    tickets_cerrados    = serializers.IntegerField(read_only=True, default=0)
    tickets_en_proceso  = serializers.IntegerField(read_only=True, default=0)
    tickets_reabiertos  = serializers.IntegerField(read_only=True, default=0)

    # ── Wiki técnica ─────────────────────────────────────────────────────────
    wikis_totales       = serializers.IntegerField(read_only=True, default=0)
    wikis_publicadas    = serializers.IntegerField(read_only=True, default=0)
    wikis_pendientes    = serializers.IntegerField(read_only=True, default=0)

    # ── Mantenimientos y bitácora ─────────────────────────────────────────────
    mantenimientos_realizados = serializers.IntegerField(read_only=True, default=0)
    entradas_bitacora         = serializers.IntegerField(read_only=True, default=0)
    reparaciones_exitosas     = serializers.IntegerField(read_only=True, default=0)

    # ── Gamificación ──────────────────────────────────────────────────────────
    canjes_total = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Usuarios
        fields = [
            # Identidad
            'id',
            'nombres',
            'apellido_paterno',
            'apellido_materno',
            'casino_nombre',
            'rol_nombre',
            'avatar',
            # Puntos
            'puntos_gamificacion',
            'puntos_gamificacion_historico',
            'rango',
            # Tickets
            'tickets_totales',
            'tickets_cerrados',
            'tickets_en_proceso',
            'tickets_reabiertos',
            # Wiki
            'wikis_totales',
            'wikis_publicadas',
            'wikis_pendientes',
            # Mantenimiento / Bitácora
            'mantenimientos_realizados',
            'entradas_bitacora',
            'reparaciones_exitosas',
            # Gamificación
            'canjes_total',
        ]
        read_only_fields = fields
