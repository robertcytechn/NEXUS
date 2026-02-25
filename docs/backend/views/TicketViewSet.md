# TicketViewSet — Gestión de Incidencias Técnicas

**Archivo fuente:** `BackEnd/Tickets/views.py`  
**Clase:** `TicketViewSet(viewsets.ModelViewSet)`  
**Base URL:** `/api/tickets/`  
**Serializer principal:** `TicketSerializer`  
**Serializer de Centro de Servicios:** `TicketCentroServiciosSerializer`  
**Filtros:** `DjangoFilterBackend`, `SearchFilter`, `OrderingFilter`

---

## Campos Filtrables (`filterset_fields`)

```python
filterset_fields = ['maquina', 'esta_activo', 'estado_ciclo', 'prioridad', 'categoria', 'maquina__casino']
```

El frontend puede combinar estos filtros en la URL:
```
GET /api/tickets/?maquina__casino=5&estado_ciclo=abierto&prioridad=critica
```

---

## Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/tickets/` | Listado con filtros |
| POST | `/api/tickets/` | Crear ticket |
| GET | `/api/tickets/{id}/` | Detalle |
| PUT/PATCH | `/api/tickets/{id}/` | Actualizar + adjunta `puntos_nexus` si aplica |
| DELETE | `/api/tickets/{id}/` | Eliminar |
| GET | `/api/tickets/lista-por-casino/{casino_id}/` | Tickets activos de un casino |
| GET | `/api/tickets/historial-maquina/{maquina_id}/` | Últimos 3 tickets de la máquina |
| PATCH | `/api/tickets/{id}/reabrir/` | Reabrir ticket cerrado |
| PATCH | `/api/tickets/{id}/switch-estado/` | Toggle de `esta_activo` |
| GET | `/api/tickets/dashboard-charts/{casino_id}/` | Datos para gráficas del dashboard |

---

## `get_queryset` — Optimización

```python
def get_queryset(self):
    return Ticket.objects.all().select_related(
        'maquina', 'maquina__casino',
        'reportante', 'reportante__rol',
        'tecnico_asignado'
    ).order_by('-creado_en')
```

El `select_related` de 5 niveles evita el problema N+1 que ocurriría si el serializer accediera a `ticket.maquina.casino.nombre` en un loop.

---

## `perform_create` — Validación de Unicidad + Reportante

```python
def perform_create(self, serializer):
    maquina_id = self.request.data.get('maquina')
    if maquina_id:
        tickets_abiertos = Ticket.objects.filter(
            maquina_id=maquina_id, esta_activo=True
        ).exclude(estado_ciclo='cerrado')
        
        if tickets_abiertos.exists():
            raise ValidationError({
                'error': 'No se puede crear un nuevo ticket',
                'mensaje': f'La máquina ya tiene tickets abiertos: {folios}',
                'tickets_abiertos': tickets_abiertos.count()
            })
    
    if self.request.user.is_authenticated:
        serializer.save(reportante=self.request.user, creado_por=usuario)
    else:
        serializer.save(creado_por=usuario)
```

**Regla de negocio:** Una máquina no puede tener más de un ticket activo abierto simultáneamente. Si se intenta crear uno, la API rechaza con 400 y muestra los folios existentes.

---

## `update` / `partial_update` — Integración con Gamificación

```python
def _update_con_puntos(self, request, *args, **kwargs):
    limpiar_puntos_context()          # Limpiar cualquier valor residual
    response = super().update(...)    # Ejecutar el update normal (dispara signals)
    puntos = get_puntos_context()     # Leer si la signal otorgó puntos
    if puntos:
        response.data['puntos_nexus'] = puntos   # Adjuntar al JSON de respuesta
        limpiar_puntos_context()
    return response
```

Si el técnico cierra un ticket, la signal `gamif_ticket_cerrado` otorga +2 pts y guarda el resultado en el thread local. Este método lee ese resultado y lo adjunta a la respuesta HTTP para que el frontend muestre el toast de celebración.

### Respuesta con Puntos
```json
{
    "id": 42, "folio": "TK-2026-0042",
    "estado_ciclo": "cerrado",
    "...",
    "puntos_nexus": {
        "puntos_otorgados": 2,
        "puntos_totales": 156,
        "rango_nivel": 3,
        "rango_titulo": "Técnico de Soporte",
        "mensaje_nexus": "🏅 +2 puntos NEXUS — ticket cerrado correctamente"
    }
}
```

---

## Acción: `lista_por_casino` (GET)

**URL:** `GET /api/tickets/lista-por-casino/{casino_id}/`

Retorna tickets **activos y no cerrados** del casino, con estadísticas:

```json
{
    "tickets": [...],
    "estadisticas": {
        "total": 15,
        "criticos": 3,
        "sin_tecnico": 7
    }
}
```

---

## Acción: `historial_maquina` (GET)

**URL:** `GET /api/tickets/historial-maquina/{maquina_id}/`

Retorna los últimos 3 tickets de la máquina. Incluye las bitácoras de cada ticket:

```json
{
    "maquina_id": "15",
    "total_tickets": 3,
    "historial": [
        {
            "id": 42,
            "folio": "TK-2026-0042",
            "bitacoras": [...]
        }
    ]
}
```

Usa `prefetch_related('bitacoras', 'bitacoras__usuario_tecnico')` para evitar N+1.

---

## Acción: `reabrir` (PATCH)

**URL:** `PATCH /api/tickets/{id}/reabrir/`

Solo funciona en tickets con `estado_ciclo = 'cerrado'`. Incrementa `contador_reaperturas`.

---

## Acción: `dashboard_charts` (GET)

**URL:** `GET /api/tickets/dashboard-charts/{casino_id}/`

Endpoint de inteligencia para el Dashboard. Acepta parámetros de filtro temporal:

| Query Param | Valores | Descripción |
|---|---|---|
| `filtro_tipo` | `dia`, `semana`, `mes` | Granularidad del análisis |
| `fecha` | `YYYY-MM-DD` | Fecha específica (para `dia`) |
| `mes` | `1-12` | Mes objetivo |
| `semana` | `1-4` | Semana del mes (para `semana`) |
| `anio` | `YYYY` | Año (default: año actual) |

Devuelve múltiples datasets para gráficas: tickets por estado, por categoría, tendencia temporal, etc.
