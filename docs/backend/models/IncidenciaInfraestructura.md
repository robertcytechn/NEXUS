# IncidenciaInfraestructura — Eventos de Infraestructura Física

**Archivo fuente:** `BackEnd/IncidenciasInfraestructura/models.py`  
**Hereda de:** `ModeloBase`  
**Tabla BD:** `infra_incidencias`  
**Propósito:** Registro de eventos externos o de infraestructura que afectan la operación del casino (apagones, goteras, fallas de AC, etc.). Diferente a un `Ticket` que apunta a una máquina específica, una incidencia de infraestructura afecta a la sala en general.

---

## Campos

| Campo | Tipo Django | Nulo | Default | Descripción |
|---|---|---|---|---|
| `casino` | `ForeignKey(Casino)` | No | — | Sala afectada. `CASCADE` |
| `titulo` | `CharField(150)` | No | — | Resumen corto del evento (ej. "Apagón zona sur") |
| `categoria` | `CharField(30)` | No | — | Origen del problema (choices) |
| `descripcion` | `TextField` | No | — | Relato completo y afectaciones visibles |
| `severidad` | `CharField(20)` | No | `'media'` | Impacto en la operación (choices) |
| `afecta_operacion` | `BooleanField` | No | `False` | Marcado si obligó a detener máquinas o servicios |
| `hora_inicio` | `DateTimeField` | No | — | Inicio del incidente |
| `hora_fin` | `DateTimeField` | Sí | `None` | Resolución. `None` = incidente activo |
| *+ campos heredados de ModeloBase* | | | | |

---

## Choices

### `CATEGORIA_CHOICES`
| Valor | Etiqueta |
|---|---|
| `electrica` | Falla Eléctrica / Luz |
| `agua` | Filtración / Agua / Gotera |
| `clima` | Climatización / Aire Acondicionado |
| `red_externa` | Proveedor de Internet / Enlace |
| `obra_civil` | Estructura / Paredes / Techos |
| `otros` | Otros Eventos Externos |

### `SEVERIDAD_CHOICES`
| Valor | Etiqueta | Notificación Generada |
|---|---|---|
| `baja` | Baja (Sin afectación) | Alerta a SUP SISTEMAS |
| `media` | Media (Afectación parcial) | Alerta a SUP SISTEMAS |
| `alta` | Alta (Riesgo operativo) | 🚨 URGENTE a SUP SISTEMAS + GERENCIA |
| `critica` | Crítica (Cierre de sala/área) | 🚨 URGENTE a SUP SISTEMAS + GERENCIA |

---

## Señales Disparadas

Este modelo dispara signals en `IncidenciasInfraestructura/signals.py`:

1. **Incidencia creada:** Genera notificación según severidad
2. **Incidencia resuelta** (cuando `hora_fin` pasa de `None` a un valor): Notificación informativa de resolución

---

## class Meta

```python
class Meta:
    db_table = 'infra_incidencias'
    verbose_name = "Incidencia de Infraestructura"
    verbose_name_plural = "Incidencias de Infraestructura"
```
