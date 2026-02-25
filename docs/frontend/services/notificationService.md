# notificationService.js — Sistema de Notificaciones

**Archivo fuente:** `FrontEnd/src/service/notificationService.js`

Instancia Axios **independiente** de `api.js` para evitar interferencia de los interceptores de redireccionamiento automático en el polling de notificaciones.

---

## Arquitectura del Sistema

```
Notificacion (mensaje)
       │ 1:N
NotificacionUsuario (quién la leyó)
```

El campo `leido` se calcula en el backend dinámicamente: si existe un registro en `NotificacionUsuario` para el usuario actual → `leido=true`.

---

## Segmentación de Notificaciones

El backend filtra automáticamente las notificaciones visibles para el usuario según:

| Tipo | Condición |
|---|---|
| Global | `es_global=True` |
| Personal | `usuario_destino == usuario_actual` |
| Por casino | `casino_destino == casino_del_usuario` |
| Por rol | `rol_destino == rol_del_usuario` |
| Casino + rol | Combinación de los últimos dos |

---

## Funciones Disponibles

### `fetchNotificaciones()`

```javascript
const response = await fetchNotificaciones();
// → { success: true, data: Array<Notificacion> }
```

Devuelve todas las notificaciones visibles para el usuario. Cada notificación incluye el campo `leido` calculado dinámicamente.

**Llamada:** `GET /notificaciones/`

### `fetchNotificacionesNoLeidas()`

```javascript
const response = await fetchNotificacionesNoLeidas();
// → { success: true, count: 5 }
```

Endpoint **optimizado para polling**. No devuelve datos completos, solo el contador. Usa `EXISTS()` en el backend para máxima eficiencia.

**Llamada:** `GET /notificaciones/count-no-leidas/`

### `marcarNotificacionLeida(notificacionId)` *(recomendado)*

```javascript
await marcarNotificacionLeida(16);
// → { success: true, data: { ... } }
```

Crea o actualiza el registro en `NotificacionUsuario` usando `get_or_create()` (idempotente).

**Llamada:** `PATCH /notificaciones/{id}/marcar-leida/`

### `crearLecturaNotificacion(notificacionId)` *(alternativa)*

```javascript
const result = await crearLecturaNotificacion(16);
// → { success: true, created: false } ← ya existía
```

Crea directamente en `NotificacionUsuario`. Devuelve `created: true/false` para saber si ya existía. Usar solo cuando se necesite saber si el registro ya existía.

**Llamada:** `POST /notificaciones-usuarios/`

---

## Polling en AppTopbar

```javascript
// Cada 45 segundos
pollingInterval = setInterval(cargarNotificaciones, 45000);
onUnmounted(() => clearInterval(pollingInterval));
```

El badge de notificaciones se actualiza automáticamente. No se usa WebSocket ni SSE — el polling cada 45s es suficiente para la frecuencia de eventos del sistema.

---

## Mapeo Visual de Notificaciones

### Por tipo

| Tipo | Ícono PrimeVue | Color |
|---|---|---|
| `ticket` | `pi pi-ticket` | `text-blue-500` |
| `infraestructura` | `pi pi-exclamation-triangle` | `text-red-500` |
| `wiki` | `pi pi-book` | `text-green-500` |
| `sistema` | `pi pi-info-circle` | `text-purple-500` |
| `DIRECTOR` | `pi pi-star-fill` | `text-yellow-500` |

### Por nivel de urgencia

| Nivel | Ícono | Color |
|---|---|---|
| `urgente` | `pi pi-times-circle` | `text-red-600` |
| `alerta` | `pi pi-exclamation-triangle` | `text-orange-500` |
| `informativa` | `pi pi-info-circle` | `text-blue-500` |

> Las notificaciones `urgente` priorizan la configuración visual por nivel sobre la de tipo.

---

## Flujo Completo de una Notificación

```
Backend (incidencia CRÍTICA creada)
    → signal crea Notificacion con es_global=True

AppTopbar (polling 45s)
    → fetchNotificaciones()
    → leido=false (sin registro en NotificacionUsuario)
    → badge muestra +1

Usuario hace clic en la notificación
    → marcarNotificacionLeida(id)
    → Backend crea NotificacionUsuario
    → leido=true en próxima actualización

Siguiente polling (45s)
    → fetchNotificaciones()
    → leido=true → ya no se cuenta en el badge
```
