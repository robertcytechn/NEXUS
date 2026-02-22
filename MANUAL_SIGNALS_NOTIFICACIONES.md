# Manual del Desarrollador — Sistema de Notificaciones (Django Signals)

> **Versión**: 2.2 — Mecanismo de sesión localStorage documentado  
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

## Sesión sin Django Sessions — Cómo funciona con localStorage

> **Este sistema NO usa las sesiones nativas de Django.** La identidad del usuario se gestiona completamente con un token UUID almacenado en el `localStorage` del navegador. Los signals no necesitan leer `localStorage` porque son código 100% servidor; el token es el puente entre el navegador y `request.user` en Django.

### Qué se guarda en localStorage tras el login

Cuando el usuario inicia sesión, el backend devuelve este objeto y el frontend lo distribuye en tres claves de `localStorage`:

```
localStorage['token']         → UUID de sesión  (ej: "06567153-156a-42ec-b8a5-a7fa2eecf3ee")
localStorage['refresh_token'] → UUID de refresco (ej: "72b2704a-3b44-447d-9cda-d571fdbf778d")
localStorage['user']          → JSON con datos completos del usuario
```

El objeto `user` en JSON contiene **todo lo necesario** para identificar al usuario en el frontend:

```json
{
  "id": 1,
  "username": "robertcyby",
  "nombres": "Cy",
  "apellido_paterno": "Tamayo",
  "nombre_completo": "Cy Tamayo Montejano",
  "casino": 1,
  "casino_nombre": "Crown City",
  "rol": 3,
  "rol_nombre": "TECNICO",
  "esta_activo": true,
  "EULAAceptada": true
}
```

### Cómo el token viaja del navegador a Django

Cada petición HTTP que hace el frontend (Axios) pasa por un **interceptor** que lee el token de `localStorage` e inyecta el header `Authorization`:

```javascript
// Dentro del interceptor de Axios (notificationService.js y api.js)
notificationApi.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');  // ← Lee de localStorage
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;  // ← Lo inyecta en el header
    }
    return config;
});
```

Esto ocurre de forma **automática y transparente** en cada llamada a cualquier endpoint, incluyendo `GET /api/notificaciones/`.

### Cómo Django convierte el token en request.user

El backend tiene dos capas que procesan el header `Authorization: Bearer {token}`:

**Capa 1 — Middleware** (`Usuarios/middleware.py`): Se ejecuta en *cada* request antes de llegar a la vista:

```python
class SessionTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = auth_header.split()[1]  # Extrae el UUID del header
        
        # Busca el usuario en la BD por su session_token
        user = Usuarios.objects.select_related('casino', 'rol').get(
            session_token=token,
            esta_activo=True
        )
        request.user = user  # ← Asigna el usuario con casino y rol ya cargados
```

**Capa 2 — Autenticación DRF** (`Usuarios/authentication.py`): Para que Django REST Framework también reconozca el usuario:

```python
class SessionTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', '').split()[1]
        user = Usuarios.objects.select_related('casino', 'rol').get(
            session_token=token, esta_activo=True
        )
        return (user, token)  # ← DRF recibe al usuario autenticado
```

Ambas capas hacen `select_related('casino', 'rol')`, lo que significa que cuando la vista accede a `request.user.casino` o `request.user.rol`, **no hace consultas adicionales a la BD**.

### Cómo esto filtra las notificaciones

La vista de notificaciones (`Notificaciones/views.py`) usa `request.user` directamente para filtrar:

```python
def get_queryset(self):
    user = self.request.user  # ← El usuario fue asignado por el middleware/authentication

    return Notificacion.objects.filter(
        Q(es_global=True)                                         # ← Todos
        | Q(usuario_destino=user)                                 # ← ID del user de localStorage
        | Q(casino_destino=user.casino, rol_destino=user.rol)     # ← Casino + Rol del user
        | Q(casino_destino=user.casino, rol_destino__isnull=True) # ← Todo el casino
    ).filter(esta_activo=True)
```

`user.casino` y `user.rol` son los **objetos FK del modelo** ya cargados desde la BD — no vienen de localStorage. El frontend nunca envía el casino o el rol en la petición; el backend los deduce internamente a partir del token.

### Diagrama completo: de localStorage a la notificación filtrada

```
NAVEGADOR                          DJANGO BACKEND
─────────────────                  ──────────────────────────────────────────
localStorage['token']
      │
      ▼ (Axios interceptor)
Authorization: Bearer UUID  ──────► SessionTokenMiddleware
                                           │
                                           │  SELECT * FROM usuarios
                                           │  WHERE session_token = UUID
                                           │  AND esta_activo = TRUE
                                           ▼
                                    request.user = Usuarios(
                                        id=1, casino=Casino(id=1),
                                        rol=Rol(nombre='TECNICO')
                                    )
                                           │
                                           ▼
                                    NotificacionViewSet.get_queryset()
                                           │
                                           │  FILTER WHERE:
                                           │   es_global=True
                                           │   OR usuario_destino=1
                                           │   OR (casino_destino=1 AND rol_destino=3)
                                           │   OR (casino_destino=1 AND rol_destino=NULL)
                                           ▼
                                    [ Solo las notificaciones del usuario ]
                                           │
                                           ▼
HTTP Response JSON  ◄─────────────  serializer.data (con campo 'leido' calculado)
      │
      ▼
AppTopbar.vue muestra badge y lista
```

### Por qué los signals NO necesitan localStorage

Los signals son funciones Python que se ejecutan en el servidor cuando Django guarda un modelo. En ese momento **no existe ningún navegador ni sesión**: es simplemente el ORM procesando una operación en la base de datos.

Los signals obtienen el casino, el técnico o el usuario directamente desde la instancia del modelo:

```python
# ✅ Los signals leen de la instancia del modelo, no de localStorage
casino = instance.maquina.casino      # ForeignKey del modelo Ticket
tecnico = instance.tecnico_asignado   # ForeignKey del modelo Ticket
casino = instance.casino              # ForeignKey del modelo TareaEspecial
```

La cadena completa es:

```
Signal crea Notificacion(casino_destino=Casino_A, rol_destino=TECNICO)
                    ↓
           Base de datos (sys_notificaciones)
                    ↓
 Técnico del Casino_A hace polling (su localStorage tiene token del Casino_A)
                    ↓
 Django resuelve token → request.user.casino = Casino_A, request.user.rol = TECNICO
                    ↓
 Filtro coincide → la notificación aparece ✅
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

## ✅ Garantía de Aislamiento por Casino

> **Regla fundamental:** Una notificación creada en el Casino A **nunca** puede ser vista por un usuario del Casino B, a menos que sea `es_global=True` o un mensaje de Dirección (`es_del_director=True`).

### Cómo funciona el aislamiento

El filtro en `Notificaciones/views.py` (`get_queryset`) aplica esta lógica:

```python
Notificacion.objects.filter(
    Q(es_global=True)                                         # 1. Globales: todos
    | Q(usuario_destino=user)                                 # 2. Personal: solo ese usuario
    | Q(casino_destino=user.casino, rol_destino=user.rol)     # 3. Casino + Rol exactos
    | Q(casino_destino=user.casino, rol_destino__isnull=True) # 4. Todo el casino
)
```

Si un signal crea `casino_destino=Casino_A, rol_destino=TECNICO`, **solo** los técnicos del Casino A la ven. Un técnico del Casino B no la verá jamás.

### Estado de los signals actuales

| Signal | Fuente del Casino | ¿Puede haber fuga? |
|--------|-------------------|--------------------|
| Tickets | `instance.maquina.casino` | ❌ No |
| TareasEspeciales | `instance.casino` | ❌ No |
| IncidenciasInfraestructura | `instance.casino` | ❌ No |
| Wiki | `instance.casino_origen` (o `es_global=True` explícito) | ❌ No |
| Usuarios | `instance.casino` | ❌ No |

### Regla obligatoria para nuevos signals

Siempre que notifiques por rol, pasa **ambos** campos juntos:

```python
# ✅ CORRECTO
Notificacion.objects.create(
    casino_destino = instance.casino,  # ← OBLIGATORIO
    rol_destino    = rol,              # ← OBLIGATORIO junto con casino_destino
)

# ❌ INCORRECTO — sin casino, el filtro de la vista no aplica correctamente
Notificacion.objects.create(
    rol_destino = rol,  # Sin casino_destino → puede llegar a todos con ese rol
)
```

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

---

## Página de Notificaciones Especiales (Admin)

Se ha creado una página de administración para enviar notificaciones manuales sin tocar el código.

### Ruta de acceso

```
/mando-central/notificaciones-especiales
```

**Archivo:** `FrontEnd/src/views/MandoCentral/NotificacionesEspeciales.vue`

### Roles con acceso

`ADMINISTRADOR`, `DB ADMIN`, `GERENCIA`, `SUP SISTEMAS`

### Tipos de alcance disponibles en el formulario

| Tipo | Descripción | Campos requeridos |
|------|-------------|-------------------|
| **Global** | Todos los usuarios del sistema, todos los casinos | Solo título y contenido |
| **Dirección** | Global + permanece 7 días (tipo DIRECTOR) | Solo título y contenido |
| **Por Casino** | Todos los usuarios de un casino específico | `casino_destino` |
| **Rol + Casino** | Un rol específico dentro de un casino | `casino_destino` + `rol_destino` |
| **Personal** | Un usuario en particular | Seleccionar casino → seleccionar usuario |

### Cómo agregar la ruta al menú de la BD

Desde el panel de administración de Menús del sistema, agrega una entrada con:

```json
{
  "label": "Notificaciones Especiales",
  "icon": "pi pi-megaphone",
  "to": "/mando-central/notificaciones-especiales",
  "componentPath": "/src/views/MandoCentral/NotificacionesEspeciales.vue",
  "roles": ["ADMINISTRADOR", "DB ADMIN", "GERENCIA", "SUP SISTEMAS"]
}
```

> La ruta ya está registrada estáticamente en `FrontEnd/src/router/index.js`, por lo que funciona de inmediato incluso sin la entrada en el menú.

---

*Fin del manual. Cualquier duda, revisar los archivos `signals.py` de cada módulo como referencia.*
