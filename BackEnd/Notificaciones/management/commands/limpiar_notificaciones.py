"""
Management Command: limpiar_notificaciones
==========================================
Elimina físicamente de la base de datos las notificaciones obsoletas
según las siguientes reglas de retención:

  LEÍDAS     → Se eliminan cuando tienen más de 48 h desde su CREACIÓN
               (una notificación está "leída" si existe al menos un registro
               en NotificacionUsuario que la referencia)

  NO LEÍDAS  → Se eliminan cuando tienen más de 72 h desde su CREACIÓN
               (no existe ningún registro en NotificacionUsuario)

  GLOBALES / DIRECTOR  → Se eliminan cuando tienen más de 7 días,
               independientemente de si fueron leídas o no.

Uso:
    python manage.py limpiar_notificaciones
    python manage.py limpiar_notificaciones --dry-run   ← Solo muestra conteos, no elimina

Programación recomendada: diaria a medianoche (00:00).
Ver el script  BackEnd/scripts/limpiar_notificaciones.ps1  para la
configuración del Programador de Tareas de Windows.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from datetime import timedelta

from Notificaciones.models import Notificacion, NotificacionUsuario


class Command(BaseCommand):
    help = 'Elimina notificaciones obsoletas según reglas de retención (48 h leídas / 72 h no leídas / 7 días globales)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra cuántos registros se eliminarían sin hacer cambios en la BD.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        ahora   = timezone.now()

        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  MODO DRY-RUN: no se eliminará nada.'))

        self.stdout.write(f'\n📅 Limpieza iniciada: {ahora.strftime("%Y-%m-%d %H:%M:%S")}\n')

        # ── Paso 1: Identificar notificaciones "leídas" ────────────────────
        # Una notificación está leída si tiene ≥1 registro en NotificacionUsuario.
        ids_leidas = set(
            NotificacionUsuario.objects
            .values_list('notificacion_id', flat=True)
            .distinct()
        )

        # ── Límites de tiempo ──────────────────────────────────────────────
        limite_leidas     = ahora - timedelta(hours=48)   # 48 h
        limite_no_leidas  = ahora - timedelta(hours=72)   # 72 h
        limite_globales   = ahora - timedelta(days=7)     # 7  días

        # ── Regla A: GLOBALES / DIRECTOR (7 días, sin importar si fueron leídas) ──
        qs_globales = Notificacion.objects.filter(
            models.Q(es_global=True) | models.Q(es_del_director=True),
            creado_en__lt=limite_globales,
        )
        count_globales = qs_globales.count()

        # ── Regla B: LEÍDAS normales con > 48 h ───────────────────────────
        qs_leidas = Notificacion.objects.filter(
            id__in=ids_leidas,
            creado_en__lt=limite_leidas,
            es_global=False,
            es_del_director=False,
        )
        count_leidas = qs_leidas.count()

        # ── Regla C: NO LEÍDAS normales con > 72 h ────────────────────────
        qs_no_leidas = Notificacion.objects.filter(
            creado_en__lt=limite_no_leidas,
            es_global=False,
            es_del_director=False,
        ).exclude(id__in=ids_leidas)
        count_no_leidas = qs_no_leidas.count()

        # ── Resumen previo ─────────────────────────────────────────────────
        self.stdout.write(f'  Globales/Director  (> 7 días)  → {count_globales:>5} registros')
        self.stdout.write(f'  Leídas             (> 48 h)    → {count_leidas:>5} registros')
        self.stdout.write(f'  No leídas          (> 72 h)    → {count_no_leidas:>5} registros')
        total = count_globales + count_leidas + count_no_leidas
        self.stdout.write(f'  ─────────────────────────────────────────')
        self.stdout.write(f'  TOTAL a eliminar               → {total:>5} registros\n')

        if dry_run:
            self.stdout.write(self.style.SUCCESS('✅ Dry-run completado. Sin cambios en la BD.'))
            return

        # ── Eliminación física ─────────────────────────────────────────────
        # Al eliminar la Notificacion, Django en cascada elimina sus
        # registros NotificacionUsuario asociados (CASCADE definido en el modelo).

        deleted_globales, _  = qs_globales.delete()
        deleted_leidas, _    = qs_leidas.delete()
        deleted_no_leidas, _ = qs_no_leidas.delete()

        total_deleted = deleted_globales + deleted_leidas + deleted_no_leidas

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Limpieza completada. Eliminadas: '
                f'{deleted_globales} globales, '
                f'{deleted_leidas} leídas, '
                f'{deleted_no_leidas} no leídas. '
                f'Total: {total_deleted}.'
            )
        )
