from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DenominacionViewSet

router = DefaultRouter()
router.register(r'denominaciones', DenominacionViewSet, basename='denominacion')

urlpatterns = [
    path('', include(router.urls)),
]