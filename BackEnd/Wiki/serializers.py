from rest_framework import serializers
from .models import WikiTecnica


# ──────────────────────────────────────────────────────────────────────────────
# SERIALIZER PARA PROPUESTAS (técnico envía nueva guía)
# Solo expone los campos que el técnico puede llenar al subir su propuesta.
# El estado y puntos son controlados exclusivamente por el sistema / admin.
# ──────────────────────────────────────────────────────────────────────────────
class WikiTecnicaPropuestaSerializer(serializers.ModelSerializer):
    """Usado en el Centro de Servicios: envío de nueva propuesta de guía."""

    autor_nombre = serializers.CharField(source='autor.username', read_only=True)
    modelo_nombre = serializers.CharField(source='modelo_relacionado.nombre_modelo', read_only=True)
    casino_nombre = serializers.CharField(source='casino_origen.nombre', read_only=True, default='')

    class Meta:
        model = WikiTecnica
        fields = [
            'id',
            'titulo_guia',
            'categoria',
            'archivo_pdf',
            'modelo_relacionado',
            'casino_origen',
            'autor_nombre',
            'modelo_nombre',
            'casino_nombre',
            'estado',
            'creado_en',
        ]
        read_only_fields = [
            'estado',
            'puntos_reconocimiento',
            'revisada_por',
            'fecha_revision',
            'nota_revision',
            'creado_en',
            'modificado_en',
            'creado_por',
            'modificado_por',
        ]


# ──────────────────────────────────────────────────────────────────────────────
# SERIALIZER PÚBLICO (técnico consulta guías publicadas en Centro de Servicios)
# ──────────────────────────────────────────────────────────────────────────────
class WikiTecnicaPublicaSerializer(serializers.ModelSerializer):
    """Lectura de guías publicadas en el Centro de Servicios (todos los técnicos)."""

    autor_nombre = serializers.CharField(source='autor.username', read_only=True)
    autor_nombres_completos = serializers.SerializerMethodField()
    modelo_nombre = serializers.CharField(source='modelo_relacionado.nombre_modelo', read_only=True)
    casino_nombre = serializers.CharField(source='casino_origen.nombre', read_only=True, default='Global')
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)

    class Meta:
        model = WikiTecnica
        fields = [
            'id',
            'titulo_guia',
            'categoria',
            'categoria_display',
            'archivo_pdf',
            'modelo_nombre',
            'casino_nombre',
            'autor_nombre',
            'autor_nombres_completos',
            'puntos_reconocimiento',
            'fecha_revision',
            'creado_en',
        ]
        read_only_fields = fields

    def get_autor_nombres_completos(self, obj):
        u = obj.autor
        return f"{u.nombres} {u.apellido_paterno}"


# ──────────────────────────────────────────────────────────────────────────────
# SERIALIZER ADMIN (Centro de Mando: revisión, aprobación, publicación)
# ──────────────────────────────────────────────────────────────────────────────
class WikiTecnicaAdminSerializer(serializers.ModelSerializer):
    """Serializer completo para el Centro de Mando del administrador."""

    autor_nombre = serializers.CharField(source='autor.username', read_only=True)
    autor_nombres_completos = serializers.SerializerMethodField()
    modelo_nombre = serializers.CharField(source='modelo_relacionado.nombre_modelo', read_only=True)
    casino_nombre = serializers.CharField(source='casino_origen.nombre', read_only=True, default='Global')
    revisado_por_nombre = serializers.CharField(source='revisada_por.username', read_only=True, default='')
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    puntos_gamificacion_autor = serializers.SerializerMethodField()

    class Meta:
        model = WikiTecnica
        fields = '__all__'
        read_only_fields = [
            'autor',
            'creado_en',
            'modificado_en',
            'creado_por',
            'modificado_por',
        ]

    def get_autor_nombres_completos(self, obj):
        u = obj.autor
        return f"{u.nombres} {u.apellido_paterno}"

    def get_puntos_gamificacion_autor(self, obj):
        """Muestra los puntos actuales del autor para que el admin vea su historial."""
        return obj.autor.puntos_gamificacion
