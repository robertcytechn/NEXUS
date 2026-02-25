# Casino — Modelo de Sede/Sucursal

**Archivo fuente:** `BackEnd/Casinos/models.py`  
**Hereda de:** `ModeloBase`  
**Tabla BD:** `casinos`  
**Propósito:** Representa cada sede física del grupo casino. Es la **entidad raíz** del sistema: usuarios, máquinas, tickets, inventario y casi todos los demás módulos apuntan a un `Casino`.

---

## Campos

| Campo | Tipo Django | Nulo | Único | Default | Descripción |
|---|---|---|---|---|---|
| `nombre` | `CharField(100)` | No | ✅ | — | Nombre oficial de la sede (ej. "Casino Monterrey Norte") |
| `identificador` | `CharField(50)` | Sí | ✅ | `None` | Código interno o número de licencia |
| `direccion` | `CharField(255)` | No | No | — | Dirección postal completa |
| `telefono` | `CharField(20)` | Sí | No | `None` | Teléfono de contacto |
| `ciudad` | `CharField(100)` | No | No | — | Ciudad donde se ubica |
| `encargado` | `CharField(100)` | Sí | No | `None` | Nombre del responsable operativo |
| `horario_apertura` | `TimeField` | Sí | No | `None` | Hora de apertura |
| `horario_cierre` | `TimeField` | Sí | No | `None` | Hora de cierre |
| `grid_width` | `PositiveIntegerField` | No | No | `50` | Columnas del mapa de sala (Digital Twin) |
| `grid_height` | `PositiveIntegerField` | No | No | `50` | Filas del mapa de sala (Digital Twin) |
| *+ campos heredados de ModeloBase* | | | | | `esta_activo`, `creado_en`, `modificado_en`, etc. |

---

## Mapa de Sala (Digital Twin)

Los campos `grid_width` y `grid_height` definen la cuadrícula del **mapa interactivo** de la sala en el frontend. Cada `Maquina` tiene coordenadas `(coordenada_x, coordenada_y)` que deben caer dentro de este rango.

```
grid_width  = 50  →  columnas 0..50
grid_height = 50  →  filas    0..50
```

> **Decisión de diseño:** Guardar la dimensión en el Casino (no en la máquina) permite que el frontend renderice el canvas correctamente con un solo GET, sin iterar máquinas.

---

## Método `clean()` — Validación de Redimensionamiento

```python
def clean(self):
    super().clean()
    ...
    # Verifica que ninguna máquina existente quede fuera del nuevo grid
    max_x = Maquina.objects.filter(casino=self).aggregate(Max('coordenada_x'))['coordenada_x__max']
    max_y = Maquina.objects.filter(casino=self).aggregate(Max('coordenada_y'))['coordenada_y__max']

    if max_x is not None and self.grid_width < max_x:
        raise ValidationError({"grid_width": f"El ancho no puede ser menor a {max_x}..."})
    if max_y is not None and self.grid_height < max_y:
        raise ValidationError({"grid_height": f"El alto no puede ser menor a {max_y}..."})
```

**Por qué:** Si un administrador reduce el tamaño del grid, máquinas ya posicionadas quedarían "fuera del mapa". Esta validación previene ese estado corrupto. El import de `Maquina` es local (dentro del método) para evitar **importaciones circulares** (`Maquinas` depende de `Casinos`, y si `Casinos` importara `Maquinas` a nivel módulo, se generaría un ciclo).

---

## Relaciones Inversas Notables

| `related_name` | Desde | Descripción |
|---|---|---|
| `maquinas` | `Maquina` | Todas las máquinas de este casino |
| `proveedores_locales` | `Proveedor` | Proveedores registrados para esta sede |
| `notificaciones_sala` | `Notificacion` | Notificaciones dirigidas a este casino |
| `recompensas_gamificacion` | `RecompensaGamificacion` | Recompensas disponibles en esta sede |
| `relevos` | `RelevoTurno` | Relevos de turno del casino |
| `incidencias_infra` | `IncidenciaInfraestructura` | Incidencias de infraestructura |

---

## class Meta

```python
class Meta:
    db_table = 'casinos'
    verbose_name = "Casino"
    verbose_name_plural = "Casinos"
    ordering = ['nombre']
```

El ordering por `nombre` hace que cualquier listado de casinos (combos, tablas) aparezca en orden alfabético sin necesidad de especificarlo en la query.
