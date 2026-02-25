# api.js — Cliente HTTP y Gestión de Sesión

**Archivo fuente:** `FrontEnd/src/service/api.js`

Este archivo es el núcleo de la capa de servicios. Define la instancia Axios, los interceptores, las operaciones de localStorage y las funciones de autenticación.

---

## Instancia Axios

```javascript
const BASE_URL = `http://${window.location.hostname}:8000/api/`;

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});
```

> `window.location.hostname` resuelve automáticamente el host actual. Funciona en local (`localhost`) y en producción (`cytechn.ddns.net`) sin configuración adicional.

---

## Interceptor de Request — Adjuntar Token

```javascript
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});
```

Añade `Authorization: Bearer <uuid>` a **todas** las peticiones automáticamente.

---

## Interceptor de Response — Manejo de 401/403

```javascript
api.interceptors.response.use(
    (response) => response,
    (error) => {
        const esEndpointAuth = url.includes('usuarios/login/') || url.includes('usuarios/refresh/');

        if (!esEndpointAuth && error.response?.status === 401 || error.response?.status === 403) {
            // Limpiar sesión y redirigir al login
            localStorage.removeItem('token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            localStorage.removeItem('roles');
            import('@/router').then(({ default: router }) => router.push('/login'));
        }
        return Promise.reject(error);
    }
);
```

**Excepciones:** Los endpoints de auth (`/login/`, `/refresh/`) no disparan el cierre de sesión en 401 — un 401 en login es credenciales incorrectas, no sesión expirada.

**Escenario de sesión concurrente:** Si otro dispositivo inicia sesión con la misma cuenta, el token del primero queda inválido. El siguiente request devuelve 401 → cierre de sesión automático.

---

## Funciones de localStorage

### Token de Acceso

| Función | Descripción |
|---|---|
| `setAuthToken(token)` | Guarda en `localStorage.token` |
| `getAuthToken()` | Lee `localStorage.token` |
| `removeAuthToken()` | Elimina `localStorage.token` |

### Refresh Token

| Función | Descripción |
|---|---|
| `setRefreshToken(token)` | Guarda en `localStorage.refresh_token` |
| `getRefreshToken()` | Lee `localStorage.refresh_token` |
| `removeRefreshToken()` | Elimina `localStorage.refresh_token` |

### Usuario

| Función | Descripción |
|---|---|
| `setUser(user)` | Guarda objeto JSON en `localStorage.user` |
| `getUser()` | Parsea y devuelve el objeto usuario o `null` |
| `removeUser()` | Elimina `localStorage.user` |

### Roles

| Función | Descripción |
|---|---|
| `setRoles(roles)` | Guarda array JSON en `localStorage.roles` |
| `getRoles()` | Devuelve array de roles o `[]` |
| `removeRoles()` | Elimina `localStorage.roles` |
| `fetchRoles()` | Llama `GET /roles/lista/` y guarda en localStorage |

---

## Funciones de Autenticación

### `login(credentials)`

```javascript
const result = await login({ username: 'jmartinez', password: 'pass123' });
// result.success → boolean
// result.data    → { token, refresh_token, usuario }
// result.user    → objeto usuario completo
```

Internamente llama `POST /usuarios/login/` → guarda token, refresh_token y usuario con `saveLoginData()`.

### `logout()`

Limpia todo el localStorage: token, refresh_token, user, roles.

### `acceptEULA()`

```javascript
const result = await acceptEULA();
// PATCH /usuarios/{id}/aceplisencia/
// Actualiza user.EULAAceptada = true en localStorage
```

---

## Sistema de Gamificación en localStorage

### `getRangoUsuario()`

Devuelve el rango RPG del usuario desde localStorage sin hacer petición al backend. El rango se incluye en la respuesta del login.

```javascript
const rango = getRangoUsuario();
// → { nivel: 5, titulo: 'Técnico Experto', insignia: '★★★★★', puntos_min: 1000, puntos_sig: 1500, progreso_pct: 65.0 }
```

### `actualizarRangoLocal(rango)`

Actualiza el rango en localStorage **y** emite un evento global para actualizar componentes reactivos sin re-login:

```javascript
actualizarRangoLocal({ nivel: 6, titulo: 'Técnico Senior', ... });
// → Emite: window.dispatchEvent(new CustomEvent('nexus:rango-actualizado', { detail: rango }))
```

El `AppTopbar` escucha este evento para actualizar `InsigniaRangoAnimada` en tiempo real.

---

## Control de Acceso por Rol

```javascript
export const hasRoleAccess = (requiredRoles) => {
    if (!requiredRoles || requiredRoles.includes('all')) return true;
    const user = getUser();
    return user && requiredRoles.includes(user.rol_nombre);
};
```

Usada en el router guard y en `AppMenu` para filtrar el menú.

---

## Estructura del Objeto Usuario en localStorage

```json
{
  "id": 5,
  "username": "jmartinez",
  "nombres": "Juan",
  "apellido_paterno": "Martínez",
  "rol_nombre": "TECNICO",
  "casino_id": 2,
  "casino_nombre": "Casino Centro",
  "avatar": "/media/avatares/jmartinez.jpg",
  "EULAAceptada": true,
  "puntos_gamificacion": 850,
  "puntos_gamificacion_historico": 1350,
  "rango_gamificacion": {
    "nivel": 5,
    "titulo": "Técnico Experto",
    "insignia": "★★★★★",
    "progreso_pct": 65.0,
    "puntos_sig": 1500
  }
}
```
