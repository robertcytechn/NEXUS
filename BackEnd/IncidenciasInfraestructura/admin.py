from django.contrib import admin
from .models import IncidenciaInfraestructura

@admin.register(IncidenciaInfraestructura)
class IncidenciaInfraestructuraAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'casino', 'categoria', 'severidad', 'afecta_operacion', 'hora_inicio', 'esta_activo', 'creado_en']
    list_filter = ['categoria', 'severidad', 'afecta_operacion', 'esta_activo', 'casino']
    search_fields = ['titulo', 'descripcion', 'casino__nombre']
    readonly_fields = ['creado_en', 'modificado_en', 'creado_por', 'modificado_por']
    date_hierarchy = 'creado_en'
    ordering = ['-creado_en']
