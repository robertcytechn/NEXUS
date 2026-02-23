from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import WikiTecnica
from .serializers import (
    WikiTecnicaAdminSerializer,
    WikiTecnicaPublicaSerializer,
    WikiTecnicaPropuestaSerializer,
)


# ──────────────────────────────────────────────────────────────────────────────
# CENTRO DE MANDO  (solo Administrador)
# Rutas: /api/wiki/centro-mando/
# ──────────────────────────────────────────────────────────────────────────────
class WikiCentroMandoViewSet(viewsets.ModelViewSet):
    """
    Centro de Mando exclusivo del Administrador.

    Acciones disponibles:
      - Listar todas las guías (cualquier estado)
      - Listar solo las pendientes de revisión
      - Aprobar una guía (pasa a 'aprobada')
      - Publicar una guía (pasa a 'publicada' y otorga puntos al autor)
      - Rechazar una guía (pasa a 'rechazada')
      - Eliminar una guía
    """
    serializer_class = WikiTecnicaAdminSerializer
    permission_classes = [IsAuthenticated]

    # ── Seguridad: solo ADMINISTRADOR puede acceder ──────────────────────────
    def get_queryset(self):
        if self.request.user.rol.nombre != 'ADMINISTRADOR':
            return WikiTecnica.objects.none()
        return WikiTecnica.objects.all().select_related(
            'autor', 'casino_origen', 'modelo_relacionado', 'revisada_por'
        )

    def _verificar_admin(self, request):
        if request.user.rol.nombre != 'ADMINISTRADOR':
            return Response(
                {'error': 'Acceso denegado. Solo el Administrador puede realizar esta acción.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return None

    # ── Listar pendientes de revisión ────────────────────────────────────────
    @action(detail=False, methods=['get'], url_path='pendientes')
    def pendientes(self, request):
        """Devuelve todas las guías en estado 'pendiente_revision'."""
        error = self._verificar_admin(request)
        if error:
            return error

        qs = self.get_queryset().filter(estado='pendiente_revision')
        serializer = self.get_serializer(qs, many=True)
        return Response({
            'total': qs.count(),
            'guias': serializer.data
        })

    # ── Aprobar guía ─────────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='aprobar')
    def aprobar(self, request, pk=None):
        """
        Marca la guía como 'aprobada'. Aún no se publica ni se otorgan puntos.
        Body opcional: { "nota_revision": "..." }
        """
        error = self._verificar_admin(request)
        if error:
            return error

        guia = self.get_object()

        if guia.estado not in ('pendiente_revision',):
            return Response(
                {'error': f'No se puede aprobar una guía en estado "{guia.get_estado_display()}".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        guia.estado = 'aprobada'
        guia.revisada_por = request.user
        guia.fecha_revision = timezone.now()
        guia.nota_revision = request.data.get('nota_revision', '')
        guia.modificado_por = request.user.username
        guia.save()

        return Response(
            {'mensaje': f'La guía "{guia.titulo_guia}" ha sido aprobada. Pendiente de publicación.'},
            status=status.HTTP_200_OK
        )

    # ── Publicar guía y otorgar puntos ───────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='publicar')
    def publicar(self, request, pk=None):
        """
        Publica la guía (estado → 'publicada') y otorga los puntos de gamificación al autor.

        Body requerido:
          {
            "puntos_reconocimiento": 50,        // entero positivo
            "nota_revision": "Excelente guía."  // opcional
          }
        """
        error = self._verificar_admin(request)
        if error:
            return error

        guia = self.get_object()

        if guia.estado == 'publicada':
            return Response(
                {'error': 'Esta guía ya está publicada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar puntos
        try:
            puntos = int(request.data.get('puntos_reconocimiento', 0))
            if puntos < 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {'error': 'El campo puntos_reconocimiento debe ser un número entero positivo.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Actualizar guía
        guia.estado = 'publicada'
        guia.puntos_reconocimiento = puntos
        guia.revisada_por = request.user
        guia.fecha_revision = timezone.now()
        guia.nota_revision = request.data.get('nota_revision', '')
        guia.modificado_por = request.user.username
        guia.save()

        # Otorgar puntos al autor
        if puntos > 0:
            autor = guia.autor
            autor.puntos_gamificacion += puntos
            autor.save(update_fields=['puntos_gamificacion'])

        return Response(
            {
                'mensaje': (
                    f'¡La guía "{guia.titulo_guia}" ha sido publicada! '
                    f'Se otorgaron {puntos} puntos de gamificación a {guia.autor.username}.'
                ),
                'puntos_otorgados': puntos,
                'puntos_totales_autor': guia.autor.puntos_gamificacion,
            },
            status=status.HTTP_200_OK
        )

    # ── Rechazar guía ────────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='rechazar')
    def rechazar(self, request, pk=None):
        """
        Rechaza la guía. El técnico puede verla en sus propuestas como 'rechazada'.
        Body requerido: { "nota_revision": "Razón del rechazo" }
        """
        error = self._verificar_admin(request)
        if error:
            return error

        guia = self.get_object()

        if guia.estado == 'publicada':
            return Response(
                {'error': 'No se puede rechazar una guía ya publicada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        nota = request.data.get('nota_revision', '').strip()
        if not nota:
            return Response(
                {'error': 'Debes proporcionar una nota explicando el motivo del rechazo.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        guia.estado = 'rechazada'
        guia.revisada_por = request.user
        guia.fecha_revision = timezone.now()
        guia.nota_revision = nota
        guia.modificado_por = request.user.username
        guia.save()

        return Response(
            {'mensaje': f'La guía "{guia.titulo_guia}" ha sido rechazada.'},
            status=status.HTTP_200_OK
        )

    def perform_destroy(self, instance):
        """El administrador puede eliminar físicamente una guía."""
        instance.delete()


# ──────────────────────────────────────────────────────────────────────────────
# CENTRO DE SERVICIOS  (todos los técnicos y personal autorizado)
# Rutas: /api/wiki/centro-servicios/
# ──────────────────────────────────────────────────────────────────────────────
class WikiCentroServiciosViewSet(viewsets.ModelViewSet):
    """
    Centro de Servicios: punto de acceso para todos los técnicos.

    REGLAS DEL CENTRO DE SERVICIOS (mostradas en el frontend):
      1. Las guías enviadas son revisadas por el Administrador antes de publicarse.
      2. Si son aceptadas, serán publicadas y se otorgarán puntos de gamificación
         al autor, dependiendo de la calidad e impacto de la guía.
      3. Los puntos acumulados podrán canjearse por reconocimientos especiales
         dentro de la plataforma.

    Acciones:
      - Listar guías publicadas (lectura pública para todos los autenticados)
      - Enviar nueva propuesta de guía (solo técnicos logueados)
      - Ver mis propuestas y su estado
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ('create', 'mis_propuestas'):
            return WikiTecnicaPropuestaSerializer
        return WikiTecnicaPublicaSerializer

    def get_queryset(self):
        """Solo guías publicadas son visibles en el Centro de Servicios."""
        return WikiTecnica.objects.filter(
            estado='publicada'
        ).select_related(
            'autor', 'casino_origen', 'modelo_relacionado'
        )

    def perform_create(self, serializer):
        """El técnico envía su propuesta; queda en estado pendiente_revision automáticamente."""
        serializer.save(
            autor=self.request.user,
            estado='pendiente_revision',
            creado_por=self.request.user.username,
            modificado_por=self.request.user.username,
        )

    # Solo se permite crear y listar (no editar ni eliminar guías publicadas)
    http_method_names = ['get', 'post', 'head', 'options']

    # ── Mis propuestas ───────────────────────────────────────────────────────
    @action(detail=False, methods=['get'], url_path='mis-propuestas')
    def mis_propuestas(self, request):
        """
        Devuelve todas las guías enviadas por el técnico logueado,
        con su estado actual (pendiente, aprobada, publicada, rechazada).
        """
        qs = WikiTecnica.objects.filter(
            autor=request.user
        ).select_related('modelo_relacionado', 'casino_origen').order_by('-creado_en')

        serializer = WikiTecnicaPropuestaSerializer(qs, many=True)
        return Response({
            'total': qs.count(),
            'propuestas': serializer.data,
        })

    # ── Reglas del centro (endpoint informativo) ─────────────────────────────
    @action(detail=False, methods=['get'], url_path='reglas')
    def reglas(self, request):
        """Devuelve las reglas del Centro de Servicios para mostrar en el frontend."""
        return Response({
            'titulo': 'Reglas del Centro de Servicios — Wiki Técnica',
            'reglas': [
                {
                    'numero': 1,
                    'texto': (
                        'Las guías enviadas serán revisadas por el Administrador '
                        'antes de ser publicadas para toda la red de casinos.'
                    ),
                },
                {
                    'numero': 2,
                    'texto': (
                        'Si tu guía es aceptada, será publicada y se te otorgarán '
                        'puntos de gamificación según el impacto y calidad de tu contribución.'
                    ),
                },
                {
                    'numero': 3,
                    'texto': (
                        'Los puntos acumulados podrán canjearse por reconocimientos '
                        'especiales dentro de la plataforma. ¡Comparte tu conocimiento!'
                    ),
                },
            ],
        })
