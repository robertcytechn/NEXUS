from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CasinoViewSet

router = DefaultRouter()
router.register(r'casinos', CasinoViewSet, basename='casinos')

urlpatterns = [
    path('', include(router.urls)),
]