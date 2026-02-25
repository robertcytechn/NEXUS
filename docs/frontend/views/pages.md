# Vistas — Páginas Generales y Autenticación

**Directorio:** `FrontEnd/src/views/pages/` + `FrontEnd/src/views/`

---

## Login.vue

**Ruta:** `/login` (sin guard)  
**Archivo:** `views/pages/auth/Login.vue`

### Flujo de autenticación

```
Usuario ingresa username + password
        ↓
handleLogin() → login({ username, password }) de api.js
        ↓
POST /usuarios/login/
        ↓
  success → token + refresh + user guardados en localStorage
               ↓
           router.push(route.query.redirect || '/')
  error → errorMessage = result.error
```

### Notas técnicas

- Si el usuario ya tiene sesión activa (`getToken()` devuelve valor), el guard de `router/index.js` lo redirige al Dashboard antes de llegar a Login.
- El componente `FloatingConfigurator` está disponible en Login para que el usuario pueda cambiar tema antes de autenticarse.
- Aplica la paleta primary/surface de `layoutConfig` en tiempo de render para que el Login respete el tema elegido.

---

## lisencia.vue (EULA)

**Ruta:** `/lisencia` (sin guard)  
**Archivo:** `views/pages/public/lisencia.vue`

### Flujo EULA

1. El guard del router detecta `user.EULAAceptada === false`.
2. Redirige a `/lisencia` en CADA navegación hasta aceptar.
3. El usuario lee y hace clic en "Aceptar".
4. `acceptEULA()` de `api.js` → `PATCH /usuarios/{id}/aceplisencia/`.
5. `user.EULAAceptada` se actualiza en localStorage.
6. `router.push('/')`.

---

## Profile.vue

**Ruta:** `/profile`  
**Archivo:** `views/pages/Profile.vue`

- Formulario de edición del perfil propio (nombre, email, contraseña).
- Avatar / foto de perfil.
- Botón "Cerrar sesión" → `logout()` de `api.js`.
- Muestra `InsigniaRangoAnimada` con los datos de gamificación actuales.

---

## Dashboard.vue

**Ruta:** `/`  
**Archivo:** `views/Dashboard.vue` (919 líneas)

Vista de inicio personalizada por rol.

### Permisos por sección

| Sección | Roles |
|---|---|
| Estadísticas globales | ADMINISTRADOR, DB ADMIN, GERENCIA |
| Estadísticas técnicas | SUP SISTEMAS, TECNICO, SUPERVISOR SALA + anteriores |
| Gráficas (DashboardCharts) | ADMINISTRADOR, DB ADMIN, SUP SISTEMAS, GERENCIA |
| Reporte diario | ADMINISTRADOR, DB ADMIN, GERENCIA, SUP SISTEMAS |

### Quick Actions disponibles

| Acción | Descripción |
|---|---|
| Reportar error (Evolución) | Abre dialog → `evolucionService.createEvolucion()` |
| Nuevo usuario | Dialog de alta usuario → `guardarUsuario()` |
| Crear ticket | Dialog ticket rápido → `crearTicket()` |
| Reporte diario | Carga estadísticas del día → `getReporteDiario()` |

### Catálogo de roles filtrado

```javascript
const rolesDisponibles = computed(() => {
    if (['ADMINISTRADOR', 'DB ADMIN'].includes(rolActual)) return roles.value; // todos
    if (rolActual === 'GERENCIA') return roles.value.filter(r => r.nombre !== 'ADMINISTRADOR' && r.nombre !== 'DB ADMIN');
    // ...
});
```

---

## EvolucionNexus.vue

**Ruta:** `/evolucion`  
**Archivo:** `views/pages/EvolucionNexus.vue`

Pantalla de créditos / changelog del sistema. Muestra:
- `DnaBackground.vue` + `EvolucionAdn.vue` como fondo decorativo.
- Lista de versiones desde `EvolucionService`.
- `InsigniaRangoAnimada` del usuario actual.

---

## NotificacionDetail.vue

**Ruta:** `/notificaciones/:id`  
**Archivo:** `views/NotificacionDetail.vue`

- Carga el detalle completo de la notificación.
- Marca como leída al montar → `marcarNotificacionLeida(id)`.
- Muestra campos: tipo, nivel urgencia, asunto, mensaje, fecha, relacionado.

---

## Vistas de Operatividad

**Directorio:** `FrontEnd/src/views/Operatividad/`

### AuditoriasExternas.vue

**Ruta:** `/operatividad/auditorias`

Registro de auditorías externas (reguladores, proveedores). CRUD con adjuntos PDF.

### RelevosTurnos.vue

**Ruta:** `/operatividad/relevos`

Registro digital de relevos entre turnos:
- Parte de turno: incidencias, estado de máquinas, novedades.
- Firma del supervisor entrante/saliente.
- Histórico por turno y fecha.

---

## Páginas de Error

| Ruta | Archivo | Descripción |
|---|---|---|
| `/access` | `pages/auth/Access.vue` | 403 — Sin permisos |
| `/error` | `pages/auth/Error.vue` | 500 — Error de aplicación |
