from django.db import models
from django.utils import timezone
from ModelBase.models import ModeloBase
from Casinos.models import Casino
from Usuarios.models import Usuarios


class TareaEspecial(ModeloBase):
    # Catálogos de estado y urgencia
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica / Inmediata'),
    ]

    ESTADO_TAREA_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En Curso'),
        ('completada', 'Terminada'),
        ('cancelada', 'Cancelada'),
    ]

    # Atributos con formato vertical
    titulo = models.CharField(
        max_length=150,
        verbose_name="Título de la Tarea",
        help_text="Descripción breve de la actividad extraordinaria"
    )

    descripcion = models.TextField(
        verbose_name="Descripción de la Tarea",
        help_text="Detalles técnicos o requerimientos de gerencia"
    )

    casino = models.ForeignKey(
        Casino,
        on_delete=models.CASCADE,
        related_name='tareas_especiales',
        verbose_name="Casino / Sucursal",
        help_text="Ubicación donde se debe realizar la tarea"
    )

    creado_por_usuario = models.ForeignKey(
        Usuarios,
        on_delete=models.PROTECT,
        related_name='tareas_creadas',
        verbose_name="Usuario que dio de Alta",
        help_text="Persona que registra la tarea en el sistema"
    )

    asignado_a = models.ForeignKey(
        Usuarios,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tareas_ejecutadas',
        verbose_name="Técnico Responsable",
        help_text="Técnico que se auto-asigna para realizar la labor"
    )

    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default='media',
        verbose_name="Prioridad de Tarea",
        help_text="Nivel de importancia de la actividad"
    )

    estatus = models.CharField(
        max_length=20,
        choices=ESTADO_TAREA_CHOICES,
        default='pendiente',
        verbose_name="Estado de Avance",
        help_text="Estatus actual de la tarea especial"
    )

    fecha_apertura = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Apertura",
        help_text="Momento exacto en que se inició la tarea"
    )

    fecha_finalizacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Finalización",
        help_text="Momento en que la tarea cambió a Terminada"
    )

    resultado_final = models.TextField(
        null=True,
        blank=True,
        verbose_name="Resultado Final",
        help_text="Observaciones sobre cómo quedó el equipo o infraestructura"
    )

    class Meta:
        db_table = 'tareas_especiales'
        verbose_name = "Tarea Especial"
        verbose_name_plural = "Tareas Especiales"

    def save(self, *args, **kwargs):
        # Lógica de cierre automático
        if self.estatus == 'completada' and not self.fecha_finalizacion:
            self.fecha_finalizacion = timezone.now()
        super().save(*args, **kwargs)