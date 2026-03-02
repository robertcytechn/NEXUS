import logging
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import ConfiguracionCasino, TicketVacio
from .serializers import (
    ConfiguracionCasinoSerializer,
    TicketVacioSerializer,
    AuditoriaVacioSerializer,
)

logger = logging.getLogger(__name__)

# Roles que pueden emitir veredictos de auditoría
ROLES_AUDITORES = ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUPERVISOR SALA', 'SUP SISTEMAS']


class ConfiguracionCasinoViewSet(viewsets.ModelViewSet):
    """
    CRUD de la configuración de parámetros de vacíos por casino.
    Endpoint: /api/vacios/configuracion/
    """
    serializer_class = ConfiguracionCasinoSerializer
    queryset = ConfiguracionCasino.objects.select_related('casino').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['casino']

    @action(detail=False, methods=['get'], url_path='por-casino/(?P<casino_id>[^/.]+)')
    def por_casino(self, request, casino_id=None):
        """
        Devuelve la configuración de un casino específico.
        Endpoint: /api/vacios/configuracion/por-casino/{casino_id}/
        """
        try:
            config = ConfiguracionCasino.objects.select_related('casino').get(casino_id=casino_id)
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        except ConfiguracionCasino.DoesNotExist:
            return Response(
                {'detail': 'Este casino no tiene configuración de vacíos registrada.'},
                status=status.HTTP_404_NOT_FOUND
            )


class TicketVacioViewSet(viewsets.ModelViewSet):
    """
    CRUD + Acciones especiales para Tickets de Vacíos.

    Endpoints clave:
      GET    /api/vacios/tickets/                          → listado completo
      POST   /api/vacios/tickets/                          → crear ticket (multipart)
      GET    /api/vacios/tickets/{id}/                     → detalle
      PATCH  /api/vacios/tickets/{id}/                     → edición parcial
      POST   /api/vacios/tickets/{id}/emitir_veredicto/    → acción de auditoría gerencial
      PATCH  /api/vacios/tickets/{id}/confirmar_carga/     → técnico confirma que realizó la recarga
      GET    /api/vacios/tickets/por_casino/{casino_id}/   → historial filtrado por casino
    """
    serializer_class = TicketVacioSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'casino',
        'maquina',
        'estado_operativo',
        'estado_auditoria',
        'tecnico_creador',
        'gerente_auditor',
    ]
    search_fields = ['cliente_nombre', 'explicacion_detallada', 'maquina__uid_sala']
    ordering_fields = ['fecha_creacion', 'monto_extraviado']

    def get_queryset(self):
        return TicketVacio.objects.select_related(
            'casino',
            'maquina',
            'tecnico_creador',
            'gerente_auditor',
        ).all().order_by('-fecha_creacion')

    # ── Creación ──────────────────────────────────────────────────────────

    def perform_create(self, serializer):
        """
        Inyecta el técnico creador desde el usuario autenticado.
        El estado operativo y el estado de auditoría los calcula el modelo en save().
        """
        serializer.save(tecnico_creador=self.request.user)

    # ── Acción de Auditoría Gerencial ─────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='emitir_veredicto')
    def emitir_veredicto(self, request, pk=None):
        """
        Permite a Gerencia/Admin emitir el veredicto de auditoría.
        Registra automáticamente el gerente auditor y la fecha.

        Body esperado:
          { "veredicto": "auditado_aprobado" | "rechazado_investigacion",
            "comentario_auditoria": "texto opcional" }

        Endpoint: POST /api/vacios/tickets/{id}/emitir_veredicto/
        """
        ticket = self.get_object()
        usuario = request.user

        # Verificar permiso de rol
        rol_nombre = getattr(getattr(usuario, 'rol', None), 'nombre', '').upper()
        if rol_nombre not in ROLES_AUDITORES:
            return Response(
                {'detail': 'No tiene permisos para emitir veredictos de auditoría.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Ya fue auditado
        if ticket.estado_auditoria != 'pendiente_revision':
            return Response(
                {'detail': f'Este ticket ya fue auditado con estado: {ticket.get_estado_auditoria_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        audit_serializer = AuditoriaVacioSerializer(data=request.data)
        audit_serializer.is_valid(raise_exception=True)

        ticket.estado_auditoria = audit_serializer.validated_data['veredicto']
        ticket.gerente_auditor = usuario
        ticket.fecha_auditoria = timezone.now()

        # Si el ticket estaba pendiente de autorización y el gerente lo aprueba,
        # trasladarlo a "Autorizado para Carga"
        if (ticket.estado_auditoria == 'auditado_aprobado'
                and ticket.estado_operativo == 'pendiente_autorizacion'):
            ticket.estado_operativo = 'autorizado_carga'

        comentario = audit_serializer.validated_data.get('comentario_auditoria', '')
        if comentario:
            ticket.notas_internas = (ticket.notas_internas or '') + f'\n[AUDITORÍA] {comentario}'

        ticket.save()

        serializer = TicketVacioSerializer(ticket, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ── Confirmar Carga ──────────────────────────────────────────────────

    @action(detail=True, methods=['patch'], url_path='confirmar_carga')
    def confirmar_carga(self, request, pk=None):
        """
        El técnico confirma que realizó la recarga física al cliente.
        Solo puede aplicarse si el estado operativo es 'autorizado_carga'.

        Endpoint: PATCH /api/vacios/tickets/{id}/confirmar_carga/
        """
        ticket = self.get_object()

        if ticket.estado_operativo != 'autorizado_carga':
            return Response(
                {'detail': f'No se puede confirmar la carga. Estado actual: {ticket.get_estado_operativo_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ticket.estado_operativo = 'carga_realizada'
        ticket.save()

        serializer = TicketVacioSerializer(ticket, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ── Historial por casino ──────────────────────────────────────────────

    @action(detail=False, methods=['get'], url_path='por_casino/(?P<casino_id>[^/.]+)')
    def por_casino(self, request, casino_id=None):
        """
        Devuelve el historial de tickets de vacíos de un casino específico.
        Endpoint: GET /api/vacios/tickets/por_casino/{casino_id}/
        """
        qs = self.get_queryset().filter(casino_id=casino_id)

        # Permitir filtros adicionales por estado en la query string
        estado_op = request.query_params.get('estado_operativo')
        estado_aud = request.query_params.get('estado_auditoria')
        if estado_op:
            qs = qs.filter(estado_operativo=estado_op)
        if estado_aud:
            qs = qs.filter(estado_auditoria=estado_aud)

        serializer = TicketVacioSerializer(qs, many=True, context={'request': request})

        stats = {
            'total': qs.count(),
            'pendientes_autorizacion': qs.filter(estado_operativo='pendiente_autorizacion').count(),
            'autorizados': qs.filter(estado_operativo='autorizado_carga').count(),
            'carga_realizada': qs.filter(estado_operativo='carga_realizada').count(),
            'pendientes_auditoria': qs.filter(estado_auditoria='pendiente_revision').count(),
            'rechazados': qs.filter(estado_auditoria='rechazado_investigacion').count(),
        }

        return Response({
            'tickets': serializer.data,
            'estadisticas': stats,
        })
