from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BitacoraTecnicaViewSet

router = DefaultRouter()
router.register(r'bitacora-tecnica', BitacoraTecnicaViewSet, basename='bitacora-tecnica')

urlpatterns = [
    path('', include(router.urls)),
]