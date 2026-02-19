from django.db import models
from ModelBase.models import ModeloBase
from Casinos.models import Casino
from Usuarios.models import Usuarios
from Proveedores.models import Proveedor # Importación directa del catálogo de proveedores

class AuditoriaServicioExterno(ModeloBase):
    AREAS_ACCESO_CHOICES = [
        ('site_servidores', 'Site de Servidores'),
        ('racks_sala', 'Racks de Sala'),
        ('area_maquinas', 'Área de Máquinas (Piso)'),
        ('oficinas_tecnicas', 'Oficinas Técnicas'),
        ('boveda_conteo', 'Bóveda / Área de Conteo'),
        ('sala', 'Sala de Juegos'),
        ('cocina', 'Cocina'),
        ('comedor', 'Comedor'),
        ('cajas', 'Cajas'),
        ('jv', 'JV / Monitoreo'),
    ]

    TIPO_SERVICIO_CHOICES = [
        ('internet_enlaces', 'Internet y Enlaces'),
        ('climatizacion', 'Aire Acondicionado / Clima'),
        ('energia_ups', 'Energía / UPS / Plantas'),
        ('seguridad_cctv', 'Seguridad / CCTV'),
        ('limpieza_profunda', 'Limpieza Especializada'),
        ('mantenimiento_equipo', 'Mantenimiento de Equipo Técnico'),
        ('fumigacion', 'Fumigación / Sanitización'),
        ('obra_civil', 'Reparaciones Locales'),
    ]

    # Relaciones y Atributos verticalizados
    casino = models.ForeignKey(
        Casino,
        on_delete=models.CASCADE,
        related_name='auditorias_externas',
        verbose_name="Casino",
        help_text="Sucursal donde se realiza el servicio externo"
    )

    empresa_proveedora = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='servicios_realizados',
        verbose_name="Empresa Proveedora",
        help_text="Compañía externa que brinda el servicio técnico"
    )

    nombre_tecnico_externo = models.CharField(
        max_length=150,
        verbose_name="Nombre del Técnico Externo",
        help_text="Nombre completo de la persona enviada por el proveedor"
    )

    supervisor_interno = models.ForeignKey(
        Usuarios,
        on_delete=models.PROTECT,
        related_name='supervisiones_externas',
        verbose_name="Supervisor de Sistemas",
        help_text="Personal interno que vigila y autoriza el acceso"
    )

    area_acceso = models.CharField(
        max_length=50,
        choices=AREAS_ACCESO_CHOICES,
        verbose_name="Área de Acceso",
        help_text="Zona crítica donde el externo realizó sus labores"
    )

    tipo_servicio = models.CharField(
        max_length=50,
        choices=TIPO_SERVICIO_CHOICES,
        verbose_name="Tipo de Servicio",
        help_text="Motivo técnico de la visita externa"
    )

    descripcion_actividad = models.TextField(
        verbose_name="Actividades Realizadas",
        help_text="Detalle de los cambios o revisiones efectuadas por el externo"
    )

    hora_entrada = models.DateTimeField(
        verbose_name="Hora de Entrada",
        help_text="Momento en que el externo ingresó al área técnica"
    )

    hora_salida = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Hora de Salida",
        help_text="Momento en que el externo se retiró del área"
    )

    class Meta:
        db_table = 'aud_servicios_externos'
        verbose_name = "Auditoría de Servicio Externo"
        verbose_name_plural = "Auditorías de Servicios Externos"

    def __str__(self):
        return f"{self.empresa_proveedora.nombre} - {self.casino.nombre}"