# Frontend — Manual del Programador

**Stack:** Vue 3 · PrimeVue 4 · Tailwind CSS v4 · Vue Router 4 · Axios · Vite 7  
**Directorio fuente:** `FrontEnd/src/`  
**Backend conectado:** `http://{hostname}:8000/api/`

---

## Índice de Documentación

### Configuración

| Archivo | Contenido |
|---|---|
| [configuracion/main.md](configuracion/main.md) | Entry point, PrimeVue, locale ES-MX, z-index |
| [configuracion/router.md](configuracion/router.md) | Rutas dinámicas desde BD, guards, EULA |
| [configuracion/layout.md](configuracion/layout.md) | useLayout(), AppMenu rol-filter, AppTopbar |

### Servicios (capa HTTP + lógica de dominio)

| Archivo | Contenido |
|---|---|
| [services/api.md](services/api.md) | Axios instance, interceptors, localStorage helpers, auth |
| [services/ticketService.md](services/ticketService.md) | crearTicket 5 pasos, crearBitacoraTecnica |
| [services/notificationService.md](services/notificationService.md) | Polling 45s, marcarLeida, instancia propia |
| [services/gamificacionUtils.md](services/gamificacionUtils.md) | mostrarToastPuntos, acumularPuntos |
| [services/dominioServices.md](services/dominioServices.md) | maquinaService, mapaService, usuarioService, wikiService, auditoriaService |

### Componentes

| Archivo | Contenido |
|---|---|
| [components/componentes.md](components/componentes.md) | InsigniaRangoAnimada, TopBarraHerramientas, DataTableToolbar, DashboardCharts, otros |

### Vistas

| Archivo | Contenido |
|---|---|
| [views/CentroServicios.md](views/CentroServicios.md) | 11 vistas — Maquinas, Tickets, Wiki, Tienda, Mapa, etc. |
| [views/MandoCentral.md](views/MandoCentral.md) | 16 vistas — Auditoria, Usuarios admin, GestorMenus, etc. |
| [views/pages.md](views/pages.md) | Dashboard, Login, EULA, Profile, Operatividad, Errores |

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────┐
│                    Vue 3 SPA                        │
│  ┌───────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  Router   │  │    Layout    │  │   PrimeVue  │  │
│  │ (dinámico)│  │  AppTopbar   │  │  Aura/Cyan  │  │
│  │ from DB   │  │  AppMenu     │  │  Toast/Conf │  │
│  └─────┬─────┘  └──────┬───────┘  └─────────────┘  │
│        │               │                            │
│        └───────┬────────┘                           │
│                ↓                                    │
│           Views (pages)                             │
│      CentroServicios / MandoCentral                 │
│                ↓                                    │
│           Services (api.js + *Service.js)           │
│                ↓                                    │
└───────────────────────────────────────────────────-─┘
              HTTP / Axios
                ↓
        Django REST Framework
        http://{hostname}:8000/api/
```

---

## Flujo de Autenticación

```
Login.vue → api.login() → POST /usuarios/login/
    ↓
localStorage: { token, refresh_token, user, rango_usuario }
    ↓
router.beforeEach:
  1. ¿Hay token?           No → /login
  2. ¿EULA aceptada?       No → /lisencia
  3. ¿Rol en requiredRoles? No → /access
  4. Continuar navegación
    ↓
Request interceptor agrega: Authorization: Bearer {token}
    ↓
Response interceptor (401/403) → logout + /login
```

---

## Flujo de Gamificación

```
Técnico crea Ticket o Bitácora
    ↓
Backend calcula puntos y devuelve { puntos_nexus: { puntos_otorgados, rango_anterior, rango_nuevo } }
    ↓
acumularPuntos(baseResponse, adicionalResponse) — suma si hay múltiples llamadas
    ↓
mostrarToastPuntos(toast, puntos) — muestra Toast de éxito con puntos ganados
    ↓
actualizarRangoLocal(rango) — escribe en localStorage + emite 'nexus:rango-actualizado'
    ↓
AppTopbar escucha el evento → actualiza InsigniaRangoAnimada sin recargar
```

---

## Flujo de Notificaciones

```
AppTopbar.onMounted → cargarNotificaciones()
    ↓
setInterval(cargarNotificaciones, 45_000) — cada 45 segundos
    ↓
fetchNotificacionesNoLeidas() → GET /notificaciones/count-no-leidas/
    ↓
Badge rojo en campana
    ↓
Usuario abre panel → fetchNotificaciones() → lista completa
    ↓
Usuario hace clic en notificación → NotificacionDetail.vue
    marcarNotificacionLeida(id) al montar
```

---

## Rutas Dinámicas

```javascript
// router/index.js — Inicialización (top-level await)
const menuData = await api.get('menus/activo/');
// Convierte items del menú en rutas de Vue Router
// import.meta.glob('/src/views/**/*.vue') lazy-carga todas las vistas
```

El menú se edita en tiempo real desde **GestorMenus.vue** — los cambios son efectivos en la **siguiente sesión** del usuario (o al recargar el navegador).

---

## Estructura de localStorage

| Clave | Tipo | Descripción |
|---|---|---|
| `token` | String | Bearer token UUID v4 |
| `refresh_token` | String | Token de renovación |
| `user` | JSON | Objeto usuario completo (id, nombre, rol_nombre, casino, EULAAceptada…) |
| `rango_usuario` | JSON | `{ nivel, nombre_rango, puntos_totales }` |

---

## Patrones de Código

### Permiso en componente
```javascript
import { hasRoleAccess } from '@/service/api';
const puedeEditar = computed(() => hasRoleAccess(['ADMINISTRADOR', 'GERENCIA']));
```

### Servicio de dominio
```javascript
const { exito, data, error } = await guardarMaquina(formData, esEdicion);
if (exito) toast.add({ severity: 'success', ... });
else       toast.add({ severity: 'error', detail: error });
```

### Gamificación tras acción
```javascript
const r = await crearBitacoraTecnica(datos);
if (r.exito && r.data?.puntos_nexus) {
    await mostrarToastPuntos(toast, r.data.puntos_nexus);
}
```

---

## Dependencias Clave

| Paquete | Versión | Uso |
|---|---|---|
| vue | 3.5.x | Framework |
| primevue | 4.5.4 | Componentes UI |
| @primeuix/themes | 1.x | Tema Aura |
| vue-router | 4.6.4 | Enrutamiento SPA |
| axios | 1.13.5 | Cliente HTTP |
| tailwindcss | 4.x | Utilidades CSS |
| chart.js | 3.3.2 | Gráficas (vía PrimeVue Chart) |
| html2pdf.js | 0.10.x | Exportación PDF |
| vite | 7.x | Build tool + dev server |
