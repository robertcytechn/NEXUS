from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventarioSalaViewSet

router = DefaultRouter()
router.register(r'inventario-sala', InventarioSalaViewSet, basename='inventario-sala')

urlpatterns = [
    path('', include(router.urls)),
]