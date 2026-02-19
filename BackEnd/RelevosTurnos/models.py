from django.db import models
from ModelBase.models import ModeloBase
from Usuarios.models import Usuarios
from Casinos.models import Casino

class RelevoTurno(ModeloBase):
    ESTADO_SALA_CHOICES = [
        ('limpia', 'Sin Pendientes / Todo Operativo'),
        ('con_pendientes', 'Con Pendientes Menores'),
        ('critica', 'Situación Crítica / Urgente'),
    ]

    # Relaciones verticalizadas
    casino = models.ForeignKey(
        Casino,
        on_delete=models.CASCADE,
        related_name='relevos',
        verbose_name="Casino",
        help_text="Sucursal donde se realiza el cambio de turno"
    )

    tecnico_saliente = models.ForeignKey(
        Usuarios,
        on_delete=models.PROTECT,
        related_name='relevos_entregados',
        verbose_name="Técnico que Entrega",
        help_text="Usuario que finaliza su jornada laboral"
    )

    tecnico_entrante = models.ForeignKey(
        Usuarios,
        on_delete=models.PROTECT,
        related_name='relevos_recibidos',
        verbose_name="Técnico que Recibe",
        help_text="Usuario que inicia el nuevo turno en la sala"
    )

    # Información del Relevo
    hora_salida_real = models.DateTimeField(
        verbose_name="Hora de Salida",
        help_text="Momento exacto en que el técnico saliente se retira"
    )

    estado_entrega = models.CharField(
        max_length=20,
        choices=ESTADO_SALA_CHOICES,
        default='limpia',
        verbose_name="Estado de la Sala",
        help_text="Evaluación general de la operación al momento del cambio"
    )

    pendientes_detallados = models.TextField(
        null=True,
        blank=True,
        verbose_name="Pendientes Técnicos",
        help_text="Lista de máquinas o tareas que quedaron sin concluir"
    )

    novedades_generales = models.TextField(
        null=True,
        blank=True,
        verbose_name="Novedades del Turno",
        help_text="Cualquier comentario relevante sobre el personal o la sala"
    )

    class Meta:
        db_table = 'ope_relevo_turnos'
        verbose_name = "Relevo de Turno"
        verbose_name_plural = "Relevos de Turnos"

    def __str__(self):
        return f"Relevo {self.casino.nombre} - {self.tecnico_saliente.username}"