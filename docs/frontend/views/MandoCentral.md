# Vistas — Mando Central

**Ruta base:** `/mando-central/`  
**Directorio:** `FrontEnd/src/views/MandoCentral/`  
**Acceso:** Roles de gestión y administración (GERENCIA, SUP SISTEMAS, ADMINISTRADOR, DB ADMIN)

---

## AuditoriaGlobal.vue

**Ruta:** `/mando-central/auditoria`

### Estado principal

| Ref | Descripción |
|---|---|
| `historial` | Logs paginados del sistema |
| `totalRecords` | Total para paginación server-side |
| `expandedRows` | Filas expandidas (muestra JSON old/new) |
| `listaTablas` | Catálogo de tablas (desde `getTablasAfectadas()`) |
| `listaAcciones` | `['CREATE', 'UPDATE', 'DELETE']` |
| `filtros` | `{ tabla, accion, usuario, fecha_desde, fecha_hasta }` |
| `pageConfig` | `{ page, size }` |
| `showJson` | Toggle para mostrar diff JSON por fila |

### Notas técnicas

- Paginación server-side → el DataTable emite `page` → llama `getAuditoriaHistorial(filtros + page)`.
- Filas expandidas muestran `datos_anteriores` / `datos_nuevos` formateados con `JSON.stringify(…, null, 2)`.

---

## BitacoraTecnica.vue

**Ruta:** `/mando-central/bitacora`

Vista de solo lectura — histórico completo de intervenciones técnicas en todas las máquinas del casino. filtros: maquina, tecnico, fecha, tipo. Exportable.

---

## Casinos.vue

**Ruta:** `/mando-central/casinos`

CRUD completo de casinos (establecimientos). Solo ADMINISTRADOR / DB ADMIN pueden crear/eliminar. GERENCIA puede editar datos de su propio casino.

---

## GestorMenus.vue

**Ruta:** `/mando-central/menus`

Administración del árbol de menú dinámico. Permite:
- Crear/editar/eliminar ítems de menú.
- Asignar roles permitidos por ítem.
- Reordenar con drag & drop.
- Activar/desactivar ítems sin eliminarlos.

> Los cambios aquí afectan el menú que ve TODO el sistema en la próxima carga de sesión (el router carga el menú en la inicialización).

---

## Maquinas.vue (Mando Central)

**Ruta:** `/mando-central/maquinas`

Igual que la vista de Centro de Servicios pero con permisos ampliados:
- Puede editar máquinas de cualquier casino (no solo el propio).
- Puede eliminar.
- Accede a reportes globales, no filtrados por casino.

---

## Tickets.vue (Mando Central)

**Ruta:** `/mando-central/tickets`

Vista global de tickets — ve tickets de todos los casinos. Puede reasignar técnicos entre casinos.

---

## Usuarios.vue (Mando Central)

**Ruta:** `/mando-central/usuarios`

CRUD completo sin restricción de casino. El admin puede:
- Cambiar el casino de un usuario.
- Asignar cualquier rol (incluyendo ADMINISTRADOR).
- Resetear contraseña.
- Activar/desactivar cuenta.

---

## Roles.vue

**Ruta:** `/mando-central/roles`

- Lista de roles del sistema.
- Solo lectura en producción normal.
- Permite vincular permisos de menú por rol (integración con GestorMenus).

---

## NotificacionesEspeciales.vue

**Ruta:** `/mando-central/notificaciones`

Creación de notificaciones manuales (broadcasts):
- `tipo`: informativa, alerta, urgente.
- `destinatario`: todos, por casino, por rol, individual.
- Historial de notificaciones enviadas.

---

## WikiMandoCentral.vue

**Ruta:** `/mando-central/wiki`

Panel de administración de la Wiki:
- Lista artículos pendientes de aprobación (`wikiAdmin.pendientes()`).
- Flujo de moderación: `aprobar()` → `publicar()` o `rechazar()`.
- Lista completa de artículos publicados con opción de eliminar.

---

## TiendaRecompensas.vue (Gerencia)

**Ruta:** `/mando-central/tienda`

Panel de gestión de la Tienda:
- CRUD de recompensas (`tiendaGerencia.crearRecompensa`, `editarRecompensa`, `toggleActivo`).
- Historial de canjes con filtros.
- Marcar entrega física → `tiendaGerencia.entregarCanje()`.

---

## MantenimientosPreventivos.vue (Mando Central)

**Ruta:** `/mando-central/mantenimientos`

Vista global de mantenimientos — todos los casinos. Puede programar planes de mantenimiento para múltiples máquinas en lote.

---

## ModelosMaquinas.vue (Mando Central)

**Ruta:** `/mando-central/modelos`

CRUD completo de modelos de máquina (catálogo maestro). ADMINISTRADOR / DB ADMIN únicamente.

---

## Proveedores.vue (Mando Central)

**Ruta:** `/mando-central/proveedores`

CRUD global de proveedores. Puede vincular proveedores a múltiples casinos.

---

## IncidentesInfraestructura.vue

**Ruta:** `/mando-central/incidentes`

Vista global de incidencias de infraestructura (todos los casinos). Puede asignar técnicos de cualquier casino.

---

## TareasEspeciales.vue

**Ruta:** `/mando-central/tareas`

CRUD de tareas especiales (inspecciones gubernamentales, auditorías externas, calibraciones). Asignables a técnicos específicos con fecha límite.
