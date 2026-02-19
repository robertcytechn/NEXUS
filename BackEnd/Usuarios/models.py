from django.db import models
from ModelBase.models import ModeloBase
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from Casinos.models import Casino
from Roles.models import Rol
import os
from datetime import datetime

def custom_upload_to(instance, filename):
    base, ext = os.path.splitext(filename)
    # Usar ID si existe, sino 'new' (aunque idealmente se actualiza depues de guardar, 
    # pero para este caso de uso principal es update)
    user_id = instance.pk if instance.pk else 'new'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Limpiar nombre de usuario de caracteres especiales si es necesario, 
    # por ahora asumimos username seguro o lo usamos tal cual
    new_filename = f"{user_id}_{instance.username}_{timestamp}{ext}"
    return os.path.join('usuarios/avatars', new_filename)

class UsuarioManager(BaseUserManager):
    """Manager personalizado para la creación de usuarios con validaciones específicas."""
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class Usuarios(AbstractBaseUser, ModeloBase):
    """
    Usuario del sistema con autenticación basada en roles y casino.
    Incluye seguimiento de sesiones y medidas de seguridad.
    """
    username = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Nombre de usuario único para acceso al sistema"
    )
    email = models.EmailField(
        max_length=150, 
        unique=True,
        help_text="Correo electrónico institucional del usuario"
    )
    
    nombres = models.CharField(
        max_length=100,
        help_text="Nombre(s) del usuario"
    )
    apellido_paterno = models.CharField(
        max_length=100,
        help_text="Primer apellido del usuario"
    )
    apellido_materno = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        help_text="Segundo apellido del usuario"
    )
    
    casino = models.ForeignKey(
        Casino, 
        on_delete=models.PROTECT,
        help_text="Casino al que pertenece el usuario"
    )
    rol = models.ForeignKey(
        Rol, 
        on_delete=models.PROTECT,
        help_text="Rol que determina los permisos del usuario"
    )
    
    session_token = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Token de sesión activa (generado automáticamente)"
    )
    refresh_token = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Token para renovar sesión (generado automáticamente)"
    )
    ultima_ip = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="Última dirección IP desde donde se conectó"
    )
    user_agent = models.TextField(
        null=True, 
        blank=True,
        help_text="Información del navegador/dispositivo utilizado"
    )
    intentos_fallidos = models.PositiveSmallIntegerField(
        default=0,
        help_text="Contador de intentos de acceso fallidos"
    )
    requiere_cambio_password = models.BooleanField(
        default=False,
        help_text="Indica si el usuario debe cambiar su contraseña en el próximo acceso"
    )

    EULAAceptada = models.BooleanField(
        default=False,
        help_text="Indica si el usuario ha aceptado el acuerdo de licencia de uso de software (EULA)"
    )

    avatar = models.FileField(
        upload_to=custom_upload_to,
        null=True,
        blank=True,
        help_text="Imagen de perfil del usuario"
    )
    
    
    objects = UsuarioManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nombres', 'apellido_paterno']

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} - {self.casino.nombre}"