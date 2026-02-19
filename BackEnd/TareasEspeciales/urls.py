from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TareaEspecialViewSet

router = DefaultRouter()
router.register(r'tareas', TareaEspecialViewSet, basename='tareas')

urlpatterns = [
    path('', include(router.urls)),
]