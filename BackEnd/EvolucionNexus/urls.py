from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EvolucionNexusViewSet

router = DefaultRouter()
router.register(r'evolucion-nexus', EvolucionNexusViewSet, basename='evolucion-nexus')

urlpatterns = [
    path('', include(router.urls)),
]
