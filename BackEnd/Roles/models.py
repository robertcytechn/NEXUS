from django.db import models
from ModelBase.models import ModeloBase


class Rol(ModeloBase):
    """
    Define los niveles de acceso y permisos dentro de la organización.

    estos son unos roles predefinidos:
    - Administrador: Acceso total a todas las funciones y configuraciones.
    - Sistemas: Acceso a funciones técnicas y de mantenimiento del sistema.
    - Tecnico: Acceso a funciones operativas y de gestión diaria.
    - Supervisor: Acceso a funciones de supervisión y reportes, pero sin permisos de configuración.
    - Proveedor: Solo puede ver sus maquinas y reportes relacionados, sin acceso a funciones administrativas.
    - observador: Acceso limitado a visualización de datos sin permisos de edición o configuración.
    """
    nombre = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Nombre del Rol",
        help_text="Identificador único del rol (ej: Administrador, Operador)"
    )
    descripcion = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Descripción de Funciones",
        help_text="Detalle de las responsabilidades y alcance del rol"
    )

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        db_table = 'roles'
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre']