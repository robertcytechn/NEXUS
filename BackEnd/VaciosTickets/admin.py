from django.contrib import admin
from .models import ConfiguracionCasino, TicketVacio


@admin.register(ConfiguracionCasino)
class ConfiguracionCasinoAdmin(admin.ModelAdmin):
    list_display = ['casino', 'umbral_autorizacion', 'siempre_requiere_autorizacion', 'creado_en']
    list_filter = ['siempre_requiere_autorizacion']
    search_fields = ['casino__nombre']


@admin.register(TicketVacio)
class TicketVacioAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'casino', 'maquina', 'cliente_nombre',
        'monto_extraviado', 'estado_operativo', 'estado_auditoria',
        'tecnico_creador', 'gerente_auditor', 'fecha_creacion',
    ]
    list_filter = ['estado_operativo', 'estado_auditoria', 'motivo_falla', 'casino']
    search_fields = ['cliente_nombre', 'maquina__uid_sala', 'explicacion_detallada']
    readonly_fields = [
        'fecha_creacion', 'fecha_auditoria',
        'creado_en', 'modificado_en', 'creado_por', 'modificado_por',
    ]
    date_hierarchy = 'fecha_creacion'
    ordering = ['-fecha_creacion']
    fieldsets = (
        ('Datos Principales', {
            'fields': ('casino', 'maquina', 'cliente_nombre', 'monto_extraviado')
        }),
        ('Trazabilidad', {
            'fields': ('tecnico_creador', 'gerente_auditor', 'fecha_creacion', 'fecha_auditoria')
        }),
        ('Evidencias', {
            'fields': (
                'foto_ultimas_operaciones', 'foto_carga_sistema',
                'foto_seguimiento_slot', 'foto_recarga_error',
            )
        }),
        ('Dictamen', {
            'fields': ('motivo_falla', 'explicacion_detallada')
        }),
        ('Estados', {
            'fields': ('estado_operativo', 'estado_auditoria')
        }),
        ('Auditoría Interna', {
            'classes': ('collapse',),
            'fields': ('creado_en', 'modificado_en', 'creado_por', 'modificado_por', 'notas_internas')
        }),
    )
