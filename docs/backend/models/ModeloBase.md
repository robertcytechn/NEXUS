# ModeloBase — Modelo Abstracto de Auditoría

**Archivo fuente:** `BackEnd/ModelBase/models.py`  
**Tipo:** Modelo Abstracto Django (`abstract = True`)  
**Propósito:** Clase padre de la que heredan prácticamente todos los modelos de negocio del sistema NEXUS. Centraliza los campos de trazabilidad y borrado lógico en un único lugar, evitando repetición de código.

---

## ¿Por qué existe este modelo?

En lugar de que cada tabla tenga sus propios campos `creado_en`, `modificado_en`, etc., todos los modelos del sistema extienden `ModeloBase`. Esto garantiza coherencia en la auditoría y permite el **borrado lógico** (soft-delete) sin eliminar registros de la base de datos.

---

## Campos

| Campo | Tipo Django | DB Column | Nulo | Default | Descripción |
|---|---|---|---|---|---|
| `esta_activo` | `BooleanField` | `esta_activo` | No | `True` | Bandera de borrado lógico. `False` = registro desactivado/eliminado lógicamente |
| `creado_en` | `DateTimeField` | `creado_en` | No | `auto_now_add=True` | Timestamp inmutable de creación. Se asigna automáticamente al INSERT |
| `modificado_en` | `DateTimeField` | `modificado_en` | No | `auto_now=True` | Timestamp actualizado automáticamente en cada UPDATE |
| `creado_por` | `CharField(100)` | `creado_por` | Sí | `None` | Username (string) del usuario que creó el registro. Lo asigna la vista (view) |
| `modificado_por` | `CharField(100)` | `modificado_por` | Sí | `None` | Username del último usuario que modificó el registro |
| `notas_internas` | `TextField` | `notas_internas` | Sí | `None` | Campo libre para notas de auditoría o seguimiento interno |

> **Nota sobre `auto_now_add` vs `auto_now`:** `auto_now_add=True` sola asigna la fecha en la creación y es inmutable. `auto_now=True` re-asigna la fecha en cada `save()`. Ambos campos son `read_only` desde la API y no deben enviarse en peticiones POST/PATCH.

---

## Patrones de uso en las vistas

Los campos `creado_por` y `modificado_por` **no son automáticos en el modelo**; deben asignarse explícitamente en `perform_create` / `perform_update` de cada ViewSet:

```python
def perform_create(self, serializer):
    serializer.save(creado_por=self.request.user.username)

def perform_update(self, serializer):
    serializer.save(modificado_por=self.request.user.username)
```

---

## Borrado Lógico

El sistema NEXUS nunca elimina físicamente registros de negocio. La convención es:

```python
# Desactivar
instancia.esta_activo = False
instancia.save()

# En los QuerySets, filtrar activos:
Model.objects.filter(esta_activo=True)
```

Los endpoints tipo `switch-estado` (e.g., `PATCH /usuarios/{id}/switch-estado/`) invierten esta bandera.

---

## Herencia en el proyecto

Todos los modelos siguientes extienden `ModeloBase` y heredan automáticamente estos campos:

- `Casino`, `Proveedor`, `ModeloMaquina`
- `Maquina`, `Ticket`, `BitacoraTecnica`
- `MantenimientoPreventivo`, `TareaEspecial`, `RelevoTurno`
- `IncidenciaInfraestructura`, `InventarioSala`
- `Notificacion`, `NotificacionUsuario`, `WikiTecnica`
- `RecompensaGamificacion`, `CanjeRecompensa`
- `AuditoriaServicioExterno`, `Rol`, `Usuarios`

> **Excepción:** `Denominacion`, `LogAuditoria`, `EvolucionNexus` y `MenuConfig` **NO** heredan de `ModeloBase` por razones de diseño (catálogo simple, log inmutable, modelo libre).

---

## class Meta

```python
class Meta:
    abstract = True
```

Al ser abstracto, Django **no crea tabla** para `ModeloBase`. Los campos se incluyen directamente en la migración de cada modelo hijo.
