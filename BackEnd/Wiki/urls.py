from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WikiTecnicaViewSet

router = DefaultRouter()
router.register(r'wiki', WikiTecnicaViewSet, basename='wiki')

urlpatterns = [
    path('', include(router.urls)),
]