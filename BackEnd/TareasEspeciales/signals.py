"""
Signals para el módulo TareasEspeciales.

Eventos cubiertos:
  1. Tarea creada     → Alerta a TECNICO y SUP SISTEMAS del casino.
  2. Tarea completada → Informativa personal al creador + alerta a GERENCIA del casino.
  3. Tarea asignada   → Informativa personal al técnico recién asignado.
  4. Tarea cancelada  → Informativa personal al creador.
"""
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import TareaEspecial
from Notificaciones.models import Notificacion
from Roles.models import Rol


def _notificar_por_rol_y_casino(titulo, contenido, nivel, tipo, casino, nombres_rol):
    roles = Rol.objects.filter(nombre__in=nombres_rol)
    for rol in roles:
        Notificacion.objects.create(
            titulo        = titulo,
            contenido     = contenido,
            nivel         = nivel,
            tipo          = tipo,
            casino_destino= casino,
            rol_destino   = rol,
        )


# ─────────────────────────────────────────────────────────────
# Captura estado y técnico asignado ANTES de guardar
# ─────────────────────────────────────────────────────────────
@receiver(pre_save, sender=TareaEspecial)
def tarea_snapshot_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            prev = TareaEspecial.objects.get(pk=instance.pk)
            instance._prev_estatus    = prev.estatus
            instance._prev_asignado_id = prev.asignado_a_id
        except TareaEspecial.DoesNotExist:
            instance._prev_estatus     = None
            instance._prev_asignado_id = None
    else:
        instance._prev_estatus     = None
        instance._prev_asignado_id = None


# ─────────────────────────────────────────────────────────────
# Post-save: generar notificaciones según el evento
# ─────────────────────────────────────────────────────────────
@receiver(post_save, sender=TareaEspecial)
def tarea_post_save(sender, instance, created, **kwargs):
    casino  = instance.casino
    titulo  = instance.titulo
    estatus = instance.estatus

    # ── 1. Tarea NUEVA ──────────────────────────────────────
    if created:
        _notificar_por_rol_y_casino(
            titulo      = "📌 Nueva Tarea Especial Asignada",
            contenido   = (
                f"Se ha registrado una nueva tarea especial: \"{titulo}\". "
                f"Prioridad: {instance.get_prioridad_display()}. "
                f"Revisa los detalles y toma acción."
            ),
            nivel       = 'alerta',
            tipo        = 'sistema',
            casino      = casino,
            nombres_rol = ['TECNICO', 'SUP SISTEMAS'],
        )
        return

    prev_estatus     = getattr(instance, '_prev_estatus', None)
    prev_asignado_id = getattr(instance, '_prev_asignado_id', None)

    # ── 2. Tarea COMPLETADA ───────────────────────────────────
    if estatus == 'completada' and prev_estatus != 'completada':
        # Al creador
        Notificacion.objects.create(
            titulo          = "✅ Tarea Especial Completada",
            contenido       = (
                f"La tarea especial \"{titulo}\" que registraste ha sido completada. "
                f"{('Resultado: ' + instance.resultado_final) if instance.resultado_final else ''}"
            ).strip(),
            nivel           = 'informativa',
            tipo            = 'sistema',
            usuario_destino = instance.creado_por_usuario,
        )
        # A la GERENCIA del casino
        _notificar_por_rol_y_casino(
            titulo      = "✅ Tarea Especial Completada",
            contenido   = (
                f"La tarea especial \"{titulo}\" ha sido finalizada satisfactoriamente en {casino.nombre}."
            ),
            nivel       = 'informativa',
            tipo        = 'sistema',
            casino      = casino,
            nombres_rol = ['GERENCIA'],
        )

    # ── 3. Tarea CANCELADA ───────────────────────────────────
    if estatus == 'cancelada' and prev_estatus != 'cancelada':
        Notificacion.objects.create(
            titulo          = "❌ Tarea Especial Cancelada",
            contenido       = f"La tarea especial \"{titulo}\" ha sido marcada como cancelada.",
            nivel           = 'informativa',
            tipo            = 'sistema',
            usuario_destino = instance.creado_por_usuario,
        )

    # ── 4. Técnico ASIGNADO (nuevo o cambio) ─────────────────
    nuevo_asignado_id = instance.asignado_a_id
    if nuevo_asignado_id and nuevo_asignado_id != prev_asignado_id:
        Notificacion.objects.create(
            titulo          = "📋 Tarea Especial Asignada a Ti",
            contenido       = (
                f"Se te ha asignado la tarea especial \"{titulo}\" "
                f"en {casino.nombre}. "
                f"Prioridad: {instance.get_prioridad_display()}."
            ),
            nivel           = 'alerta',
            tipo            = 'sistema',
            usuario_destino = instance.asignado_a,
        )
