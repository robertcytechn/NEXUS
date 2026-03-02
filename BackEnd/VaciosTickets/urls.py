from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConfiguracionCasinoViewSet, TicketVacioViewSet

router = DefaultRouter()
router.register(r'vacios/configuracion', ConfiguracionCasinoViewSet, basename='vacios-configuracion')
router.register(r'vacios/tickets', TicketVacioViewSet, basename='vacios-tickets')

urlpatterns = [
    path('', include(router.urls)),
]
