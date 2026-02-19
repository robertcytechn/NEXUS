from django.db import models
from ModelBase.models import ModeloBase
from Casinos.models import Casino # Importación directa solicitada

class IncidenciaInfraestructura(ModeloBase):
    CATEGORIA_CHOICES = [
        ('electrica', 'Falla Eléctrica / Luz'),
        ('agua', 'Filtración / Agua / Gotera'),
        ('clima', 'Climatización / Aire Acondicionado'),
        ('red_externa', 'Proveedor de Internet / Enlace'),
        ('obra_civil', 'Estructura / Paredes / Techos'),
        ('otros', 'Otros Eventos Externos'),
    ]

    SEVERIDAD_CHOICES = [
        ('baja', 'Baja (Sin afectación)'),
        ('media', 'Media (Afectación parcial)'),
        ('alta', 'Alta (Riesgo operativo)'),
        ('critica', 'Crítica (Cierre de sala/área)'),
    ]

    # Relaciones y Atributos verticalizados
    casino = models.ForeignKey(
        Casino,
        on_delete=models.CASCADE,
        related_name='incidencias_infra',
        verbose_name="Casino Afectado",
        help_text="Sala donde ocurrió el evento de infraestructura"
    )

    titulo = models.CharField(
        max_length=150,
        verbose_name="Título del Evento",
        help_text="Descripción corta (ej: Apagón zona sur, Gotera fila 5)"
    )

    categoria = models.CharField(
        max_length=30,
        choices=CATEGORIA_CHOICES,
        verbose_name="Categoría del Incidente",
        help_text="Origen del problema de infraestructura"
    )

    descripcion = models.TextField(
        verbose_name="Anotaciones Detalladas",
        help_text="Relato completo de lo ocurrido y afectaciones visibles"
    )

    severidad = models.CharField(
        max_length=20,
        choices=SEVERIDAD_CHOICES,
        default='media',
        verbose_name="Nivel de Severidad",
        help_text="Impacto del evento en la operación de la sala"
    )

    afecta_operacion = models.BooleanField(
        default=False,
        verbose_name="¿Afecta Operación?",
        help_text="Marcar si el evento obligó a detener máquinas o servicios"
    )

    hora_inicio = models.DateTimeField(
        verbose_name="Hora de Inicio",
        help_text="Momento aproximado en que comenzó el incidente"
    )

    hora_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Hora de Finalización",
        help_text="Momento en que la situación fue controlada o resuelta"
    )

    class Meta:
        db_table = 'infra_incidencias'
        verbose_name = "Incidencia de Infraestructura"
        verbose_name_plural = "Incidencias de Infraestructura"

    def __str__(self):
        return f"{self.titulo} - {self.casino.nombre}"