from django.db import models
from ModelBase.models import ModeloBase
from Usuarios.models import Usuarios # Importación directa solicitada
from Casinos.models import Casino
from ModelosMaquinas.models import ModeloMaquina

class WikiTecnica(ModeloBase):
    CATEGORIA_GUIA_CHOICES = [
        ('reparacion', 'Guía de Reparación'),
        ('configuracion', 'Manual de Configuración'),
        ('limpieza', 'Procedimiento de Limpieza'),
        ('error_code', 'Diccionario de Códigos de Error'),
    ]

    ESTADO_CHOICES = [
        ('pendiente_revision', 'Pendiente de Revisión'),
        ('aprobada', 'Aprobada'),
        ('publicada', 'Publicada'),
        ('rechazada', 'Rechazada'),
    ]

    # Relaciones y Atributos verticalizados
    autor = models.ForeignKey(
        Usuarios,
        on_delete=models.PROTECT,
        related_name='guias_creadas',
        verbose_name="Autor de la Guía",
        help_text="Técnico que redactó y subió el material (Para reconocimiento público)"
    )

    casino_origen = models.ForeignKey(
        Casino,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guias_locales',
        verbose_name="Casino de Origen",
        help_text="Sucursal donde se originó la solución o el caso de estudio"
    )

    modelo_relacionado = models.ForeignKey(
        ModeloMaquina,
        on_delete=models.CASCADE,
        related_name='manuales',
        verbose_name="Modelo de Máquina",
        help_text="Modelo específico al que aplica esta documentación"
    )

    titulo_guia = models.CharField(
        max_length=200,
        verbose_name="Título de la Guía",
        help_text="Nombre claro del problema o procedimiento (ej: Error de RAM en EGT)"
    )

    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIA_GUIA_CHOICES,
        default='reparacion',
        verbose_name="Categoría",
        help_text="Tipo de documento para facilitar la búsqueda"
    )

    archivo_pdf = models.FileField(
        upload_to='wiki_tecnica/pdfs/',
        verbose_name="Archivo PDF",
        help_text="Documento oficial con la resolución o manual técnico"
    )

    # ─── Flujo de aprobación y gamificación ─────────────────────────────────
    estado = models.CharField(
        max_length=30,
        choices=ESTADO_CHOICES,
        default='pendiente_revision',
        db_index=True,
        verbose_name="Estado de la Guía",
        help_text="Ciclo de vida: pendiente_revision → aprobada → publicada (o rechazada)"
    )

    puntos_reconocimiento = models.PositiveIntegerField(
        default=0,
        verbose_name="Puntos de Reconocimiento",
        help_text="Puntos que el administrador asigna al técnico autor al publicar la guía. "
                  "Se suman automáticamente a puntos_gamificacion del usuario."
    )

    revisada_por = models.ForeignKey(
        Usuarios,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guias_revisadas',
        verbose_name="Revisada por",
        help_text="Administrador que aprobó, rechazó o publicó la guía"
    )

    fecha_revision = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Revisión",
        help_text="Fecha y hora en que el administrador tomó acción sobre la guía"
    )

    nota_revision = models.TextField(
        null=True,
        blank=True,
        verbose_name="Nota del Revisor",
        help_text="Comentario del administrador al aprobar, rechazar o publicar la guía"
    )

    class Meta:
        db_table = 'wiki_tecnica'
        verbose_name = "Guía Técnica"
        verbose_name_plural = "Wiki de Conocimiento"
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.titulo_guia} — {self.autor.username} [{self.get_estado_display()}]"