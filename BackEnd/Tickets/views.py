from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ticket
from .serializers import TicketSerializer, TicketCentroServiciosSerializer
from Gamificacion.signals_gamificacion import get_puntos_context, limpiar_puntos_context

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

    def _update_con_puntos(self, request, *args, **kwargs):
        """Helper compartido por update() y partial_update()."""
        limpiar_puntos_context()
        kwargs['partial'] = kwargs.get('partial', False)
        response = super().update(request, *args, **kwargs)
        puntos = get_puntos_context()
        if puntos:
            # response.data puede ser un ReturnDict (no siempre mutable directamente)
            try:
                response.data['puntos_nexus'] = puntos
            except Exception:
                pass
            limpiar_puntos_context()
        return response

    def update(self, request, *args, **kwargs):
        return self._update_con_puntos(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self._update_con_puntos(request, *args, **kwargs)
        

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

    @action(detail=False, methods=['get'], url_path='dashboard-charts/(?P<casino_id>[^/.]+)')
    def dashboard_charts(self, request, casino_id=None):
        """
        Devuelve datos para las gráficas del dashboard filtradas por casino y fecha dinámica.
        Query params permitidos:
          - filtro_tipo: 'dia', 'semana', 'mes' (default: 'mes')
          - fecha: YYYY-MM-DD (usado si filtro_tipo='dia')
          - mes: 1-12 (usado si filtro_tipo='semana' o 'mes')
          - semana: 1-4 (usado si filtro_tipo='semana')
          - anio: YYYY (por defecto año actual)
        """
        from datetime import timedelta, date, datetime
        from django.utils import timezone
        from django.db.models import Count, Q, Avg, F, ExpressionWrapper, DurationField
        from Maquinas.models import Maquina
        from BitacoraTecnica.models import BitacoraTecnica
        from IncidenciasInfraestructura.models import IncidenciaInfraestructura
        from MantenimientosPreventivos.models import MantenimientoPreventivo
        from calendar import monthrange
        
        if not casino_id:
            return Response({'error': 'Se requiere el ID del casino'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Parámetros Base
        filtro_tipo = request.query_params.get('filtro_tipo', 'mes')
        hoy = timezone.localdate()
        anio = int(request.query_params.get('anio', hoy.year))
        
        # Inicializamos rangos de fecha limite
        fecha_inicio = hoy
        fecha_fin = hoy + timedelta(days=1) # Exclusivo para gte / lt
        
        try:
            if filtro_tipo == 'dia':
                str_fecha = request.query_params.get('fecha')
                if str_fecha:
                    fecha_inicio = datetime.strptime(str_fecha, '%Y-%m-%d').date()
                else:
                    fecha_inicio = hoy
                fecha_fin = fecha_inicio + timedelta(days=1)
                
            elif filtro_tipo == 'semana':
                mes = int(request.query_params.get('mes', hoy.month))
                semana_idx = int(request.query_params.get('semana', 1)) # 1 a 4
                
                # Calculamos el inicio del mes
                primer_dia_mes = date(anio, mes, 1)
                
                # Estimamos semanas por bloques de 7 días (para mantener simpleza)
                dia_comienzo = 1 + (semana_idx - 1) * 7
                # Si se pasa del mes, lo topamos al final
                ultimo_dia_mes = monthrange(anio, mes)[1]
                
                if dia_comienzo > ultimo_dia_mes:
                     dia_comienzo = ultimo_dia_mes - 6 if ultimo_dia_mes - 6 > 0 else 1
                
                fecha_inicio = date(anio, mes, dia_comienzo)
                
                # Si es la semana 4, abarcamos hasta fin de mes
                if semana_idx >= 4:
                    fecha_fin = date(anio, mes, ultimo_dia_mes) + timedelta(days=1)
                else:
                    fecha_fin = fecha_inicio + timedelta(days=7)
                    if fecha_fin.month != mes: # No pasarse de mes
                        fecha_fin = date(anio, mes, ultimo_dia_mes) + timedelta(days=1)
                        
            else: # filtro_tipo == 'mes' o default
                mes = int(request.query_params.get('mes', hoy.month))
                fecha_inicio = date(anio, mes, 1)
                ultimo_dia_mes = monthrange(anio, mes)[1]
                fecha_fin = date(anio, mes, ultimo_dia_mes) + timedelta(days=1)
                
        except ValueError as e:
            return Response({'error': f'Parámetros de fecha inválidos: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Convertimos a datetimes con timezone para filtros precisos django __gte __lt
        tz = timezone.get_current_timezone()
        dt_inicio = timezone.make_aware(datetime.combine(fecha_inicio, datetime.min.time()), tz)
        dt_fin = timezone.make_aware(datetime.combine(fecha_fin, datetime.min.time()), tz)
            
        # 1. Fallas por Categoría (Tickets creados en el periodo)
        tickets_periodo_creados = Ticket.objects.filter(
            maquina__casino_id=casino_id,
            creado_en__gte=dt_inicio,
            creado_en__lt=dt_fin,
            esta_activo=True
        )
        
        categorias_dict = dict(Ticket.CATEGORIAS_CHOICES)
        fallas_raw = list(tickets_periodo_creados.values('categoria').annotate(total=Count('id')).order_by('-total'))
        fallas_categoria = [
            {'categoria': c['categoria'], 'label': categorias_dict.get(c['categoria'], c['categoria']), 'total': c['total']}
            for c in fallas_raw
        ]
        
        # 1b. Top 5 Máquinas Problemáticas (NUEVO)
        maquinas_problematicas_raw = list(tickets_periodo_creados.values(
            'maquina__uid_sala', 
            'maquina__modelo__nombre_modelo'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:5])
        
        top_maquinas = [
            {
                'uid_sala': m['maquina__uid_sala'], 
                'modelo': m['maquina__modelo__nombre_modelo'], 
                'total': m['total']
            } for m in maquinas_problematicas_raw
        ]
        
        # 2. Resolución y MTTR (Cerrados en el periodo)
        tickets_creados_count = tickets_periodo_creados.count()
        
        tickets_cerrados_query = Ticket.objects.filter(
            maquina__casino_id=casino_id,
            estado_ciclo='cerrado',
            modificado_en__gte=dt_inicio, # Usamos modificacion como fecha de cierre proxy (y suelto para MTTR real)
            modificado_en__lt=dt_fin,
            esta_activo=True
        )
        tickets_cerrados_count = tickets_cerrados_query.count()
        
        # Cálculo de MTTR (Mean Time To Repair) - NUEVO
        mttr_horas = 0
        if tickets_cerrados_count > 0:
            # Anotar el tiempo empleado en cada ticket
            tickets_con_tiempo = tickets_cerrados_query.annotate(
                tiempo_reparacion=ExpressionWrapper(
                    F('modificado_en') - F('creado_en'),
                    output_field=DurationField()
                )
            )
            promedio_str = tickets_con_tiempo.aggregate(promedio=Avg('tiempo_reparacion'))['promedio']
            if promedio_str:
                mttr_horas = round(promedio_str.total_seconds() / 3600.0, 1)

        # 3. Preventivos vs Correctivos - NUEVO
        preventivos_count = MantenimientoPreventivo.objects.filter(
            maquina__casino__id=casino_id,
            fecha_mantenimiento__gte=fecha_inicio,
            fecha_mantenimiento__lt=fecha_fin,
            esta_activo=True
        ).count()
        
        # 4. Técnico más activo
        tecnicos_activos = list(BitacoraTecnica.objects.filter(
            ticket__maquina__casino_id=casino_id,
            creado_en__gte=dt_inicio,
            creado_en__lt=dt_fin
        ).values(
            'usuario_tecnico__nombres', 
            'usuario_tecnico__apellido_paterno'
        ).annotate(
            total_intervenciones=Count('id')
        ).order_by('-total_intervenciones')[:5])
        
        tecnicos = []
        for t in tecnicos_activos:
            nombre = f"{t['usuario_tecnico__nombres']} {t['usuario_tecnico__apellido_paterno'] or ''}".strip()
            tecnicos.append({
                'nombre': nombre,
                'total': t['total_intervenciones']
            })
            
        # 5. Estado de la Sala (Instantánea actual, no depende del rango de fechas)
        maquinas_estado = list(Maquina.objects.filter(
            casino_id=casino_id,
            esta_activo=True
        ).values('estado_actual').annotate(total=Count('id')))
        
        # 6. Incidencias de Infraestructura (Inciadas en el periodo)
        incidencias = IncidenciaInfraestructura.objects.filter(
            casino_id=casino_id,
            hora_inicio__gte=dt_inicio,
            hora_inicio__lt=dt_fin,
            esta_activo=True
        ).count()
        
        return Response({
            'periodo': {
                'tipo': filtro_tipo,
                'rango': f"{fecha_inicio.strftime('%Y-%m-%d')} a {fecha_fin.strftime('%Y-%m-%d')}"
            },
            'fallas_categoria': fallas_categoria,
            'top_maquinas': top_maquinas,
            'resolucion': {
                'creados': tickets_creados_count,
                'cerrados': tickets_cerrados_count
            },
            'mantenimientos': {
                'preventivos': preventivos_count,
                'correctivos': tickets_cerrados_count
            },
            'mttr_horas': mttr_horas,
            'tecnicos_activos': tecnicos,
            'estado_sala': maquinas_estado,
            'incidencias_infra': incidencias
        })