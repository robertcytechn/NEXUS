from django.contrib import admin
from .models import Notificacion, NotificacionUsuario


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'nivel', 'es_global', 'usuario_destino', 'casino_destino', 'rol_destino', 'creado_en', 'esta_activo']
    list_filter = ['tipo', 'nivel', 'es_global', 'es_del_director', 'esta_activo', 'creado_en']
    search_fields = ['titulo', 'contenido']
    readonly_fields = ['creado_en', 'modificado_en', 'creado_por', 'modificado_por']
    
    fieldsets = (
        ('Información de la Notificación', {
            'fields': ('titulo', 'contenido', 'tipo', 'nivel')
        }),
        ('Segmentación', {
            'fields': ('es_global', 'es_del_director', 'usuario_destino', 'casino_destino', 'rol_destino')
        }),
        ('Estado', {
            'fields': ('esta_activo',)
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'modificado_en', 'creado_por', 'modificado_por', 'notas_internas'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificacionUsuario)
class NotificacionUsuarioAdmin(admin.ModelAdmin):
    list_display = ['notificacion', 'usuario', 'fecha_visto', 'creado_en']
    list_filter = ['fecha_visto', 'creado_en']
    search_fields = ['notificacion__titulo', 'usuario__username', 'usuario__nombres', 'usuario__apellido_paterno']
    readonly_fields = ['fecha_visto', 'creado_en', 'modificado_en', 'creado_por', 'modificado_por']
    
    fieldsets = (
        ('Lectura de Notificación', {
            'fields': ('notificacion', 'usuario', 'fecha_visto')
        }),
        ('Auditoría', {
            'fields': ('esta_activo', 'creado_en', 'modificado_en', 'creado_por', 'modificado_por', 'notas_internas'),
            'classes': ('collapse',)
        }),
    )
