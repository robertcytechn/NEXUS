# NotificacionViewSet — Sistema de Alertas en Tiempo Real

**Archivo fuente:** `BackEnd/Notificaciones/views.py`  
**Clases:** `NotificacionViewSet`, `NotificacionUsuarioViewSet`  
**Base URL:** `/api/notificaciones/`  
**Serializer:** `NotificacionSerializer`, `NotificacionUsuarioSerializer`  
**Permisos:** `IsAuthenticated`

---

## `NotificacionViewSet`

### Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/notificaciones/` | Listado filtrado por identidad del usuario |
| POST | `/api/notificaciones/` | Crear notificación |
| PATCH | `/api/notificaciones/{id}/` | Actualizar notificación |
| DELETE | `/api/notificaciones/{id}/` | Eliminar notificación |
| PATCH | `/api/notificaciones/{id}/marcar-leida/` | Marcar como leída |
| GET | `/api/notificaciones/count-no-leidas/` | Conteo de no leídas (para badge) |

---

## `get_queryset` — Lógica de Filtro por Identidad

```python
def get_queryset(self):
    user = self.request.user
    return Notificacion.objects.filter(
        Q(es_global=True) |
        Q(usuario_destino=user) |
        Q(casino_destino=user.casino, rol_destino=user.rol) |
        Q(casino_destino=user.casino, rol_destino__isnull=True, usuario_destino__isnull=True)
    ).filter(esta_activo=True).distinct().order_by('-creado_en')
```

**El `distinct()` es obligatorio:** La combinación de Q-objects con OR puede causar duplicados en el resultado SQL cuando un registro satisface múltiples condiciones. `distinct()` elimina estos duplicados.

**`esta_activo=True`:** Las notificaciones obsoletas no se eliminan físicamente; se desactivan mediante el comando de limpieza programado.

---

## Acción: `marcar_leida` (PATCH)

**URL:** `PATCH /api/notificaciones/{id}/marcar-leida/`

```python
lectura, created = NotificacionUsuario.objects.get_or_create(
    notificacion=notificacion,
    usuario=usuario,
    defaults={'creado_por': usuario.username}
)
return Response({
    'status': 'ok',
    'leido': True,
    'created': created,      # True si es la primera vez, False si ya la había marcado
    'fecha_visto': lectura.fecha_visto
})
```

Usa `get_or_create` para ser idempotente: si el usuario llama al endpoint dos veces, no se crea un registro duplicado.

---

## Acción: `count_no_leidas` (GET)

**URL:** `GET /api/notificaciones/count-no-leidas/`  
**Uso típico:** Polling del frontend cada 45 segundos para actualizar el badge de notificaciones

```python
lectura_exists = NotificacionUsuario.objects.filter(
    notificacion=OuterRef('pk'),
    usuario=user
)

count = Notificacion.objects.filter(
    Q(es_global=True) | ...
).filter(esta_activo=True).distinct().annotate(
    leido=Exists(lectura_exists)
).filter(leido=False).count()
```

**`Exists(OuterRef('pk'))`:** Subconsulta correlacionada altamente eficiente. En vez de traer todos los registros y filtrar en Python, deja a la DB hacer el JOIN con `EXISTS()` que tiene index support.

### Respuesta
```json
{"count": 5}
```

---

## `get_serializer_context`

```python
def get_serializer_context(self):
    context = super().get_serializer_context()
    context['request'] = self.request
    return context
```

**Por qué:** El `NotificacionSerializer.get_leido()` necesita `request.user` para saber si el usuario actual leyó la notificación. El context del serializer es la forma estándar de DRF para pasar información extra al serializer sin cambiar su firma.

---

## `perform_create`

```python
def perform_create(self, serializer):
    user = self.request.user
    serializer.save(
        creado_por=user.username if hasattr(user, 'username') else str(user)
    )
```

---

## `NotificacionUsuarioViewSet`

ViewSet secundario para gestionar los registros de lectura directamente.

### Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/notificaciones-usuarios/` | Lecturas del usuario actual |
| POST | `/api/notificaciones-usuarios/` | Marcar notificación como leída |

### `create` Personalizado

```python
# Body esperado
{"notificacion": 42}

# El usuario se toma del token, no se envía en el body
lectura, created = NotificacionUsuario.objects.get_or_create(
    notificacion=notificacion,
    usuario=usuario,
    ...
)

# Respuesta
{
    "success": True,
    "created": True,
    "data": {...}
}
```

El usuario siempre se extrae del token de sesión, nunca del body del request. Esto es una medida de seguridad para evitar que un usuario marque notificaciones como leídas en nombre de otro.

---

## Limpieza Automática

```python
# BackEnd/scripts/limpiar_notificaciones.py (comando de management)
# Programado via Windows Task Scheduler a medianoche

# Lógica de limpieza:
# - Notificaciones normales de más de N días → esta_activo = False
# - Notificaciones con es_del_director=True → máximo 7 días
```
