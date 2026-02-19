from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IncidenciaInfraestructuraViewSet

router = DefaultRouter()
router.register(r'infra-incidencias', IncidenciaInfraestructuraViewSet, basename='infra-incidencias')

urlpatterns = [
    path('', include(router.urls)),
]