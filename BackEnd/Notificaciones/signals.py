"""
Sistema de Signals para Generación Automática de Notificaciones
Plataforma: NEXUS - Gestión de Casinos

Optimización 2026: Polling REST cada 45s, sin WebSockets
Reglas de Notificación:
- Alerta de Infraestructura CRÍTICA → gerente, supervisor_sala, supervisor_sistemas
- Ticket Cerrado/Operativo → Usuario reportante
- Mensajes de roles admin/administrador → Tipo DIRECTOR (7 días)

Restricciones de Ruido:
PROHIBIDO: Notificaciones por creación de máquinas, relevos normales, 
mantenimientos preventivos o altas de usuarios.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Q


def crear_notificacion_system(titulo, contenido, nivel, tipo, **kwargs):
    """
    Función auxiliar para crear notificaciones con auditoría SYSTEM.
    
    Args:
        titulo: Título de la notificación
        contenido: Contenido detallado
        nivel: 'urgente', 'alerta' o 'informativa'
        tipo: 'ticket', 'infraestructura', 'wiki', 'sistema', 'DIRECTOR'
        **kwargs: Campos adicionales (usuario_destino, casino_destino, rol_destino, es_global)
    """
    from .models import Notificacion
    
    # Detectar si el creador es admin o administrador para marcar como DIRECTOR
    creador = kwargs.get('creado_por', 'SYSTEM')
    if creador != 'SYSTEM':
        # Si es una notificación creada por admin/administrador
        from Usuarios.models import Usuarios
        try:
            usuario = Usuarios.objects.get(username=creador)
            if usuario.rol.nombre.lower() in ['admin', 'administrador', 'de_admin']:
                tipo = 'DIRECTOR'
        except:
            pass
    
    return Notificacion.objects.create(
        titulo=titulo,
        contenido=contenido,
        nivel=nivel,
        tipo=tipo,
        creado_por='SYSTEM',
        modificado_por='SYSTEM',
        **kwargs
    )


# ============================================================================
# TRIGGER 1: INCIDENCIA DE INFRAESTRUCTURA CRÍTICA
# ============================================================================

@receiver(post_save, sender='IncidenciasInfraestructura.IncidenciaInfraestructura')
def notificar_incidencia_critica(sender, instance, created, **kwargs):
    """
    Solo si severidad es 'critica', notificar a:
    - gerente
    - supervisor_sala
    - supervisor_sistemas
    del casino afectado.
    """
    from Usuarios.models import Usuarios
    
    # Solo al crear
    if not created:
        return
    
    # Solo severidad CRÍTICA
    if instance.severidad != 'critica':
        return
    
    # Obtener roles específicos del casino afectado
    roles_criticos = ['gerente', 'supervisor_sala', 'supervisor_sistemas']
    
    # Notificar por casino y rol (usando el nuevo filtro optimizado)
    from Roles.models import Rol
    for rol_nombre in roles_criticos:
        try:
            rol = Rol.objects.get(nombre__iexact=rol_nombre)
            crear_notificacion_system(
                titulo=f"🚨 ALERTA CRÍTICA: Incidencia de Infraestructura",
                contenido=f"{instance.titulo}\\n\\n"
                          f"Casino: {instance.casino.nombre}\\n"
                          f"Categoría: {instance.get_categoria_display()}\\n"
                          f"Afecta operación: {'SÍ - CIERRE DE ÁREA' if instance.afecta_operacion else 'No'}\\n\\n"
                          f"Descripción: {instance.descripcion[:300]}\\n\\n"
                          f"⚠️ Requiere atención inmediata.",
                nivel='urgente',
                tipo='infraestructura',
                casino_destino=instance.casino,
                rol_destino=rol
            )
        except Rol.DoesNotExist:
            pass  # Si el rol no existe, continuar con el siguiente


# ============================================================================
# TRIGGER 2: TICKET CERRADO/OPERATIVO
# ============================================================================

# Variable para rastrear estados previos de tickets
_ticket_estados_previos = {}

@receiver(pre_save, sender='Tickets.Ticket')
def guardar_estado_previo_ticket(sender, instance, **kwargs):
    """
    Guardar el estado previo del ticket antes de guardar.
    """
    if instance.pk:
        try:
            ticket_anterior = sender.objects.get(pk=instance.pk)
            _ticket_estados_previos[instance.pk] = ticket_anterior.estado_ciclo
        except sender.DoesNotExist:
            pass

@receiver(post_save, sender='Tickets.Ticket')
def notificar_ticket_resuelto(sender, instance, created, **kwargs):
    """
    Cuando un Ticket cambia su estado a 'cerrado', notificar al reportante.
    """
    # No notificar en creación
    if created:
        return
    
    # Verificar si el estado cambió a 'cerrado'
    estado_previo = _ticket_estados_previos.get(instance.pk)
    if estado_previo != 'cerrado' and instance.estado_ciclo == 'cerrado':
        # Notificar al reportante
        crear_notificacion_system(
            titulo=f"✅ Ticket Resuelto: {instance.folio}",
            contenido=f"Tu ticket ha sido cerrado exitosamente.\\n\\n"
                      f"Máquina: {instance.maquina}\\n"
                      f"Casino: {instance.maquina.casino.nombre}\\n"
                      f"Categoría: {instance.get_categoria_display()}\\n"
                      f"Técnico asignado: {instance.tecnico_asignado or 'No asignado'}\\n\\n"
                      f"Explicación de cierre:\\n{instance.explicacion_cierre or 'Sin observaciones'}\\n\\n"
                      f"Gracias por tu reporte.",
            nivel='informativa',
            tipo='ticket',
            usuario_destino=instance.reportante
        )
        
        # Limpiar el estado previo
        if instance.pk in _ticket_estados_previos:
            del _ticket_estados_previos[instance.pk]


# ============================================================================
# TRIGGER 3: WIKI TÉCNICA (Mantener funcionalidad existente)
# ============================================================================

@receiver(post_save, sender='Wiki.WikiTecnica')
def notificar_publicacion_wiki(sender, instance, created, **kwargs):
    """
    Al publicarse una guía, notificar de forma global.
    Reducción de ruido: Solo una notificación global por rol técnico.
    """
    # Solo al crear/publicar la guía
    if not created:
        return
    
    # Notificación global para roles técnicos de todos los casinos
    from Roles.models import Rol
    try:
        rol_tecnico = Rol.objects.get(nombre__iexact='tecnico')
        crear_notificacion_system(
            titulo="📚 Nueva Guía Técnica Disponible",
            contenido=f"{instance.titulo_guia}\\n\\n"
                      f"Autor: {instance.autor.nombres} {instance.autor.apellido_paterno}\\n"
                      f"Modelo: {instance.modelo_relacionado}\\n"
                      f"Categoría: {instance.get_categoria_display()}\\n\\n"
                      f"¡Consulta la Wiki para más detalles!",
            nivel='informativa',
            tipo='wiki',
            es_global=True  # Visible para todos los técnicos
        )
    except Rol.DoesNotExist:
        pass
    
    # Notificación personal al autor (tipo DIRECTOR para durar 7 días)
    crear_notificacion_system(
        titulo="🎉 ¡Tu guía ha sido publicada!",
        contenido=f"¡Felicidades {instance.autor.nombres}!\\n\\n"
                  f"Tu guía '{instance.titulo_guia}' ha sido publicada exitosamente en la Wiki.\\n\\n"
                  f"Gracias por compartir tu conocimiento con el equipo.\\n"
                  f"¡Sigue compartiendo tu experiencia!",
        nivel='informativa',
        tipo='DIRECTOR',  # 7 días de duración
        usuario_destino=instance.autor
    )


# ============================================================================
# NOTIFICACIONES OPCIONALES (Agregar según necesidad)
# ============================================================================

@receiver(post_save, sender='TareasEspeciales.TareaEspecial')
def notificar_tarea_especial_critica(sender, instance, created, **kwargs):
    """
    Solo notificar tareas especiales con prioridad 'critica' o 'emergencia'.
    Reducción de ruido: No todas las tareas generan notificaciones.
    """
    # Solo al crear
    if not created:
        return
    
    # Solo prioridades críticas
    if instance.prioridad not in ['critica', 'emergencia']:
        return
    
    # Notificar al casino específico, roles supervisores
    from Roles.models import Rol
    for rol_nombre in ['gerente', 'supervisor_sala', 'supervisor_sistemas']:
        try:
            rol = Rol.objects.get(nombre__iexact=rol_nombre)
            crear_notificacion_system(
                titulo=f"⚡ Tarea Especial URGENTE",
                contenido=f"{instance.titulo}\\n\\n"
                          f"Casino: {instance.casino.nombre}\\n"
                          f"Prioridad: {instance.get_prioridad_display()}\\n"
                          f"Fecha límite: {instance.fecha_limite}\\n\\n"
                          f"Descripción: {instance.descripcion[:300]}",
                nivel='urgente',
                tipo='sistema',
                casino_destino=instance.casino,
                rol_destino=rol
            )
        except Rol.DoesNotExist:
            pass


# ============================================================================
# REGISTRO DE SIGNALS DESHABILITADOS (Para evitar ruido)
# ============================================================================

# ❌ NO SE NOTIFICA: Creación de máquinas
# ❌ NO SE NOTIFICA: Relevos de turno normales
# ❌ NO SE NOTIFICA: Mantenimientos preventivos
# ❌ NO SE NOTIFICA: Altas de usuarios
# ❌ NO SE NOTIFICA: Tickets en creación (solo en cierre)
