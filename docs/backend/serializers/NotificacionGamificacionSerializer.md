# NotificacionSerializer — Serialización de Alertas

**Archivo fuente:** `BackEnd/Notificaciones/serializers.py`  
**Modelos:** `Notificacion`, `NotificacionUsuario`  
**Propósito:** Serializa notificaciones con seguimiento de estado de lectura por usuario y validación estricta de las reglas de segmentación de audiencia.

---

## `NotificacionSerializer`

### Campos

Usa `fields = '__all__'` (todos los campos del modelo) más un campo calculado:

| Campo Adicional | Tipo | Descripción |
|---|---|---|
| `leido` | `SerializerMethodField` | `True` si el usuario actual ya leyó esta notificación |

### `get_leido`
```python
def get_leido(self, obj):
    request = self.context.get('request')
    if request and hasattr(request, 'user'):
        return NotificacionUsuario.objects.filter(
            notificacion=obj,
            usuario=request.user
        ).exists()
    return False
```

Consulta la tabla `NotificacionUsuario` para saber si el usuario del request tiene un registro de lectura. Requiere que el context incluya `request` (lo garantiza `get_serializer_context` del ViewSet).

---

## `validate()` — Reglas de Segmentación

Es la validación más importante del sistema de notificaciones. Garantiza que la audiencia de una notificación nunca sea ambigua:

```python
def validate(self, data):
    # Los valores can venir del request o del objeto existente (para PATCH parciales)
    es_global       = data.get('es_global',       getattr(self.instance, 'es_global',       False))
    usuario_destino = data.get('usuario_destino', getattr(self.instance, 'usuario_destino', None))
    casino_destino  = data.get('casino_destino',  getattr(self.instance, 'casino_destino',  None))
    rol_destino     = data.get('rol_destino',     getattr(self.instance, 'rol_destino',     None))
    ...
```

> **Nota de implementación:** Usar `getattr(self.instance, ...)` permite que el `validate()` funcione correctamente en PATCHes parciales. Si solo se envía `rol_destino`, el resto de campos se lee del objeto ya existente en la BD.

### Tabla de Reglas

| Regla | Condición | Error |
|---|---|---|
| 1 — Global exclusiva | `es_global=True` + cualquier destino → Error | `"Una notificación global no puede combinarse con..."` |
| 2 — Personal exclusiva | `usuario_destino` + `casino_destino` o `rol_destino` → Error | `"Una notificación personal no puede llevar casino_destino..."` |
| 3 — Rol requiere Casino | `rol_destino` sin `casino_destino` → Error | `"Para segmentar por rol debes indicar también casino_destino"` |
| 4 — Mínimo un destino | Sin ningún criterio → Error | `"Debes indicar al menos un criterio de destino..."` |

---

## `NotificacionUsuarioSerializer`

Serializer simple para el modelo de lectura. Los campos `fecha_visto`, `creado_en`, etc. son de solo lectura.

### Campos de Solo Lectura
```python
read_only_fields = ['fecha_visto', 'creado_en', 'modificado_en', 'creado_por', 'modificado_por']
```

---

# GamificacionSerializer — Tienda y Canjes

**Archivo fuente:** `BackEnd/Gamificacion/serializers.py`

---

## Serializers Disponibles

| Clase | Propósito | Acceso |
|---|---|---|
| `RecompensaGamificacionSerializer` | CRUD completo. Uso de GERENCIA | Escritura/Lectura |
| `RecompensaPublicaSerializer` | Vista de tienda. Solo lectura | Solo lectura |
| `CanjeRecompensaSerializer` | Historial de canjes | Solo lectura |

---

## `RecompensaGamificacionSerializer`

Serializer completo para gerencia. Incluye `casino_nombre` via `source`:

```python
casino_nombre = serializers.CharField(source='casino.nombre', read_only=True)
```

---

## `RecompensaPublicaSerializer`

Expone solo los campos necesarios para la tienda del técnico. Los campos sensibles como `esta_activo` de `ModeloBase` o `creado_por` no se expondrán:

```python
fields = ['id', 'titulo', 'descripcion', 'costo_puntos', 'casino_nombre', 'stock', 'activo']
read_only_fields = fields  # Todo es solo lectura en la tienda
```

---

## `CanjeRecompensaSerializer`

Incluye campos calculados para el historial:

| Campo | Fuente | Descripción |
|---|---|---|
| `usuario_nombre` | `source='usuario.username'` | Username del técnico |
| `recompensa_titulo` | `source='recompensa.titulo'` | Nombre de la recompensa |
| `estado_display` | `source='get_estado_display'` | Etiqueta legible del estado (ej. "Pendiente de Entrega") |

Los campos `usuario` y `puntos_descontados` son de solo lectura porque son asignados automáticamente por la vista al momento del canje.
