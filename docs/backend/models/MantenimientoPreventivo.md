# MantenimientoPreventivo — Registro de Rutinas Preventivas

**Archivo fuente:** `BackEnd/MantenimientosPreventivos/models.py`  
**Hereda de:** `ModeloBase`  
**Tabla BD:** `maquina_mantenimientos`  
**Propósito:** Documenta cada rutina preventiva (limpieza, revisión, calibración programada) ejecutada sobre una máquina. Al guardarse, dispara automáticamente la actualización de la fecha de último mantenimiento y el estado de la máquina.

---

## Campos

| Campo | Tipo Django | Nulo | Default | Descripción |
|---|---|---|---|---|
| `maquina` | `ForeignKey(Maquina)` | No | — | Unidad intervenida. `CASCADE` |
| `tecnico_responsable` | `ForeignKey(Usuarios)` | No | — | Técnico que ejecutó el mantenimiento. `PROTECT` |
| `fecha_mantenimiento` | `DateField` | No | — | Fecha de ejecución de la rutina |
| `estado_final_maquina` | `CharField(30)` | No | `'operativa'` | Estado en que queda la máquina tras el mantenimiento |
| `observaciones` | `TextField` | Sí | `None` | Notas adicionales (ej. desgaste detectado) |
| *+ campos heredados de ModeloBase* | | | | |

---

## Choices `ESTADO_RESULTANTE_CHOICES`

| Valor | Etiqueta |
|---|---|
| `operativa` | Operativa |
| `dañada_operativa` | Dañada pero Operativa |
| `dañada` | Dañada |
| `observacion` | En Observación |

---

## Signal Interna: `actualizar_estatus_maquina_preventivo`

Este modelo define su propia signal dentro del mismo archivo:

```python
@receiver(post_save, sender=MantenimientoPreventivo)
def actualizar_estatus_maquina_preventivo(sender, instance, created, **kwargs):
    if created:
        maquina = instance.maquina
        maquina.ultimo_mantenimiento = instance.fecha_mantenimiento
        maquina.estado_actual = instance.estado_final_maquina
        maquina.save(update_fields=['ultimo_mantenimiento', 'estado_actual', 'modificado_en'])
```

**Por qué `update_fields`:** Al especificar solo los campos que cambian, se evita:
1. Ejecutar el `full_clean()` del modelo `Maquina` (que validaría todas las coordenadas, IPs, etc.)
2. Actualizar campos como `puntos_gamificacion` o datos de red innecesariamente
3. Reducir el tiempo de la query SQL

---

## Gamificación

Registrar un mantenimiento preventivo otorga **+50 puntos** al `tecnico_responsable` (la recompensa más alta de todas las acciones del sistema), disparada por la signal `gamif_mantenimiento_creado`.

---

## class Meta

```python
class Meta:
    db_table = 'maquina_mantenimientos'
    verbose_name = "Mantenimiento Preventivo"
    verbose_name_plural = "Mantenimientos Preventivos"
```
