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

    puntos_reconocimiento = models.PositiveIntegerField(
        default=0,
        verbose_name="Puntos de Medalla",
        help_text="Puntos acumulados por la utilidad de esta guía para el equipo"
    )

    class Meta:
        db_table = 'wiki_tecnica'
        verbose_name = "Guía Técnica"
        verbose_name_plural = "Wiki de Conocimiento"

    def __str__(self):
        return f"{self.titulo_guia} - {self.autor.username}"