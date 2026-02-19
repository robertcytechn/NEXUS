from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import Maquina
from .serializers import MaquinaSerializer, MaquinaMapaSerializer
import logging

logger = logging.getLogger(__name__)

class MaquinaViewSet(viewsets.ModelViewSet):
    serializer_class = MaquinaSerializer

    def get_queryset(self):
        """
        Optimización de consultas y filtrado por parámetros de URL.
        Permite filtrar por: ?uid=XXX&casino=Y&estado=OPERATIVA&search=termino
        """
        from django.db.models import Q
        
        queryset = Maquina.objects.filter(esta_activo=True).select_related(
            'modelo', 'casino', 'modelo__proveedor'
        ).prefetch_related('denominaciones')
        
        # Filtro por UID (busca en uid_sala, case-insensitive)
        uid = self.request.query_params.get('uid', None)
        if uid:
            queryset = queryset.filter(uid_sala__iexact=uid)
        
        # Filtro por Casino
        casino = self.request.query_params.get('casino', None)
        if casino:
            queryset = queryset.filter(casino_id=casino)
        
        # Filtro por Estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado_actual=estado)
        
        # Filtro de búsqueda general (uid_sala, numero_serie, juego, nombre del modelo)
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(uid_sala__icontains=search) |
                Q(numero_serie__icontains=search) |
                Q(juego__icontains=search) |
                Q(modelo__nombre_modelo__icontains=search) |
                Q(modelo__nombre_producto__icontains=search)
            )
        
        return queryset
    
    def partial_update(self, request, *args, **kwargs):
        """
        Override del partial_update para manejar actualizaciones de estado.
        """
        instance = self.get_object()
        
        # CASO ESPECIAL: Actualización solo de estado_actual
        if 'estado_actual' in request.data and len(request.data) <= 2:
            # Validar que el nuevo estado sea válido
            nuevo_estado = request.data.get('estado_actual')
            estados_validos = [choice[0] for choice in Maquina.ESTADOS_CHOICES]
            
            if nuevo_estado not in estados_validos:
                raise ValidationError({
                    'estado_actual': f'Estado inválido. Valores permitidos: {estados_validos}'
                })
            
            # Actualizar la instancia específica
            instance.estado_actual = nuevo_estado
            instance.modificado_por = request.user.username if request.user.is_authenticated else 'Sistema'
            instance.save(update_fields=['estado_actual', 'modificado_por', 'modificado_en'])
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        
        # CASO NORMAL: Actualización completa con validaciones
        else:
            return super().partial_update(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        """Agregar auditoría en actualizaciones normales."""
        modificado_por = self.request.user.username if self.request.user.is_authenticated else 'Sistema'
        serializer.save(modificado_por=modificado_por)

    @action(detail=True, methods=['patch'], url_path='switch-estado')
    def switch_estado(self, request, pk=None):
        """Cambia el estado activo/inactivo de una máquina."""
        from django.shortcuts import get_object_or_404
        
        # Obtenemos el modelo dinámicamente desde el serializer
        ModeloMaquina = self.get_serializer().Meta.model
        
        # IMPORTANTE: Buscamos en .all() para encontrar la máquina aunque esté inactiva
        # Esto evita el error 404 cuando get_queryset filtra por esta_activo=True
        maquina = get_object_or_404(ModeloMaquina.objects.all(), pk=pk)
        
        maquina.esta_activo = not maquina.esta_activo
        maquina.modificado_por = request.user.username if request.user.is_authenticated else 'Anónimo'
        maquina.save()
        
        serializer = self.get_serializer(maquina)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='lista')
    def lista(self, request):
        """Devuelve todas las máquinas, incluyendo inactivos."""
        queryset = Maquina.objects.all().order_by('uid_sala')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='lista-por-casino/(?P<casino_id>[^/.]+)')
    def lista_por_casino(self, request, casino_id=None):
        """
        Devuelve todas las máquinas de un casino específico.
        Endpoint: /maquinas/lista-por-casino/{casino_id}/
        """
        if not casino_id:
            return Response(
                {'error': 'Se requiere el ID del casino'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            queryset = Maquina.objects.filter(
                casino_id=casino_id,
                esta_activo=True
            ).select_related(
                'modelo', 'casino', 'modelo__proveedor'
            ).prefetch_related('denominaciones').order_by('uid_sala')
            
            serializer = self.get_serializer(queryset, many=True)
            
            # Calcular estadísticas para la gráfica
            total = queryset.count()
            danadas = queryset.filter(
                estado_actual__in=['DAÑADA', 'DAÑADA_OPERATIVA']
            ).count()
            
            return Response({
                'maquinas': serializer.data,
                'estadisticas': {
                    'total': total,
                    'danadas': danadas,
                    'porcentaje_danadas': round((danadas / total * 100) if total > 0 else 0, 2)
                }
            })
        except Exception as e:
            logger.error(f"Error al obtener máquinas del casino {casino_id}: {str(e)}")
            return Response(
                {'error': 'Error al obtener las máquinas del casino'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='incrementar-fallas')
    def incrementar_fallas(self, request, pk=None):
        """
        Incrementa el contador de fallas de una máquina.
        Endpoint: /maquinas/{id}/incrementar-fallas/
        """
        from django.db.models import F
        
        maquina = self.get_object()
        
        try:
            # Usar F() expression para incremento atómico
            Maquina.objects.filter(pk=maquina.pk).update(
                contador_fallas=F('contador_fallas') + 1,
                modificado_por=request.user.username if request.user.is_authenticated else 'Sistema'
            )
            
            # Recargar la instancia para obtener el valor actualizado
            maquina.refresh_from_db()
            
            logger.info(f"Contador de fallas incrementado para máquina {maquina.uid_sala} (ID: {maquina.pk}): {maquina.contador_fallas}")
            
            serializer = self.get_serializer(maquina)
            return Response({
                'mensaje': 'Contador de fallas incrementado correctamente',
                'contador_fallas': maquina.contador_fallas,
                'uid_sala': maquina.uid_sala,
                'maquina': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error al incrementar contador_fallas para máquina {pk}: {str(e)}")
            return Response(
                {'error': f'Error al incrementar contador de fallas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        creado_por = self.request.user.username if self.request.user.is_authenticated else 'system'
        serializer.save(creado_por=creado_por)

    # =========================================================================
    # ENDPOINTS DE MAPA INTERACTIVO
    # =========================================================================

    @action(detail=True, methods=['patch'], url_path='actualizar-coordenadas')
    def actualizar_coordenadas(self, request, pk=None):
        """
        Actualiza exclusivamente las coordenadas X e Y de una máquina en el mapa.
        Endpoint: PATCH /maquinas/{id}/actualizar-coordenadas/
        Body: { "coordenada_x": int, "coordenada_y": int }
        """
        maquina = get_object_or_404(Maquina.objects.all(), pk=pk)

        nueva_x = request.data.get('coordenada_x')
        nueva_y = request.data.get('coordenada_y')

        # Validar que se enviaron ambas coordenadas
        if nueva_x is None or nueva_y is None:
            return Response(
                {'error': 'Se requieren coordenada_x y coordenada_y'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Convertir a entero y validar positivos
        try:
            nueva_x = int(nueva_x)
            nueva_y = int(nueva_y)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Las coordenadas deben ser números enteros'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if nueva_x < 0 or nueva_y < 0:
            return Response(
                {'error': 'Las coordenadas deben ser valores positivos (>= 0)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar colisión (si no son 0,0 — sin asignar)
        if not (nueva_x == 0 and nueva_y == 0):
            colision = Maquina.objects.filter(
                casino=maquina.casino,
                ubicacion_piso=maquina.ubicacion_piso,
                ubicacion_sala=maquina.ubicacion_sala,
                coordenada_x=nueva_x,
                coordenada_y=nueva_y,
                esta_activo=True
            ).exclude(pk=maquina.pk).exists()

            if colision:
                return Response(
                    {'error': 'Ya existe una máquina activa en esa posición dentro de la misma sala y piso'},
                    status=status.HTTP_409_CONFLICT
                )

        # Aplicar cambio con update_fields para omitir full_clean
        maquina.coordenada_x = nueva_x
        maquina.coordenada_y = nueva_y
        maquina.modificado_por = request.user.username if request.user.is_authenticated else 'Sistema'
        maquina.save(update_fields=['coordenada_x', 'coordenada_y', 'modificado_por', 'modificado_en'])

        logger.info(
            f"Coordenadas actualizadas para máquina {maquina.uid_sala} (ID: {maquina.pk}): "
            f"({nueva_x}, {nueva_y}) por {maquina.modificado_por}"
        )

        serializer = MaquinaMapaSerializer(maquina)
        return Response({
            'mensaje': 'Coordenadas actualizadas correctamente',
            'maquina': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='mapa-completo')
    def mapa_completo(self, request):
        """
        Devuelve la configuración del grid del casino y las máquinas con filtros opcionales.
        Endpoint: GET /maquinas/mapa-completo/?casino_id=1&piso=PISO_1&area=SALA_A
        """
        from Casinos.models import Casino

        casino_id = request.query_params.get('casino_id')
        piso = request.query_params.get('piso')
        area = request.query_params.get('area')

        if not casino_id:
            return Response(
                {'error': 'Se requiere el parámetro casino_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            casino = Casino.objects.get(pk=casino_id, esta_activo=True)
        except Casino.DoesNotExist:
            return Response(
                {'error': 'Casino no encontrado o inactivo'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Construir queryset base
        queryset = Maquina.objects.filter(
            casino=casino,
            esta_activo=True
        ).select_related('modelo', 'modelo__proveedor').prefetch_related('denominaciones')

        # Aplicar filtros opcionales
        if piso:
            queryset = queryset.filter(ubicacion_piso=piso)
        if area:
            queryset = queryset.filter(ubicacion_sala=area)

        # Obtener pisos y áreas disponibles para el casino (para los selectores del frontend)
        todos = Maquina.objects.filter(casino=casino, esta_activo=True)
        pisos_disponibles = list(
            todos.values_list('ubicacion_piso', flat=True).distinct().order_by('ubicacion_piso')
        )
        areas_disponibles = list(
            todos.values_list('ubicacion_sala', flat=True).distinct().order_by('ubicacion_sala')
        )

        serializer = MaquinaMapaSerializer(queryset, many=True)

        return Response({
            'casino': {
                'id': casino.id,
                'nombre': casino.nombre,
                'grid_width': casino.grid_width,
                'grid_height': casino.grid_height,
            },
            'pisos_disponibles': pisos_disponibles,
            'areas_disponibles': areas_disponibles,
            'piso_choices': [{'value': k, 'label': v} for k, v in Maquina.PISO_CHOICES],
            'sala_choices': [{'value': k, 'label': v} for k, v in Maquina.SALA_CHOICES],
            'filtros_activos': {'piso': piso, 'area': area},
            'total': queryset.count(),
            'maquinas': serializer.data
        }, status=status.HTTP_200_OK)