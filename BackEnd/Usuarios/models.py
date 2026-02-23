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

    puntos_gamificacion = models.PositiveIntegerField(
        default=0,
        help_text="Puntos disponibles actualmente. Se suman al ganar reconocimientos y "
                  "se descuentan al canjear recompensas en la tienda."
    )

    puntos_gamificacion_historico = models.PositiveIntegerField(
        default=0,
        help_text="Total acumulado de puntos ganados en toda la trayectoria del técnico. "
                  "Solo se incrementa, nunca disminuye. Refleja el esfuerzo real independientemente "
                  "de canjes realizados. Se usa para calcular el rango."
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

    # ──────────────────────────────────────────────────────────────────────
    # SISTEMA RPG — RANGOS DE GAMIFICACIÓN (basados en histórico acumulado)
    # ──────────────────────────────────────────────────────────────────────
    RANGOS_GAMIFICACION = [
        (4500, 10, 'Leyenda de NEXUS',        '⭐⭐⭐⭐⭐'),
        (3600, 9,  'Guardián del Casino',     '⭐⭐⭐⭐'),
        (2800, 8,  'Arquitecto de Sala',      '🔷🔷🔷🔷'),
        (2100, 7,  'Maestro Electrónico',     '🔷🔷🔷'),
        (1500, 6,  'Técnico Élite',           '🔷🔷'),
        (1000, 5,  'Especialista en Hardware','🔷'),
        (600,  4,  'Operador de Máquinas',    '🔶🔶🔶'),
        (300,  3,  'Técnico de Soporte',      '🔶🔶'),
        (100,  2,  'Aprendiz de Sala',        '🔶'),
        (0,    1,  'Novato de Mantenimiento', '🔩'),
    ]

    @property
    def rango_gamificacion(self) -> dict:
        """
        Calcula el rango actual del técnico en función de sus
        `puntos_gamificacion_historico` (el total histórico no disminuye).

        Retorna un diccionario con:
          - nivel (int):       Número de nivel del 1 al 10
          - titulo (str):      Nombre del rango
          - insignia (str):    Emoji/icono decorativo
          - puntos_min (int):  Umbral de entrada al nivel actual
          - puntos_sig (int|None): Puntos del siguiente nivel (None si es máximo)
          - progreso_pct (float): % de avance dentro del nivel actual (0.0–100.0)
        """
        pts = self.puntos_gamificacion_historico
        for puntos_min, nivel, titulo, insignia in self.RANGOS_GAMIFICACION:
            if pts >= puntos_min:
                # Calcular siguiente umbral para la barra de progreso
                idx = self.RANGOS_GAMIFICACION.index((puntos_min, nivel, titulo, insignia))
                if idx > 0:
                    puntos_sig = self.RANGOS_GAMIFICACION[idx - 1][0]
                    rango_tamaño = puntos_sig - puntos_min
                    progreso = round(((pts - puntos_min) / rango_tamaño) * 100, 1)
                else:
                    puntos_sig = None  # Nivel máximo
                    progreso = 100.0

                return {
                    'nivel': nivel,
                    'titulo': titulo,
                    'insignia': insignia,
                    'puntos_min': puntos_min,
                    'puntos_sig': puntos_sig,
                    'progreso_pct': min(progreso, 100.0),
                }
        # Fallback (nunca debería llegar aquí)
        return {'nivel': 1, 'titulo': 'Novato de Mantenimiento', 'insignia': '🔩',
                'puntos_min': 0, 'puntos_sig': 100, 'progreso_pct': 0.0}

    def save(self, *args, **kwargs):
        """
        Override de save:
          - Sincroniza `puntos_gamificacion_historico` automáticamente.
          - El histórico SOLO sube: si los puntos actuales superan el histórico
            previo, se actualiza. Nunca se decrementa (canjear no afecta el rango).
          - Compatible con llamadas que usen `update_fields`: si puntos_gamificacion
            está en update_fields, se agrega puntos_gamificacion_historico
            automáticamente para que el histórico siempre sea consistente.
        """
        update_fields = kwargs.get('update_fields')

        if self.pk:
            try:
                previo = Usuarios.objects.get(pk=self.pk)
                if self.puntos_gamificacion > previo.puntos_gamificacion:
                    diferencia = self.puntos_gamificacion - previo.puntos_gamificacion
                    self.puntos_gamificacion_historico = (
                        previo.puntos_gamificacion_historico + diferencia
                    )
                    # Si se usa update_fields, aseguramos que historico también se persista
                    if update_fields is not None:
                        campos = list(update_fields)
                        if 'puntos_gamificacion_historico' not in campos:
                            campos.append('puntos_gamificacion_historico')
                        kwargs['update_fields'] = campos
            except Usuarios.DoesNotExist:
                pass
        else:
            # Usuario nuevo: si se crea con puntos, el histórico arranca igual
            self.puntos_gamificacion_historico = self.puntos_gamificacion
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} - {self.casino.nombre}"