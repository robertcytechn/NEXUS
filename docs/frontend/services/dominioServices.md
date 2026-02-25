# Servicios de Dominio — maquinaService, mapaService, usuarioService, wikiService, auditoriaService

**Directorio fuente:** `FrontEnd/src/service/`

Servicios especializados que encapsulan lógica de dominio junto con las llamadas HTTP.

---

## maquinaService.js

### `guardarMaquina(maquinaData, esEdicion)`

Función unificada de creación y edición de máquinas con validaciones previas en el cliente.

**Validaciones antes de la petición:**
- `uid_sala` requerido
- `numero_serie` requerido
- `casino` requerido
- `modelo` requerido

**Formateo automático de fechas:**
```javascript
// Convierte Date a 'YYYY-MM-DD' antes de enviar
if (payload.ultimo_mantenimiento) payload.ultimo_mantenimiento = formatDate(payload.ultimo_mantenimiento);
if (payload.fecha_vencimiento_licencia) payload.fecha_vencimiento_licencia = formatDate(payload.fecha_vencimiento_licencia);
```

**Enrutamiento dinámico:**
```javascript
if (esEdicion && payload.id) response = await api.put(`maquinas/${payload.id}/`, payload);
else                         response = await api.post('maquinas/', payload);
```

**Manejo de errores específicos de backend:**

| Error backend | Error al usuario |
|---|---|
| `400 ip_maquina` | "IP Duplicada" |
| `400 numero_serie` | "Serie Duplicada" |
| `400 uid_sala` | "UID Duplicado" |

---

## mapaService.js

Servicio para el Digital Twin (mapa interactivo de sala).

### `obtenerMapaCasino(casinoId, piso?, area?)`

```javascript
const result = await obtenerMapaCasino(2, 'PISO_1', 'SALA_A');
// → { exito, data: { casino, pisos_disponibles, areas_disponibles, piso_choices, sala_choices, maquinas, total } }
```

Llama a `GET /maquinas/mapa-completo/?casino_id=2&piso=PISO_1&area=SALA_A`

### `actualizarCoordenadas(maquinaId, x, y)`

```javascript
const result = await actualizarCoordenadas(15, 5, 3);
// → { exito, data, mensaje }
```

Traduce el HTTP 409 en un mensaje específico de colisión:
```javascript
if (status === 409) mensaje = 'Ya existe una máquina en esa posición de la sala';
```

---

## usuarioService.js

### `guardarUsuario(usuarioData, esEdicion)`

Mismo patrón que `guardarMaquina`. Validaciones previas:
- `nombres`, `apellido_paterno`, `username`, `email`, `casino`, `rol` requeridos
- Si es creación (`!esEdicion`): `password` requerido
- Si es edición y no se envió password: se elimina del payload antes de `PUT`

```javascript
if (esEdicion && payload.id && !payload.password) delete payload.password;
```

---

## wikiService.js

Organiza las funciones en **4 objetos** según el actor y contexto:

### `wikiAdmin` — Centro de Mando (Administrador)

| Método | HTTP | Endpoint |
|---|---|---|
| `listar()` | GET | `/wiki/centro-mando/` |
| `pendientes()` | GET | `/wiki/centro-mando/pendientes/` |
| `aprobar(id, payload)` | POST | `/wiki/centro-mando/{id}/aprobar/` |
| `publicar(id, payload)` | POST | `/wiki/centro-mando/{id}/publicar/` |
| `rechazar(id, payload)` | POST | `/wiki/centro-mando/{id}/rechazar/` |
| `eliminar(id)` | DELETE | `/wiki/centro-mando/{id}/` |

### `wikiPublica` — Centro de Servicios (Técnicos)

| Método | HTTP | Endpoint |
|---|---|---|
| `listar()` | GET | `/wiki/centro-servicios/` |
| `reglas()` | GET | `/wiki/centro-servicios/reglas/` |
| `enviarPropuesta(formData)` | POST | `/wiki/centro-servicios/` con `multipart/form-data` |
| `misPropuestas()` | GET | `/wiki/centro-servicios/mis-propuestas/` |

> `enviarPropuesta` usa `multipart/form-data` porque incluye el archivo PDF:
> ```javascript
> api.post('wiki/centro-servicios/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
> ```

### `tiendaGerencia` — Tienda (Gerencia)

| Método | Descripción |
|---|---|
| `listarRecompensas()` | GET lista de recompensas del casino |
| `crearRecompensa(data)` | POST nueva recompensa |
| `editarRecompensa(id, data)` | PUT actualizar recompensa |
| `toggleActivo(id)` | POST activar/desactivar |
| `eliminar(id)` | DELETE |
| `historialCanjes()` | GET todos los canjes del casino |
| `entregarCanje(recompensaId, canjeId, payload)` | POST marcar como entregado |

### `tiendaTecnico` — Tienda Técnico

| Método | Descripción |
|---|---|
| `listarRecompensas()` | GET recompensas activas |
| `miRango()` | GET puntos y rango del técnico |
| `misCanjes()` | GET historial personal de canjes |
| `canjear(id)` | POST canjear una recompensa |

---

## auditoriaService.js

Servicio simple sin lógica de dominio adicional.

| Función | HTTP | Descripción |
|---|---|---|
| `getAuditoriaHistorial(filtros)` | GET `/auditoria-sistema/?{filtros}` | Lista paginada de logs |
| `getTablasAfectadas()` | GET `/auditoria-sistema/tablas_afectadas/` | Lista de tablas con logs |

Lanza la excepción si falla (no envuelve en `{exito, error}` como los otros servicios) — el componente que la llama maneja el `catch`.

---

## Servicios Simples (sin lógica adicional)

Los siguientes servicios son wrappers directos de axios y se documentan brevemente:

| Archivo | Función principal | Endpoint |
|---|---|---|
| `modeloService.js` | CRUD de modelos de máquina | `/modelos/` |
| `proveedorService.js` | CRUD de proveedores | `/proveedores/` |
| `tareasEspecialesService.js` | CRUD de tareas especiales | `/tareas/` |
| `infraestructuraService.js` | CRUD de incidencias | `/incidencias/` |
| `inventarioSalaService.js` | CRUD de inventario | `/inventario/` |
| `EvolucionService.js` | Lista cambios de versión | `/evolucion/` |
