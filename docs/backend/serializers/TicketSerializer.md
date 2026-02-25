# TicketSerializer — Serialización de Incidencias Técnicas

**Archivo fuente:** `BackEnd/Tickets/serializers.py`  
**Modelos:** `Ticket`  
**Propósito:** Expone todos los campos del ticket más información calculada de relaciones (nombre completo del reportante, técnico, estado de la máquina) y métricas de tiempo calculadas dinámicamente.

---

## Serializers Disponibles

| Clase | Propósito |
|---|---|
| `TicketSerializer` | CRUD completo del ticket |
| `TicketCentroServiciosSerializer` | Vista específica para Centro de Servicios con campos adicionales |

---

## `TicketSerializer`

### Campos Adicionales (no del modelo)

| Campo | Tipo | Solo Lectura | Descripción |
|---|---|---|---|
| `maquina_uid` | `CharField` (source) | ✅ | `maquina.uid_sala` |
| `maquina_estado_actual` | `SerializerMethodField` | ✅ | Estado actual de la máquina (consulta fresca) |
| `casino_nombre` | `CharField` (source) | ✅ | `maquina.casino.nombre` |
| `reportante_nombre` | `CharField` (source) | ✅ | `reportante.nombres` |
| `reportante_apellidos` | `SerializerMethodField` | ✅ | Apellidos concatenados |
| `reportante_rol` | `CharField` (source) | ✅ | `reportante.rol.nombre` |
| `tecnico_nombre` | `CharField` (source) | ✅ | `tecnico_asignado.nombres` |
| `tecnico_asignado_nombre` | `SerializerMethodField` | ✅ | Nombre completo del técnico |
| `tiempo_respuesta` | `SerializerMethodField` | ✅ | Duración desde creación hasta cierre |

### Campos de Solo Lectura del Modelo

```python
read_only_fields = [
    'folio',              # Autogenerado en save()
    'creado_en',          # auto_now_add
    'modificado_en',      # auto_now
    'creado_por',         # Asignado en perform_create
    'modificado_por',     # Asignado en perform_update
    'contador_reaperturas' # Gestionado en endpoint /reabrir/
]
```

---

## Métodos Personalizados

### `get_maquina_estado_actual`
```python
def get_maquina_estado_actual(self, obj):
    if obj.maquina_id:
        from Maquinas.models import Maquina
        try:
            maquina = Maquina.objects.only('estado_actual').get(id=obj.maquina_id)
            return maquina.estado_actual
        except Maquina.DoesNotExist:
            return None
    return None
```

**Por qué no usar `source='maquina.estado_actual'`:** El estado de la máquina puede cambiar después de que se creó el ticket. Al usar `SerializerMethodField` con `objects.only()`, se hace una consulta fresca a la DB, garantizando que el frontend siempre vea el estado real actual de la máquina (no el snapshot del momento de creación del ticket).

**`objects.only('estado_actual')`:** Optimización — solo trae un campo de la BD en vez de toda la fila.

### `get_tiempo_respuesta`
```python
def get_tiempo_respuesta(self, obj):
    if obj.estado_ciclo == 'cerrado' and obj.modificado_en:
        diff = obj.modificado_en - obj.creado_en
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m"
    return "En curso"
```

Calcula el tiempo total de resolución del ticket. Solo aplica si el ticket está cerrado. Ejemplo de respuesta: `"2d 3h 45m"`.

---

## `TicketCentroServiciosSerializer`

Variante del serializer optimizada para el módulo de Centro de Servicios. Expone menos campos del modelo y agrega:

| Campo Adicional | Descripción |
|---|---|
| `dias_abierto` | Días transcurridos desde creación (mientras no esté cerrado) |
| `total_intervenciones` | `obj.bitacoras.filter(esta_activo=True).count()` |

### Cálculo de `dias_abierto`
```python
def get_dias_abierto(self, obj):
    if obj.estado_ciclo != 'cerrado':
        ahora = timezone.now()
        diferencia = ahora - obj.creado_en
        return diferencia.days
    return 0
```

---

## Notas de Rendimiento

El `TicketSerializer` aprovecha los `select_related` definidos en `get_queryset` del ViewSet:

```python
Ticket.objects.all().select_related(
    'maquina',
    'maquina__casino',
    'reportante',
    'reportante__rol',
    'tecnico_asignado'
)
```

Los campos `source='maquina.casino.nombre'` NO generan queries adicionales gracias a este prefetch. La única query extra es `get_maquina_estado_actual` que es deliberada (estado fresco).
