"""
signals_gamificacion.py
=======================
Sistema de gamificación automática NEXUS.

Otorga puntos a los técnicos (TECNICO / SUP SISTEMAS) cuando realizan
acciones relevantes en la plataforma.

Regla técnica: se usa F() + update() directo para evitar race conditions,
actualizando puntos_gamificacion Y puntos_gamificacion_historico de forma
atómica en una sola consulta.

Fuente de verdad de los puntos:
  - puntos_gamificacion          → disponibles para canjear (sube y baja)
  - puntos_gamificacion_historico → historial acumulado (solo sube, determina rango)
"""

import logging
import threading

from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from Usuarios.models import Usuarios

logger = logging.getLogger('gamificacion')

# ──────────────────────────────────────────────────────────────────────────────
# Roles que participan en la gamificación
# ──────────────────────────────────────────────────────────────────────────────
ROLES_GAMIFICACION = {'TECNICO', 'SUP SISTEMAS'}

# ──────────────────────────────────────────────────────────────────────────────
# Contexto thread-local
# Permite que las vistas lean el resultado del último otorgamiento de puntos
# sin necesidad de consultas extra, ya que los signals corren en el mismo thread.
# ──────────────────────────────────────────────────────────────────────────────
_ctx = threading.local()


def _guardar_en_contexto(resultado: dict):
    """Acumula el resultado de puntos en el contexto del thread actual."""
    if resultado is None:
        return
    previo = getattr(_ctx, 'puntos_nexus', None)
    if previo:
        previo['puntos_otorgados'] += resultado['puntos_otorgados']
        previo['puntos_totales'] = resultado['puntos_totales']
        previo['puntos_historico'] = resultado['puntos_historico']
        previo['mensaje_nexus'] = (
            f"🏅 +{previo['puntos_otorgados']} puntos NEXUS acumulados en esta acción"
        )
    else:
        _ctx.puntos_nexus = resultado.copy()


def get_puntos_context() -> dict | None:
    """Lee y devuelve el resultado de puntos acumulado en el thread actual."""
    return getattr(_ctx, 'puntos_nexus', None)


def limpiar_puntos_context():
    """Limpia el contexto del thread. Llamar al final de cada view action."""
    _ctx.puntos_nexus = None


# ──────────────────────────────────────────────────────────────────────────────
# Helper principal: otorgar puntos
# ──────────────────────────────────────────────────────────────────────────────
def otorgar_puntos(user, puntos: int, motivo: str) -> dict | None:
    """
    Otorga `puntos` de forma atómica al `user` indicado, si es elegible.

    Parámetros
    ----------
    user    : instancia de Usuarios, pk entero, o None.
    puntos  : cantidad de puntos a otorgar (debe ser > 0).
    motivo  : cadena descriptiva para el log y el mensaje del toast.

    Retorna
    -------
    dict con claves: puntos_otorgados, puntos_totales, puntos_historico,
    rango_nivel, mensaje_nexus — o None si el usuario no es elegible.
    """
    if user is None or puntos <= 0:
        return None

    # Admitimos pk o instancia
    user_id = user if isinstance(user, int) else user.pk

    try:
        usuario = Usuarios.objects.select_related('rol').get(pk=user_id)
    except Usuarios.DoesNotExist:
        logger.warning('[Gamificación] Usuario pk=%s no encontrado.', user_id)
        return None

    # Verificar que el rol participa en la gamificación
    try:
        rol_nombre = usuario.rol.nombre
    except Exception:
        return None

    if rol_nombre not in ROLES_GAMIFICACION:
        return None

    # UPDATE atómico con F() — evita race conditions
    # Actualiza AMBOS campos en una sola consulta SQL.
    Usuarios.objects.filter(pk=user_id).update(
        puntos_gamificacion=F('puntos_gamificacion') + puntos,
        puntos_gamificacion_historico=F('puntos_gamificacion_historico') + puntos,
    )

    # Refrescar para obtener los valores actualizados
    usuario.refresh_from_db(fields=['puntos_gamificacion', 'puntos_gamificacion_historico'])

    # Leer rango actual
    try:
        rango = usuario.rango_gamificacion  # property del modelo
    except Exception:
        rango = {}

    resultado = {
        'puntos_otorgados': puntos,
        'puntos_totales': usuario.puntos_gamificacion,
        'puntos_historico': usuario.puntos_gamificacion_historico,
        'rango_nivel': rango.get('nivel', 1),
        'rango_titulo': rango.get('titulo', ''),
        'usuario': usuario.username,
        'motivo': motivo,
        'mensaje_nexus': f'🏅 +{puntos} puntos NEXUS — {motivo}',
    }

    _guardar_en_contexto(resultado)

    logger.info(
        '[Gamificación] +%d pts → %s (total: %d) | %s',
        puntos, usuario.username, usuario.puntos_gamificacion, motivo,
    )
    return resultado


# ══════════════════════════════════════════════════════════════════════════════
# SEÑALES
# ══════════════════════════════════════════════════════════════════════════════

# ── 1. Ticket cerrado → +2 pts al técnico asignado ───────────────────────────
@receiver(post_save, sender='Tickets.Ticket')
def gamif_ticket_cerrado(sender, instance, created, **kwargs):
    """
    Otorga +2 puntos al técnico_asignado cuando el ticket pasa a 'cerrado'.
    Detecta el cambio comparando con el valor anterior almacenado en _estado_anterior.
    """
    if created:
        return  # Solo en actualizaciones

    estado_anterior = getattr(instance, '_estado_anterior', None)
    if instance.estado_ciclo == 'cerrado' and estado_anterior != 'cerrado':
        otorgar_puntos(
            instance.tecnico_asignado,
            2,
            'ticket cerrado correctamente',
        )


# Signal pre_save para capturar el estado anterior del ticket
from django.db.models.signals import pre_save


@receiver(pre_save, sender='Tickets.Ticket')
def gamif_ticket_capturar_estado(sender, instance, **kwargs):
    """Guarda el estado anterior del ticket antes de que se actualice."""
    if instance.pk:
        try:
            anterior = sender.objects.get(pk=instance.pk)
            instance._estado_anterior = anterior.estado_ciclo
        except sender.DoesNotExist:
            instance._estado_anterior = None


# ── 2. Bitácora Técnica creada → +2 pts al técnico ───────────────────────────
@receiver(post_save, sender='BitacoraTecnica.BitacoraTecnica')
def gamif_bitacora_creada(sender, instance, created, **kwargs):
    """Otorga +2 puntos al técnico_tecnico cuando crea una entrada de bitácora."""
    if created:
        otorgar_puntos(
            instance.usuario_tecnico,
            2,
            'entrada de bitácora técnica registrada',
        )


# ── 3. Mantenimiento Preventivo registrado → +50 pts ────────────────────────
@receiver(post_save, sender='MantenimientosPreventivos.MantenimientoPreventivo')
def gamif_mantenimiento_creado(sender, instance, created, **kwargs):
    """
    Otorga +50 puntos al tecnico_responsable al registrar un mantenimiento preventivo.
    El acto de registrar equivale a la ejecución del mantenimiento.
    """
    if created:
        otorgar_puntos(
            instance.tecnico_responsable,
            50,
            'mantenimiento preventivo registrado',
        )


# ── 4. Tarea Especial completada → +20 pts al asignado ───────────────────────
@receiver(pre_save, sender='TareasEspeciales.TareaEspecial')
def gamif_tarea_capturar_estado(sender, instance, **kwargs):
    """Guarda el estado anterior de la tarea antes de actualizarse."""
    if instance.pk:
        try:
            anterior = sender.objects.get(pk=instance.pk)
            instance._estatus_anterior = anterior.estatus
        except sender.DoesNotExist:
            instance._estatus_anterior = None


@receiver(post_save, sender='TareasEspeciales.TareaEspecial')
def gamif_tarea_completada(sender, instance, created, **kwargs):
    """Otorga +20 puntos al técnico asignado cuando la tarea pasa a completada."""
    if created:
        return

    estatus_anterior = getattr(instance, '_estatus_anterior', None)
    if instance.estatus == 'completada' and estatus_anterior != 'completada':
        otorgar_puntos(
            instance.asignado_a,
            20,
            'tarea especial completada',
        )


# ── 5. Relevo de Turno creado → +2 pts al técnico saliente ───────────────────
@receiver(post_save, sender='RelevosTurnos.RelevoTurno')
def gamif_relevo_creado(sender, instance, created, **kwargs):
    """Otorga +2 puntos al tecnico_saliente al documentar su relevo de turno."""
    if created:
        otorgar_puntos(
            instance.tecnico_saliente,
            2,
            'relevo de turno documentado',
        )


# ── 6. Reporte EvolucionNexus creado → +15 pts al autor ──────────────────────
@receiver(post_save, sender='EvolucionNexus.EvolucionNexus')
def gamif_evolucion_creada(sender, instance, created, **kwargs):
    """Otorga +15 puntos al usuario que reporta un problema o mejora en la plataforma."""
    if created:
        otorgar_puntos(
            instance.usuario,
            15,
            'reporte/propuesta de evolución NEXUS enviado',
        )
