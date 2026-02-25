# Serializers Operacionales

**Archivos fuente:**
- `BackEnd/BitacoraTecnica/serializers.py`
- `BackEnd/MantenimientosPreventivos/serializers.py`
- `BackEnd/RelevosTurnos/serializers.py`
- `BackEnd/TareasEspeciales/serializers.py`
- `BackEnd/IncidenciasInfraestructura/serializers.py`

Serializers del núcleo operacional del sistema. Se documentan en un solo archivo por su tamaño reducido.

---

## BitacoraTecnicaSerializer

**Modelo:** `BitacoraTecnica`

### Campos

| Campo | Tipo | Notas |
|---|---|---|
| `id` | Auto | Read-only |
| `ticket` | FK (int) | ID del ticket relacionado |
| `usuario_tecnico` | FK (int) | ID del técnico |
| `tecnico_nombre` | CharField | `source='usuario_tecnico.username'` — read-only |
| `tipo_intervencion` | CharField | Choices del modelo |
| `descripcion_trabajo` | TextField | Descripción libre |
| `resultado_intervencion` | TextField | Resultado de la intervención |
| `estado_maquina_resultante` | CharField | Estado de la máquina al terminar |
| `finaliza_ticket` | BooleanField | Si `True`, el ticket se cierra |
| `fecha_registro` | DateTimeField | `source='creado_en'`, formato `YYYY-MM-DD HH:MM:SS` — read-only |

**Campos excluidos de escritura:** `creado_en`, `modificado_en`, `creado_por`, `modificado_por`

---

## MantenimientoPreventivoSerializer

**Modelo:** `MantenimientoPreventivo`

### Campos

| Campo | Tipo | Notas |
|---|---|---|
| `id` | Auto | Read-only |
| `maquina` | FK (int) | ID de la máquina |
| `maquina_uid` | CharField | `source='maquina.uid_sala'` — read-only |
| `casino_nombre` | CharField | `source='maquina.casino.nombre'` — read-only (JOIN doble) |
| `tecnico_responsable` | FK (int) | ID del técnico |
| `tecnico_nombre` | CharField | `source='tecnico_responsable.username'` — read-only |
| `fecha_mantenimiento` | DateField | Fecha del preventivo |
| `estado_final_maquina` | CharField | Estado de la máquina al completar |
| `observaciones` | TextField | Notas adicionales |
| `creado_en` | DateTimeField | Read-only |

> `casino_nombre` accede a una relación doble (`maquina.casino.nombre`). El `select_related('maquina__casino')` en el ViewSet evita queries N+1.

---

## RelevoTurnoSerializer

**Modelo:** `RelevoTurno`  
**`fields = '__all__'`** — expone todos los campos del modelo.

### Campos adicionales (read-only)

| Campo | `source` | Descripción |
|---|---|---|
| `nombre_saliente` | `tecnico_saliente.username` | Username del técnico que entrega |
| `nombre_entrante` | `tecnico_entrante.username` | Username del técnico que recibe |
| `casino_nombre` | `casino.nombre` | Nombre del casino |
| `estado_entrega_display` | `get_estado_entrega_display` | Label legible del choice |

### `validate` — 3 validaciones cruzadas

```python
def validate(self, data):
    # 1. técnico_saliente.casino == relevo.casino
    if tecnico_saliente.casino_id != casino.id:
        raise ValidationError({'tecnico_saliente': '...'})

    # 2. técnico_entrante.casino == relevo.casino
    if tecnico_entrante.casino_id != casino.id:
        raise ValidationError({'tecnico_entrante': '...'})

    # 3. No pueden ser el mismo técnico
    if tecnico_saliente.id == tecnico_entrante.id:
        raise ValidationError({'tecnico_entrante': '...'})
```

### `create` — `hora_salida_real` automática

```python
def create(self, validated_data):
    validated_data['hora_salida_real'] = timezone.now()
    return super().create(validated_data)
```

`hora_salida_real` es `read_only` en el Meta. El serializer la establece automáticamente al momento de creación.

---

## TareaEspecialSerializer

**Modelo:** `TareaEspecial`  
**`fields = '__all__'`** — expone todos los campos del modelo.

### Campos adicionales (read-only)

| Campo | `source` | Default | Descripción |
|---|---|---|---|
| `creador_nombre` | `creado_por_usuario.username` | — | Username del creador |
| `tecnico_nombre` | `asignado_a.username` | `"Pendiente"` | Username del técnico asignado |
| `casino_nombre` | `casino.nombre` | — | Nombre del casino |

> `tecnico_nombre` tiene `default="Pendiente"` para manejar tareas sin técnico asignado aún (FK nullable).

---

## IncidenciaInfraestructuraSerializer

**Modelo:** `IncidenciaInfraestructura`

### Campos

| Campo | Tipo | Notas |
|---|---|---|
| `id` | Auto | Read-only |
| `casino` | FK (int) | ID del casino |
| `casino_nombre` | CharField | `source='casino.nombre'` — read-only |
| `titulo` | CharField | Título breve de la incidencia |
| `categoria` | CharField | Choices: ELECTRICA, RED, CLIMA, ESTRUCTURA, OTROS |
| `descripcion` | TextField | Descripción detallada |
| `severidad` | CharField | Choices: BAJA, MEDIA, ALTA, CRITICA |
| `afecta_operacion` | BooleanField | Si impacta las operaciones de sala |
| `hora_inicio` | DateTimeField | Inicio de la incidencia |
| `hora_fin` | DateTimeField | Resolución (nullable) |
| `esta_activo` | BooleanField | Si la incidencia está abierta |
| `creado_en` | DateTimeField | Read-only |
| `modificado_en` | DateTimeField | Read-only |
| `creado_por` | CharField | Read-only (texto) |
| `modificado_por` | CharField | Read-only (texto) |
| `notas_internas` | TextField | Notas internas de auditoría |

> `creado_por` y `modificado_por` son `read_only` en el serializer. El ViewSet los establece con la lógica de resolución desde `creado_por_id` del body.
