# Manual del Desarrollador — Sistema de Notificaciones (Django Signals)

> **Versión**: 2.0 — Sistema reactivo con Django Signals  
> **Fecha**: Febrero 2026  

---

## ¿Cómo funciona el sistema?

Las notificaciones se generan **exclusivamente desde el backend** usando
[Django Signals](https://docs.djangoproject.com/en/5.x/topics/signals/).
El frontend solo **lee y marca como leídas** las notificaciones; nunca las crea.

### Flujo completo

```
Acción del usuario (ej. guarda un Ticket)
        │
        ▼
Django ORM dispara: pre_save → post_save
        │
        ▼
signals.py correspondiente evalúa el evento
        │
        ├── ¿Es un evento que merece notificación?
        │       SÍ → Notificacion.objects.create(...)
        │       NO → No hace nada
        │
        ▼
Frontend hace polling cada 45s → GET /api/notificaciones/count-no-leidas/
        │
        ▼
Usuario ve la campana con el contador y abre las notificaciones
```

---

## Modelo de datos

### `Notificacion` (tabla: `sys_notificaciones`)

| Campo             | Tipo          | Descripción |
|-------------------|---------------|-------------|
| `titulo`          | CharField     | Encabezado corto (máx 150 chars) |
| `contenido`       | TextField     | Cuerpo completo del mensaje |
| `nivel`           | CharField     | `'urgente'`, `'alerta'`, `'informativa'` |
| `tipo`            | CharField     | `'ticket'`, `'infraestructura'`, `'wiki'`, `'sistema'`, `'DIRECTOR'` |
| `usuario_destino` | FK → Usuarios | Solo este usuario la verá (notificación personal) |
| `casino_destino`  | FK → Casino   | Todos los del casino la ven (combinable con rol_destino) |
| `rol_destino`     | FK → Rol      | Filtra por rol dentro del casino_destino |
| `es_global`       | BooleanField  | `True` → Todos los usuarios del sistema la ven |
| `es_del_director` | BooleanField  | `True` → Dura 7 días (en vez de 48 h) |

### Reglas de segmentación (resumen rápido)

| Quieres notificar a... | Configuración |
|------------------------|---------------|
| **Un usuario específico** | `usuario_destino=instancia_usuario` |
| **Todo un casino** | `casino_destino=instancia_casino` |
| **Un rol en un casino** | `casino_destino=casino`, `rol_destino=rol` |
| **Todos en el sistema** | `es_global=True` |

---

## Archivos de signals existentes

| Módulo | Archivo | Eventos cubiertos |
|--------|---------|-------------------|
| Tickets | `BackEnd/Tickets/signals.py` | Creación, cierre, reapertura, asignación |
| Tareas Especiales | `BackEnd/TareasEspeciales/signals.py` | Creación, completada, cancelada, asignación |
| Incidencias Infraestructura | `BackEnd/IncidenciasInfraestructura/signals.py` | Creación (con nivel según severidad), resolución |
| Wiki Técnica | `BackEnd/Wiki/signals.py` | Nueva guía publicada |
| Usuarios | `BackEnd/Usuarios/signals.py` | Nuevo usuario dado de alta |

---

## Cómo crear un nuevo signal (paso a paso)

### Paso 1 — Localiza o crea `signals.py`

Cada app Django tiene su propio `signals.py`. Si no existe, créalo dentro de la carpeta del módulo:

```
BackEnd/
  MiModulo/
    __init__.py
    apps.py
    models.py
    signals.py   ← aquí
```

### Paso 2 — Conecta el signal en `apps.py`

Django no carga los signals automáticamente. Debes inicializarlos en el método `ready()`:

```python
# BackEnd/MiModulo/apps.py
from django.apps import AppConfig

class MimoduloConfig(AppConfig):
    name = 'MiModulo'

    def ready(self):
        import MiModulo.signals  # noqa: F401  ← LÍNEA CLAVE
```

### Paso 3 — Escribe el signal

#### Plantilla para evento de CREACIÓN

```python
# BackEnd/MiModulo/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MiModelo
from Notificaciones.models import Notificacion
from Roles.models import Rol

@receiver(post_save, sender=MiModelo)
def mi_modelo_post_save(sender, instance, created, **kwargs):
    if not created:
        return  # Solo al crear

    # Notificación personal
    Notificacion.objects.create(
        titulo          = "¡Algo nuevo!",
        contenido       = f"Descripción del evento para {instance}.",
        nivel           = 'alerta',         # urgente | alerta | informativa
        tipo            = 'sistema',        # ticket | infraestructura | wiki | sistema | DIRECTOR
        usuario_destino = instance.usuario_responsable,
    )
```

#### Plantilla para detectar CAMBIO DE ESTADO

```python
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import MiModelo
from Notificaciones.models import Notificacion
from Roles.models import Rol

# 1. Guarda el estado anterior ANTES de guardar
@receiver(pre_save, sender=MiModelo)
def mi_modelo_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            prev = MiModelo.objects.get(pk=instance.pk)
            instance._prev_estado = prev.estado  # ← campo que quieres monitorear
        except MiModelo.DoesNotExist:
            instance._prev_estado = None
    else:
        instance._prev_estado = None

# 2. Evalúa la transición DESPUÉS de guardar
@receiver(post_save, sender=MiModelo)
def mi_modelo_post_save(sender, instance, created, **kwargs):
    if created:
        return  # Este bloque solo maneja cambios, no creaciones

    prev_estado = getattr(instance, '_prev_estado', None)

    if instance.estado == 'completado' and prev_estado != 'completado':
        Notificacion.objects.create(
            titulo          = "✅ Proceso completado",
            contenido       = f"El registro {instance} fue completado.",
            nivel           = 'informativa',
            tipo            = 'sistema',
            usuario_destino = instance.creado_por,
        )
```

#### Plantilla para notificar a un ROL en un CASINO

```python
def notificar_rol_casino(titulo, contenido, nivel, tipo, casino, nombres_rol):
    """
    Helper reutilizable: crea una notificación por cada rol en la lista,
    segmentada al casino indicado.
    """
    roles = Rol.objects.filter(nombre__in=nombres_rol)
    for rol in roles:
        Notificacion.objects.create(
            titulo        = titulo,
            contenido     = contenido,
            nivel         = nivel,
            tipo          = tipo,
            casino_destino= casino,
            rol_destino   = rol,
        )

# Uso:
notificar_rol_casino(
    titulo      = "Aviso importante",
    contenido   = "Descripción detallada...",
    nivel       = 'alerta',
    tipo        = 'sistema',
    casino      = instance.casino,
    nombres_rol = ['TECNICO', 'SUP SISTEMAS'],
)
```

---

## Nombres de roles disponibles en el sistema

| Nombre exacto en BD | Descripción |
|---------------------|-------------|
| `'TECNICO'` | Técnico de sala |
| `'SUP SISTEMAS'` | Supervisor de Sistemas |
| `'SUPERVISOR SALA'` | Supervisor de Sala |
| `'GERENCIA'` | Gerencia del casino |
| `'ADMINISTRADOR'` | Administrador del sistema |
| `'DB ADMIN'` | Administrador de base de datos |
| `'ENCARGADO AREA'` | Encargado de área |

> **Importante:** Usa exactamente estos nombres con `Rol.objects.filter(nombre__in=[...])`.
> Si el rol no existe en la BD, simplemente no se creará la notificación (no rompe nada).

---

## Niveles y cuándo usar cada uno

| Nivel | Cuándo usarlo | Color en UI |
|-------|--------------|-------------|
| `'urgente'` | Requiere acción **inmediata**: incidencia crítica, operación afectada | 🔴 Rojo |
| `'alerta'` | Requiere atención pronto: nuevo ticket, nueva tarea | 🟡 Naranja |
| `'informativa'` | Solo para conocimiento: cierre, registro nuevo, wiki | 🔵 Azul |

---

## Regla de Oro — Anti-Spam

> ❌ **NUNCA** crear notificaciones para acciones masivas o implícitas.

Ejemplos **prohibidos**:
- Creación, edición o eliminación de `Maquinas`
- Cambio de estado de múltiples registros en un bulk update
- Mantenimientos preventivos (ya hay señal de actualización en el modelo)
- Login / logout de usuarios

Ejemplos **permitidos**:
- Apertura de un nuevo Ticket
- Cierre o resolución de un Ticket
- Nueva Tarea Especial asignada
- Tarea completada o cancelada
- Nueva guía publicada en la Wiki
- Incidencia crítica de infraestructura
- Alta de un usuario nuevo

---

## Cómo eliminar un signal

1. Abre el `signals.py` del módulo correspondiente.
2. Elimina (o comenta) el decorador `@receiver(...)` y la función.
3. Si eliminas **todos** los signals de un módulo, también puedes remover
   `import MiModulo.signals` de `apps.py`, aunque dejarlo no causa errores.

---

## Cómo verificar que los signals están funcionando

Desde la terminal del backend, ejecuta el shell de Django y simula un guardado:

```bash
cd BackEnd
python manage.py shell
```

```python
from Tickets.models import Ticket
from Notificaciones.models import Notificacion

count_antes = Notificacion.objects.count()
print(f"Notificaciones antes: {count_antes}")

# Modifica el estado de un ticket existente para disparar el signal
t = Ticket.objects.first()
t.estado_ciclo = 'cerrado'
t.save()

count_despues = Notificacion.objects.count()
print(f"Notificaciones después: {count_despues}")
print(f"Nuevas notificaciones creadas: {count_despues - count_antes}")
```

---

*Fin del manual. Cualquier duda, revisar los archivos `signals.py` de cada módulo como referencia.*
