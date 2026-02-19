from rest_framework import serializers
from django.utils import timezone
from .models import RelevoTurno

class RelevoTurnoSerializer(serializers.ModelSerializer):
    nombre_saliente = serializers.CharField(
        source='tecnico_saliente.username', 
        read_only=True
    )
    nombre_entrante = serializers.CharField(
        source='tecnico_entrante.username', 
        read_only=True
    )
    casino_nombre = serializers.CharField(
        source='casino.nombre',
        read_only=True
    )
    estado_entrega_display = serializers.CharField(
        source='get_estado_entrega_display',
        read_only=True
    )

    class Meta:
        model = RelevoTurno
        fields = '__all__'
        
        # Blindaje de campos de auditoría
        read_only_fields = [
            'creado_en',
            'modificado_en',
            'creado_por',
            'modificado_por',
            'nombre_saliente',
            'nombre_entrante',
            'casino_nombre',
            'estado_entrega_display',
            'hora_salida_real'  # La hora de salida se establece automáticamente
        ]

    def validate(self, data):
        """
        Validar que ambos técnicos pertenezcan al mismo casino
        """
        tecnico_saliente = data.get('tecnico_saliente')
        tecnico_entrante = data.get('tecnico_entrante')
        casino = data.get('casino')

        # Verificar que el técnico saliente pertenece al casino del relevo
        if tecnico_saliente and casino and tecnico_saliente.casino_id != casino.id:
            raise serializers.ValidationError({
                'tecnico_saliente': f'El técnico {tecnico_saliente.username} no pertenece al casino {casino.nombre}'
            })

        # Verificar que el técnico entrante pertenece al casino del relevo
        if tecnico_entrante and casino and tecnico_entrante.casino_id != casino.id:
            raise serializers.ValidationError({
                'tecnico_entrante': f'El técnico {tecnico_entrante.username} no pertenece al casino {casino.nombre}'
            })

        # Verificar que no sean el mismo técnico
        if tecnico_saliente and tecnico_entrante and tecnico_saliente.id == tecnico_entrante.id:
            raise serializers.ValidationError({
                'tecnico_entrante': 'El técnico que recibe debe ser diferente al técnico que entrega'
            })

        return data

    def create(self, validated_data):
        """
        Establecer la hora de salida automáticamente al momento de creación
        """
        validated_data['hora_salida_real'] = timezone.now()
        return super().create(validated_data)