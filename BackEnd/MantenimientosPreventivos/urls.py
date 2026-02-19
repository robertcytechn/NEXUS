from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MantenimientoPreventivoViewSet

router = DefaultRouter()
router.register(r'mantenimientos-preventivos', MantenimientoPreventivoViewSet, basename='mantenimientos-preventivos')

urlpatterns = [
    path('', include(router.urls)),
]