from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from ModelBase.models import ModeloBase

class MantenimientoPreventivo(ModeloBase):
    # Estados finales permitidos (Choices de la máquina)
    ESTADO_RESULTANTE_CHOICES = [
        ('operativa', 'Operativa'),
        ('dañada_operativa', 'Dañada pero Operativa'),
        ('dañada', 'Dañada'),
        ('observacion', 'En Observación'),
    ]

    # Atributos con formato vertical
    maquina = models.ForeignKey(
        'Maquinas.Maquina',
        on_delete=models.CASCADE,
        related_name='mantenimientos_preventivos',
        verbose_name="Máquina Intervenida",
        help_text="Selección de la unidad a la que se le realiza la rutina preventiva"
    )

    tecnico_responsable = models.ForeignKey(
        'Usuarios.Usuarios',
        on_delete=models.PROTECT,
        verbose_name="Técnico Ejecutor",
        help_text="Usuario que realiza físicamente el mantenimiento preventivo"
    )

    fecha_mantenimiento = models.DateField(
        verbose_name="Fecha de Ejecución",
        help_text="Día en el que se llevó a cabo la limpieza y revisión programada"
    )

    estado_final_maquina = models.CharField(
        max_length=30,
        choices=ESTADO_RESULTANTE_CHOICES,
        default='operativa',
        verbose_name="Estado Final",
        help_text="Estatus en el que queda la máquina tras concluir la rutina"
    )

    observaciones = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observaciones Técnicas",
        help_text="Notas adicionales sobre el estado general (ej: desgaste de piezas, limpieza profunda)"
    )

    class Meta:
        db_table = 'maquina_mantenimientos'
        verbose_name = "Mantenimiento Preventivo"
        verbose_name_plural = "Mantenimientos Preventivos"

# --- TRIGGER DE ACTUALIZACIÓN DE MÁQUINA ---
@receiver(post_save, sender=MantenimientoPreventivo)
def actualizar_estatus_maquina_preventivo(sender, instance, created, **kwargs):
    """
    Al guardar un mantenimiento preventivo, se actualiza la fecha oficial 
    en la tabla de máquinas y su estado de operatividad.
    """
    if created:
        maquina = instance.maquina
        # Actualizamos la fecha de último mantenimiento oficial
        maquina.ultimo_mantenimiento = instance.fecha_mantenimiento
        # Actualizamos el estado operativo
        maquina.estado_actual = instance.estado_final_maquina
        # Usar update_fields para asegurar que solo se actualicen estos campos específicos
        maquina.save(update_fields=['ultimo_mantenimiento', 'estado_actual', 'modificado_en'])