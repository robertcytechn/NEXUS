# IncidenciaInfraestructuraViewSet · InventarioSalaViewSet

**Archivos fuente:**  
- `BackEnd/IncidenciasInfraestructura/views.py`  
- `BackEnd/InventarioSala/views.py`

Dos ViewSets simples de CRUD con filtros por casino. Se documentan juntos por su brevedad.

---

## IncidenciaInfraestructuraViewSet

**Clase:** `IncidenciaInfraestructuraViewSet(viewsets.ModelViewSet)`  
**Base URL:** `/api/incidencias/`  
**Serializer:** `IncidenciaInfraestructuraSerializer`

### Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/incidencias/` | Listado ordenado por `-creado_en` (filtros: `?casino=id`) |
| POST | `/api/incidencias/` | Registrar nueva incidencia |
| GET | `/api/incidencias/{id}/` | Detalle |
| PATCH | `/api/incidencias/{id}/` | Actualizar (p.ej. cerrar con `hora_fin`) |
| DELETE | `/api/incidencias/{id}/` | Eliminar |

### `get_queryset`

```python
queryset = IncidenciaInfraestructura.objects.all().select_related('casino').order_by('-creado_en')
casino_id = self.request.query_params.get('casino')
if casino_id:
    queryset = queryset.filter(casino_id=casino_id)
return queryset
```

### `perform_create` / `perform_update` — Resolución de usuario por localStorage

El frontend puede enviar `creado_por_id` o `modificado_por_id` en el body para referenciar al usuario real (puede ser diferente al portador del token en dispositivos compartidos).

```python
def perform_create(self, serializer):
    usuario_id = self.request.data.get('creado_por_id')
    if usuario_id:
        try:
            usuario = Usuarios.objects.get(id=usuario_id)
            serializer.save(creado_por=usuario.username)
        except Usuarios.DoesNotExist:
            serializer.save(creado_por='Sistema')
    else:
        serializer.save(creado_por='Sistema')
```

### Efecto colateral — Signal de Notificaciones

Al crear una incidencia, el signal en `IncidenciasInfraestructura/signals.py` genera automáticamente notificaciones según la severidad:

| Severidad | Destinatarios |
|---|---|
| `CRITICA` | Todos (global) |
| `ALTA` | Casino afectado + Administrador |
| `MEDIA` | Solo el casino afectado |
| `BAJA` | Solo el casino afectado |

> La lógica de notificación es invisible para el ViewSet; ocurre en la capa de signals.

---

## InventarioSalaViewSet

**Clase:** `InventarioSalaViewSet(viewsets.ModelViewSet)`  
**Base URL:** `/api/inventario/`  
**Serializer:** `InventarioSalaSerializer`

### Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/inventario/` | Listado (filtro: `?casino=id`) |
| POST | `/api/inventario/` | Dar de alta artículo |
| GET | `/api/inventario/{id}/` | Detalle |
| PATCH | `/api/inventario/{id}/` | Actualizar cantidad/estado |
| DELETE | `/api/inventario/{id}/` | Eliminar |

### `get_queryset`

```python
queryset = InventarioSala.objects.all().select_related('casino')
casino_id = self.request.query_params.get('casino')
if casino_id:
    queryset = queryset.filter(casino_id=casino_id)
return queryset
```

### `perform_create`

```python
serializer.save(creado_por=self.request.user.username)
```

No hay integración especial con gamificación ni signals en este ViewSet.

---

## Comparativa

| Característica | IncidenciaViewSet | InventarioViewSet |
|---|---|---|
| Filtro por casino | `?casino=id` (query param) | `?casino=id` (query param) |
| Resolución de usuario | `creado_por_id` del body | Token de autenticación |
| Signals activos | Sí (notificaciones por severidad) | No |
| Gamificación | No | No |
| `select_related` | `casino` | `casino` |
| Orden por defecto | `-creado_en` | Sin orden explícito |
