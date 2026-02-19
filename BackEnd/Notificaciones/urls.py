from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificacionViewSet, NotificacionUsuarioViewSet

router = DefaultRouter()
router.register(r'notificaciones', NotificacionViewSet, basename='notificaciones')
router.register(r'notificaciones-usuarios', NotificacionUsuarioViewSet, basename='notificaciones-usuarios')

urlpatterns = [
    path('', include(router.urls)),
]