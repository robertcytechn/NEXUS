from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WikiCentroMandoViewSet, WikiCentroServiciosViewSet

router = DefaultRouter()

# Centro de Mando — solo administrador puede acceder
router.register(r'wiki/centro-mando', WikiCentroMandoViewSet, basename='wiki-centro-mando')

# Centro de Servicios — todos los técnicos autenticados
router.register(r'wiki/centro-servicios', WikiCentroServiciosViewSet, basename='wiki-centro-servicios')

urlpatterns = [
    path('', include(router.urls)),
]
