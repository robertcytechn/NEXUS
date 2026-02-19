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