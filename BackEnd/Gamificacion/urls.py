from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecompensaGerenciaViewSet, RecompensaTecnicoViewSet

router = DefaultRouter()

# Panel de Gerencia — CRUD de recompensas + gestión de canjes
router.register(r'gamificacion/tienda', RecompensaGerenciaViewSet, basename='gamificacion-tienda')

# Tienda pública — técnicos consultan y canjean
router.register(r'gamificacion/tienda-tecnico', RecompensaTecnicoViewSet, basename='gamificacion-tecnico')

urlpatterns = [
    path('', include(router.urls)),
]
