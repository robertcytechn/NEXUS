from django.db import models

class MenuConfig(models.Model):
    configuracion = models.JSONField(default=list)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'menu_config'
        verbose_name = "Configuración de Menú"
        verbose_name_plural = "Configuraciones de Menú"

    def __str__(self):
        return f"Menu Configurado ({self.actualizado_en})"
