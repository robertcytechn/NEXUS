# BitacoraTecnicaViewSet — Bitácora Técnica

**Archivo fuente:** `BackEnd/BitacoraTecnica/views.py`  
**Clase:** `BitacoraTecnicaViewSet(viewsets.ModelViewSet)`  
**Base URL:** `/api/bitacora/`  
**Serializer:** `BitacoraTecnicaSerializer`  
**Permisos:** `IsAuthenticated` (global)

---

## Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/bitacora/` | Listado (filtrable por `?ticket={id}`) |
| POST | `/api/bitacora/` | Crear nueva entrada |
| GET | `/api/bitacora/{id}/` | Detalle |
| PATCH | `/api/bitacora/{id}/` | Actualizar parcialmente |
| DELETE | `/api/bitacora/{id}/` | Eliminar |

---

## `get_queryset`

```python
queryset = BitacoraTecnica.objects.all().select_related(
    'ticket',
    'usuario_tecnico'
)
```

### Filtro por ticket

```python
def list(self, request, *args, **kwargs):
    ticket_id = self.request.query_params.get('ticket')
    if ticket_id:
        self.queryset = self.queryset.filter(ticket_id=ticket_id)
    return super().list(request, *args, **kwargs)
```

**Uso:** `GET /api/bitacora/?ticket=42` devuelve todas las entradas de ese ticket.

---

## `perform_create` — Resolución de usuario

El frontend puede enviar `usuario_tecnico` (ID) en el body para reflejar al técnico real que realizó la intervención (puede ser distinto del usuario autenticado en el dispositivo compartido).

```python
def perform_create(self, serializer):
    usuario_tecnico_id = self.request.data.get('usuario_tecnico')
    
    if usuario_tecnico_id:
        try:
            usuario = Usuarios.objects.get(id=usuario_tecnico_id, esta_activo=True)
            serializer.save(
                usuario_tecnico=usuario,
                creado_por=usuario.username
            )
        except Usuarios.DoesNotExist:
            # Fallback al usuario autenticado
            serializer.save(creado_por=request.user.username)
    else:
        # Usar usuario del token
        serializer.save(
            usuario_tecnico=request.user,
            creado_por=request.user.username
        )
```

Prioridad de resolución de usuario:
1. `usuario_tecnico` del body (ID)
2. Usuario autenticado del token
3. `'sistema'` como texto de auditoría

---

## `create` — Integración con Gamificación

```python
def create(self, request, *args, **kwargs):
    limpiar_puntos_context()                    # Limpia contexto thread-local previo
    response = super().create(request, *args, **kwargs)   # Ejecuta perform_create + signal
    puntos = get_puntos_context()               # Lee puntos inyectados por la signal
    if puntos:
        response.data['puntos_nexus'] = puntos  # Inyecta en la respuesta
        limpiar_puntos_context()
    return response
```

Cuando se crea una entrada de bitácora, el signal de gamificación (`post_save`) otorga puntos al técnico. El ViewSet captura esos puntos del contexto thread-local y los devuelve en la respuesta para que el frontend pueda mostrar la animación.

### Respuesta con gamificación
```json
{
  "id": 15,
  "ticket": 42,
  "descripcion": "Revisión de tarjeta...",
  "puntos_nexus": {
    "puntos_otorgados": 20,
    "puntos_totales": 340,
    "rango_titulo": "Técnico II",
    "mensaje_nexus": "+20 pts NEXUS — bitácora técnica registrada"
  }
}
```
