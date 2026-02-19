from django.db import models
from ModelBase.models import ModeloBase
from Casinos.models import Casino # Importación directa arriba

class InventarioSala(ModeloBase):
    TIPO_ARTICULO_CHOICES = [
        ('herramienta', 'Herramienta'),
        ('consumible', 'Consumible'),
    ]

    # Relación verticalizada
    casino = models.ForeignKey(
        Casino,
        on_delete=models.CASCADE,
        related_name='inventarios',
        verbose_name="Casino",
        help_text="Sala a la que pertenece este artículo"
    )

    # Atributos del artículo
    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre del Artículo",
        help_text="Nombre de la herramienta o consumible (ej: Cautín, Tornillos M3)"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_ARTICULO_CHOICES, # Corregido conceptualmente a TIPO_ARTICULO_CHOICES
        default='consumible',
        verbose_name="Tipo de Artículo",
        help_text="Categorización para separar herramientas de consumibles"
    )

    cantidad = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad",
        help_text="Existencia física actual en la sala"
    )

    class Meta:
        db_table = 'alm_inventario_sala'
        verbose_name = "Artículo de Inventario"
        verbose_name_plural = "Artículos de Inventario"

    def __str__(self):
        return f"{self.nombre} - {self.casino.nombre}"