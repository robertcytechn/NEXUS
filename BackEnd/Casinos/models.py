from django.db import models
from ModelBase.models import ModeloBase


class Casino(ModeloBase):
    """
    Representa una sede física o unidad de negocio de la organización.
    """
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Casino", help_text="Nombre oficial del casino")
    identificador = models.CharField(
        max_length=50, unique=True, verbose_name="Identificador", 
        help_text="Código único para identificar el casino (ej. código interno o número de licencia)",
        blank=True, null=True
        )
    direccion = models.CharField(max_length=255, verbose_name="Dirección", help_text="Dirección completa del casino")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono de Contacto", help_text="Número de teléfono del casino (opcional)")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad", help_text="Ciudad donde se encuentra el casino")
    encargado = models.CharField(max_length=100, blank=True, null=True, verbose_name="Encargado", help_text="Nombre del responsable operativo del casino")

    horario_apertura = models.TimeField(verbose_name="Horario de Apertura", 
                                        help_text="Hora de apertura del casino",
                                        blank=True, null=True)
    horario_cierre = models.TimeField(verbose_name="Horario de Cierre", 
                                        help_text="Hora de cierre del casino",
                                        blank=True, null=True)


    # Configuración del Mapa de Sala (Digital Twin)
    grid_width = models.PositiveIntegerField(
        default=50,
        verbose_name="Ancho de Cuadrícula",
        help_text="Número de columnas del mapa de sala (ancho de la cuadrícula). Default: 50"
    )
    grid_height = models.PositiveIntegerField(
        default=50,
        verbose_name="Alto de Cuadrícula",
        help_text="Número de filas del mapa de sala (alto de la cuadrícula). Default: 50"
    )

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'casinos'
        verbose_name = "Casino"
        verbose_name_plural = "Casinos"
        ordering = ['nombre']
