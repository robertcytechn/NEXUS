from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class ModeloBase(models.Model):
    """
    Modelo abstracto que proporciona campos de auditoría y borrado lógico.
    Hereda este modelo en lugar de models.Model para tener trazabilidad completa.
    """
    esta_activo = models.BooleanField(
        default=True, 
        verbose_name="Estado Activo",
        help_text="Indica si el registro está activo o fue eliminado lógicamente"
    )
    creado_en = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de Creación",
        help_text="Fecha y hora de creación del registro"
    )
    modificado_en = models.DateTimeField(
        auto_now=True, 
        verbose_name="Última Modificación",
        help_text="Fecha y hora de la última actualización"
    )
    creado_por = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="Creado por",
        help_text="Usuario que creó el registro"
    )
    modificado_por = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="Modificado por",
        help_text="Usuario que realizó la última modificación"
    )
    notas_internas = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Notas de Auditoría",
        help_text="Observaciones internas para seguimiento y auditoría"
    )

    class Meta:
        abstract = True