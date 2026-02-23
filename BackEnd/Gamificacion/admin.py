from django.contrib import admin
from .models import RecompensaGamificacion, CanjeRecompensa


@admin.register(RecompensaGamificacion)
class RecompensaGamificacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'costo_puntos', 'casino', 'activo', 'stock', 'creado_en']
    list_filter = ['activo', 'casino']
    search_fields = ['titulo', 'descripcion']
    list_editable = ['activo']


@admin.register(CanjeRecompensa)
class CanjeRecompensaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'recompensa', 'puntos_descontados', 'estado', 'creado_en']
    list_filter = ['estado', 'recompensa__casino']
    search_fields = ['usuario__username', 'recompensa__titulo']
    readonly_fields = ['usuario', 'recompensa', 'puntos_descontados', 'creado_en']
