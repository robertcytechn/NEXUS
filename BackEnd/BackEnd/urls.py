from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('Roles.urls')),
    path('api/', include('Casinos.urls')),
    path('api/', include('Usuarios.urls')),
    path('api/', include('Proveedores.urls')),
    path('api/', include('ModelosMaquinas.urls')),
    path('api/', include('Denominaciones.urls')),
    path('api/', include('Maquinas.urls')),
    path('api/', include('Tickets.urls')),
    path('api/', include('BitacoraTecnica.urls')),
    path('api/', include('MantenimientosPreventivos.urls')),
    path('api/', include('TareasEspeciales.urls')),
    path('api/', include('InventarioSala.urls')),
    path('api/', include('IncidenciasInfraestructura.urls')),
    path('api/', include('RelevosTurnos.urls')),
    path('api/', include('Wiki.urls')),
    path('api/', include('AuditoriasExternas.urls')),
    path('api/', include('Notificaciones.urls')),
    path('api/', include('EvolucionNexus.urls')),
    path('api/', include('Menus.urls')),
    path('api/', include('AuditoriaGlobal.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
