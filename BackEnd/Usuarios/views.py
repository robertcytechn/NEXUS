import uuid
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from .models import Usuarios
from .serializers import UsuariosSerializer, UsuarioLoginSerializer, UsuarioRefreshSerializer

class UsuariosViewSet(viewsets.ModelViewSet):
    """
    API para gestión de usuarios con control de sesión y seguridad avanzada.
    """
    serializer_class = UsuariosSerializer

    def get_queryset(self):
        return Usuarios.objects.filter(esta_activo=True).select_related('rol', 'casino')

    @action(detail=False, methods=['get'], url_path='lista')
    def lista(self, request):
        """Devuelve todos los usuarios, incluyendo inactivos."""
        queryset = Usuarios.objects.all().order_by('apellido_paterno')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='lista-por-casino/(?P<casino_id>[^/.]+)')
    def lista_por_casino(self, request, casino_id=None):
        """
        Devuelve todos los usuarios de un casino específico con estadísticas.
        Endpoint: /usuarios/lista-por-casino/{casino_id}/
        """
        if not casino_id:
            return Response(
                {'error': 'Se requiere el ID del casino'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            queryset = Usuarios.objects.filter(
                casino_id=casino_id
            ).exclude(
                rol__nombre='ADMINISTRADOR'
            ).select_related('rol', 'casino').order_by('apellido_paterno')

            serializer = self.get_serializer(queryset, many=True)

            total = queryset.count()
            activos = queryset.filter(esta_activo=True).count()
            inactivos = total - activos

            return Response({
                'usuarios': serializer.data,
                'estadisticas': {
                    'total': total,
                    'activos': activos,
                    'inactivos': inactivos
                }
            })
        except Exception as e:
            return Response(
                {'error': 'Error al obtener los usuarios del casino'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='login', serializer_class=UsuarioLoginSerializer, permission_classes=[])
    def login(self, request):
        """Autentica usuario y genera tokens de sesión."""
        serializer_input = self.get_serializer(data=request.data)
        if not serializer_input.is_valid():
            return Response(serializer_input.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer_input.validated_data.get('username')
        password = serializer_input.validated_data.get('password')
        try:
            user_obj = Usuarios.objects.get(username=username)
        except Usuarios.DoesNotExist:
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user_obj.esta_activo:
            return Response({"error": "Cuenta bloqueada o desactivada."}, status=status.HTTP_401_UNAUTHORIZED)

        if user_obj.check_password(password):
            user = user_obj
            user.intentos_fallidos = 0
            user.ultima_ip = request.META.get('REMOTE_ADDR')
            user.user_agent = request.META.get('HTTP_USER_AGENT')
            user.last_login = timezone.now()
            token = str(uuid.uuid4())
            refresh = str(uuid.uuid4())
            user.session_token = token
            user.refresh_token = refresh
            user.save()
            
            serializer_output = UsuariosSerializer(user, context={'request': request})
            return Response({"message": "Login exitoso", "token": token, "refresh_token": refresh, "usuario": serializer_output.data})
        else:
            user_obj.intentos_fallidos += 1
            if user_obj.intentos_fallidos >= 3:
                user_obj.esta_activo = False
                user_obj.intentos_fallidos = 0
                user_obj.save()
                return Response({"error": "Cuenta bloqueada por seguridad."}, status=status.HTTP_403_FORBIDDEN)
            
            user_obj.save()
            return Response({"error": "Credenciales inválidas."}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], url_path='refresh', serializer_class=UsuarioRefreshSerializer, permission_classes=[])
    def refresh_token(self, request):
        """Renueva el session_token usando el refresh_token."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        refresh_token = serializer.validated_data.get('refresh_token')
        
        try:
            user = Usuarios.objects.get(refresh_token=refresh_token)
        except Usuarios.DoesNotExist:
            return Response({"error": "Token de actualización inválido o expirado."}, status=status.HTTP_401_UNAUTHORIZED)
            
        if not user.esta_activo:
            return Response({"error": "Usuario inactivo."}, status=status.HTTP_401_UNAUTHORIZED)
            
        new_token = str(uuid.uuid4())
        new_refresh = str(uuid.uuid4())
        
        user.session_token = new_token
        user.refresh_token = new_refresh
        user.save()
        
        return Response({
            "token": new_token,
            "refresh_token": new_refresh
        })

    @action(detail=True, methods=['patch'], url_path='switch-estado')
    def switch_estado(self, request, pk=None):
        """Cambia el estado activo/inactivo de un usuario."""
        from django.shortcuts import get_object_or_404
        
        # Obtenemos el modelo dinámicamente desde el serializer
        ModeloUsuario = self.get_serializer().Meta.model
        
        # IMPORTANTE: Buscamos en .all() para encontrar el usuario aunque esté inactivo
        # Esto evita el error 404 cuando get_queryset filtra por esta_activo=True
        usuario = get_object_or_404(ModeloUsuario.objects.all(), pk=pk)
        
        usuario.esta_activo = not usuario.esta_activo
        usuario.modificado_por = request.user.username if request.user.is_authenticated else 'Anónimo'
        usuario.save()
        
        serializer = self.get_serializer(usuario)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='aceplisencia', serializer_class=UsuariosSerializer, url_name='aceplisencia', permission_classes=[])
    def aceptar_eula(self, request, pk=None):
        """Marca que el usuario ha aceptado el EULA."""
        # Obtener usuario sin filtro de esta_activo para permitir actualización incluso si está inactivo
        try:
            usuario = Usuarios.objects.get(pk=pk)
        except Usuarios.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        usuario.EULAAceptada = True
        # Usar username si está autenticado, sino 'aceptacion_eula'
        usuario.modificado_por = request.user.username if request.user.is_authenticated else 'aceptacion_eula'
        usuario.save()
        return Response({"message": "EULA aceptada correctamente."}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        creado_por = self.request.user.username if self.request.user.is_authenticated else 'system'
        serializer.save(creado_por=creado_por)

    def perform_update(self, serializer):
        modificado_por = self.request.user.username if self.request.user.is_authenticated else 'system'
        serializer.save(modificado_por=modificado_por)

    @action(detail=False, methods=['get'], url_path='dashboard-stats')
    def dashboard_stats(self, request):
        """
        Devuelve estadísticas para el Dashboard:
        - KPIs: Usuarios Activos, Tickets Pendientes, Reportes Evolución.
        - Actividad Reciente: Feed combinado de eventos.
        """
        from Tickets.models import Ticket
        from EvolucionNexus.models import EvolucionNexus
        
        # 1. KPIs
        usuarios_activos = Usuarios.objects.filter(esta_activo=True).count()
        tickets_pendientes = Ticket.objects.filter(estado_ciclo__in=['abierto', 'proceso', 'espera']).count()
        tickets_criticos = Ticket.objects.filter(estado_ciclo__in=['abierto', 'proceso'], prioridad__in=['critica', 'emergencia']).count()
        reportes_evolucion = EvolucionNexus.objects.filter(estado__in=['NO_REVISADO', 'POR_REVISAR', 'ANALIZANDO']).count()

        # 2. Actividad Reciente (Últimos 10 eventos combinados)
        actividad = []

        # Usuarios recientes
        ultimos_usuarios = Usuarios.objects.order_by('-creado_en')[:5]
        for u in ultimos_usuarios:
            actividad.append({
                'tipo': 'usuario',
                'icono': 'pi pi-user',
                'color': 'text-blue-500',
                'titulo': f'Nuevo Usuario: {u.username}',
                'descripcion': f'Registrado por {u.creado_por or "Sistema"}',
                'fecha': u.creado_en
            })

        # Tickets recientes
        ultimos_tickets = Ticket.objects.order_by('-creado_en')[:5]
        for t in ultimos_tickets:
            actividad.append({
                'tipo': 'ticket',
                'icono': 'pi pi-ticket',
                'color': 'text-orange-500',
                'titulo': f'Ticket #{t.folio}',
                'descripcion': f'{t.get_categoria_display()} - {t.get_estado_ciclo_display()}',
                'fecha': t.creado_en
            })

        # Evolución reciente
        ultimas_evoluciones = EvolucionNexus.objects.order_by('-fecha_creacion')[:5]
        for e in ultimas_evoluciones:
            actividad.append({
                'tipo': 'evolucion',
                'icono': 'pi pi-bolt',
                'color': 'text-purple-500',
                'titulo': f'Evolución: {e.get_categoria_display()}',
                'descripcion': e.titulo,
                'fecha': e.fecha_creacion
            })

        # Ordenar por fecha descendente y tomar los últimos 10
        actividad.sort(key=lambda x: x['fecha'], reverse=True)
        actividad = actividad[:10]

        return Response({
            'kpis': {
                'usuarios_activos': usuarios_activos,
                'tickets_pendientes': tickets_pendientes,
                'tickets_criticos': tickets_criticos,
                'reportes_evolucion': reportes_evolucion
            },
            'actividad_reciente': actividad
        })

    @action(detail=True, methods=['get'], url_path='estadisticas-perfil')
    def estadisticas_perfil(self, request, pk=None):
        """
        Devuelve estadísticas de actividad del usuario para su página de perfil.
        Endpoint: /usuarios/{id}/estadisticas-perfil/
        """
        from Tickets.models import Ticket
        from EvolucionNexus.models import EvolucionNexus
        from django.utils import timezone

        try:
            usuario = Usuarios.objects.get(pk=pk)
        except Usuarios.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # Estadísticas de Tickets
        tickets_reportados = Ticket.objects.filter(reportante_id=pk).count()
        tickets_asignados = Ticket.objects.filter(tecnico_asignado_id=pk).count()
        tickets_abiertos = Ticket.objects.filter(
            reportante_id=pk,
            estado_ciclo__in=['abierto', 'proceso', 'espera']
        ).count()
        tickets_cerrados = Ticket.objects.filter(
            reportante_id=pk,
            estado_ciclo='cerrado'
        ).count()

        # Últimos 5 tickets reportados
        ultimos_tickets = Ticket.objects.filter(reportante_id=pk).select_related('maquina').order_by('-creado_en')[:5]
        tickets_recientes = [
            {
                'folio': t.folio,
                'categoria': t.get_categoria_display(),
                'estado': t.get_estado_ciclo_display(),
                'prioridad': t.get_prioridad_display(),
                'fecha': t.creado_en,
            }
            for t in ultimos_tickets
        ]

        # Estadísticas de Evolución NEXUS
        evoluciones_reportadas = EvolucionNexus.objects.filter(usuario_id=pk).count()
        evoluciones_pendientes = EvolucionNexus.objects.filter(
            usuario_id=pk,
            estado__in=['NO_REVISADO', 'POR_REVISAR', 'ANALIZANDO']
        ).count()

        # Métricas de cuenta
        dias_en_sistema = None
        if usuario.creado_en:
            dias_en_sistema = (timezone.now() - usuario.creado_en).days

        return Response({
            'tickets': {
                'reportados': tickets_reportados,
                'asignados': tickets_asignados,
                'abiertos': tickets_abiertos,
                'cerrados': tickets_cerrados,
                'recientes': tickets_recientes,
            },
            'evoluciones': {
                'total': evoluciones_reportadas,
                'pendientes': evoluciones_pendientes,
            },
            'cuenta': {
                'fecha_registro': usuario.creado_en,
                'ultimo_acceso': usuario.last_login,
                'dias_en_sistema': dias_en_sistema,
                'ultima_ip': usuario.ultima_ip,
                'intentos_fallidos': usuario.intentos_fallidos,
                'requiere_cambio_password': usuario.requiere_cambio_password,
            }
        })

    @action(detail=False, methods=['get'], url_path='global-search')
    def global_search(self, request):
        """
        Búsqueda global (Spotlight) para el sistema.
        Busca en múltiples modelos basado en el término 'q'.
        
        NUEVO: Recibe parámetro 'types' (separado por comas) para filtrar qué buscar.
        La seguridad y permisos (RBAC) se delegan al Frontend, el Backend busca lo que se le pide.
        """
        from django.db.models import Q
        
        # Importación de Modelos
        from Maquinas.models import Maquina
        from Tickets.models import Ticket
        from Proveedores.models import Proveedor
        from ModelosMaquinas.models import ModeloMaquina
        from InventarioSala.models import InventarioSala
        from EvolucionNexus.models import EvolucionNexus
        from Casinos.models import Casino
        from AuditoriasExternas.models import AuditoriaServicioExterno
        from IncidenciasInfraestructura.models import IncidenciaInfraestructura
        from TareasEspeciales.models import TareaEspecial
        from Wiki.models import WikiTecnica

        query = request.query_params.get('q', '').strip()
        requested_types = request.query_params.get('types', '').split(',')
        requested_types = [t.strip() for t in requested_types if t.strip()]

        # Validación mínima
        if not query or len(query) < 2:
            return Response([])

        results = []

        # ==============================================================================
        # CONFIGURACIÓN DE BÚSQUEDA
        # ==============================================================================
        SEARCH_CONFIG = [
            {
                'type': 'user',
                'model': Usuarios,
                'fields': ['username', 'nombres', 'apellido_paterno', 'apellido_materno'],
                'icon': 'pi pi-user',
                'label_fn': lambda x: f"{x.nombres} {x.apellido_paterno} {x.apellido_materno or ''}",
                'sublabel_fn': lambda x: f"Usuario: {x.username} - {x.rol.nombre}",
                'route_fn': lambda x: f"/admin/usuarios?search={x.username}"
            },
            {
                'type': 'machine',
                'model': Maquina,
                'fields': ['uid_sala', 'numero_serie'],
                'icon': 'pi pi-cog',
                'label_fn': lambda x: f"{x.uid_sala} - {x.modelo.nombre_modelo}",
                'sublabel_fn': lambda x: f"Serie: {x.numero_serie} - {x.casino.nombre}",
                'route_fn': lambda x: f"/centro-servicios/maquinas"
            },
            {
                'type': 'ticket',
                'model': Ticket,
                'fields': ['folio', 'id'],
                'icon': 'pi pi-ticket',
                'label_fn': lambda x: f"{x.folio}",
                'sublabel_fn': lambda x: f"{x.get_categoria_display()} - {x.maquina.uid_sala if x.maquina else 'Sin Máquina'}",
                'route_fn': lambda x: f"/centro-servicios/tickets"
            },
            {
                'type': 'supplier',
                'model': Proveedor,
                'fields': ['nombre', 'rfc', 'nombre_contacto_tecnico'],
                'icon': 'pi pi-truck',
                'label_fn': lambda x: f"{x.nombre}",
                'sublabel_fn': lambda x: f"RFC: {x.rfc} - Contacto: {x.nombre_contacto_tecnico or 'N/A'}",
                'route_fn': lambda x: f"/centro-servicios/proveedores"
            },
            {
                'type': 'model',
                'model': ModeloMaquina,
                'fields': ['nombre_modelo', 'nombre_producto'],
                'icon': 'pi pi-list',
                'label_fn': lambda x: f"{x.nombre_modelo}",
                'sublabel_fn': lambda x: f"Producto: {x.nombre_producto} - Prov: {x.proveedor.nombre}",
                'route_fn': lambda x: f"/centro-servicios/modelos"
            },
            {
                'type': 'inventory',
                'model': InventarioSala,
                'fields': ['nombre'],
                'icon': 'pi pi-box',
                'label_fn': lambda x: f"{x.nombre}",
                'sublabel_fn': lambda x: f"Tipo: {x.get_tipo_display()} - Cantidad: {x.cantidad}",
                'route_fn': lambda x: f"/centro-servicios/inventario"
            },
            {
                'type': 'evolution',
                'model': EvolucionNexus,
                'fields': ['titulo', 'descripcion'],
                'icon': 'pi pi-bolt',
                'label_fn': lambda x: f"{x.titulo}",
                'sublabel_fn': lambda x: f"Evolución: {x.get_categoria_display()} - {x.get_estado_display()}",
                'route_fn': lambda x: f"/evolucion-nexus"
            },
            {
                'type': 'casino',
                'model': Casino,
                'fields': ['nombre', 'identificador', 'ciudad'],
                'icon': 'pi pi-building',
                'label_fn': lambda x: f"{x.nombre}",
                'sublabel_fn': lambda x: f"{x.ciudad} - ID: {x.identificador or 'N/A'}",
                'route_fn': lambda x: f"/admin/casinos"
            },
            # --- NUEVOS MODELOS AGREAGADOS ---
            {
                'type': 'audit',
                'model': AuditoriaServicioExterno,
                'fields': ['empresa_proveedora__nombre', 'nombre_tecnico_externo', 'descripcion_actividad'],
                'icon': 'pi pi-file-check',
                'label_fn': lambda x: f"Auditoria: {x.empresa_proveedora.nombre}",
                'sublabel_fn': lambda x: f"Técnico: {x.nombre_tecnico_externo} - {x.get_area_acceso_display()}",
                'route_fn': lambda x: f"/operatividad/auditorias-externas"
            },
            {
                'type': 'infra',
                'model': IncidenciaInfraestructura,
                'fields': ['titulo', 'descripcion', 'categoria'],
                'icon': 'pi pi-exclamation-triangle',
                'label_fn': lambda x: f"Infra: {x.titulo}",
                'sublabel_fn': lambda x: f"{x.get_categoria_display()} - {x.casino.nombre}",
                'route_fn': lambda x: f"/operatividad/incidencias-infraestructura"
            },
            {
                'type': 'task',
                'model': TareaEspecial,
                'fields': ['titulo', 'descripcion'],
                'icon': 'pi pi-check-square',
                'label_fn': lambda x: f"Tarea: {x.titulo}",
                'sublabel_fn': lambda x: f"{x.get_prioridad_display()} - {x.get_estatus_display()}",
                'route_fn': lambda x: f"/operatividad/tareas-especiales"
            },
            {
                'type': 'wiki',
                'model': WikiTecnica,
                'fields': ['titulo_guia', 'categoria'],
                'icon': 'pi pi-book',
                'label_fn': lambda x: f"Wiki: {x.titulo_guia}",
                'sublabel_fn': lambda x: f"Categoría: {x.get_categoria_display()}",
                'route_fn': lambda x: f"/centro-servicios/wiki"
            }
        ]

        # ==============================================================================
        # MOTOR DE BÚSQUEDA
        # ==============================================================================
        
        for config in SEARCH_CONFIG:
            # 1. Filtrado frontend: Si se especificaron 'types' y este no está, saltar.
            # Si 'types' viene vacío, buscamos en TODO (comportamiento default permisivo o restrictivo según se desee, aqui permisivo).
            if requested_types and config['type'] not in requested_types:
                continue

            # 2. Construir Query
            q_objects = Q()
            for field in config['fields']:
                q_objects |= Q(**{f"{field}__icontains": query})

            # 3. Ejecutar Consulta
            try:
                queryset = config['model'].objects.filter(q_objects)
                
                # Optimizaciones select_related
                if config['type'] == 'user':
                    queryset = queryset.select_related('rol')
                elif config['type'] == 'machine':
                    queryset = queryset.select_related('modelo', 'casino')
                elif config['type'] == 'ticket':
                    queryset = queryset.select_related('maquina')
                elif config['type'] == 'supplier':
                    queryset = queryset.select_related('casino')
                elif config['type'] == 'model':
                    queryset = queryset.select_related('proveedor')
                elif config['type'] == 'audit':
                    queryset = queryset.select_related('empresa_proveedora')
                elif config['type'] == 'infra':
                    queryset = queryset.select_related('casino')
                elif config['type'] == 'wiki':
                    pass # Wiki no tiene relaciones complejas urgentes para listado
                
                queryset = queryset[:5] # Limite para no saturar

                for item in queryset:
                    results.append({
                        'type': config['type'],
                        'label': config['label_fn'](item),
                        'sublabel': config['sublabel_fn'](item),
                        'icon': config['icon'],
                        'route': config['route_fn'](item)
                    })
            except Exception as e:
                print(f"Error buscando en {config['type']}: {str(e)}")
                continue

        return Response(results)

    def destroy(self, request, *args, **kwargs):
        """Implementa borrado lógico e invalida tokens de sesión."""
        instance = self.get_object()
        instance.esta_activo = False
        instance.session_token = None
        instance.refresh_token = None
        instance.modificado_por = self.request.user.username if self.request.user.is_authenticated else 'system'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
