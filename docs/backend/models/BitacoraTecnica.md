# BitacoraTecnica — Entradas de Intervención Técnica

**Archivo fuente:** `BackEnd/BitacoraTecnica/models.py`  
**Hereda de:** `ModeloBase`  
**Tabla BD:** `tickets_bitacora`  
**Propósito:** Registro cronológico de cada intervención realizada por un técnico sobre un ticket. Múltiples bitácoras pueden pertenecer a un mismo ticket, formando el historial completo de una reparación.

---

## Campos

| Campo | Tipo Django | Nulo | Default | Descripción |
|---|---|---|---|---|
| `ticket` | `ForeignKey(Ticket)` | No | — | Ticket al que pertenece esta entrada. `CASCADE` |
| `usuario_tecnico` | `ForeignKey(Usuarios)` | No | — | Técnico que registra la anotación. `PROTECT` |
| `tipo_intervencion` | `CharField(30)` | No | — | Categoría del trabajo (choices) |
| `descripcion_trabajo` | `TextField` | No | — | Detalle técnico de pruebas y acciones |
| `resultado_intervencion` | `CharField(30)` | No | — | Resultado de la reparación (choices) |
| `estado_maquina_resultante` | `CharField(30)` | No | — | Estado físico en que queda la máquina |
| `finaliza_ticket` | `BooleanField` | No | `False` | Si `True`, indica que esta entrada cierra el ticket |
| *+ campos heredados de ModeloBase* | | | | |

---

## Choices

### `TIPO_INTERVENCION_CHOICES`
| Valor | Etiqueta |
|---|---|
| `correctiva` | Correctiva (Reparación) |
| `ajuste` | Ajuste / Calibración |
| `instalacion` | Instalación / Movimiento |
| `actualización` | Actualización de Software |
| `diagnostico` | Solo Diagnóstico |

### `RESULTADO_CHOICES`
| Valor | Etiqueta |
|---|---|
| `exitosa` | Reparación Exitosa |
| `parcial` | Reparación Parcial |
| `fallida` | Prueba Fallida |
| `espera_refaccion` | En espera de Refacción |

### `estado_maquina_resultante` (inline choices)
| Valor | Etiqueta |
|---|---|
| `operativa` | Operativa |
| `dañada_operativa` | Dañada pero Operativa |
| `dañada` | Dañada |
| `mantenimiento` | En Mantenimiento |

---

## Relación con Ticket

```
Ticket (1) ──────── (N) BitacoraTecnica
```

La relación inversa `ticket.bitacoras.all()` se usa en múltiples serializadores para mostrar el historial de intervenciones dentro del detalle del ticket.

---

## Gamificación

Crear una entrada de bitácora otorga **+2 puntos** al `usuario_tecnico` mediante la signal `gamif_bitacora_creada` en `Gamificacion/signals_gamificacion.py`.

---

## class Meta

```python
class Meta:
    db_table = 'tickets_bitacora'
    verbose_name = "Entrada de Bitácora"
    verbose_name_plural = "Bitácoras Técnicas"
```
