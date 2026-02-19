from django.db import models

class Denominacion(models.Model):
    """Maestra de valores permitidos en las máquinas."""
    valor = models.DecimalField(
        verbose_name="Valor",
        help_text="Valor monetario de la denominación (ej: 1.00, 0.25)",
        max_digits=5, 
        decimal_places=2, 
        unique=True
        )
    etiqueta = models.CharField(
        max_length=20,
        help_text="Etiqueta para mostrar la denominación (ej: \"$1.00\", \"$0.25 ctv\")",
        verbose_name="Etiqueta",
    )

    class Meta:
        db_table = 'cat_denominaciones'
        verbose_name = "Denominación"
        verbose_name_plural = "Denominaciones"

    def __str__(self):
        return self.etiqueta