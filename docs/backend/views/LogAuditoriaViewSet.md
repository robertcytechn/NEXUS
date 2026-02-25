# LogAuditoriaViewSet — Panel de Auditoría Global

**Archivo fuente:** `BackEnd/AuditoriaGlobal/views.py`  
**Clase:** `LogAuditoriaViewSet(viewsets.ReadOnlyModelViewSet)`  
**Base URL:** `/api/auditoria/`  
**Serializer:** `LogAuditoriaSerializer`  
**Permisos:** `IsAuthenticated` (con intención de restringir a admin, ver notas)  
**Paginación:** `AuditoriaPagination` — 50 registros por página

---

## Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/auditoria/` | Listado paginado de logs con filtros |
| GET | `/api/auditoria/{id}/` | Detalle de un log específico |
| GET | `/api/auditoria/tablas_afectadas/` | Lista de tablas con logs registrados |

> `ReadOnlyModelViewSet` solo provee `list` y `retrieve`. No se puede crear, editar o eliminar un log desde la API.

---

## Paginación: `AuditoriaPagination`

```python
class AuditoriaPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
```

El frontend puede ajustar el tamaño de página: `GET /api/auditoria/?page_size=100`.

---

## `get_queryset` — Filtros Dinámicos

```python
def get_queryset(self):
    qs = super().get_queryset()
    
    tabla     = self.request.query_params.get('tabla', None)
    accion    = self.request.query_params.get('accion', None)
    casino_id = self.request.query_params.get('casino', None)
    usuario_id= self.request.query_params.get('usuario', None)
    
    if tabla:      qs = qs.filter(tabla__icontains=tabla)       # Search insensible a mayúsculas
    if accion:     qs = qs.filter(accion__iexact=accion)        # Exacto pero case-insensitive
    if casino_id and casino_id.isdigit():  qs = qs.filter(casino_id=casino_id)
    if usuario_id and usuario_id.isdigit(): qs = qs.filter(usuario_id=usuario_id)
    
    return qs
```

**`isdigit()` antes de filtrar:** Previene inyecciones y errores de conversión. Si el parámetro no es numérico, se ignora silenciosamente.

**Ejemplo de uso:**
```
GET /api/auditoria/?tabla=Maquina&accion=UPDATE&casino=5&page=2
```

---

## Acción: `tablas_afectadas` (GET)

**URL:** `GET /api/auditoria/tablas_afectadas/`

```python
@action(detail=False, methods=['GET'])
def tablas_afectadas(self, request):
    tablas = LogAuditoria.objects.values_list('tabla', flat=True).distinct().order_by('tabla')
    return Response(list(tablas))
```

Devuelve la lista de nombres de modelos que tienen al menos un log. Usado para poblar el combobox de filtro en el panel de administración.

### Respuesta
```json
["BitacoraTecnica", "Casino", "Maquina", "Ticket", "Usuarios", ...]
```

---

## Permisos: `IsAdminPermission`

```python
class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol == 'admin')
```

> **⚠️ Nota del código:** Esta clase está definida pero actualmente el ViewSet usa `IsAuthenticated` en vez de `IsAdminPermission`. Hay un comentario TODo en el código indicando que debe protegerse el acceso a solo administradores. En producción, cambiar a `permission_classes = [IsAdminPermission]`.
