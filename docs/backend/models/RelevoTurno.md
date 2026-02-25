# RelevoTurno — Documentación de Cambio de Turno

**Archivo fuente:** `BackEnd/RelevosTurnos/models.py`  
**Hereda de:** `ModeloBase`  
**Tabla BD:** `ope_relevo_turnos`  
**Propósito:** Formaliza la transferencia de información entre el técnico que termina su jornada y el que la inicia. Garantiza continuidad operativa al documentar pendientes y novedades.

---

## Campos

| Campo | Tipo Django | Nulo | Default | Descripción |
|---|---|---|---|---|
| `casino` | `ForeignKey(Casino)` | No | — | Sede donde ocurre el relevo. `CASCADE` |
| `tecnico_saliente` | `ForeignKey(Usuarios)` | No | — | Quien termina el turno. `PROTECT` |
| `tecnico_entrante` | `ForeignKey(Usuarios)` | No | — | Quien inicia el turno. `PROTECT` |
| `hora_salida_real` | `DateTimeField` | No | — | Timestamp de salida del técnico saliente |
| `estado_entrega` | `CharField(20)` | No | `'limpia'` | Evaluación general de la sala (choices) |
| `pendientes_detallados` | `TextField` | Sí | `None` | Lista de máquinas o tareas sin concluir |
| `novedades_generales` | `TextField` | Sí | `None` | Comentarios relevantes sobre personal o sala |
| *+ campos heredados de ModeloBase* | | | | |

---

## Choices `ESTADO_SALA_CHOICES`

| Valor | Etiqueta |
|---|---|
| `limpia` | Sin Pendientes / Todo Operativo |
| `con_pendientes` | Con Pendientes Menores |
| `critica` | Situación Crítica / Urgente |

---

## Gamificación

Documentar un relevo de turno otorga **+2 puntos** al `tecnico_saliente`, disparado por la signal `gamif_relevo_creado`.

---

## class Meta

```python
class Meta:
    db_table = 'ope_relevo_turnos'
    verbose_name = "Relevo de Turno"
    verbose_name_plural = "Relevos de Turnos"
```
