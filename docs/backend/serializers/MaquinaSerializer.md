# MaquinaSerializer — Serialización de Máquinas de Casino

**Archivo fuente:** `BackEnd/Maquinas/serializers.py`  
**Modelos:** `Maquina`  
**Propósito:** Expone la información completa de una máquina incluyendo datos anidados del modelo, proveedor y denominaciones. Tiene una variante ligera (`MaquinaMapaSerializer`) optimizada para el renderizado del mapa de sala.

---

## Serializers Disponibles

| Clase | Propósito | Campos |
|---|---|---|
| `MaquinaSerializer` | CRUD completo de máquinas | `__all__` + campos calculados |
| `MaquinaMapaSerializer` | Vista del Mapa Interactivo (Digital Twin) | Subset ligero + labels legibles |

---

## `MaquinaSerializer`

### Campos de Solo Lectura Adicionales

| Campo | Origen | Descripción |
|---|---|---|
| `modelo_nombre` | `source='modelo.nombre_modelo'` | Código del modelo de máquina |
| `modelo_producto` | `source='modelo.nombre_producto'` | Nombre comercial |
| `modelo_descripcion` | `source='modelo.descripcion'` | Descripción técnica |
| `imagen_url` | `source='modelo.imagen'` | URL de imagen del modelo |
| `casino_nombre` | `source='casino.nombre'` | Nombre de la sede |
| `proveedor_id` | `source='modelo.proveedor.id'` | PK del proveedor |
| `proveedor_nombre` | `source='modelo.proveedor.nombre'` | Razón social del proveedor |
| `proveedor_rfc` | `source='modelo.proveedor.rfc'` | RFC del proveedor |
| `proveedor_email` | `source='modelo.proveedor.email_corporativo'` | Email principal del proveedor |
| `proveedor_telefono` | `source='modelo.proveedor.telefono_soporte'` | Teléfono de soporte |
| `proveedor_contacto` | `source='modelo.proveedor.nombre_contacto_tecnico'` | Nombre del técnico asignado |
| `denominaciones_info` | `SerializerMethodField` | Lista de objetos `{id, etiqueta, valor}` |
| `uid` | `source='uid_sala'` | Alias para compatibilidad con el frontend |
| `dias_licencia` | `SerializerMethodField` | Días hasta vencimiento de licencia |
| `fecha_instalacion` | `source='creado_en'` | Fecha de creación formateada como `YYYY-MM-DD` |

### `get_dias_licencia`
```python
def get_dias_licencia(self, obj):
    if not obj.fecha_vencimiento_licencia:
        return "Indefinida"
    delta = obj.fecha_vencimiento_licencia - date.today()
    return max(delta.days, 0)
```

Retorna la cantidad de días hasta que vence la licencia. Si ya venció, retorna `0` (nunca negativo). Si no tiene licencia configurada, retorna la cadena `"Indefinida"`.

### `get_denominaciones_info`
```python
def get_denominaciones_info(self, obj):
    return [
        {
            'id': denom.id,
            'etiqueta': denom.etiqueta,
            'valor': str(denom.valor)
        }
        for denom in obj.denominaciones.all()
    ]
```

La relación `ManyToMany` requiere un método personalizado. El `value` se convierte a `str` para evitar problemas de serialización de `Decimal` en JSON.

---

## `MaquinaMapaSerializer`

Serializer de **solo lectura** diseñado para el Mapa Interactivo (Digital Twin). Todos los campos son `read_only_fields = fields`.

### Campos Adicionales Exclusivos del Mapa

| Campo | Descripción |
|---|---|
| `ubicacion_piso_label` | Etiqueta legible del choice (ej. `"PISO_1"` → `"Piso 1"`) |
| `ubicacion_sala_label` | Etiqueta legible del choice de sala |

### `get_ubicacion_piso_label` / `get_ubicacion_sala_label`
```python
def get_ubicacion_piso_label(self, obj):
    choices_dict = dict(Maquina.PISO_CHOICES)
    return choices_dict.get(obj.ubicacion_piso, obj.ubicacion_piso)
```

Convierte el valor almacenado (`PISO_1`) a su etiqueta legible (`Piso 1`). Se usa `dict(choices)` para lookup en O(1). El fallback `obj.ubicacion_piso` asegura que si el valor no está en el diccionario (datos legados), igual se muestra algo útil.

---

## Optimización de Queries

Para evitar el problema N+1 al serializar múltiples máquinas, las vistas deben usar `select_related` y `prefetch_related`:

```python
# En la vista
queryset = Maquina.objects.select_related(
    'modelo',
    'modelo__proveedor',
    'casino',
).prefetch_related('denominaciones')
```

Sin esto, cada máquina generaría ~5 queries adicionales para obtener `modelo`, `proveedor`, `casino` y `denominaciones`.
