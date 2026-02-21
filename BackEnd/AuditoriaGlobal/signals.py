import json
import logging
from django.db.models.signals import pre_save, post_save, post_delete
from django.core.serializers.json import DjangoJSONEncoder
from django.dispatch import receiver
from .models import LogAuditoria
import threading

logger = logging.getLogger(__name__)

# Referencia al middleware local
from .middleware import _thread_locals

# Tupla de modelos a ignorar (típicamente tokens, log, django sessions)
IGNORE_MODELS = [
    'LogAuditoria', 'Session', 'LogEntry', 'ContentType', 'Permission', 'Group'
]

def obtener_usuario_casino():
    user = getattr(_thread_locals, 'user', None)
    casino = getattr(_thread_locals, 'casino', None)
    return user, casino

def model_to_dict(instance):
    """
    Convierte una instancia de modelo a un diccionario serializable JSON.
    """
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields:
        val = f.value_from_object(instance)
        # Convertimos campos especiales a string si es necesario 
        # (Fechas con JSONEncoder, pero para seguridad y rapidez usamos strings crudos donde no se soporte)
        data[f.name] = val
    return data

def serialize_dict(d):
    """
    Convierte un dict a string JSON de forma segura.
    Las fechas, UUIDs y Decimales se manejan con DjangoJSONEncoder.
    """
    if d is None:
        return None
    try:
        return json.dumps(d, cls=DjangoJSONEncoder)
    except TypeError:
        # Fallback si no se puede
        return str(d)

@receiver(pre_save)
def auditoria_pre_save(sender, instance, **kwargs):
    """
    Captura los datos del registro ANTES de que se guarden en DB
    y los almacena temporalmente en la instancia para uso en post_save.
    """
    nombre_tabla = sender.__name__
    if nombre_tabla in IGNORE_MODELS:
        return

    # Evitamos interacciones sin PK (Creaciones nuevas no tienen datos anteriores)
    if not instance.pk:
        instance._old_data_dict = None
        return

    try:
        # Obtenemos el registro viejo desde la DB 
        # (podría generar Queries extras, pero es necesario para la auditoría)
        old_instance = sender.objects.get(pk=instance.pk)
        instance._old_data_dict = model_to_dict(old_instance)
    except sender.DoesNotExist:
        # Si no existe, es una creación forzada o hay error
        instance._old_data_dict = None
    except Exception as e:
        logger.warning(f"Error auditoría pre_save para {nombre_tabla}: {e}")
        instance._old_data_dict = None

@receiver(post_save)
def auditoria_post_save(sender, instance, created, **kwargs):
    """
    Captura la acción (CREAR o ACTUALIZAR), toma los datos nuevos y usa los viejos (si existen).
    Registra el LogAuditoria con Base a lo capturado.
    """
    nombre_tabla = sender.__name__
    if nombre_tabla in IGNORE_MODELS:
        return

    # Determinar acción
    accion = 'CREATE' if created else 'UPDATE'
    user, casino = obtener_usuario_casino()

    # Si no hay usuario y se está creando desde consola admin, se ignora o se marca Anónimo.
    # En proyectos grandes, puedes filtrar para que solo grabe si user no es None
    
    old_data_dict = getattr(instance, '_old_data_dict', None)
    new_data_dict = model_to_dict(instance)

    # Convertir a JSON nativo en vez de strings
    datos_anteriores_json = None
    if old_data_dict:
        # Parsearlo de vuelta porque Django requiere diccionarios para JSONField
        try:
           datos_anteriores_json = json.loads(serialize_dict(old_data_dict))
        except: pass
        
    datos_nuevos_json = None
    if new_data_dict:
        try:
           datos_nuevos_json = json.loads(serialize_dict(new_data_dict))
        except: pass

    # Solo guardar logs si se modifica algo en caso de UPDATE
    if accion == 'UPDATE' and old_data_dict == new_data_dict:
        return # No registrar updates vacios

    try:
        LogAuditoria.objects.create(
            tabla=nombre_tabla,
            registro_id=str(instance.pk),
            accion=accion,
            datos_anteriores=datos_anteriores_json,
            datos_nuevos=datos_nuevos_json,
            usuario=user,
            casino=casino
        )
    except Exception as e:
        logger.error(f"Error guardando auditoria post_save en {nombre_tabla}: {e}")


@receiver(post_delete)
def auditoria_post_delete(sender, instance, **kwargs):
    """
    Registra un borrado en DB.
    Guarda la última foto de la data en `datos_anteriores`.
    """
    nombre_tabla = sender.__name__
    if nombre_tabla in IGNORE_MODELS:
        return

    user, casino = obtener_usuario_casino()
    
    old_data_dict = model_to_dict(instance)
    datos_anteriores_json = None

    if old_data_dict:
        try:
           datos_anteriores_json = json.loads(serialize_dict(old_data_dict))
        except: pass

    try:
        LogAuditoria.objects.create(
            tabla=nombre_tabla,
            registro_id=str(instance.pk),
            accion='DELETE',
            datos_anteriores=datos_anteriores_json,
            datos_nuevos=None,
            usuario=user,
            casino=casino
        )
    except Exception as e:
        logger.error(f"Error guardando auditoria post_delete en {nombre_tabla}: {e}")
