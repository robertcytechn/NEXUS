from rest_framework import serializers
from .models import AuditoriaServicioExterno

class AuditoriaServicioExternoSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(
        source='empresa_proveedora.nombre', 
        read_only=True
    )
    supervisor_nombre = serializers.CharField(
        source='supervisor_interno.username', 
        read_only=True
    )
    casino_nombre = serializers.CharField(
        source='casino.nombre', 
        read_only=True
    )
    
    # Etiquetas legibles para área y tipo de servicio
    area_acceso_display = serializers.CharField(
        source='get_area_acceso_display',
        read_only=True
    )
    tipo_servicio_display = serializers.CharField(
        source='get_tipo_servicio_display',
        read_only=True
    )
    
    # Duración calculada (en minutos)
    duracion_minutos = serializers.SerializerMethodField()

    class Meta:
        model = AuditoriaServicioExterno
        fields = '__all__'
        
        # Blindaje de auditoría inalterable
        read_only_fields = [
            'creado_en',
            'modificado_en',
            'creado_por',
            'modificado_por',
            'proveedor_nombre',
            'supervisor_nombre',
            'casino_nombre',
            'area_acceso_display',
            'tipo_servicio_display',
            'duracion_minutos'
        ]
    
    def get_duracion_minutos(self, obj):
        """Calcula la duración en minutos entre entrada y salida"""
        if obj.hora_entrada and obj.hora_salida:
            delta = obj.hora_salida - obj.hora_entrada
            return int(delta.total_seconds() / 60)
        return None