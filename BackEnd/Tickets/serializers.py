from rest_framework import serializers
from .models import Ticket
from datetime import datetime
from django.utils import timezone

class TicketSerializer(serializers.ModelSerializer):
    # Datos informativos de relaciones para el frontend de Sakai
    maquina_uid = serializers.CharField(source='maquina.uid_sala', read_only=True)
    # Usar SerializerMethodField para obtener siempre el estado fresco de la máquina
    maquina_estado_actual = serializers.SerializerMethodField()
    casino_nombre = serializers.CharField(source='maquina.casino.nombre', read_only=True)
    reportante_nombre = serializers.CharField(source='reportante.nombres', read_only=True)
    reportante_apellidos = serializers.SerializerMethodField()
    reportante_rol = serializers.CharField(source='reportante.rol.nombre', read_only=True)
    tecnico_nombre = serializers.CharField(source='tecnico_asignado.nombres', read_only=True, default="Sin asignar")
    tecnico_asignado_nombre = serializers.SerializerMethodField()
    
    # Cálculo dinámico de tiempo de resolución
    tiempo_respuesta = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = [
            'folio', 
            'creado_en', 
            'modificado_en', 
            'creado_por', 
            'modificado_por',
            'contador_reaperturas'
        ]
    
    def get_maquina_estado_actual(self, obj):
        """Obtiene el estado actual de la máquina desde la base de datos."""
        if obj.maquina_id:
            from Maquinas.models import Maquina
            try:
                maquina = Maquina.objects.only('estado_actual').get(id=obj.maquina_id)
                return maquina.estado_actual
            except Maquina.DoesNotExist:
                return None
        return None

    def get_reportante_apellidos(self, obj):
        """Obtiene los apellidos del reportante."""
        if obj.reportante:
            apellidos = [obj.reportante.apellido_paterno]
            if obj.reportante.apellido_materno:
                apellidos.append(obj.reportante.apellido_materno)
            return ' '.join(apellidos)
        return ''
    
    def get_tecnico_asignado_nombre(self, obj):
        """Obtiene el nombre completo del técnico asignado."""
        if obj.tecnico_asignado:
            nombres = [obj.tecnico_asignado.nombres]
            if obj.tecnico_asignado.apellido_paterno:
                nombres.append(obj.tecnico_asignado.apellido_paterno)
            if obj.tecnico_asignado.apellido_materno:
                nombres.append(obj.tecnico_asignado.apellido_materno)
            return ' '.join(nombres)
        return None
    
    def get_tiempo_respuesta(self, obj):
        """Calcula cuánto tiempo pasó desde la creación hasta el cierre."""
        if obj.estado_ciclo == 'cerrado' and obj.modificado_en:
            diff = obj.modificado_en - obj.creado_en
            days = diff.days
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{days}d {hours}h {minutes}m"
        return "En curso"


class TicketCentroServiciosSerializer(serializers.ModelSerializer):
    """Serializer para Centro de Servicios con campos calculados."""
    maquina_uid = serializers.CharField(source='maquina.uid_sala', read_only=True)
    maquina_estado_actual = serializers.SerializerMethodField()
    casino_nombre = serializers.CharField(source='maquina.casino.nombre', read_only=True)
    reportante_nombre = serializers.CharField(source='reportante.nombres', read_only=True)
    reportante_apellidos = serializers.SerializerMethodField()
    tecnico_nombre = serializers.CharField(source='tecnico_asignado.nombres', read_only=True, allow_null=True)
    tecnico_asignado_nombre = serializers.SerializerMethodField()
    
    # Campos calculados para Centro de Servicios
    dias_abierto = serializers.SerializerMethodField()
    total_intervenciones = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'folio', 'maquina', 'maquina_uid', 'maquina_estado_actual', 'casino_nombre',
            'categoria', 'subcategoria', 'prioridad', 'descripcion_problema',
            'estado_ciclo', 'estado_maquina_reportado', 'reportante', 'reportante_nombre', 'reportante_apellidos',
            'tecnico_asignado', 'tecnico_nombre', 'tecnico_asignado_nombre',
            'notas_seguimiento', 'contador_reaperturas', 'dias_abierto', 'total_intervenciones',
            'creado_en', 'modificado_en', 'esta_activo'
        ]
        read_only_fields = ['folio', 'creado_en', 'modificado_en', 'contador_reaperturas']

    def get_maquina_estado_actual(self, obj):
        """Obtiene el estado actual de la máquina desde la base de datos."""
        if obj.maquina_id:
            from Maquinas.models import Maquina
            try:
                maquina = Maquina.objects.only('estado_actual').get(id=obj.maquina_id)
                return maquina.estado_actual
            except Maquina.DoesNotExist:
                return None
        return None

    def get_reportante_apellidos(self, obj):
        """Obtiene los apellidos del reportante."""
        if obj.reportante:
            apellidos = [obj.reportante.apellido_paterno]
            if obj.reportante.apellido_materno:
                apellidos.append(obj.reportante.apellido_materno)
            return ' '.join(apellidos)
        return ''
    
    def get_tecnico_asignado_nombre(self, obj):
        """Obtiene el nombre completo del técnico asignado."""
        if obj.tecnico_asignado:
            nombres = [obj.tecnico_asignado.nombres]
            if obj.tecnico_asignado.apellido_paterno:
                nombres.append(obj.tecnico_asignado.apellido_paterno)
            if obj.tecnico_asignado.apellido_materno:
                nombres.append(obj.tecnico_asignado.apellido_materno)
            return ' '.join(nombres)
        return None
    
    def get_dias_abierto(self, obj):
        """Calcula cuántos días lleva abierto el ticket."""
        if obj.estado_ciclo != 'cerrado':
            ahora = timezone.now()
            diferencia = ahora - obj.creado_en
            return diferencia.days
        return 0
    
    def get_total_intervenciones(self, obj):
        """Cuenta el número total de bitacoras/intervenciones del ticket."""
        return obj.bitacoras.filter(esta_activo=True).count()