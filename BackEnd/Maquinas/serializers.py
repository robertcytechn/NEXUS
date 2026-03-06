from rest_framework import serializers
from .models import Maquina
from Denominaciones.models import Denominacion
from datetime import date

class MaquinaSerializer(serializers.ModelSerializer):
    # Denominaciones: se requiere al menos una, rechaza lista vacía
    denominaciones = serializers.PrimaryKeyRelatedField(
        many=True,
        allow_empty=False,
        queryset=Denominacion.objects.all(),
    )

    # Campos de lectura para el frontend de PrimeVue
    modelo_nombre = serializers.CharField(source='modelo.nombre_modelo', read_only=True)
    modelo_producto = serializers.CharField(source='modelo.nombre_producto', read_only=True)
    modelo_descripcion = serializers.CharField(source='modelo.descripcion', read_only=True)
    imagen_url = serializers.ImageField(source='modelo.imagen', read_only=True)
    casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)
    
    # Información del Proveedor
    proveedor_id = serializers.IntegerField(source='modelo.proveedor.id', read_only=True)
    proveedor_nombre = serializers.CharField(source='modelo.proveedor.nombre', read_only=True)
    proveedor_rfc = serializers.CharField(source='modelo.proveedor.rfc', read_only=True)
    proveedor_email = serializers.EmailField(source='modelo.proveedor.email_corporativo', read_only=True)
    proveedor_telefono = serializers.CharField(source='modelo.proveedor.telefono_soporte', read_only=True)
    proveedor_contacto = serializers.CharField(source='modelo.proveedor.nombre_contacto_tecnico', read_only=True)
    
    # Denominaciones como lista de objetos
    denominaciones_info = serializers.SerializerMethodField()
    
    # Alias para compatibilidad: uid es el mismo que uid_sala
    uid = serializers.CharField(source='uid_sala', read_only=True)
    
    # Cálculo de licencia
    dias_licencia = serializers.SerializerMethodField()
    
    # Fecha de creación formateada
    fecha_instalacion = serializers.DateTimeField(source='creado_en', read_only=True, format='%Y-%m-%d')

    class Meta:
        model = Maquina
        fields = '__all__'

        # Campos de readonly
        read_only_fields = (
            'creado_en', 'modificado_en', 'creado_por', 'modificado_por', 
            'modelo_nombre', 'modelo_producto', 'modelo_descripcion', 'imagen_url', 
            'casino_nombre', 'proveedor_id', 'proveedor_nombre', 'proveedor_rfc', 
            'proveedor_email', 'proveedor_telefono', 'proveedor_contacto',
            'denominaciones_info', 'dias_licencia', 'fecha_instalacion'
        )

    def get_dias_licencia(self, obj):
        if not obj.fecha_vencimiento_licencia:
            return "Indefinida"
        delta = obj.fecha_vencimiento_licencia - date.today()
        return max(delta.days, 0)
    
    def get_denominaciones_info(self, obj):
        """Retorna las denominaciones como lista de objetos con id y etiqueta"""
        return [
            {
                'id': denom.id,
                'etiqueta': denom.etiqueta,
                'valor': str(denom.valor)
            }
            for denom in obj.denominaciones.all()
        ]


class MaquinaTablaSerializer(serializers.ModelSerializer):
    """
    Serializer liviano para la tabla de CentroServicios/Maquinas.
    Solo incluye los campos que muestra el DataTable, evitando la carga
    de proveedor, imagen, denominciones y otros campos pesados.
    """
    casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)
    modelo_nombre = serializers.CharField(source='modelo.nombre_modelo', read_only=True)

    class Meta:
        model = Maquina
        fields = [
            'id', 'uid_sala', 'numero_serie', 'juego', 'ip_maquina',
            'ubicacion_piso', 'ubicacion_sala', 'estado_actual',
            'contador_fallas', 'esta_activo', 'casino_nombre', 'modelo_nombre'
        ]


class MaquinaFKSerializer(serializers.ModelSerializer):
    """
    Serializer ultra-ligero para dropdowns FK (ej. selector de máquina en Tickets).
    Solo devuelve los campos que necesita el frontend para mostrar la opción.
    """
    casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)
    modelo_nombre = serializers.CharField(source='modelo.nombre_modelo', read_only=True)

    class Meta:
        model = Maquina
        fields = ['id', 'uid_sala', 'casino_nombre', 'modelo_nombre']


class MaquinaMapaSerializer(serializers.ModelSerializer):
    """
    Serializer ligero para el Mapa Interactivo de Sala.
    Incluye solo los campos necesarios para renderizar y gestionar el grid.
    """
    # Alias para compatibilidad con el frontend
    uid = serializers.CharField(source='uid_sala', read_only=True)

    # Datos del modelo (para tooltip y diálogo)
    modelo_nombre = serializers.CharField(source='modelo.nombre_modelo', read_only=True)
    modelo_producto = serializers.CharField(source='modelo.nombre_producto', read_only=True)
    imagen_url = serializers.ImageField(source='modelo.imagen', read_only=True)
    casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)

    # Datos del proveedor (para Modo Proveedor en el mapa)
    proveedor_id = serializers.IntegerField(source='modelo.proveedor.id', read_only=True)
    proveedor_nombre = serializers.CharField(source='modelo.proveedor.nombre', read_only=True)
    proveedor_rfc = serializers.CharField(source='modelo.proveedor.rfc', read_only=True)
    proveedor_email = serializers.EmailField(source='modelo.proveedor.email_corporativo', read_only=True)
    proveedor_telefono = serializers.CharField(source='modelo.proveedor.telefono_soporte', read_only=True)

    # Datos adicionales para el diálogo de detalles
    dias_licencia = serializers.SerializerMethodField()
    fecha_instalacion = serializers.DateTimeField(source='creado_en', read_only=True, format='%Y-%m-%d')
    denominaciones_info = serializers.SerializerMethodField()

    # Labels legibles para piso y sala
    ubicacion_piso_label = serializers.SerializerMethodField()
    ubicacion_sala_label = serializers.SerializerMethodField()

    class Meta:
        model = Maquina
        fields = [
            'id', 'uid', 'uid_sala', 'juego',
            'coordenada_x', 'coordenada_y',
            'ubicacion_piso', 'ubicacion_piso_label',
            'ubicacion_sala', 'ubicacion_sala_label',
            'estado_actual', 'contador_fallas',
            'casino', 'casino_nombre',
            'modelo_nombre', 'modelo_producto', 'imagen_url',
            'proveedor_id', 'proveedor_nombre', 'proveedor_rfc', 'proveedor_email', 'proveedor_telefono',
            'ip_maquina', 'numero_serie',
            'ultimo_mantenimiento', 'fecha_vencimiento_licencia', 'dias_licencia', 'fecha_instalacion', 'denominaciones_info'
        ]
        read_only_fields = fields

    def get_ubicacion_piso_label(self, obj):
        """Retorna la etiqueta legible del piso según los choices del modelo."""
        choices_dict = dict(Maquina.PISO_CHOICES)
        return choices_dict.get(obj.ubicacion_piso, obj.ubicacion_piso)

    def get_ubicacion_sala_label(self, obj):
        """Retorna la etiqueta legible de la sala según los choices del modelo."""
        choices_dict = dict(Maquina.SALA_CHOICES)
        return choices_dict.get(obj.ubicacion_sala, obj.ubicacion_sala)

    def get_dias_licencia(self, obj):
        if not obj.fecha_vencimiento_licencia:
            return "Indefinida"
        delta = obj.fecha_vencimiento_licencia - date.today()
        return max(delta.days, 0)
    
    def get_denominaciones_info(self, obj):
        """Retorna las denominaciones como lista de objetos con id y etiqueta"""
        return [
            {
                'id': denom.id,
                'etiqueta': denom.etiqueta,
                'valor': str(denom.valor)
            }
            for denom in obj.denominaciones.all()
        ]
