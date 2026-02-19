from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModeloMaquinaViewSet

router = DefaultRouter()
router.register(r'modelos', ModeloMaquinaViewSet, basename='modelos')

urlpatterns = [
    path('', include(router.urls)),
]