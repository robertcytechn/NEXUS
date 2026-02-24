"""
Signals para el módulo Wiki — Flujo de Gamificación.

Eventos cubiertos:
  1. Nueva propuesta recibida → Notifica al ADMINISTRADOR para que la revise.
  2. Guía publicada (estado → 'publicada') → Notifica a técnicos y supervisores
     de toda la red (o del casino de origen) que hay nuevo conocimiento disponible.
     Además, confirma al autor cuántos puntos de gamificación recibió.

Nota anti-spam: Las notificaciones de publicación solo se disparan una vez,
cuando la guía pasa de cualquier estado a 'publicada'.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import WikiTecnica
from Notificaciones.models import Notificacion
from Roles.models import Rol


# ── 1. Al recibir una nueva propuesta → notificar al Administrador ─────────
@receiver(post_save, sender=WikiTecnica)
def wiki_nueva_propuesta(sender, instance, created, **kwargs):
    """
    Alerta al Administrador cada vez que un técnico sube una nueva propuesta de guía.
    """
    if not created:
        return  # Solo en creación

    autor = instance.autor

    # Notificación solo para el administrador (global, llegará a todos los admins)
    Notificacion.objects.create(
        titulo='📥 Nueva Propuesta de Guía Técnica',
        contenido=(
            f"{autor.nombres} {autor.apellido_paterno} ha enviado una nueva propuesta: "
            f'"{instance.titulo_guia}" para el modelo {instance.modelo_relacionado.nombre_modelo}. '
            f"Categoría: {instance.get_categoria_display()}. Pendiente de revisión."
        ),
        nivel='informativa',
        tipo='wiki',
        es_global=True,
    )


# ── 2. Al publicar → notificar a técnicos y autor ────────────────────────────
@receiver(pre_save, sender=WikiTecnica)
def wiki_detectar_publicacion(sender, instance, **kwargs):
    """
    Detecta si el estado está cambiando a 'publicada' y guarda el estado anterior
    en el atributo transitorio `_estado_anterior` para que post_save lo use.
    """
    if instance.pk:
        try:
            anterior = WikiTecnica.objects.get(pk=instance.pk)
            instance._estado_anterior = anterior.estado
        except WikiTecnica.DoesNotExist:
            instance._estado_anterior = None
    else:
        instance._estado_anterior = None


@receiver(post_save, sender=WikiTecnica)
def wiki_post_publicacion(sender, instance, created, **kwargs):
    """
    Se dispara cuando una guía pasa a estado 'publicada':
      - Notifica a TECNICO y SUP SISTEMAS del casino origen (o globalmente).
      - Confirma al autor sus puntos de gamificación.
    """
    if created:
        return

    estado_anterior = getattr(instance, '_estado_anterior', None)
    if not (estado_anterior != 'publicada' and instance.estado == 'publicada'):
        return  # No cambió a publicada, ignorar

    autor = instance.autor
    modelo = instance.modelo_relacionado
    casino = instance.casino_origen
    puntos = instance.puntos_reconocimiento

    roles_tecnicos = Rol.objects.filter(nombre__in=['TECNICO', 'SUP SISTEMAS'])

    contenido_red = (
        f"{autor.nombres} {autor.apellido_paterno} publicó una nueva guía técnica: "
        f'"{instance.titulo_guia}" para el modelo {modelo.nombre_modelo}. '
        f"Categoría: {instance.get_categoria_display()}. ¡Disponible en el Centro de Servicios!"
    )

    if casino:
        for rol in roles_tecnicos:
            Notificacion.objects.create(
                titulo='📚 Nueva Guía Técnica Disponible',
                contenido=contenido_red,
                nivel='informativa',
                tipo='wiki',
                casino_destino=casino,
                rol_destino=rol,
            )
    else:
        Notificacion.objects.create(
            titulo='📚 Nueva Guía Técnica Global Disponible',
            contenido=contenido_red,
            nivel='informativa',
            tipo='wiki',
            es_global=True,
        )

    # Notificación personal al autor con sus puntos ganados.
    # Usamos instance.puntos_reconocimiento (ya guardado en la guía)
    # en lugar de autor.puntos_gamificacion, que sería stale en este
    # punto del signal (la vista otorga los puntos DESPUÉS de guia.save()).
    puntos_otorgados = instance.puntos_reconocimiento or 0
    if puntos_otorgados > 0:
        Notificacion.objects.create(
            titulo='🏅 ¡Puntos de Gamificación Otorgados!',
            contenido=(
                f'Tu guía "{instance.titulo_guia}" fue publicada. '
                f'¡Se te han otorgado {puntos_otorgados} puntos de gamificación! '
                f'Revisa tu perfil para ver tu total actualizado.'
            ),
            nivel='informativa',
            tipo='wiki',
            usuario_destino=autor,
        )

