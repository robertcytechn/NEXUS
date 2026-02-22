"""
Signals para el módulo Usuarios.

Eventos cubiertos:
  1. Nuevo usuario creado → Informativa a SUP SISTEMAS y ADMINISTRADOR del mismo casino.

Razón: Los supervisores de sistemas deben saber cuándo un nuevo integrante
entra al sistema para poder asistirlo o verificar sus permisos.

Anti-spam: NO se notifica al editar, activar o desactivar usuarios.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuarios
from Notificaciones.models import Notificacion
from Roles.models import Rol


@receiver(post_save, sender=Usuarios)
def usuario_post_save(sender, instance, created, **kwargs):
    if not created:
        return  # Solo al dar de alta un usuario nuevo

    casino = instance.casino
    nombre = f"{instance.nombres} {instance.apellido_paterno}".strip()

    roles = Rol.objects.filter(nombre__in=['SUP SISTEMAS', 'ADMINISTRADOR'])
    for rol in roles:
        Notificacion.objects.create(
            titulo        = "👤 Nuevo Usuario Registrado",
            contenido     = (
                f"El usuario \"{nombre}\" ({instance.username}) "
                f"ha sido dado de alta en {casino.nombre} "
                f"con el rol \"{instance.rol.nombre}\"."
            ),
            nivel         = 'informativa',
            tipo          = 'sistema',
            casino_destino= casino,
            rol_destino   = rol,
        )
