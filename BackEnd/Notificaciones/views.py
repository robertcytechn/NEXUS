from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Exists, OuterRef
from .models import Notificacion, NotificacionUsuario
from .serializers import NotificacionSerializer, NotificacionUsuarioSerializer

class NotificacionViewSet(viewsets.ModelViewSet):
    """
    Controlador de alertas optimizado con polling REST.
    Incluye filtrado por identidad (usuario, casino, rol) y auto-limpieza.
    """
    serializer_class = NotificacionSerializer

    def get_queryset(self):
        """
        Filtro por Identidad: Solo devolver notificaciones donde:
        - es_global == True
        - destino_casino == user.casino Y destino_rol == user.rol
        - destino_usuario == user.id
        
        Auto-limpieza: Desactivar notificaciones caducadas en cada consulta.
        """
        user = self.request.user
        ahora = timezone.now()
        
        # Auto-limpieza de notificaciones caducadas
        limite_normales = ahora - timedelta(hours=48)
        limite_director = ahora - timedelta(days=7)
        
        # Desactivar notificaciones normales con más de 48 horas
        Notificacion.objects.filter(
            tipo__in=['ticket', 'infraestructura', 'wiki', 'sistema'],
            creado_en__lt=limite_normales,
            esta_activo=True
        ).update(esta_activo=False)
        
        # Desactivar notificaciones DIRECTOR con más de 7 días
        Notificacion.objects.filter(
            tipo='DIRECTOR',
            creado_en__lt=limite_director,
            esta_activo=True
        ).update(esta_activo=False)
        
        # Filtro principal por identidad
        return Notificacion.objects.filter(
            Q(es_global=True) |
            Q(usuario_destino=user) |
            Q(casino_destino=user.casino, rol_destino=user.rol) |
            Q(casino_destino=user.casino, rol_destino__isnull=True)
        ).filter(esta_activo=True).order_by('-creado_en')

    def get_serializer_context(self):
        """
        Agregar el request al contexto del serializer para poder acceder al usuario.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['patch'], url_path='marcar-leida')
    def marcar_leida(self, request, pk=None):
        """
        Marca una notificación como leída para el usuario actual.
        Crea un registro en la tabla NotificacionUsuario.
        """
        notificacion = self.get_object()
        usuario = request.user
        
        # Crear o actualizar el registro de lectura
        lectura, created = NotificacionUsuario.objects.get_or_create(
            notificacion=notificacion,
            usuario=usuario,
            defaults={'creado_por': usuario.username if hasattr(usuario, 'username') else str(usuario)}
        )
        
        return Response({
            'status': 'ok',
            'leido': True,
            'created': created,
            'fecha_visto': lectura.fecha_visto
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='count-no-leidas')
    def count_no_leidas(self, request):
        """
        Endpoint rápido para obtener el count de notificaciones no leídas.
        Optimizado para polling cada 45 segundos.
        """
        user = request.user
        
        # Subconsulta para verificar si existe una lectura del usuario
        lectura_exists = NotificacionUsuario.objects.filter(
            notificacion=OuterRef('pk'),
            usuario=user
        )
        
        # Contar notificaciones que el usuario puede ver y que no ha leído
        count = Notificacion.objects.filter(
            Q(es_global=True) |
            Q(usuario_destino=user) |
            Q(casino_destino=user.casino, rol_destino=user.rol) |
            Q(casino_destino=user.casino, rol_destino__isnull=True)
        ).filter(esta_activo=True).annotate(
            leido=Exists(lectura_exists)
        ).filter(leido=False).count()
        
        return Response({'count': count}, status=status.HTTP_200_OK)


class NotificacionUsuarioViewSet(viewsets.ModelViewSet):
    """
    Controlador para gestionar las lecturas de notificaciones por usuario.
    Permite crear registros de lectura (POST) y listarlos (GET).
    """
    serializer_class = NotificacionUsuarioSerializer
    
    def get_queryset(self):
        """
        Filtrar solo las lecturas del usuario actual.
        """
        return NotificacionUsuario.objects.filter(
            usuario=self.request.user
        ).select_related('notificacion', 'usuario').order_by('-fecha_visto')
    
    def create(self, request, *args, **kwargs):
        """
        Crea un registro de lectura. El usuario se toma del request.
        Body esperado: { "notificacion": <id> }
        """
        usuario = request.user
        notificacion_id = request.data.get('notificacion')
        
        if not notificacion_id:
            return Response({
                'error': 'Se requiere el ID de la notificación'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            notificacion = Notificacion.objects.get(pk=notificacion_id)
        except Notificacion.DoesNotExist:
            return Response({
                'error': 'Notificación no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Crear o recuperar el registro de lectura
        lectura, created = NotificacionUsuario.objects.get_or_create(
            notificacion=notificacion,
            usuario=usuario,
            defaults={'creado_por': usuario.username if hasattr(usuario, 'username') else str(usuario)}
        )
        
        serializer = self.get_serializer(lectura)
        return Response({
            'success': True,
            'created': created,
            'data': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)