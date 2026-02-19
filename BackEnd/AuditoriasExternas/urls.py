from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditoriaServicioExternoViewSet

router = DefaultRouter()
router.register(r'auditorias-externas', AuditoriaServicioExternoViewSet, basename='auditoria-servicio-externo')

urlpatterns = [
    path('', include(router.urls)),
]