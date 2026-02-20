from django.urls import path
from .views import MenuActivoView, MenuConfigView

urlpatterns = [
    path('menus/activo/', MenuActivoView.as_view(), name='menu-activo'),
    path('menus/', MenuConfigView.as_view(), name='menu-config'),
]
