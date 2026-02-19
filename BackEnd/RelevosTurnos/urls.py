from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RelevoTurnoViewSet

router = DefaultRouter()
router.register(r'relevos-turnos', RelevoTurnoViewSet, basename='relevos-turnos')

urlpatterns = [
    path('', include(router.urls)),
]