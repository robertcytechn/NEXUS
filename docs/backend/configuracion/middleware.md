# Middleware Personalizado — Autenticación y Auditoría

**Archivos fuente:**
- `BackEnd/Usuarios/middleware.py` → `SessionTokenMiddleware`
- `BackEnd/AuditoriaGlobal/middleware.py` → `AuditMiddleware`

---

## SessionTokenMiddleware

**Clase:** `SessionTokenMiddleware(MiddlewareMixin)`  
**Ubicación en MIDDLEWARE:** Posición 7 (después de `AuthenticationMiddleware`)

### Propósito

Autentica al usuario leyendo un **token UUID** desde el header `Authorization: Bearer <token>` y lo asigna a `request.user`. Esto reemplaza el sistema de sesiones de Django nativo.

### Flujo de `process_request`

```mermaid
flowchart TD
    A[request llega] --> B{¿Tiene Authorization header?}
    B -- No --> C[request.user = AnonymousUser]
    B -- Sí --> D{¿Formato Bearer token?}
    D -- No --> C
    D -- Sí --> E[extraer token UUID]
    E --> F{Usuarios.objects.get\nsession_token=token\nesta_activo=True}
    F -- Encontrado --> G[request.user = usuario con casino y rol]
    F -- DoesNotExist --> C
```

```python
def process_request(self, request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    parts = auth_header.split()
    
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        request.user = AnonymousUser()
        return None
    
    token = parts[1]
    try:
        user = Usuarios.objects.select_related('casino', 'rol').get(
            session_token=token,
            esta_activo=True
        )
        request.user = user
    except Usuarios.DoesNotExist:
        request.user = AnonymousUser()
```

### Características clave

- Usa `select_related('casino', 'rol')` en el lookup → **una sola consulta SQL** con JOINs
- Verifica `esta_activo=True` → usuarios desactivados son rechazados aunque tengan token válido
- El `session_token` es un UUID v4 generado al hacer login y almacenado en `Usuarios.session_token`
- Compatible con `IsAuthenticated` de DRF: si `request.user` es `AnonymousUser`, la comprobación falla

### Header requerido

```
Authorization: Bearer 550e8400-e29b-41d4-a716-446655440000
```

---

## AuditMiddleware

**Clase:** `AuditMiddleware(MiddlewareMixin)`  
**Ubicación en MIDDLEWARE:** Posición 8 (después de `SessionTokenMiddleware`)

### Propósito

Captura el usuario y casino autenticados y los guarda en **variables thread-local** para que los signals de auditoría puedan acceder a ellos sin necesidad de recibir el `request` como argumento.

### Variables thread-local

```python
_thread_locals = threading.local()

def get_current_user():   # Accesible desde signals
    return getattr(_thread_locals, 'user', None)

def get_current_casino():  # Accesible desde signals
    return getattr(_thread_locals, 'casino', None)
```

### Ciclo de vida del thread-local

| Método | Acción |
|---|---|
| `process_request` | `user = None`, `casino = None` — limpia contexto previo |
| `process_view` | Asigna `user` y `casino` desde `request.user` |
| `process_response` | Limpia `user` y `casino` |
| `process_exception` | Limpia `user` y `casino` |

### ¿Por qué `process_view` en vez de `process_request`?

```python
def process_view(self, request, view_func, view_args, view_kwargs):
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        _thread_locals.user = user
        if hasattr(user, 'casino'):
            _thread_locals.casino = user.casino
```

`process_request` ocurre **antes** de que DRF ejecute su capa de autenticación. `process_view` ocurre **durante la ejecución de la vista**, cuando `request.user` ya fue resuelto por `SessionTokenMiddleware`. Si se usara `process_request`, el usuario aún no estaría autenticado.

### Uso en Signals

```python
# En AuditoriaGlobal/signals.py
from AuditoriaGlobal.middleware import get_current_user, get_current_casino

@receiver(post_save, sender=...)
def crear_log(sender, instance, **kwargs):
    usuario = get_current_user()     # Obtiene el usuario sin pasar request
    casino = get_current_casino()    # Obtiene el casino sin pasar request
    
    LogAuditoria.objects.create(
        usuario=usuario,
        casino=casino,
        ...
    )
```

---

## Interacción entre los dos Middlewares

```
Request →
  SessionTokenMiddleware.process_request()
    → request.user = Usuarios(...) o AnonymousUser
    
  AuditMiddleware.process_request()
    → _thread_locals.user = None (limpieza)

  [DRF Authentication ejecuta SessionTokenAuthentication]
  
  AuditMiddleware.process_view()
    → _thread_locals.user = request.user (ya autenticado)
    → _thread_locals.casino = request.user.casino

  [Signal post_save llama get_current_user()]
    → retorna _thread_locals.user ✓

Response ←
  AuditMiddleware.process_response()
    → _thread_locals.user = None (limpieza)
```

> La limpieza en `process_response` y `process_exception` es **esencial** para evitar que el usuario de un request quede en el hilo y contamine el siguiente request que reutilice el mismo hilo del servidor.
