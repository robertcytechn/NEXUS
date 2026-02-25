# Serializers Catalog — Casino, Rol, AuditoriasExternas, InventarioSala

**Archivos fuente:**
- `BackEnd/Casinos/serializers.py`
- `BackEnd/Roles/serializers.py`
- `BackEnd/AuditoriasExternas/serializers.py`
- `BackEnd/InventarioSala/serializers.py`

Serializers de catálogo y registros de acceso externo. Se documentan juntos por su tamaño compacto.

---

## CasinoSerializer

**Modelo:** `Casino`

### Campos

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | Auto | PK |
| `nombre` | CharField | Nombre comercial |
| `identificador` | CharField | Código interno único |
| `direccion` | TextField | Dirección física |
| `telefono` | CharField | Teléfono de contacto |
| `ciudad` | CharField | Ciudad |
| `encargado` | CharField | Nombre del encargado |
| `esta_activo` | BooleanField | Estado activo/inactivo |
| `horario_apertura` | TimeField | Hora de apertura |
| `horario_cierre` | TimeField | Hora de cierre |
| `grid_width` | IntegerField | Ancho del grid del Digital Twin |
| `grid_height` | IntegerField | Alto del grid del Digital Twin |
| `creado_en` | DateTimeField | Read-only |
| `modificado_en` | DateTimeField | Read-only |
| `creado_por` | CharField | Read-only |
| `modificado_por` | CharField | Read-only |
| `notas_internas` | TextField | Notas internas |

> `grid_width` y `grid_height` son usados por el frontend para renderizar el mapa interactivo del Digital Twin. Por defecto `20×15`.

---

## RolSerializer

**Modelo:** `Rol`

### Campos

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | Auto | PK |
| `nombre` | CharField | Nombre del rol |
| `descripcion` | TextField | Descripción del rol |
| `esta_activo` | BooleanField | |
| `creado_en` | DateTimeField | Read-only |
| `modificado_en` | DateTimeField | Read-only |
| `creado_por` | CharField | Read-only |
| `modificado_por` | CharField | Read-only |
| `notas_internas` | TextField | |

Serializer puramente plano. Sin lógica adicional.

**Roles hardcodeados en el sistema:**

| Nombre | Descripción |
|---|---|
| `ADMINISTRADOR` | Acceso total |
| `SUP SISTEMAS` | Supervisor de sistemas |
| `TECNICO` | Técnico de campo |
| `GERENCIA` | Gerencia de casino |
| `PROVEEDOR` | Personal de proveedor externo |
| `OBSERVADOR` | Solo lectura |

---

## AuditoriaServicioExternoSerializer

**Modelo:** `AuditoriaServicioExterno`  
**`fields = '__all__'`** más campos calculados.

### Campos adicionales (read-only)

| Campo | `source` / método | Descripción |
|---|---|---|
| `proveedor_nombre` | `empresa_proveedora.nombre` | Nombre del proveedor |
| `supervisor_nombre` | `supervisor_interno.username` | Username del supervisor NEXUS |
| `casino_nombre` | `casino.nombre` | Nombre del casino |
| `area_acceso_display` | `get_area_acceso_display` | Label legible del área |
| `tipo_servicio_display` | `get_tipo_servicio_display` | Label legible del tipo de servicio |
| `duracion_minutos` | `get_duracion_minutos()` | Minutos entre entrada y salida |

### `get_duracion_minutos`

```python
def get_duracion_minutos(self, obj):
    if obj.hora_entrada and obj.hora_salida:
        delta = obj.hora_salida - obj.hora_entrada
        return int(delta.total_seconds() / 60)
    return None  # Cuando aún no hay salida registrada
```

Retorna `None` si la visita aún está activa (sin `hora_salida`). El frontend puede mostrar "En progreso".

---

## InventarioSalaSerializer

**Modelo:** `InventarioSala`  
**`fields = '__all__'`**

### Campos adicionales

| Campo | `source` | Descripción |
|---|---|---|
| `casino_nombre` | `casino.nombre` | Nombre del casino — read-only |

Serializer simple. Solo añade el nombre del casino para evitar que el frontend tenga que hacer una segunda consulta.
