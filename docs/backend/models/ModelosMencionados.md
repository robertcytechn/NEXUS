# ModeloMaquina — Ficha Técnica de Modelo

**Archivo fuente:** `BackEnd/ModelosMaquinas/models.py`  
**Hereda de:** `ModeloBase`  
**Tabla BD:** `maquina_modelos`  
**Propósito:** Catálogo de los modelos técnicos de máquinas registrados en el sistema. Cada `Maquina` referencia un `ModeloMaquina`, que a su vez apunta al `Proveedor/fabricante`.

---

## Campos

| Campo | Tipo Django | Nulo | Descripción |
|---|---|---|---|
| `proveedor` | `ForeignKey(Proveedor)` | No | Fabricante/distribuidor. `CASCADE`: si se elimina el proveedor, se eliminan sus modelos |
| `nombre_modelo` | `CharField(100)` | No | Código interno del modelo (ej. `"EGT-A220"`) |
| `nombre_producto` | `CharField(100)` | No | Nombre comercial o marca (ej. `"Diamond Club"`) |
| `descripcion` | `TextField` | Sí | Detalles técnicos adicionales |
| *+ campos heredados de ModeloBase* | | | |

---

## Restricción de Unicidad

```python
unique_together = ['proveedor', 'nombre_modelo']
```

El mismo código de modelo no puede repetirse para el mismo proveedor, pero sí entre proveedores diferentes.

---

## Jerarquía

```
Proveedor ──(1:N)──> ModeloMaquina ──(1:N)──> Maquina
```

---

## class Meta

```python
class Meta:
    db_table = 'maquina_modelos'
    verbose_name = "Modelo de Máquina"
    verbose_name_plural = "Modelos de Máquinas"
```

---

# EvolucionNexus — Reportes de Mejora del Sistema

**Archivo fuente:** `BackEnd/EvolucionNexus/models.py`  
**Hereda de:** `models.Model` (sin `ModeloBase`)  
**Propósito:** Canal interno para que los usuarios reporten bugs, propuestas de mejora, nuevas funcionalidades o cambios visuales directamente al desarrollador.

---

## Campos

| Campo | Tipo Django | Nulo | Default | Descripción |
|---|---|---|---|---|
| `usuario` | `ForeignKey(AUTH_USER_MODEL)` | Sí | `None` | Usuario que reporta. `SET_NULL` |
| `categoria` | `CharField(20)` | No | `'ERROR'` | Tipo de reporte (choices) |
| `estado` | `CharField(20)` | No | `'NO_REVISADO'` | Flujo de desarrollo (choices) |
| `titulo` | `CharField(200)` | No | — | Resumen del reporte |
| `descripcion` | `TextField` | No | — | Descripción detallada |
| `datos_extra` | `JSONField` | No | `{}` | Datos estructurados según categoría |
| `fecha_creacion` | `DateTimeField` | No | `auto_now_add` | Timestamp de creación |
| `fecha_actualizacion` | `DateTimeField` | No | `auto_now` | Timestamp de última actualización |

### `CATEGORIA_CHOICES`
`ERROR`, `VISUAL`, `COMPORTAMIENTO`, `FUNCIONALIDAD`, `CREAR`

### `ESTADO_CHOICES`
`NO_REVISADO` → `POR_REVISAR` → `ANALIZANDO` → `ADQUISICION` → `MAQUETACION` → `DESARROLLO` → `PRUEBAS` → `COMPLETADO`

### Campo `datos_extra` (JSONField dinámico)
La estructura varía según la categoría:
```json
// ERROR
{"modulo_afectado": "Tickets", "pasos_reproducir": "1. Ir a...\n2. Hacer click en..."}

// VISUAL o COMPORTAMIENTO
{"situacion_actual": "El botón...", "cambio_propuesto": "Debería..."}

// FUNCIONALIDAD
{"beneficio": "Permitiría que..."}
```

### Gamificación
Crear un reporte de EvolucionNexus otorga **+15 puntos** al autor, disparado por `gamif_evolucion_creada`.

---

# InventarioSala — Control de Herramientas y Consumibles

**Archivo fuente:** `BackEnd/InventarioSala/models.py`  
**Hereda de:** `ModeloBase`  
**Tabla BD:** `alm_inventario_sala`

| Campo | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `casino` | `ForeignKey(Casino)` | No | — | Sala propietaria del artículo |
| `nombre` | `CharField(150)` | No | — | Nombre (ej. "Cautín", "Tornillos M3") |
| `tipo` | `CharField(20)` | No | `'consumible'` | `herramienta` o `consumible` |
| `cantidad` | `PositiveIntegerField` | No | `0` | Existencia física actual |

---

# MenuConfig — Configuración de Menú Dinámico

**Archivo fuente:** `BackEnd/Menus/models.py`  
**Hereda de:** `models.Model` (sin `ModeloBase`)  
**Tabla BD:** `menu_config`  
**Propósito:** Almacena en un único registro JSON la configuración del menú lateral del frontend. Permite al administrador modificar la estructura de navegación sin desplegar código.

| Campo | Tipo | Descripción |
|---|---|---|
| `configuracion` | `JSONField` | Array JSON con la estructura del menú |
| `actualizado_en` | `DateTimeField(auto_now)` | Timestamp de la última modificación |
