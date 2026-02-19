from django.db import models
from django.conf import settings

class EvolucionNexus(models.Model):
    # Categorías
    CATEGORIA_CHOICES = [
        ('ERROR', 'Error (Bug)'),
        ('VISUAL', 'Visual (Estilo)'),
        ('COMPORTAMIENTO', 'Comportamiento (Lógica)'),
        ('FUNCIONALIDAD', 'Funcionalidad (Nuevo Módulo)'),
        ('CREAR', 'Crear Nuevo ...'),
    ]

    # Flujo de Estados
    ESTADO_CHOICES = [
        ('NO_REVISADO', 'No Revisado'),
        ('POR_REVISAR', 'Abierto por Revisar'),
        ('ANALIZANDO', 'Analizando Requerimientos'),
        ('ADQUISICION', 'Estudio de Mercado / Adquisición de Info'),
        ('MAQUETACION', 'Iniciando Maquetación'),
        ('DESARROLLO', 'En Desarrollo'),
        ('PRUEBAS', 'Pruebas / QA'),
        ('COMPLETADO', 'Completado'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reportes_evolucion')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='ERROR')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='NO_REVISADO')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    
    # Campo JSON para datos dinámicos según la categoría
    # ERROR: { "modulo_afectado": "...", "pasos_reproducir": "..." }
    # VISUAL/COMPORTAMIENTO: { "situacion_actual": "...", "cambio_propuesto": "..." }
    # FUNCIONALIDAD/REPORTE: { "beneficio": "..." }
    datos_extra = models.JSONField(default=dict, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Evolución NEXUS'
        verbose_name_plural = 'Evoluciones NEXUS'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.titulo} - {self.get_estado_display()}"
