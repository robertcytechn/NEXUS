"""
Signals para el módulo Tickets.

Eventos cubiertos:
  1. Ticket creado     → Alerta a TECNICO y SUP SISTEMAS del casino afectado.
  2. Ticket cerrado    → Informativa personal al reportante.
  3. Ticket reabierto  → Alerta al técnico asignado (si existe).
  4. Técnico asignado  → Informativa personal al nuevo técnico.
"""
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Ticket
from Notificaciones.models import Notificacion
from Roles.models import Rol


def _notificar_por_rol_y_casino(titulo, contenido, nivel, tipo, casino, nombres_rol):
    """
    Crea una notificación separada por cada rol de la lista, 
    segmentada al casino indicado.
    """
    roles = Rol.objects.filter(nombre__in=nombres_rol)
    for rol in roles:
        Notificacion.objects.create(
            titulo=titulo,
            contenido=contenido,
            nivel=nivel,
            tipo=tipo,
            casino_destino=casino,
            rol_destino=rol,
        )


# ─────────────────────────────────────────────────────────────
# Captura el estado ANTES de guardar para detectar transiciones
# ─────────────────────────────────────────────────────────────
@receiver(pre_save, sender=Ticket)
def ticket_snapshot_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            prev = Ticket.objects.get(pk=instance.pk)
            instance._prev_estado     = prev.estado_ciclo
            instance._prev_tecnico_id = prev.tecnico_asignado_id
        except Ticket.DoesNotExist:
            instance._prev_estado     = None
            instance._prev_tecnico_id = None
    else:
        instance._prev_estado     = None
        instance._prev_tecnico_id = None


# ─────────────────────────────────────────────────────────────
# Post-save: generar notificaciones según el evento detectado
# ─────────────────────────────────────────────────────────────
@receiver(post_save, sender=Ticket)
def ticket_post_save(sender, instance, created, **kwargs):
    casino  = instance.maquina.casino
    uid     = instance.maquina.uid_sala
    folio   = instance.folio
    estado  = instance.estado_ciclo

    # ── 1. Ticket NUEVO ─────────────────────────────────────
    if created:
        _notificar_por_rol_y_casino(
            titulo   = f"🎰 Nuevo Ticket {folio}",
            contenido= (
                f"Se ha abierto el ticket {folio} para la máquina {uid}. "
                f"Categoría: {instance.get_categoria_display()} — "
                f"Prioridad: {instance.get_prioridad_display()}."
            ),
            nivel    = 'alerta',
            tipo     = 'ticket',
            casino   = casino,
            nombres_rol = ['TECNICO', 'SUP SISTEMAS'],
        )
        return  # Las demás transiciones solo aplican a tickets existentes

    prev_estado     = getattr(instance, '_prev_estado', None)
    prev_tecnico_id = getattr(instance, '_prev_tecnico_id', None)

    # ── 2. Ticket CERRADO ────────────────────────────────────
    if estado == 'cerrado' and prev_estado != 'cerrado':
        Notificacion.objects.create(
            titulo          = f"✅ Ticket {folio} Resuelto",
            contenido       = (
                f"Tu ticket {folio} para la máquina {uid} ha sido marcado como resuelto. "
                f"{('Resolución: ' + instance.explicacion_cierre) if instance.explicacion_cierre else ''}"
            ).strip(),
            nivel           = 'informativa',
            tipo            = 'ticket',
            usuario_destino = instance.reportante,
        )

    # ── 3. Ticket REABIERTO ──────────────────────────────────
    if estado == 'reabierto' and prev_estado != 'reabierto':
        if instance.tecnico_asignado:
            Notificacion.objects.create(
                titulo          = f"🔄 Ticket {folio} Reabierto",
                contenido       = (
                    f"El ticket {folio} (máquina {uid}) ha sido reabierto. "
                    f"Requiere tu atención nuevamente."
                ),
                nivel           = 'alerta',
                tipo            = 'ticket',
                usuario_destino = instance.tecnico_asignado,
            )

    # ── 4. Técnico ASIGNADO (nuevo o cambio) ─────────────────
    nuevo_tecnico_id = instance.tecnico_asignado_id
    if nuevo_tecnico_id and nuevo_tecnico_id != prev_tecnico_id:
        Notificacion.objects.create(
            titulo          = f"📋 Ticket {folio} Asignado a Ti",
            contenido       = (
                f"Se te ha asignado el ticket {folio} para la máquina {uid}. "
                f"Prioridad: {instance.get_prioridad_display()}. "
                f"Por favor, revisa los detalles."
            ),
            nivel           = 'alerta',
            tipo            = 'ticket',
            usuario_destino = instance.tecnico_asignado,
        )
