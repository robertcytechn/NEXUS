from django.db import models
from ModelBase.models import ModeloBase
from Casinos.models import Casino

class Proveedor(ModeloBase):
    """
    Proveedor de servicios o productos vinculado a un casino específico.
    Cada casino mantiene sus propios contactos y credenciales de acceso.
    """
    casino = models.ForeignKey(
        Casino, 
        on_delete=models.CASCADE, 
        related_name='proveedores_locales',
        help_text="Casino al que pertenece este proveedor"
    )

    nombre = models.CharField(
        max_length=150, 
        verbose_name="Nombre del Proveedor",
        help_text="Razón social o nombre comercial del proveedor"
    )
    rfc = models.CharField(
        max_length=13, 
        verbose_name="RFC",
        help_text="Registro Federal de Contribuyentes"
    )
    email_corporativo = models.EmailField(
        verbose_name="Email Corporativo",
        help_text="Correo electrónico principal de contacto"
    )
    
    telefono_soporte = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        verbose_name="Teléfono Soporte",
        help_text="Línea directa de soporte técnico"
    )
    email_soporte = models.EmailField(
        null=True, 
        blank=True, 
        verbose_name="Email de Soporte",
        help_text="Correo del departamento de soporte técnico"
    )
    nombre_contacto_tecnico = models.CharField(
        max_length=150, 
        null=True, 
        blank=True, 
        verbose_name="Contacto Técnico",
        help_text="Nombre del técnico o responsable asignado"
    )
    
    username = models.CharField(
        max_length=50, 
        verbose_name="Usuario de Acceso",
        help_text="Nombre de usuario para acceder al sistema del proveedor"
    )
    password = models.CharField(
        max_length=100, 
        verbose_name="Contraseña",
        help_text="Contraseña de acceso (almacenada sin cifrado)"
    )

    class Meta:
        db_table = 'proveedores'
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        unique_together = [
            ('casino', 'nombre'),
            ('casino', 'username')
        ]

    def __str__(self):
        return f"{self.nombre} - {self.casino.nombre}"