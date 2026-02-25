# TareaEspecial — Tareas Extraordinarias de Mantenimiento

**Archivo fuente:** `BackEnd/TareasEspeciales/models.py`  
**Hereda de:** `ModeloBase`  
**Tabla BD:** `tareas_especiales`  
**Propósito:** Gestiona actividades técnicas que no encajan en el flujo de tickets (no están ligadas a una máquina específica) ni en mantenimientos preventivos. Ejemplos: reubicación de equipos, instalación de cableado, configuración de red.

---

## Campos

| Campo | Tipo Django | Nulo | Default | Descripción |
|---|---|---|---|---|
| `titulo` | `CharField(150)` | No | — | Descripción breve de la actividad |
| `descripcion` | `TextField` | No | — | Detalle técnico o requerimientos |
| `casino` | `ForeignKey(Casino)` | No | — | Ubicación donde se realiza. `CASCADE` |
| `creado_por_usuario` | `ForeignKey(Usuarios)` | No | — | Usuario que registra la tarea. `PROTECT` |
| `asignado_a` | `ForeignKey(Usuarios)` | Sí | `None` | Técnico que se auto-asigna. `SET_NULL` |
| `prioridad` | `CharField(20)` | No | `'media'` | Urgencia (choices) |
| `estatus` | `CharField(20)` | No | `'pendiente'` | Estado de avance (choices) |
| `fecha_apertura` | `DateTimeField` | No | `timezone.now` | Momento de creación de la tarea |
| `fecha_finalizacion` | `DateTimeField` | Sí | `None` | Auto-rellenado al completar (ver `save()`) |
| `resultado_final` | `TextField` | Sí | `None` | Observaciones sobre el resultado |
| *+ campos heredados de ModeloBase* | | | | |

---

## Choices

### `PRIORIDAD_CHOICES`
| Valor | Etiqueta |
|---|---|
| `baja` | Baja |
| `media` | Media |
| `alta` | Alta |
| `critica` | Crítica / Inmediata |

### `ESTADO_TAREA_CHOICES`
| Valor | Etiqueta |
|---|---|
| `pendiente` | Pendiente |
| `en_curso` | En Curso |
| `completada` | Terminada → dispara +20 pts gamificación |
| `cancelada` | Cancelada |

---

## `save()` — Cierre Automático

```python
def save(self, *args, **kwargs):
    if self.estatus == 'completada' and not self.fecha_finalizacion:
        self.fecha_finalizacion = timezone.now()
    super().save(*args, **kwargs)
```

Al marcar la tarea como `completada`, si `fecha_finalizacion` aún está vacía, se registra automáticamente el timestamp actual. Esto asegura que siempre haya una fecha de cierre sin depender del frontend.

---

## Gamificación

Completar una tarea especial otorga **+20 puntos** al `asignado_a`, disparado por la signal `gamif_tarea_completada` en `Gamificacion/signals_gamificacion.py`.

---

## class Meta

```python
class Meta:
    db_table = 'tareas_especiales'
    verbose_name = "Tarea Especial"
    verbose_name_plural = "Tareas Especiales"
```
