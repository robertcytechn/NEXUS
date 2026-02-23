from rest_framework import serializers
from .models import Notificacion, NotificacionUsuario

class NotificacionSerializer(serializers.ModelSerializer):
    leido = serializers.SerializerMethodField()
    
    class Meta:
        model = Notificacion
        fields = '__all__'
        
        # Blindaje de campos de auditoría heredados de ModeloBase
        read_only_fields = [
            'creado_en',
            'modificado_en',
            'creado_por',
            'modificado_por',
        ]
    
    def get_leido(self, obj):
        """
        Determina si la notificación ha sido leída por el usuario actual.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return NotificacionUsuario.objects.filter(
                notificacion=obj,
                usuario=request.user
            ).exists()
        return False

    def validate(self, data):
        """
        Garantiza que la combinación de campos de segmentación sea válida
        y mutuamente excluyente para evitar fugas entre grupos.

        Reglas:
          ① Global / Director  → es_global=True, sin destinos.
          ② Personal            → usuario_destino set, sin casino ni rol.
          ③ Casino              → casino_destino set, sin rol ni usuario.
          ④ Rol + Casino        → casino_destino + rol_destino, sin usuario.
        """
        es_global       = data.get('es_global',       getattr(self.instance, 'es_global',       False))
        usuario_destino = data.get('usuario_destino', getattr(self.instance, 'usuario_destino', None))
        casino_destino  = data.get('casino_destino',  getattr(self.instance, 'casino_destino',  None))
        rol_destino     = data.get('rol_destino',     getattr(self.instance, 'rol_destino',     None))

        # ── Regla 1: Global no acepta destinos específicos ──────────
        if es_global:
            if usuario_destino or casino_destino or rol_destino:
                raise serializers.ValidationError(
                    "Una notificación global no puede combinarse con "
                    "usuario_destino, casino_destino ni rol_destino."
                )

        # ── Regla 2: Personal no acepta casino ni rol ────────────────
        if usuario_destino:
            if casino_destino or rol_destino:
                raise serializers.ValidationError(
                    "Una notificación personal (usuario_destino) no puede "
                    "llevar casino_destino ni rol_destino."
                )
            if es_global:
                raise serializers.ValidationError(
                    "Una notificación personal no puede ser global."
                )

        # ── Regla 3: rol_destino requiere casino_destino ─────────────
        if rol_destino and not casino_destino:
            raise serializers.ValidationError(
                "Para segmentar por rol debes indicar también casino_destino."
            )

        # ── Regla 4: debe haber al menos un criterio de destino ──────
        if not es_global and not usuario_destino and not casino_destino:
            raise serializers.ValidationError(
                "Debes indicar al menos un criterio de destino: "
                "es_global, usuario_destino o casino_destino."
            )

        return data


class NotificacionUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificacionUsuario
        fields = '__all__'
        
        read_only_fields = [
            'fecha_visto',
            'creado_en',
            'modificado_en',
            'creado_por',
            'modificado_por',
        ]