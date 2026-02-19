from rest_framework import serializers
from .models import Usuarios

class UsuariosSerializer(serializers.ModelSerializer):
    """
    Serializer completo para el modelo de usuarios con campos calculados.
    """
    nombre_completo = serializers.SerializerMethodField()
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Usuarios
        fields = [
            'id', 'username', 'email', 'nombres', 
            'apellido_paterno', 'apellido_materno', 'nombre_completo',
            'casino', 'casino_nombre', 'rol', 'rol_nombre', 'esta_activo', 
            'creado_en', 'modificado_en', 'creado_por', 'modificado_por',
            'ultima_ip', 'user_agent', 'requiere_cambio_password', 
            'password', 'session_token', 'refresh_token', 'intentos_fallidos', 'EULAAceptada',
            'avatar'
        ]
        
        extra_kwargs = {
            'password': {'write_only': True},
            'creado_en': {'read_only': True},
            'modificado_en': {'read_only': True},
            'creado_por': {'read_only': True},
            'modificado_por': {'read_only': True},
            'ultima_ip': {'read_only': True},
            'user_agent': {'read_only': True},
            'session_token': {'read_only': True},
            'refresh_token': {'read_only': True},
            'intentos_fallidos': {'read_only': True},
            'EULAAceptada': {'read_only': True},
        }

    def get_nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellido_paterno} {obj.apellido_materno or ''}".strip()

    def get_avatar(self, obj):
        """Devuelve la URL absoluta del avatar o None si no tiene."""
        if not obj.avatar:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.avatar.url)
        # Fallback sin request (ej. login que no pasa context)
        from django.conf import settings
        return f"{settings.MEDIA_URL}{obj.avatar.name}"

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance

class UsuarioLoginSerializer(serializers.Serializer):
    """Serializer para autenticación de usuario."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class UsuarioRefreshSerializer(serializers.Serializer):
    """Serializer para renovación de token de sesión."""
    refresh_token = serializers.CharField(required=True)
