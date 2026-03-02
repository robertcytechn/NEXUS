from django.db import transaction
from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from .models import CanjeRecompensa, RecompensaGamificacion
from .serializers import (
    CanjeRecompensaSerializer,
    RecompensaGamificacionSerializer,
    RecompensaPublicaSerializer,
    TecnicoSalonFamaSerializer,
)
from Usuarios.models import Usuarios
from Tickets.models import Ticket          # noqa: F401 — usado en annotate
from Wiki.models import WikiTecnica         # noqa: F401 — usado en annotate
from MantenimientosPreventivos.models import MantenimientoPreventivo  # noqa
from BitacoraTecnica.models import BitacoraTecnica                     # noqa


_ROLES_TIENDA = {'GERENCIA', 'ADMINISTRADOR', 'DB ADMIN'}


def _tiene_acceso_tienda(user) -> bool:
    return user.rol.nombre in _ROLES_TIENDA


# ──────────────────────────────────────────────────────────────────────────────
# TIENDA — GERENCIA: crear, editar, listar, activar/desactivar recompensas
# Ruta: /api/gamificacion/tienda/
# ──────────────────────────────────────────────────────────────────────────────
class RecompensaGerenciaViewSet(viewsets.ModelViewSet):
    """
    Panel de Gerencia para gestionar la Tienda de Recompensas.
    Acceso exclusivo para usuarios con rol GERENCIA.

    Acciones:
      - CRUD completo de recompensas
      - Activar / desactivar sin eliminar
      - Ver historial de canjes de su casino
    """
    serializer_class = RecompensaGamificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not _tiene_acceso_tienda(self.request.user):
            return RecompensaGamificacion.objects.none()
        return RecompensaGamificacion.objects.filter(
            casino=self.request.user.casino
        ).select_related('casino')

    def _check_acceso(self, request):
        if not _tiene_acceso_tienda(request.user):
            return Response(
                {'error': 'Acceso denegado. Solo Gerencia, Administrador o DB Admin pueden gestionar las recompensas.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def create(self, request, *args, **kwargs):
        err = self._check_acceso(request)
        if err:
            return err
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        err = self._check_acceso(request)
        if err:
            return err
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        err = self._check_acceso(request)
        if err:
            return err
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        err = self._check_acceso(request)
        if err:
            return err
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(
            casino=self.request.user.casino,
            creado_por=self.request.user.username,
            modificado_por=self.request.user.username,
        )

    # ── Activar / Desactivar recompensa ──────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='toggle-activo')
    def toggle_activo(self, request, pk=None):
        """Activa o desactiva una recompensa sin eliminarla."""
        err = self._check_acceso(request)
        if err:
            return err
        recompensa = self.get_object()
        recompensa.activo = not recompensa.activo
        recompensa.modificado_por = request.user.username
        recompensa.save(update_fields=['activo', 'modificado_por'])
        estado_txt = 'activada' if recompensa.activo else 'desactivada'
        return Response({'mensaje': f'Recompensa "{recompensa.titulo}" {estado_txt} correctamente.'})

    # ── Historial de canjes del casino ────────────────────────────────────────
    @action(detail=False, methods=['get'], url_path='canjes')
    def historial_canjes(self, request):
        """Lista todos los canjes realizados en el casino de la gerencia."""
        err = self._check_acceso(request)
        if err:
            return err
        canjes = CanjeRecompensa.objects.filter(
            recompensa__casino=request.user.casino
        ).select_related('usuario', 'recompensa').order_by('-creado_en')
        serializer = CanjeRecompensaSerializer(canjes, many=True)
        return Response({'total': canjes.count(), 'canjes': serializer.data})

    # ── Marcar canje como entregado ───────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='canjes/(?P<canje_id>[^/.]+)/entregar')
    def entregar_canje(self, request, pk=None, canje_id=None):
        """Gerencia marca un canje como 'entregado'."""
        err = self._check_acceso(request)
        if err:
            return err
        try:
            canje = CanjeRecompensa.objects.get(
                pk=canje_id, recompensa__casino=request.user.casino
            )
        except CanjeRecompensa.DoesNotExist:
            return Response({'error': 'Canje no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if canje.estado == 'entregado':
            return Response({'error': 'Este canje ya fue entregado.'}, status=status.HTTP_400_BAD_REQUEST)

        canje.estado = 'entregado'
        canje.nota_gerencia = request.data.get('nota_gerencia', '')
        canje.modificado_por = request.user.username
        canje.save(update_fields=['estado', 'nota_gerencia', 'modificado_por'])
        return Response({'mensaje': f'Canje de {canje.usuario.username} marcado como entregado.'})


# ──────────────────────────────────────────────────────────────────────────────
# TIENDA PÚBLICA — Técnicos: ver recompensas y canjear
# Ruta: /api/gamificacion/tienda-tecnico/
# ──────────────────────────────────────────────────────────────────────────────
class RecompensaTecnicoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Tienda de Recompensas desde la perspectiva del técnico.
    Solo lectura de recompensas activas + acción de canje.
    """
    serializer_class = RecompensaPublicaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Solo recompensas activas del casino del técnico."""
        return RecompensaGamificacion.objects.filter(
            casino=self.request.user.casino,
            activo=True,
        ).select_related('casino')

    # ── Canjear recompensa ────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='canjear')
    def canjear(self, request, pk=None):
        """
        El técnico canjea una recompensa.

        - Valida que tenga suficientes puntos disponibles.
        - Descuenta de puntos_gamificacion (disponibles).
        - NO modifica puntos_gamificacion_historico (el rango no cae).
        - Registra el canje para que gerencia lo procese.
        - Control de stock: si la recompensa tiene stock limitado, lo decrementa.
        """
        recompensa = self.get_object()
        usuario = request.user

        if not recompensa.activo:
            return Response(
                {'error': 'Esta recompensa ya no está disponible.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if usuario.puntos_gamificacion < recompensa.costo_puntos:
            return Response(
                {
                    'error': 'No tienes suficientes puntos para canjear esta recompensa.',
                    'puntos_disponibles': usuario.puntos_gamificacion,
                    'costo_requerido': recompensa.costo_puntos,
                    'faltan': recompensa.costo_puntos - usuario.puntos_gamificacion,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Verificar y decrementar stock si aplica
            if recompensa.stock is not None:
                if recompensa.stock <= 0:
                    return Response(
                        {'error': 'Esta recompensa se ha agotado.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                recompensa.stock -= 1
                recompensa.save(update_fields=['stock'])

            # Descontar puntos disponibles (histórico INTOCADO)
            usuario.puntos_gamificacion -= recompensa.costo_puntos
            usuario.save(update_fields=['puntos_gamificacion'])

            # Registrar el canje
            canje = CanjeRecompensa.objects.create(
                usuario=usuario,
                recompensa=recompensa,
                puntos_descontados=recompensa.costo_puntos,
                estado='pendiente',
                creado_por=usuario.username,
                modificado_por=usuario.username,
            )

        return Response(
            {
                'mensaje': (
                    f'¡Canje exitoso! "{recompensa.titulo}" está pendiente de entrega. '
                    f'Gerencia se pondrá en contacto contigo.'
                ),
                'puntos_restantes': usuario.puntos_gamificacion,
                'puntos_historico': usuario.puntos_gamificacion_historico,
                'rango_actual': usuario.rango_gamificacion,
                'canje_id': canje.pk,
            },
            status=status.HTTP_201_CREATED,
        )

    # ── Mis canjes ────────────────────────────────────────────────────────────
    @action(detail=False, methods=['get'], url_path='mis-canjes')
    def mis_canjes(self, request):
        """Historial personal de canjes del técnico logueado."""
        canjes = CanjeRecompensa.objects.filter(
            usuario=request.user
        ).select_related('recompensa').order_by('-creado_en')
        serializer = CanjeRecompensaSerializer(canjes, many=True)
        return Response({'total': canjes.count(), 'canjes': serializer.data})

    # ── Mi perfil RPG ─────────────────────────────────────────────────────────
    @action(detail=False, methods=['get'], url_path='mi-rango')
    def mi_rango(self, request):
        """Devuelve el rango, puntos disponibles e histórico del técnico logueado."""
        u = request.user
        return Response({
            'username': u.username,
            'puntos_disponibles': u.puntos_gamificacion,
            'puntos_historico': u.puntos_gamificacion_historico,
            'rango': u.rango_gamificacion,
        })


# ──────────────────────────────────────────────────────────────────────────────
# SALÓN DE LA FAMA
# Ruta: /api/gamificacion/salon-fama/
# ──────────────────────────────────────────────────────────────────────────────
class SalonFamaListAPIView(ListAPIView):
    """
    Vista pública que retorna la lista de técnicos ordenados por 
    puntos de gamificación históricos de mayor a menor.
    """
    serializer_class = TecnicoSalonFamaSerializer
    permission_classes = [AllowAny] # [IsAuthenticated] si se requiere login para verlo
    
    def get_queryset(self):
        """
        Técnicos activos ordenados por XP histórico.
        Todas las métricas de actividad se anotan en una sola consulta SQL.
        """
        return (
            Usuarios.objects
            .filter(esta_activo=True, rol__nombre__in=['Tecnico', 'Sup Sistemas'])
            .select_related('casino', 'rol')
            .annotate(
                # ── Tickets ────────────────────────────────────────────────
                # Total de tickets asignados al técnico (cualquier estado)
                tickets_totales=Count(
                    'tickets_asignados',
                    distinct=True,
                ),
                # Tickets cerrados (estado_ciclo es el campo correcto en el modelo)
                tickets_cerrados=Count(
                    'tickets_asignados',
                    filter=Q(tickets_asignados__estado_ciclo='cerrado'),
                    distinct=True,
                ),
                # Tickets actualmente en proceso
                tickets_en_proceso=Count(
                    'tickets_asignados',
                    filter=Q(tickets_asignados__estado_ciclo='proceso'),
                    distinct=True,
                ),
                # Tickets que fueron reabiertos al menos una vez
                tickets_reabiertos=Count(
                    'tickets_asignados',
                    filter=Q(tickets_asignados__contador_reaperturas__gt=0),
                    distinct=True,
                ),

                # ── Wiki técnica ───────────────────────────────────────────
                # Total de guías creadas (cualquier estado)
                wikis_totales=Count(
                    'guias_creadas',
                    distinct=True,
                ),
                # Guías ya publicadas (visibles para todos)
                wikis_publicadas=Count(
                    'guias_creadas',
                    filter=Q(guias_creadas__estado='publicada'),
                    distinct=True,
                ),
                # Guías pendientes de revisión
                wikis_pendientes=Count(
                    'guias_creadas',
                    filter=Q(guias_creadas__estado='pendiente_revision'),
                    distinct=True,
                ),

                # ── Mantenimientos preventivos ─────────────────────────────
                mantenimientos_realizados=Count(
                    'mantenimientopreventivo',
                    distinct=True,
                ),

                # ── Bitácora técnica ────────────────────────────────────────
                # Total de entradas registradas
                entradas_bitacora=Count(
                    'bitacoratecnica',
                    distinct=True,
                ),
                # Intervenciones con resultado exitoso
                reparaciones_exitosas=Count(
                    'bitacoratecnica',
                    filter=Q(bitacoratecnica__resultado_intervencion='exitosa'),
                    distinct=True,
                ),

                # ── Gamificación — canjes ───────────────────────────────────
                # Total de recompensas canjeadas (cualquier estado)
                canjes_total=Count(
                    'canjes_realizados',
                    distinct=True,
                ),
            )
            .order_by('-puntos_gamificacion_historico')
        )
