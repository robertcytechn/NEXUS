from django.db import models
from django.utils import timezone
from Casinos.models import Casino
from Usuarios.models import Usuarios

class LogAuditoria(models.Model):
    ACCIONES = (
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
    )

    tabla = models.CharField(max_length=100, verbose_name="Tabla Afectada")
    registro_id = models.CharField(max_length=50, verbose_name="ID de Registro")
    accion = models.CharField(max_length=20, choices=ACCIONES, verbose_name="Acción Realizada")
    
    # JSONField nativo de Django, no requiere librerías extra
    datos_anteriores = models.JSONField(null=True, blank=True, verbose_name="Datos Anteriores")
    datos_nuevos = models.JSONField(null=True, blank=True, verbose_name="Datos Nuevos")
    
    fecha = models.DateTimeField(default=timezone.now, verbose_name="Fecha del Evento")
    
    usuario = models.ForeignKey(
        Usuarios, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Usuario"
    )
    casino = models.ForeignKey(
        Casino, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Casino Relacionado"
    )

    class Meta:
        db_table = 'auditoria_global'
        verbose_name = "Log de Auditoría"
        verbose_name_plural = "Logs de Auditoría"
        ordering = ['-fecha']

    def __str__(self):
        usr = self.usuario.username if self.usuario else "Sistema"
        return f"[{self.fecha.strftime('%Y-%m-%d %H:%M:%S')}] {usr} {self.accion} en {self.tabla} (ID: {self.registro_id})"
