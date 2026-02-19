from django.db import models
from ModelBase.models import ModeloBase

class BitacoraTecnica(ModeloBase):
    # Catálogos de opciones verticalizados
    TIPO_INTERVENCION_CHOICES = [
        ('correctiva', 'Correctiva (Reparación)'),
        ('ajuste', 'Ajuste / Calibración'),
        ('instalacion', 'Instalación / Movimiento'),
        ('actualización', 'Actualización de Software'),
        ('diagnostico', 'Solo Diagnóstico'),
    ]

    RESULTADO_CHOICES = [
        ('exitosa', 'Reparación Exitosa'),
        ('parcial', 'Reparación Parcial'),
        ('fallida', 'Prueba Fallida'),
        ('espera_refaccion', 'En espera de Refacción'),
    ]

    # Relaciones y Atributos con formato vertical
    ticket = models.ForeignKey(
        'Tickets.Ticket',
        on_delete=models.CASCADE,
        related_name='bitacoras',
        verbose_name="Ticket Relacionado",
        help_text="Vínculo obligatorio al folio del ticket en cuestión"
    )

    usuario_tecnico = models.ForeignKey(
        'Usuarios.Usuarios',
        on_delete=models.PROTECT,
        verbose_name="Técnico Responsable",
        help_text="Usuario técnico que realiza la anotación en bitácora"
    )

    tipo_intervencion = models.CharField(
        max_length=30,
        choices=TIPO_INTERVENCION_CHOICES,
        verbose_name="Tipo de Intervención",
        help_text="Categoría del trabajo realizado en la máquina"
    )

    descripcion_trabajo = models.TextField(
        verbose_name="Descripción del Trabajo",
        help_text="Detalle técnico de las pruebas y acciones ejecutadas"
    )

    resultado_intervencion = models.CharField(
        max_length=30,
        choices=RESULTADO_CHOICES,
        verbose_name="Resultado de la Intervención",
        help_text="Estatus final de la reparación tras las pruebas"
    )

    estado_maquina_resultante = models.CharField(
        max_length=30,
        choices=[
            ('operativa', 'Operativa'),
            ('dañada_operativa', 'Dañada pero Operativa'),
            ('dañada', 'Dañada'),
            ('mantenimiento', 'En Mantenimiento'),
        ],
        verbose_name="Estado de Máquina Resultante",
        help_text="Estatus en el que se deja la unidad físicamente en sala"
    )

    finaliza_ticket = models.BooleanField(
        default=False,
        verbose_name="Cierra Ticket",
        help_text="Marcar únicamente si esta acción resuelve el folio por completo"
    )

    class Meta:
        db_table = 'tickets_bitacora'
        verbose_name = "Entrada de Bitácora"
        verbose_name_plural = "Bitácoras Técnicas"

    def __str__(self):
        return f"Bitácora {self.id} - Ticket {self.ticket.folio}"