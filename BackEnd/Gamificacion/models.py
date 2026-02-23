from django.db import models
from ModelBase.models import ModeloBase
from Casinos.models import Casino


class RecompensaGamificacion(ModeloBase):
    """
    Tienda de Recompensas del sistema RPG de NEXUS.

    Solo el personal con rol GERENCIA puede crear y editar recompensas.
    Los técnicos pueden verlas y canjearlas consumiendo sus puntos_gamificacion
    (puntos disponibles), sin afectar el puntos_gamificacion_historico que
    determina su rango.
    """

    titulo = models.CharField(
        max_length=150,
        verbose_name="Título de la Recompensa",
        help_text="Nombre de la recompensa (ej: Día libre adicional, Bono de alimentación)"
    )

    descripcion = models.TextField(
        verbose_name="Descripción",
        help_text="Detalle completo de la recompensa: qué incluye, cómo se reclama, vigencia, etc."
    )

    costo_puntos = models.PositiveIntegerField(
        verbose_name="Costo en Puntos",
        help_text="Cantidad de puntos de gamificación necesarios para canjear esta recompensa"
    )

    casino = models.ForeignKey(
        Casino,
        on_delete=models.CASCADE,
        related_name='recompensas_gamificacion',
        verbose_name="Casino",
        help_text="Sucursal que ofrece esta recompensa. Solo los técnicos de este casino pueden verla."
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Controla la visibilidad de la recompensa. Desactívala para retirarla sin eliminarla."
    )

    stock = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Stock Disponible",
        help_text="Cantidad máxima de canjes permitidos. Deja vacío para stock ilimitado."
    )

    class Meta:
        db_table = 'recompensa_gamificacion'
        verbose_name = "Recompensa de Gamificación"
        verbose_name_plural = "Tienda de Recompensas"
        ordering = ['costo_puntos']

    def __str__(self):
        estado = "✅" if self.activo else "❌"
        return f"{estado} {self.titulo} — {self.costo_puntos} pts ({self.casino.nombre})"


class CanjeRecompensa(ModeloBase):
    """
    Registro histórico de cada canje realizado por un técnico.

    Al canjear:
      - Se descuenta de usuario.puntos_gamificacion (puntos disponibles)
      - El puntos_gamificacion_historico NO se modifica (protege el rango)
    """

    ESTADO_CANJE_CHOICES = [
        ('pendiente', 'Pendiente de Entrega'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(
        'Usuarios.Usuarios',
        on_delete=models.PROTECT,
        related_name='canjes_realizados',
        verbose_name="Técnico",
        help_text="Usuario que realizó el canje"
    )

    recompensa = models.ForeignKey(
        RecompensaGamificacion,
        on_delete=models.PROTECT,
        related_name='canjes',
        verbose_name="Recompensa Canjeada",
        help_text="Recompensa seleccionada por el técnico"
    )

    puntos_descontados = models.PositiveIntegerField(
        verbose_name="Puntos Descontados",
        help_text="Puntos deducidos al momento del canje (snapshot del costo en ese instante)"
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CANJE_CHOICES,
        default='pendiente',
        verbose_name="Estado del Canje",
        help_text="El personal de gerencia actualiza este estado al entregar la recompensa"
    )

    nota_gerencia = models.TextField(
        null=True,
        blank=True,
        verbose_name="Nota de Gerencia",
        help_text="Observaciones de gerencia al procesar el canje"
    )

    class Meta:
        db_table = 'canje_recompensa'
        verbose_name = "Canje de Recompensa"
        verbose_name_plural = "Historial de Canjes"
        ordering = ['-creado_en']

    def __str__(self):
        return (
            f"{self.usuario.username} → {self.recompensa.titulo} "
            f"({self.puntos_descontados} pts) [{self.get_estado_display()}]"
        )
