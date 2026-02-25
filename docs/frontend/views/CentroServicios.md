# Vistas — Centro de Servicios

**Ruta base:** `/centro-servicios/`  
**Directorio:** `FrontEnd/src/views/CentroServicios/`  
**Acceso:** Roles operativos (TECNICO, SUPERVISOR SALA, SUP SISTEMAS, GERENCIA, ADMINISTRADOR)

Todas las vistas de esta sección comparten el mismo patrón de componentes:
- `DataTableToolbar` para búsqueda, exportación e impresión.
- PrimeVue `DataTable` con lazy-loading por paginación.
- Dialogo de creación/edición en el mismo componente (sin rutas separadas).
- `computed permisos` derivado de `hasRoleAccess()`.

---

## Maquinas.vue

**Ruta:** `/centro-servicios/maquinas`

### Estado principal

| Ref | Descripción |
|---|---|
| `maquinas` | Array de máquinas recuperadas del backend |
| `casinos`, `modelos`, `denominaciones` | Catálogos para los selectores del formulario |
| `estadisticas` | `{ total, danadas, porcentaje_danadas }` — tarjetas de resumen |
| `maquinaDialog` | Visibilidad del diálogo crear/editar |
| `maquina` | Objeto en edición / nuevo |
| `detalleDialog` | Visibilidad del panel de historial de tickets de la máquina |
| `historialTickets` | Tickets pasados de la máquina seleccionada |

### Computed de permisos

```javascript
const permisos = computed(() => ({
    puedeCrear:    hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS']),
    puedeEditar:   hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'TECNICO', 'SUP SISTEMAS']),
    puedeEliminar: hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN']),
}));
```

### Flujo

1. `onMounted` → `cargarMaquinas()` + `cargarCasinos()` + `cargarModelos()`
2. Guardar → `guardarMaquina()` de `maquinaService.js`
3. Detalle → `GET /maquinas/{id}/historial-tickets/`

---

## Tickets.vue

**Ruta:** `/centro-servicios/tickets`

### Estado principal

| Ref | Descripción |
|---|---|
| `tickets` | Lista completa |
| `maquinas`, `tecnicos` | Para los selectores del formulario |
| `estadisticas` | `{ total, criticos, sin_tecnico }` |
| `ticketDialog` | Crear/editar ticket manual |
| `detalleDialog` | Panel completo del ticket con bitácoras |
| `bitacoras` | Bitácoras de un ticket específico |
| `nuevaBitacora` | Objeto en construcción para agregar bitácora |
| `guardandoBitacora` | Loader del guardado de bitácora |

### Acción principal

- Crear ticket → `crearTicket()` de `ticketService.js` (5 pasos orquestados).
- Crear bitácora técnica → `crearBitacoraTecnica()` de `ticketService.js`.
- Ver detalle → carga ticket + bitácoras en `detalleDialog`.

---

## WikiCentroServicios.vue

**Ruta:** `/centro-servicios/wiki`

### Funcionalidad

- Lista artículos publicados (wikiPublica.listar()).
- Filtrado por categoría + búsqueda libre.
- Dialog "Proponer artículo" → `wikiPublica.enviarPropuesta(formData)` (con adjunto PDF).
- Link "Mis propuestas" → `wikiPublica.misPropuestas()`.

---

## TiendaRecompensas.vue (versión técnico)

**Ruta:** `/centro-servicios/tienda`

- Lista recompensas activas del casino.
- Botón "Canjear" → `tiendaTecnico.canjear(id)` — descuenta puntos.
- Panel lateral → `tiendaTecnico.miRango()` — muestra `InsigniaRangoAnimada`.
- Historial → `tiendaTecnico.misCanjes()`.

---

## MapaSala.vue

**Ruta:** `/centro-servicios/mapa`

Digital Twin de la sala de casino.

- Carga con `obtenerMapaCasino()` de `mapaService.js`.
- Selectores de casino/piso/área → recarga el mapa.
- Drag & Drop para reposicionar máquinas → `actualizarCoordenadas()`.
- Celda ocupada (HTTP 409) → muestra toast de error sin bloquear la UI.

---

## Usuarios.vue (Centro de Servicios)

**Ruta:** `/centro-servicios/usuarios`

- CRUD de usuarios del casino del supervisor.
- Solo crea usuarios para su propio casino (campo casino pre-llenado y bloqueado).
- Guardar → `guardarUsuario()` de `usuarioService.js`.

---

## InventarioSala.vue

**Ruta:** `/centro-servicios/inventario`

- CRUD de elementos de inventario (mobiliario, equipos, periféricos).
- Exportación CSV / impresión con `DataTableToolbar`.

---

## MantenimientosPreventivos.vue

**Ruta:** `/centro-servicios/mantenimientos`

- Lista de mantenimientos preventivos programados.
- Acciones: marcar como realizado, reagendar.
- Integra `crearBitacoraTecnica()` para registrar el trabajo en la máquina.

---

## ModelosMaquinas.vue (Centro de Servicios)

**Ruta:** `/centro-servicios/modelos`

- Consulta de catálogo de modelos (solo lectura para técnicos).
- Edición habilitada para SUP SISTEMAS+.

---

## Proveedores.vue (Centro de Servicios)

**Ruta:** `/centro-servicios/proveedores`

- Directorio de proveedores del casino.
- Permisos: escritura solo para roles de gestión.

---

## IncidenciasInfraestructura.vue

**Ruta:** `/centro-servicios/incidencias`

- CRUD de incidencias de infraestructura física (HVAC, instalaciones eléctricas, etc.).
- `signals.py` en backend envía notificaciones al técnico asignado.
