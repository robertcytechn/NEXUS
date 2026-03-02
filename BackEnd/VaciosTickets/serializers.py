from rest_framework import serializers
from django.utils import timezone
from .models import ConfiguracionCasino, TicketVacio


class ConfiguracionCasinoSerializer(serializers.ModelSerializer):
    casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)

    class Meta:
        model = ConfiguracionCasino
        fields = '__all__'
        read_only_fields = ['creado_en', 'modificado_en', 'creado_por', 'modificado_por']


class TicketVacioSerializer(serializers.ModelSerializer):
    # ── Campos read-only de relaciones ────────────────────────────────────
    casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)
    maquina_uid = serializers.CharField(source='maquina.uid_sala', read_only=True)

    tecnico_creador_nombre = serializers.SerializerMethodField()
    gerente_auditor_nombre = serializers.SerializerMethodField()

    # Representaciones legibles de los choice fields
    estado_operativo_display = serializers.CharField(
        source='get_estado_operativo_display', read_only=True
    )
    estado_auditoria_display = serializers.CharField(
        source='get_estado_auditoria_display', read_only=True
    )
    motivo_falla_display = serializers.CharField(
        source='get_motivo_falla_display', read_only=True
    )

    class Meta:
        model = TicketVacio
        fields = '__all__'
        read_only_fields = [
            'fecha_creacion',
            'creado_en',
            'modificado_en',
            'creado_por',
            'modificado_por',
            # estado operativo y auditoria los calcula el modelo en save()
            # pero pueden ser sobreescritos por la acción de auditoría (views)
        ]

    def get_tecnico_creador_nombre(self, obj):
        u = obj.tecnico_creador
        if not u:
            return ''
        partes = [u.nombres or '']
        if u.apellido_paterno:
            partes.append(u.apellido_paterno)
        if u.apellido_materno:
            partes.append(u.apellido_materno)
        return ' '.join(filter(None, partes))

    def get_gerente_auditor_nombre(self, obj):
        u = obj.gerente_auditor
        if not u:
            return None
        partes = [u.nombres or '']
        if u.apellido_paterno:
            partes.append(u.apellido_paterno)
        if u.apellido_materno:
            partes.append(u.apellido_materno)
        return ' '.join(filter(None, partes))

    def validate(self, data):
        """Valida que las 4 fotos estén presentes en la creación."""
        request = self.context.get('request')
        if request and request.method == 'POST':
            fotos_requeridas = [
                'foto_ultimas_operaciones',
                'foto_carga_sistema',
                'foto_seguimiento_slot',
                'foto_recarga_error',
            ]
            faltantes = [f for f in fotos_requeridas if not data.get(f)]
            if faltantes:
                raise serializers.ValidationError(
                    {f: 'Este campo de imagen es obligatorio.' for f in faltantes}
                )
        return data


class AuditoriaVacioSerializer(serializers.Serializer):
    """
    Serializador mínimo para la acción de auditoría.
    Solo acepta el veredicto; el gerente_auditor lo inyecta la vista.
    """
    VEREDICTOS = [
        ('auditado_aprobado', 'Auditado / Aprobado'),
        ('rechazado_investigacion', 'Rechazado / En Investigación'),
    ]
    veredicto = serializers.ChoiceField(choices=VEREDICTOS)
    comentario_auditoria = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Observación opcional del gerente'
    )
