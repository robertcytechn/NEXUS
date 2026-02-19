from django.db import models
from ModelBase.models import ModeloBase

class ModeloMaquina(ModeloBase):
    """
    Representa el modelo técnico de una máquina
    """
    # Relación con el Proveedor
    proveedor = models.ForeignKey(
        'Proveedores.Proveedor', 
        on_delete=models.CASCADE, 
        related_name='modelos_maquinas'
    )
    
    # Datos del Modelo
    nombre_modelo = models.CharField(
        max_length=100, 
        verbose_name="Nombre del Modelo",
        help_text="Identificador único del modelo de máquina dentro del proveedor"
    )
    nombre_producto = models.CharField(
        max_length=100, 
        verbose_name="Nombre del Producto/Marca",
        help_text="Nombre comercial o marca del producto"
    )
    descripcion = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Descripción Técnica",
        help_text="Detalles técnicos adicionales del modelo de máquina"
    )

    class Meta:
        db_table = 'maquina_modelos'
        verbose_name = "Modelo de Máquina"
        verbose_name_plural = "Modelos de Máquinas"
        # Regla: No repetir nombre de modelo para el MISMO proveedor
        unique_together = ['proveedor', 'nombre_modelo']

    def __str__(self):
        return f"{self.nombre_modelo} - {self.proveedor.nombre}"