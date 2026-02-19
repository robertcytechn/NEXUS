from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ticket
from .serializers import TicketSerializer, TicketCentroServiciosSerializer

import logging
logger = logging.getLogger(__name__)

class TicketViewSet(viewsets.ModelViewSet):
    """
    Controlador para la gestión de incidencias en las máquinas de los casinos.
    """
    serializer_class = TicketSerializer

    def get_queryset(self):
        """Optimización de consultas para las 17 salas."""
        return Ticket.objects.all().select_related(
            'maquina',
            'maquina__casino',
            'reportante',
            'reportante__rol',
            'tecnico_asignado'
        ).order_by('-creado_en')

    @action(detail=False, methods=['get'], url_path='lista-por-casino/(?P<casino_id>[^/.]+)')
    def lista_por_casino(self, request, casino_id=None):
        """
        Devuelve todos los tickets abiertos de un casino específico.
        Filtra solo tickets que NO estén cerrados.
        Endpoint: /tickets/lista-por-casino/{casino_id}/
        """
        if not casino_id:
            return Response(
                {'error': 'Se requiere el ID del casino'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            queryset = Ticket.objects.filter(
                maquina__casino_id=casino_id,
                esta_activo=True
            ).exclude(
                estado_ciclo='cerrado'
            ).select_related(
                'maquina',
                'maquina__casino',
                'reportante',
                'reportante__rol',
                'tecnico_asignado'
            ).prefetch_related(
                'bitacoras'
            ).order_by('-creado_en')

            serializer = TicketCentroServiciosSerializer(queryset, many=True)

            # Calcular estadísticas
            total = queryset.count()
            criticos = queryset.filter(prioridad__in=['critica', 'emergencia']).count()
            sin_tecnico = queryset.filter(tecnico_asignado__isnull=True).count()

            return Response({
                'tickets': serializer.data,
                'estadisticas': {
                    'total': total,
                    'criticos': criticos,
                    'sin_tecnico': sin_tecnico
                }
            })
        except Exception as e:
            logger.error(f"Error al obtener tickets del casino {casino_id}: {str(e)}")
            return Response(
                {'error': 'Error al obtener los tickets del casino'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        # El reportante será el usuario logueado, y creado_por guardará el username
        # Si no hay usuario autenticado, se debe manejar en el frontend
        usuario = self.request.user.username if self.request.user.is_authenticated else 'Sistema'
        
        # Validación de seguridad: No permitir crear ticket si ya hay tickets abiertos para la máquina
        maquina_id = self.request.data.get('maquina')
        if maquina_id:
            # Buscar tickets abiertos para esta máquina (estados diferentes a 'cerrado')
            tickets_abiertos = Ticket.objects.filter(
                maquina_id=maquina_id,
                esta_activo=True
            ).exclude(estado_ciclo='cerrado')
            
            if tickets_abiertos.exists():
                # Obtener información de los tickets abiertos
                folios = ', '.join([t.folio for t in tickets_abiertos[:3]])
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    'error': 'No se puede crear un nuevo ticket',
                    'mensaje': f'La máquina ya tiene tickets abiertos: {folios}',
                    'tickets_abiertos': tickets_abiertos.count()
                })
        
        # Solo asignar reportante si el usuario está autenticado
        if self.request.user.is_authenticated:
            serializer.save(reportante=self.request.user, creado_por=usuario)
        else:
            # Si no está autenticado, el reportante debe venir en los datos del request
            serializer.save(creado_por=usuario)
    
    def perform_update(self, serializer):
        usuario = self.request.user.username if self.request.user.is_authenticated else 'Sistema'
        serializer.save(modificado_por=usuario)
        

    @action(detail=True, methods=['patch'], url_path='reabrir')
    def reabrir(self, request, pk=None):
        """
        URL: /api/tickets/{id}/reabrir/
        Incrementa el contador y regresa el estado a abierto.
        """
        ticket = self.get_object()
        if ticket.estado_ciclo == 'cerrado':
            ticket.estado_ciclo = 'abierto'
            ticket.contador_reaperturas += 1
            ticket.modificado_por = request.user.username if request.user.is_authenticated else 'Sistema'
            ticket.save()
            return Response({'message': 'Ticket reabierto con éxito.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Solo se pueden reabrir tickets cerrados.'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'], url_path='switch-estado')
    def switch_estado(self, request, pk=None):
        """
        URL: /api/tickets/{id}/switch-estado/
        Cambia el estado activo/inactivo del ticket (borrado lógico).
        SIN lógica automática - el frontend maneja las actualizaciones.
        """
        ticket = self.get_object()
        
        # Cambiar estado activo del ticket - SIN actualizar máquina automáticamente
        ticket.esta_activo = not ticket.esta_activo
        ticket.modificado_por = request.user.username if request.user.is_authenticated else 'Sistema'
        ticket.save()
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='historial-maquina/(?P<maquina_id>[^/.]+)')
    def historial_maquina(self, request, maquina_id=None):
        """
        URL: /api/tickets/historial-maquina/{maquina_id}/
        Retorna los últimos 3 tickets de una máquina con sus bitácoras técnicas.
        Optimizado para evitar sobrecarga al traer toda la tabla.
        """
        if not maquina_id:
            return Response(
                {'error': 'Se requiere el ID de la máquina'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener los últimos 3 tickets de la máquina, ordenados por fecha de creación
            tickets = Ticket.objects.filter(
                maquina_id=maquina_id,
                esta_activo=True
            ).select_related(
                'maquina',
                'reportante',
                'tecnico_asignado'
            ).prefetch_related(
                'bitacoras',
                'bitacoras__usuario_tecnico'
            ).order_by('-creado_en')[:3]
            
            # Serializar los datos
            from BitacoraTecnica.serializers import BitacoraTecnicaSerializer
            
            historial = []
            for ticket in tickets:
                # Obtener bitácoras del ticket
                bitacoras = ticket.bitacoras.all().order_by('-creado_en')
                
                historial.append({
                    'id': ticket.id,
                    'folio': ticket.folio,
                    'categoria': ticket.categoria,
                    'prioridad': ticket.prioridad,
                    'estado_ciclo': ticket.estado_ciclo,
                    'descripcion_problema': ticket.descripcion_problema,
                    'fecha_creacion': ticket.creado_en,
                    'fecha_modificacion': ticket.modificado_en if ticket.estado_ciclo == 'cerrado' else None,
                    'tecnico_asignado': {
                        'id': ticket.tecnico_asignado.id if ticket.tecnico_asignado else None,
                        'nombre': ticket.tecnico_asignado.nombres if ticket.tecnico_asignado else 'Sin asignar',
                        'apellidos': f"{ticket.tecnico_asignado.apellido_paterno or ''} {ticket.tecnico_asignado.apellido_materno or ''}".strip() if ticket.tecnico_asignado else ''
                    },
                    'bitacoras': BitacoraTecnicaSerializer(bitacoras, many=True).data
                })
            
            return Response({
                'maquina_id': maquina_id,
                'total_tickets': len(historial),
                'historial': historial
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener historial: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )