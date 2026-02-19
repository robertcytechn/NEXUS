from django.db import models
from ModelBase.models import ModeloBase 
from datetime import date

from Maquinas.models import Maquina
from Usuarios.models import Usuarios


class Ticket(ModeloBase):
    CATEGORIAS_CHOICES = [
        ('hardware', 'Hardware'),
        ('perifericos', 'Periféricos'),
        ('software', 'Software'),
        ('red', 'Red / Comunicación'),
        ('otros', 'Otros'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
        ('emergencia', 'Emergencia'),
        ('sin_prioridad', 'Sin Prioridad'),
    ]

    ESTADO_TICKET_CHOICES = [
        ('abierto', 'Abierto'),
        ('proceso', 'En Proceso'),
        ('espera', 'En Espera'),
        ('cerrado', 'Cerrado'),
        ('reabierto', 'Reabierto'),
    ]

    # Relaciones
    maquina = models.ForeignKey(
        Maquina, 
        on_delete=models.CASCADE, 
        related_name='tickets',
        help_text="Máquina relacionada con el problema reportado"
        )
    reportante = models.ForeignKey(
        Usuarios, 
        on_delete=models.PROTECT, 
        related_name='tickets_reportados',
        help_text="Usuario que reporta el problema"
        )
    tecnico_asignado = models.ForeignKey(
        Usuarios, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='tickets_asignados',
        help_text="Técnico asignado al ticket"
        )

    # Información del Problema
    folio = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False,
        help_text="Identificador único del ticket (generado automáticamente)"
    )
    categoria = models.CharField(
        max_length=30, 
        choices=CATEGORIAS_CHOICES,
        help_text="Categoría del problema reportado"
    )
    subcategoria = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Subcategoría o detalle específico del problema"
    ) # Ejemplo: "Billetero trabado"
    prioridad = models.CharField(
        max_length=20, 
        choices=PRIORIDAD_CHOICES, 
        default='media'
    )
    descripcion_problema = models.TextField(
        help_text="Descripción detallada del problema reportado"
    )
    estado_maquina_reportado = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        choices=Maquina.ESTADOS_CHOICES,
        help_text="Estado al que se actualizó la máquina al reportar el ticket"
    )
    
    # Seguimiento y Control
    estado_ciclo = models.CharField(
        max_length=20, 
        choices=ESTADO_TICKET_CHOICES, 
        default='abierto'
    )
    notas_seguimiento = models.TextField(
        null=True, blank=True,
        help_text="Notas adicionales para el seguimiento del ticket"
    )
    explicacion_cierre = models.TextField(
        null=True, blank=True,
        help_text="Explicación o motivo del cierre del ticket"
    )
    contador_reaperturas = models.PositiveIntegerField(
        default=0,
        help_text="Número de veces que el ticket ha sido reabierto"
    )

    class Meta:
        db_table = 'tickets'
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ['-creado_en']


    def save(self, *args, **kwargs):
        # Generación automática de Folio si no existe
        if not self.folio:
            count = Ticket.objects.count() + 1
            self.folio = f"TK-{date.today().year}-{count:04d}"
        super().save(*args, **kwargs)