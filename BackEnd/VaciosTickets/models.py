from django.db import models
from ModelBase.models import ModeloBase
from Casinos.models import Casino
from Maquinas.models import Maquina
from Usuarios.models import Usuarios
import os
from datetime import datetime


def vacio_foto_upload(instance, filename):
    """Genera ruta dinámica para subir imágenes de evidencia de vacíos."""
    base, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ticket_id = instance.pk if instance.pk else 'new'
    nuevo_nombre = f"vacio_{ticket_id}_{timestamp}{ext}"
    return os.path.join('vacios/evidencias', nuevo_nombre)


class ConfiguracionCasino(ModeloBase):
    """
    Parámetros operativos por casino que gobiernan la aprobación automática
    de reembolsos de vacíos.
    - umbral_autorizacion: si el monto excede este valor se exige autorización gerencial.
    - siempre_requiere_autorizacion: fuerza autorización sin importar el monto.
    """
    casino = models.OneToOneField(
        Casino,
        on_delete=models.CASCADE,
        related_name='configuracion_vacios',
        verbose_name='Casino',
        help_text='Casino al que pertenece esta configuración'
    )
    umbral_autorizacion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1000,
        verbose_name='Umbral de Autorización ($)',
        help_text='Monto a partir del cual el ticket requiere aprobación gerencial'
    )
    siempre_requiere_autorizacion = models.BooleanField(
        default=False,
        verbose_name='Siempre Requiere Autorización',
        help_text='Si está activado, todo ticket de este casino pasa a estado pendiente sin importar el monto'
    )

    class Meta:
        verbose_name = 'Configuración de Casino (Vacíos)'
        verbose_name_plural = 'Configuraciones de Casino (Vacíos)'

    def __str__(self):
        return f'Config Vacíos — {self.casino.nombre}'


class TicketVacio(ModeloBase):
    """
    Ticket de reembolso forense para dinero «vacío»: fondos que el cliente cargó
    en la máquina pero que el sistema no registró correctamente por falla de red o software.

    Estados operativos
    ------------------
    - pendiente_autorizacion : monto >= umbral o casino con flag activo.
    - autorizado_carga        : aprobado automáticamente (bajo el umbral).
    - carga_realizada         : el técnico confirmó la recarga física.

    Estados de auditoría
    --------------------
    Todos los tickets, independientemente de si fueron auto-aprobados, nacen
    con estado_auditoria = 'pendiente_revision'. La Gerencia/Admin emite el
    veredicto posteriormente.
    """

    # ── Choices ──────────────────────────────────────────────────────────

    ESTADO_OPERATIVO_CHOICES = [
        ('pendiente_autorizacion', 'Pendiente Autorización'),
        ('autorizado_carga', 'Autorizado para Carga'),
        ('carga_realizada', 'Carga Realizada'),
    ]

    ESTADO_AUDITORIA_CHOICES = [
        ('pendiente_revision', 'Pendiente de Revisión'),
        ('auditado_aprobado', 'Auditado / Aprobado'),
        ('rechazado_investigacion', 'Rechazado / En Investigación'),
    ]

    MOTIVO_FALLA_CHOICES = [
        ('error_red', 'Error de Red / Timeout'),
        ('caida_sistema', 'Caída del Sistema Central'),
        ('falla_software_maquina', 'Falla de Software en Máquina'),
        ('desconexion_brusca', 'Desconexión Brusca de Energía'),
        ('error_billetero', 'Error de Billetero / Ticket'),
        ('doble_cobro', 'Doble Cobro / Transacción Duplicada'),
        ('otro', 'Otro (ver explicación)'),
    ]

    # ── Datos base ────────────────────────────────────────────────────────

    casino = models.ForeignKey(
        Casino,
        on_delete=models.PROTECT,
        related_name='tickets_vacios',
        verbose_name='Casino',
        help_text='Casino donde ocurrió el vacío'
    )
    maquina = models.ForeignKey(
        Maquina,
        on_delete=models.PROTECT,
        related_name='tickets_vacios',
        verbose_name='Máquina',
        help_text='Máquina afectada'
    )
    cliente_nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del Cliente',
        help_text='Nombre completo del cliente que reporta el vacío'
    )
    monto_extraviado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto Extraviado ($)',
        help_text='Cantidad de dinero que el cliente cargó y no fue acreditada'
    )

    # ── Trazabilidad de usuarios ──────────────────────────────────────────

    tecnico_creador = models.ForeignKey(
        Usuarios,
        on_delete=models.PROTECT,
        related_name='tickets_vacios_creados',
        verbose_name='Técnico Creador',
        help_text='Técnico que abrió el ticket de vacío'
    )
    gerente_auditor = models.ForeignKey(
        Usuarios,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_vacios_auditados',
        verbose_name='Gerente Auditor',
        help_text='Gerente o Admin que emitió el veredicto de auditoría'
    )

    # ── Fechas ────────────────────────────────────────────────────────────

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_auditoria = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Auditoría',
        help_text='Timestamp en que el gerente emitió su veredicto'
    )

    # ── Evidencias fotográficas ───────────────────────────────────────────

    foto_ultimas_operaciones = models.ImageField(
        upload_to=vacio_foto_upload,
        verbose_name='Foto: Últimas Operaciones',
        help_text='Captura de las últimas transacciones registradas en la máquina'
    )
    foto_carga_sistema = models.ImageField(
        upload_to=vacio_foto_upload,
        verbose_name='Foto: Carga en Sistema',
        help_text='Captura de la pantalla del sistema en el momento de la carga'
    )
    foto_seguimiento_slot = models.ImageField(
        upload_to=vacio_foto_upload,
        verbose_name='Foto: Seguimiento Slot',
        help_text='Captura del seguimiento de slot / historial de la máquina'
    )
    foto_recarga_error = models.ImageField(
        upload_to=vacio_foto_upload,
        verbose_name='Foto: Error de Recarga',
        help_text='Captura del error mostrado durante el intento de recarga'
    )

    # ── Dictamen ─────────────────────────────────────────────────────────

    motivo_falla = models.CharField(
        max_length=50,
        choices=MOTIVO_FALLA_CHOICES,
        verbose_name='Motivo de Falla',
        help_text='Categoría del fallo que originó el vacío'
    )
    explicacion_detallada = models.TextField(
        verbose_name='Explicación Detallada',
        help_text='Descripción técnica completa de lo ocurrido'
    )

    # ── Estados ────────────────────────────────────────────────────────────

    estado_operativo = models.CharField(
        max_length=30,
        choices=ESTADO_OPERATIVO_CHOICES,
        default='autorizado_carga',
        verbose_name='Estado Operativo',
        help_text='Refleja si el ticket ha sido autorizado para proceder con la recarga'
    )
    estado_auditoria = models.CharField(
        max_length=30,
        choices=ESTADO_AUDITORIA_CHOICES,
        default='pendiente_revision',
        verbose_name='Estado de Auditoría',
        help_text='Veredicto del gerente sobre la legitimidad del vacío. Siempre inicia en "Pendiente de Revisión"'
    )

    # ── Lógica de negocio ─────────────────────────────────────────────────

    def _determinar_estado_operativo(self):
        """
        Regla de negocio:
        - Si el casino tiene «siempre_requiere_autorizacion» activo → pendiente_autorizacion.
        - Si el monto excede el umbral configurado en el casino → pendiente_autorizacion.
        - En cualquier otro caso → autorizado_carga.
        """
        try:
            config = self.casino.configuracion_vacios
            if config.siempre_requiere_autorizacion:
                return 'pendiente_autorizacion'
            if self.monto_extraviado is not None and self.monto_extraviado >= config.umbral_autorizacion:
                return 'pendiente_autorizacion'
        except ConfiguracionCasino.DoesNotExist:
            # Si el casino no tiene configuración, por seguridad se pide autorización
            return 'pendiente_autorizacion'
        return 'autorizado_carga'

    def save(self, *args, **kwargs):
        # Aplicar regla de negocio solo en la creación (pk es None)
        if not self.pk:
            self.estado_operativo = self._determinar_estado_operativo()
            # Regla de oro: todo ticket nace con auditoría pendiente
            self.estado_auditoria = 'pendiente_revision'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Ticket de Vacío'
        verbose_name_plural = 'Tickets de Vacíos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Vacío #{self.pk} | {self.casino.nombre} | ${self.monto_extraviado} | {self.get_estado_operativo_display()}'
