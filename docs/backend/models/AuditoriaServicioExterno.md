# AuditoriaServicioExterno — Control de Acceso de Personal Externo

**Archivo fuente:** `BackEnd/AuditoriasExternas/models.py`  
**Hereda de:** `ModeloBase`  
**Tabla BD:** `aud_servicios_externos`  
**Propósito:** Registro de cada visita de personal externo (técnicos de proveedores) a las zonas críticas del casino. Documenta quién entró, a qué área, cuándo, y bajo supervisión de quién.

---

## Campos

| Campo | Tipo Django | Nulo | Default | Descripción |
|---|---|---|---|---|
| `casino` | `ForeignKey(Casino)` | No | — | Sede donde se realiza el servicio. `CASCADE` |
| `empresa_proveedora` | `ForeignKey(Proveedor)` | No | — | Empresa que envía al técnico. `PROTECT` (no borrar proveedor si hay auditorías) |
| `nombre_tecnico_externo` | `CharField(150)` | No | — | Nombre completo del técnico externo enviado |
| `supervisor_interno` | `ForeignKey(Usuarios)` | No | — | Personal interno que autoriza y supervisa el acceso. `PROTECT` |
| `area_acceso` | `CharField(50)` | No | — | Zona crítica a la que accedió (choices) |
| `tipo_servicio` | `CharField(50)` | No | — | Motivo técnico de la visita (choices) |
| `descripcion_actividad` | `TextField` | No | — | Detalle de los cambios o revisiones efectuadas |
| `hora_entrada` | `DateTimeField` | No | — | Momento exacto de acceso al área |
| `hora_salida` | `DateTimeField` | Sí | `None` | Momento de retiro. Null mientras el técnico sigue dentro |
| *+ campos heredados de ModeloBase* | | | | |

---

## Choices

### `AREAS_ACCESO_CHOICES`
| Valor | Etiqueta |
|---|---|
| `site_servidores` | Site de Servidores |
| `racks_sala` | Racks de Sala |
| `area_maquinas` | Área de Máquinas (Piso) |
| `oficinas_tecnicas` | Oficinas Técnicas |
| `boveda_conteo` | Bóveda / Área de Conteo |
| `sala` | Sala de Juegos |
| `cocina` | Cocina |
| `comedor` | Comedor |
| `cajas` | Cajas |
| `jv` | JV / Monitoreo |

### `TIPO_SERVICIO_CHOICES`
| Valor | Etiqueta |
|---|---|
| `internet_enlaces` | Internet y Enlaces |
| `climatizacion` | Aire Acondicionado / Clima |
| `energia_ups` | Energía / UPS / Plantas |
| `seguridad_cctv` | Seguridad / CCTV |
| `limpieza_profunda` | Limpieza Especializada |
| `mantenimiento_equipo` | Mantenimiento de Equipo Técnico |
| `fumigacion` | Fumigación / Sanitización |
| `obra_civil` | Reparaciones Locales |

---

## class Meta

```python
class Meta:
    db_table = 'aud_servicios_externos'
    verbose_name = "Auditoría de Servicio Externo"
    verbose_name_plural = "Auditorías de Servicios Externos"
```
