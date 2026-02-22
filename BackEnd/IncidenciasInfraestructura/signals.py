"""
Signals para el módulo IncidenciasInfraestructura.

Eventos cubiertos:
  1. Incidencia creada con severidad alta/crítica → Urgente a SUP SISTEMAS y GERENCIA.
  2. Incidencia creada con afecta_operacion=True  → Urgente (complementa severidad).
  3. Incidencia creada con severidad baja/media   → Alerta informativa al SUP SISTEMAS.
  4. Incidencia resuelta (hora_fin registrada)    → Informativa al SUP SISTEMAS del casino.
"""
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import IncidenciaInfraestructura
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
# Captura si ya tenía hora_fin ANTES de guardar (para detectar cierre)
# ─────────────────────────────────────────────────────────────
@receiver(pre_save, sender=IncidenciaInfraestructura)
def incidencia_snapshot_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            prev = IncidenciaInfraestructura.objects.get(pk=instance.pk)
            instance._prev_hora_fin = prev.hora_fin
        except IncidenciaInfraestructura.DoesNotExist:
            instance._prev_hora_fin = None
    else:
        instance._prev_hora_fin = None


# ─────────────────────────────────────────────────────────────
# Post-save
# ─────────────────────────────────────────────────────────────
@receiver(post_save, sender=IncidenciaInfraestructura)
def incidencia_post_save(sender, instance, created, **kwargs):
    casino     = instance.casino
    severidad  = instance.severidad
    es_critica = severidad in ('alta', 'critica') or instance.afecta_operacion

    # ── 1. Incidencia NUEVA ──────────────────────────────────
    if created:
        nivel_notif = 'urgente' if es_critica else 'alerta'

        prefijo = "🚨 URGENTE:" if es_critica else "⚠️"
        detalle_op = " — OPERACIÓN AFECTADA" if instance.afecta_operacion else ""

        _notificar_por_rol_y_casino(
            titulo      = f"{prefijo} Incidencia de Infraestructura{detalle_op}",
            contenido   = (
                f"Nueva incidencia registrada en {casino.nombre}: \"{instance.titulo}\". "
                f"Categoría: {instance.get_categoria_display()} — "
                f"Severidad: {instance.get_severidad_display()}."
                + (f" La operación del casino está siendo afectada." if instance.afecta_operacion else "")
            ),
            nivel       = nivel_notif,
            tipo        = 'infraestructura',
            casino      = casino,
            nombres_rol = ['SUP SISTEMAS', 'GERENCIA'] if es_critica else ['SUP SISTEMAS'],
        )
        return

    # ── 2. Incidencia RESUELTA (se registró hora_fin) ────────
    prev_hora_fin = getattr(instance, '_prev_hora_fin', None)
    if instance.hora_fin and not prev_hora_fin:
        _notificar_por_rol_y_casino(
            titulo      = "✅ Incidencia de Infraestructura Resuelta",
            contenido   = (
                f"La incidencia \"{instance.titulo}\" en {casino.nombre} "
                f"ha sido controlada y marcada como resuelta."
            ),
            nivel       = 'informativa',
            tipo        = 'infraestructura',
            casino      = casino,
            nombres_rol = ['SUP SISTEMAS', 'GERENCIA'],
        )
