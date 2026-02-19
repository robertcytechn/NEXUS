# 🔔 Sistema de Notificaciones NEXUS

Sistema de notificaciones con lectura individual por usuario usando tabla intermedia `NotificacionUsuario`.

## 📁 Archivos del Sistema

### Backend (Django)
- **`BackEnd/Notificaciones/models.py`** - Modelos `Notificacion` y `NotificacionUsuario`
- **`BackEnd/Notificaciones/views.py`** - Endpoints REST
- **`BackEnd/Notificaciones/serializers.py`** - Serialización con campo `leido` dinámico
- **`BackEnd/ejemplos_notificaciones.py`** - Script para crear notificaciones de prueba

### Frontend (Vue.js)
- **`FrontEnd/src/service/notificationService.js`** - ⭐ Servicio principal de notificaciones
- **`FrontEnd/src/service/ejemplos-notificaciones.js`** - 📚 Ejemplos de uso y documentación
- **`FrontEnd/src/service/api.js`** - Servicio general (ya no incluye notificaciones)
- **`FrontEnd/src/layout/AppTopbar.vue`** - Componente de header con ícono de notificaciones

---

## 🚀 Inicio Rápido

### 1. Importar el servicio
```javascript
// Opción 1: Importar funciones específicas (RECOMENDADO)
import { 
  fetchNotificaciones, 
  marcarNotificacionLeida 
} from '@/service/notificationService';

// Opción 2: Importar todo el servicio
import notificationService from '@/service/notificationService';
```

### 2. Obtener notificaciones
```javascript
const response = await fetchNotificaciones();

if (response.success) {
  const notificaciones = response.data;
  // Cada notificación tiene campo 'leido' calculado dinámicamente
}
```

### 3. Marcar como leída
```javascript
const response = await marcarNotificacionLeida(notificacionId);

if (response.success) {
  console.log('✅ Notificación marcada como leída');
  // Backend creó registro en NotificacionUsuario
}
```

---

## 🔍 ¿Cómo Funciona?

### Arquitectura de Tablas

```
┌─────────────────────┐
│   Notificacion      │
├─────────────────────┤
│ id                  │
│ titulo              │
│ contenido           │
│ nivel               │
│ tipo                │
│ es_global           │
│ casino_destino      │
│ rol_destino         │
│ usuario_destino     │
└─────────────────────┘
          │
          │ (1 a muchos)
          ▼
┌─────────────────────┐
│ NotificacionUsuario │ ← Tabla Intermedia
├─────────────────────┤
│ id                  │
│ notificacion_id     │
│ usuario_id          │
│ fecha_visto         │
└─────────────────────┘
unique_together: [notificacion, usuario]
```

### Flujo de Lectura

```
1. CREAR NOTIFICACIÓN
   └─> Se guarda en tabla Notificacion
       └─> NotificacionUsuario queda VACÍA ❌

2. USUARIO VE LA NOTIFICACIÓN
   └─> Backend calcula campo 'leido' dinámicamente
       └─> Si existe registro en NotificacionUsuario → leido: true
       └─> Si NO existe registro → leido: false ❌

3. USUARIO HACE CLIC (Marcar como leída)
   └─> Frontend llama a marcarNotificacionLeida(id)
       └─> Backend crea registro en NotificacionUsuario ✅
           ┌────┬──────────────┬──────────┬─────────────────────┐
           │ id │ notificacion │ usuario  │ fecha_visto         │
           ├────┼──────────────┼──────────┼─────────────────────┤
           │ 1  │ 16           │ 3        │ 2026-02-17 10:30:00 │
           └────┴──────────────┴──────────┴─────────────────────┘

4. PRÓXIMA VEZ
   └─> Backend encuentra el registro → leido: true ✅
```

---

## 📊 ¿Cuándo se Llena la Tabla Intermedia?

### ❌ NO se llena automáticamente cuando:
- Se crea la notificación
- El usuario ve o recibe la notificación
- Se lista la notificación en el frontend

### ✅ SÍ se llena cuando:
- El usuario hace clic en "Marcar como leída"
- Se llama a `marcarNotificacionLeida(id)`
- Se llama a `crearLecturaNotificacion(id)` (alternativa)

### 💡 ¿Por qué este diseño?
Las notificaciones empiezan como "no leídas" para todos. La tabla intermedia **solo rastrea quién YA leyó** la notificación, no quién debe recibirla.

---

## 📝 Tipos de Notificaciones

### 1. Global (Todos los usuarios)
```javascript
{
  titulo: "Actualización del sistema",
  contenido: "...",
  es_global: true
}
```

### 2. Por Casino
```javascript
{
  titulo: "Mantenimiento en Crown City",
  contenido: "...",
  casino_destino: 1,  // ID del casino
  es_global: false
}
```

### 3. Por Casino + Rol
```javascript
{
  titulo: "Reunión de técnicos",
  contenido: "...",
  casino_destino: 1,  // ID del casino
  rol_destino: 2,     // ID del rol
  es_global: false
}
```

### 4. Personal (Un usuario)
```javascript
{
  titulo: "Recordatorio personal",
  contenido: "...",
  usuario_destino: 5,  // ID del usuario
  es_global: false
}
```

### 5. Mensaje del Director (7 días)
```javascript
{
  titulo: "Mensaje del Director",
  contenido: "...",
  tipo: "DIRECTOR",
  es_global: true,
  es_del_director: true
}
```

---

## 🔧 API Endpoints

### Obtener notificaciones
```
GET /api/notificaciones/
```
Respuesta:
```json
[
  {
    "id": 16,
    "titulo": "Nueva actualización",
    "contenido": "...",
    "nivel": "informativa",
    "tipo": "sistema",
    "leido": false,  ← Calculado dinámicamente
    "fecha_creacion": "2026-02-17T10:00:00Z"
  }
]
```

### Count de no leídas (optimizado para polling)
```
GET /api/notificaciones/count-no-leidas/
```
Respuesta:
```json
{ "count": 5 }
```

### Marcar como leída
```
PATCH /api/notificaciones/{id}/marcar-leida/
```
Respuesta:
```json
{
  "success": true,
  "message": "Notificación marcada como leída"
}
```

---

## 🎯 Polling Sistema (45 segundos)

```javascript
let pollingInterval = null;

// Iniciar polling al montar componente
onMounted(() => {
  pollingInterval = setInterval(async () => {
    const { count } = await fetchNotificacionesNoLeidas();
    // Actualizar badge con el count
  }, 45000); // 45 segundos
});

// Limpiar al desmontar
onUnmounted(() => {
  if (pollingInterval) {
    clearInterval(pollingInterval);
  }
});
```

---

## 🧪 Crear Notificaciones de Prueba

### Desde el backend:
```bash
cd BackEnd
python ejemplos_notificaciones.py
```

Esto creará:
- ✅ 1 notificación global
- ✅ 1 mensaje del director
- ✅ 1 notificación por casino
- ✅ 1 notificación por casino + rol
- ✅ 1 notificación personal

---

## 📚 Documentación Completa

Ver archivo completo con ejemplos detallados:
- **`FrontEnd/src/service/ejemplos-notificaciones.js`**

Incluye:
- ✅ Ejemplos de componentes Vue completos
- ✅ Explicación detallada de cada función
- ✅ Casos de uso reales
- ✅ Composables reutilizables
- ✅ Flujos de datos paso a paso

---

## ⚡ Funciones Disponibles

### Funciones Principales
- `fetchNotificaciones()` - Obtener todas las notificaciones del usuario
- `fetchNotificacionesNoLeidas()` - Obtener count de no leídas (polling)
- `marcarNotificacionLeida(id)` - Marcar como leída (RECOMENDADO)
- `fetchNotificacionById(id)` - Obtener una notificación específica
- `fetchMisLecturas()` - Historial de lecturas del usuario

### Funciones de Administración
- `crearNotificacion(data)` - Crear nueva notificación
- `actualizarNotificacion(id, data)` - Actualizar notificación
- `eliminarNotificacion(id)` - Eliminar notificación

### Utilidades
- `marcarTodasLeidas()` - Marcar todas como leídas
- `getNivelPrioridad(nivel)` - Obtener prioridad numérica
- `getIconoNivel(nivel)` - Obtener ícono según nivel
- `getColorNivel(nivel)` - Obtener color según nivel

---

## 🎨 Niveles de Notificación

| Nivel | Ícono | Color | Uso |
|-------|-------|-------|-----|
| `urgente` | 🚨 | Rojo | Incidencias críticas, emergencias |
| `alerta` | ⚠️ | Naranja | Avisos importantes, recordatorios |
| `informativa` | ℹ️ | Azul | Información general, actualizaciones |

---

## 🔐 Autenticación

El servicio usa el token almacenado en `localStorage`:
```javascript
const token = localStorage.getItem('token');
// Se agrega automáticamente como: Authorization: Bearer {token}
```

Backend valida con `SessionTokenAuthentication` y filtra notificaciones según el usuario autenticado.

---

## ✅ Checklist de Implementación

### Backend
- [x] Modelo `Notificacion` sin campo `leido`
- [x] Modelo `NotificacionUsuario` con `unique_together`
- [x] Serializer con `get_leido()` dinámico
- [x] Endpoint `marcar-leida/` (PATCH)
- [x] Endpoint `count-no-leidas/` (GET)
- [x] Filtrado automático por usuario/casino/rol

### Frontend
- [x] Servicio `notificationService.js` creado
- [x] Funciones de notificaciones movidas de `api.js`
- [x] AppTopbar.vue actualizado para usar nuevo servicio
- [x] Documentación completa con ejemplos
- [x] Sistema de polling cada 45s

---

## 🚀 Próximos Pasos

1. **Probar en el navegador:**
   ```bash
   # Terminal 1 - Backend
   cd BackEnd
   python manage.py runserver
   
   # Terminal 2 - Frontend
   cd FrontEnd
   npm run dev
   ```

2. **Hacer login** con cualquier usuario

3. **Ver notificaciones** en el ícono de campana 🔔

4. **Hacer clic en una notificación** y verificar:
   - Se llama a `marcarNotificacionLeida(id)`
   - El badge de "NUEVO" desaparece
   - El count se reduce en 1
   - En la base de datos se creó registro en `NotificacionUsuario`

5. **Verificar con otro usuario:**
   - Login con otro usuario
   - Debe ver la misma notificación como "no leída"
   - Al marcar como leída, solo afecta a ese usuario

---

## 🐛 Troubleshooting

### La notificación no se marca como leída
- Verificar que el endpoint retorna 200 OK
- Verificar que el token está en localStorage
- Verificar que el usuario tiene acceso a esa notificación
- Ver console del navegador para errores

### El count no se actualiza
- Verificar que el polling está activo (intervalo de 45s)
- Verificar en Network tab que se llama `count-no-leidas/`
- Recargar la página para reiniciar el polling

### No veo mis notificaciones
- Verificar filtros en el backend (casino/rol)
- Verificar que hay notificaciones creadas (ejecutar `ejemplos_notificaciones.py`)
- Verificar que el usuario está activo y tiene sesión válida

---

## 📞 Soporte

Para más información, ver:
- **Backend:** `BackEnd/ejemplos_notificaciones.py` (ejemplos de creación)
- **Frontend:** `FrontEnd/src/service/ejemplos-notificaciones.js` (ejemplos de uso)
- **Documentación API:** `SOLUCION_ERROR_403_CSRF_FINAL.md`

---

Creado por: Sistema NEXUS - Gestión de Casinos
Fecha: 17 de febrero de 2026
