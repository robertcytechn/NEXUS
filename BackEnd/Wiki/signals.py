"""
Signals para el módulo Wiki.

Eventos cubiertos:
  1. Nueva guía técnica publicada → Informativa a todos los TECNICO y SUP SISTEMAS
     del casino de origen (o global si casino_origen es nulo).
     
Razón anti-spam: Solo se dispara al CREAR, nunca al editar, y solo para un 
recurso de conocimiento que no se publica con frecuencia masiva.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WikiTecnica
from Notificaciones.models import Notificacion
from Roles.models import Rol


@receiver(post_save, sender=WikiTecnica)
def wiki_post_save(sender, instance, created, **kwargs):
    if not created:
        return  # Solo al publicar una guía nueva

    autor    = instance.autor
    modelo   = instance.modelo_relacionado
    casino   = instance.casino_origen

    roles = Rol.objects.filter(nombre__in=['TECNICO', 'SUP SISTEMAS'])

    if casino:
        # Notificación segmentada al casino de origen de la guía
        for rol in roles:
            Notificacion.objects.create(
                titulo        = "📚 Nueva Guía Técnica Disponible",
                contenido     = (
                    f"{autor.nombres} publicó una nueva guía: \"{instance.titulo_guia}\" "
                    f"para el modelo {modelo.nombre}. "
                    f"Categoría: {instance.get_categoria_display()}."
                ),
                nivel         = 'informativa',
                tipo          = 'wiki',
                casino_destino= casino,
                rol_destino   = rol,
            )
    else:
        # Si no tiene casino de origen, aplica a todos (es_global)
        Notificacion.objects.create(
            titulo    = "📚 Nueva Guía Técnica Global Disponible",
            contenido = (
                f"{autor.nombres} publicó una nueva guía: \"{instance.titulo_guia}\" "
                f"para el modelo {modelo.nombre}. "
                f"Categoría: {instance.get_categoria_display()}."
            ),
            nivel     = 'informativa',
            tipo      = 'wiki',
            es_global = True,
        )
