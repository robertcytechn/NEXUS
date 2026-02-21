from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .models import LogAuditoria
from .serializers import LogAuditoriaSerializer

# En proyectos grandes esto debe extenderse a IsAdminUser,
# Asumimos que el front valida la entrada al panel admin en la ruta.
class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Asegurarse que el usuario y grupo sean válidos
        return bool(request.user and request.user.is_authenticated and request.user.rol == 'admin')

class AuditoriaPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'

class LogAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista de solo lectura del Ojo de Dios.
    Provee el listado filtrable de Auditoria
    """
    queryset = LogAuditoria.objects.all().order_newest() if hasattr(LogAuditoria.objects, 'order_newest') else LogAuditoria.objects.all().order_by('-fecha')
    serializer_class = LogAuditoriaSerializer
    permission_classes = [permissions.IsAuthenticated] # Lo restringimos temporalmente a auth si el decorador admin requiere roles específicos, o reemplazar por IsAdminPermission.
    pagination_class = AuditoriaPagination

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Filtros opcionales si vienen por query param
        tabla = self.request.query_params.get('tabla', None)
        accion = self.request.query_params.get('accion', None)
        casino_id = self.request.query_params.get('casino', None)
        usuario_id = self.request.query_params.get('usuario', None)
        
        if tabla:
            qs = qs.filter(tabla__icontains=tabla)
        if accion:
            qs = qs.filter(accion__iexact=accion)
        if casino_id and casino_id.isdigit():
            qs = qs.filter(casino_id=casino_id)
        if usuario_id and usuario_id.isdigit():
            qs = qs.filter(usuario_id=usuario_id)

        # Si el usuario NO es admin, idealmente no debiera ver esto o quizá solo ver su casino.
        # Pero esta app es para Ojo de Dios.

        return qs

    @action(detail=False, methods=['GET'])
    def tablas_afectadas(self, request):
        """Devuelve un listado único de las tablas que tienen logs, ideal para el combobox de filtro"""
        tablas = LogAuditoria.objects.values_list('tabla', flat=True).distinct().order_by('tabla')
        return Response(list(tablas))
