from django.db import models
from ModelBase.models import ModeloBase
from Usuarios.models import Usuarios
from Casinos.models import Casino
from Roles.models import Rol

class Notificacion(ModeloBase):
    # Niveles de prioridad para el sistema
    NIVEL_CHOICES = [
        ('urgente', 'Urgente (Acción Inmediata)'),
        ('alerta', 'Alerta (Atención Requerida)'),
        ('informativa', 'Informativa (Solo lectura)'),
    ]

    # Origen del evento
    TIPO_CHOICES = [
        ('ticket', 'Gestión de Tickets'),
        ('infraestructura', 'Incidencia de Infraestructura'),
        ('wiki', 'Nueva Guía en Wiki'),
        ('sistema', 'Aviso del Sistema'),
        ('DIRECTOR', 'Mensaje de Dirección'),
    ]

    # Atributos verticalizados y descriptivos
    titulo = models.CharField(
        max_length=150,
        verbose_name="Título",
        help_text="Encabezado de la alerta"
    )

    contenido = models.TextField(
        verbose_name="Contenido",
        help_text="Detalle completo del mensaje"
    )

    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        default='informativa',
        verbose_name="Nivel de Prioridad"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Notificación"
    )

    # Segmentación de destino
    usuario_destino = models.ForeignKey(
        Usuarios,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones_personales',
        verbose_name="Usuario Destino",
        help_text="Si se define, solo este usuario recibirá la alerta"
    )

    casino_destino = models.ForeignKey(
        Casino,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones_sala',
        verbose_name="Casino Destino",
        help_text="Si se define, la verán los técnicos de esta sala"
    )

    rol_destino = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones_rol',
        verbose_name="Rol Destino",
        help_text="Si se define junto con casino, solo usuarios de ese rol en ese casino verán la notificación"
    )

    es_global = models.BooleanField(
        default=False,
        verbose_name="¿Es Global?",
        help_text="Marcar para que todos los usuarios de Sakai la vean"
    )

    es_del_director = models.BooleanField(
        default=False,
        verbose_name="Aviso de Dirección",
        help_text="Si es True, la notificación durará 7 días en el sistema"
    )

    class Meta:
        db_table = 'sys_notificaciones'
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        indexes = [
            models.Index(fields=['creado_en', 'es_del_director']),
        ]

    def __str__(self):
        return f"{self.titulo} ({self.nivel})"


class NotificacionUsuario(ModeloBase):
    """
    Tabla de unión para gestionar el estado de lectura de notificaciones por usuario.
    Permite que cada usuario marque independientemente una notificación como vista.
    """
    notificacion = models.ForeignKey(
        Notificacion,
        on_delete=models.CASCADE,
        related_name='lecturas',
        verbose_name="Notificación"
    )

    usuario = models.ForeignKey(
        Usuarios,
        on_delete=models.CASCADE,
        related_name='notificaciones_vistas',
        verbose_name="Usuario"
    )

    fecha_visto = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Lectura",
        help_text="Fecha y hora en que el usuario marcó la notificación como vista"
    )

    class Meta:
        db_table = 'sys_notificaciones_usuarios'
        verbose_name = "Lectura de Notificación"
        verbose_name_plural = "Lecturas de Notificaciones"
        unique_together = [['notificacion', 'usuario']]
        indexes = [
            models.Index(fields=['usuario', 'fecha_visto']),
            models.Index(fields=['notificacion', 'usuario']),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.notificacion.titulo}"