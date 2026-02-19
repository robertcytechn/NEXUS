/**
 * ============================================================================
 * NOTIFICATION SERVICE - Sistema de Notificaciones NEXUS
 * ============================================================================
 * 
 * Este servicio maneja todas las operaciones relacionadas con notificaciones
 * del sistema NEXUS utilizando el modelo de tabla intermedia NotificacionUsuario.
 * 
 * ARQUITECTURA:
 * -------------
 * - Tabla Principal: Notificacion (contiene el mensaje)
 * - Tabla Intermedia: NotificacionUsuario (rastrea quién leyó la notificación)
 * 
 * FLUJO DE LECTURA:
 * -----------------
 * 1. Backend filtra notificaciones según usuario/casino/rol automáticamente
 * 2. Frontend obtiene lista de notificaciones (campo 'leido' calculado dinámicamente)
 * 3. Usuario hace clic en una notificación
 * 4. Frontend llama a marcarNotificacionLeida(id)
 * 5. Backend crea registro en NotificacionUsuario
 * 6. En la siguiente petición, 'leido' aparece como true para ese usuario
 * 
 * TABLA INTERMEDIA (NotificacionUsuario):
 * ---------------------------------------
 * Se llena automáticamente cuando:
 * - El usuario hace clic en una notificación (RECOMENDADO)
 * - Se llama a marcarNotificacionLeida(id) - Backend crea el registro
 * - Se llama a crearLecturaNotificacion(id) - Frontend crea el registro directamente
 * 
 * La tabla tiene unique_together=['notificacion', 'usuario'] para evitar duplicados.
 * 
 * POLLING:
 * --------
 * Se recomienda polling cada 45 segundos usando fetchNotificacionesNoLeidas()
 * para obtener el count de notificaciones no leídas sin sobrecargar el servidor.
 * 
 * ============================================================================
 */

import axios from 'axios';

// URL base del backend Django construida dinámicamente
// Detecta el hostname actual y construye la URL con el puerto 8000 de Django
const BASE_URL = `http://${window.location.hostname}:8000/api/`;

// Crear instancia de axios específica para notificaciones
const notificationApi = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el token a cada petición
notificationApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y errores
notificationApi.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Si el token expiró o no es válido (401)
    if (error.response && error.response.status === 401) {
      // Limpiar localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      
      // Opcional: redirigir al login
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// FUNCIONES PRINCIPALES - NOTIFICACIONES
// ============================================================================

/**
 * Obtener todas las notificaciones del usuario actual
 * 
 * FUNCIONAMIENTO:
 * ---------------
 * - El backend filtra automáticamente según el usuario autenticado
 * - Solo devuelve notificaciones visibles para ese usuario basado en:
 *   * es_global=True (todos las ven)
 *   * usuario_destino=usuario_actual (notificación personal)
 *   * casino_destino=casino_del_usuario (notificación por casino)
 *   * rol_destino=rol_del_usuario (notificación por rol)
 *   * casino_destino + rol_destino (notificación por casino y rol)
 * 
 * CAMPO 'leido':
 * --------------
 * - Se calcula dinámicamente en el backend usando el serializer
 * - Verifica si existe un registro en NotificacionUsuario para este usuario
 * - Si existe registro → leido=true
 * - Si NO existe registro → leido=false
 * 
 * RESPUESTA:
 * ----------
 * [
 *   {
 *     id: 1,
 *     titulo: "Mensaje del Director",
 *     contenido: "...",
 *     nivel: "informativa",
 *     tipo: "sistema",
 *     leido: false,  ← Calculado dinámicamente
 *     fecha_creacion: "2026-02-17T10:00:00Z",
 *     ...
 *   }
 * ]
 * 
 * @returns {Promise<{success: boolean, data?: Array, error?: string}>}
 */
export const fetchNotificaciones = async () => {
  try {
    const response = await notificationApi.get('notificaciones/');
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.message || error.response?.data?.detail || 'Error al obtener notificaciones'
    };
  }
};

/**
 * Obtener el count de notificaciones no leídas
 * 
 * FUNCIONAMIENTO:
 * ---------------
 * Endpoint optimizado para polling frecuente (45s).
 * 
 * Backend ejecuta:
 * 1. Filtra notificaciones visibles para el usuario
 * 2. Cuenta cuántas NO tienen registro en NotificacionUsuario
 * 3. Usa subconsulta Exists() para eficiencia (no trae datos completos)
 * 
 * USO RECOMENDADO:
 * ----------------
 * - Polling cada 45 segundos
 * - Actualizar badge/contador en la UI
 * - No trae notificaciones completas (más rápido)
 * 
 * RESPUESTA:
 * ----------
 * { count: 5 }
 * 
 * @returns {Promise<{success: boolean, count: number, error?: string}>}
 */
export const fetchNotificacionesNoLeidas = async () => {
  try {
    const response = await notificationApi.get('notificaciones/count-no-leidas/');
    return {
      success: true,
      count: response.data.count
    };
  } catch (error) {
    return {
      success: false,
      count: 0,
      error: error.response?.data?.message || error.response?.data?.detail || 'Error al obtener count de notificaciones'
    };
  }
};

/**
 * Marcar una notificación como leída (MÉTODO RECOMENDADO)
 * 
 * FUNCIONAMIENTO:
 * ---------------
 * Usa el endpoint personalizado: PATCH /notificaciones/{id}/marcar-leida/
 * 
 * Backend ejecuta:
 * 1. Verifica que la notificación existe
 * 2. Verifica que el usuario tiene acceso a esa notificación
 * 3. Crea (o actualiza) registro en NotificacionUsuario con:
 *    - notificacion = id
 *    - usuario = request.user (del token)
 *    - fecha_visto = timezone.now()
 * 4. Usa get_or_create() para evitar duplicados
 * 
 * TABLA INTERMEDIA:
 * -----------------
 * Al ejecutarse, se llena automáticamente la tabla NotificacionUsuario:
 * 
 * +----------------+-----------+--------------+---------------------+
 * | id             | notif_id  | usuario_id   | fecha_visto         |
 * +----------------+-----------+--------------+---------------------+
 * | 1              | 16        | 3            | 2026-02-17 10:30:00 |
 * | 2              | 17        | 3            | 2026-02-17 10:31:15 |
 * +----------------+-----------+--------------+---------------------+
 * 
 * unique_together=['notificacion', 'usuario'] previene duplicados.
 * 
 * DESPUÉS DE MARCAR:
 * ------------------
 * - En la siguiente llamada a fetchNotificaciones(), el campo 'leido' será true
 * - El count de fetchNotificacionesNoLeidas() se reduce en 1
 * 
 * @param {number} notificacionId - ID de la notificación a marcar como leída
 * @returns {Promise<{success: boolean, data?: Object, error?: string}>}
 */
export const marcarNotificacionLeida = async (notificacionId) => {
  try {
    const response = await notificationApi.patch(`notificaciones/${notificacionId}/marcar-leida/`);
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error al marcar notificación como leída:', error.response?.data);
    return {
      success: false,
      error: error.response?.data?.detail || error.response?.data?.message || 'Error al marcar notificación como leída'
    };
  }
};

/**
 * Crear registro de lectura directamente en NotificacionUsuario
 * 
 * FUNCIONAMIENTO:
 * ---------------
 * Crea directamente un registro en la tabla intermedia NotificacionUsuario.
 * Es una alternativa a marcarNotificacionLeida().
 * 
 * Endpoint: POST /notificaciones-usuarios/
 * Body: { notificacion: <id> }
 * 
 * Backend ejecuta:
 * 1. Toma el usuario del token automáticamente (request.user)
 * 2. Valida que la notificación existe
 * 3. Verifica que el usuario tiene acceso a esa notificación
 * 4. Crea registro con get_or_create():
 *    - notificacion = notificacionId
 *    - usuario = request.user
 *    - fecha_visto = timezone.now()
 * 5. Retorna { created: true/false, data: {...} }
 * 
 * RESPUESTA:
 * ----------
 * {
 *   created: true,  ← true si se creó nuevo, false si ya existía
 *   data: {
 *     id: 1,
 *     notificacion: 16,
 *     usuario: 3,
 *     fecha_visto: "2026-02-17T10:30:00Z"
 *   }
 * }
 * 
 * CUÁNDO USAR:
 * ------------
 * - Si necesitas controlar directamente la tabla intermedia
 * - Si quieres saber si el registro ya existía (created=false)
 * - Para operaciones batch (marcar varias como leídas)
 * 
 * RECOMENDACIÓN:
 * --------------
 * Usar marcarNotificacionLeida() en lugar de esta función.
 * Es más semántico y maneja mejor los errores.
 * 
 * @param {number} notificacionId - ID de la notificación
 * @returns {Promise<{success: boolean, created?: boolean, data?: Object, error?: string}>}
 */
export const crearLecturaNotificacion = async (notificacionId) => {
  try {
    const response = await notificationApi.post('notificaciones-usuarios/', {
      notificacion: notificacionId
    });
    return {
      success: true,
      created: response.data.created,
      data: response.data.data
    };
  } catch (error) {
    console.error('Error al crear lectura de notificación:', error.response?.data);
    return {
      success: false,
      error: error.response?.data?.error || error.response?.data?.detail || 'Error al crear lectura de notificación'
    };
  }
};

/**
 * Obtener todas las lecturas del usuario actual
 * 
 * FUNCIONAMIENTO:
 * ---------------
 * Obtiene todos los registros de NotificacionUsuario del usuario autenticado.
 * Útil para ver el historial de notificaciones leídas.
 * 
 * Backend filtra automáticamente: NotificacionUsuario.objects.filter(usuario=request.user)
 * 
 * RESPUESTA:
 * ----------
 * [
 *   {
 *     id: 1,
 *     notificacion: 16,
 *     usuario: 3,
 *     fecha_visto: "2026-02-17T10:30:00Z"
 *   },
 *   {
 *     id: 2,
 *     notificacion: 17,
 *     usuario: 3,
 *     fecha_visto: "2026-02-17T10:31:15Z"
 *   }
 * ]
 * 
 * USO:
 * ----
 * - Ver historial de lecturas
 * - Debugging (verificar qué notificaciones ha leído el usuario)
 * - Analytics (cuándo y qué lee cada usuario)
 * 
 * @returns {Promise<{success: boolean, data?: Array, error?: string}>}
 */
export const fetchMisLecturas = async () => {
  try {
    const response = await notificationApi.get('notificaciones-usuarios/');
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.message || error.response?.data?.detail || 'Error al obtener lecturas'
    };
  }
};

/**
 * Obtener una notificación específica por ID
 * 
 * FUNCIONAMIENTO:
 * ---------------
 * Obtiene los detalles completos de una notificación específica.
 * Backend verifica que el usuario tiene acceso a esa notificación.
 * 
 * Incluye el campo 'leido' calculado dinámicamente.
 * 
 * RESPUESTA:
 * ----------
 * {
 *   id: 16,
 *   titulo: "Mensaje del Director",
 *   contenido: "...",
 *   nivel: "informativa",
 *   tipo: "sistema",
 *   leido: true,
 *   fecha_creacion: "2026-02-17T10:00:00Z",
 *   ...
 * }
 * 
 * USO:
 * ----
 * - Ver detalles de una notificación específica
 * - Modal de notificación expandida
 * - Vista de detalle
 * 
 * @param {number} notificacionId - ID de la notificación
 * @returns {Promise<{success: boolean, data?: Object, error?: string}>}
 */
export const fetchNotificacionById = async (notificacionId) => {
  try {
    const response = await notificationApi.get(`notificaciones/${notificacionId}/`);
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.message || error.response?.data?.detail || 'Error al obtener la notificación'
    };
  }
};

// ============================================================================
// FUNCIONES DE ADMINISTRACIÓN (Para usuarios con permisos)
// ============================================================================

/**
 * Crear una nueva notificación (Solo Administradores)
 * 
 * FUNCIONAMIENTO:
 * ---------------
 * Crea una nueva notificación en la tabla Notificacion.
 * 
 * LA TABLA INTERMEDIA NO SE LLENA AUTOMÁTICAMENTE al crear.
 * ¿Por qué? Las notificaciones empiezan como "no leídas" para todos.
 * 
 * FLUJO:
 * ------
 * 1. Se crea la notificación en la tabla Notificacion
 * 2. La notificación queda sin registros en NotificacionUsuario
 * 3. Los usuarios la ven como "no leída" (leido: false)
 * 4. Cuando un usuario la marca como leída, SE CREA el registro en NotificacionUsuario
 * 
 * TIPOS DE NOTIFICACIÓN:
 * ----------------------
 * 
 * 1. GLOBAL (Todos los usuarios):
 *    {
 *      titulo: "Actualización del sistema",
 *      contenido: "...",
 *      nivel: "informativa",
 *      tipo: "sistema",
 *      es_global: true
 *    }
 * 
 * 2. POR CASINO (Todos los usuarios de un casino):
 *    {
 *      titulo: "Mantenimiento en Crown City",
 *      contenido: "...",
 *      nivel: "alerta",
 *      tipo: "sistema",
 *      casino_destino: 1,  ← ID del casino
 *      es_global: false
 *    }
 * 
 * 3. POR ROL EN CASINO (Usuarios de un rol en un casino específico):
 *    {
 *      titulo: "Reunión de técnicos",
 *      contenido: "...",
 *      nivel: "informativa",
 *      tipo: "sistema",
 *      casino_destino: 1,  ← ID del casino
 *      rol_destino: 2,     ← ID del rol
 *      es_global: false
 *    }
 * 
 * 4. PERSONAL (Solo un usuario):
 *    {
 *      titulo: "Recordatorio personal",
 *      contenido: "...",
 *      nivel: "alerta",
 *      tipo: "sistema",
 *      usuario_destino: 5,  ← ID del usuario
 *      es_global: false
 *    }
 * 
 * 5. MENSAJE DEL DIRECTOR (Permanece 7 días):
 *    {
 *      titulo: "Mensaje del Director",
 *      contenido: "...",
 *      nivel: "informativa",
 *      tipo: "DIRECTOR",
 *      es_global: true,
 *      es_del_director: true
 *    }
 * 
 * @param {Object} notificacionData - Datos de la notificación
 * @returns {Promise<{success: boolean, data?: Object, error?: string}>}
 */
export const crearNotificacion = async (notificacionData) => {
  try {
    const response = await notificationApi.post('notificaciones/', notificacionData);
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error al crear notificación:', error.response?.data);
    return {
      success: false,
      error: error.response?.data?.error || error.response?.data?.detail || 'Error al crear notificación'
    };
  }
};

/**
 * Actualizar una notificación existente (Solo Administradores)
 * 
 * IMPORTANTE:
 * -----------
 * - NO afecta los registros en NotificacionUsuario
 * - Los usuarios que ya la leyeron seguirán viéndola como "leída"
 * - Solo actualiza el contenido/título/nivel de la notificación
 * 
 * @param {number} notificacionId - ID de la notificación
 * @param {Object} notificacionData - Datos a actualizar
 * @returns {Promise<{success: boolean, data?: Object, error?: string}>}
 */
export const actualizarNotificacion = async (notificacionId, notificacionData) => {
  try {
    const response = await notificationApi.patch(`notificaciones/${notificacionId}/`, notificacionData);
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error al actualizar notificación:', error.response?.data);
    return {
      success: false,
      error: error.response?.data?.error || error.response?.data?.detail || 'Error al actualizar notificación'
    };
  }
};

/**
 * Eliminar una notificación (Solo Administradores)
 * 
 * IMPORTANTE:
 * -----------
 * - La base de datos tiene ON DELETE CASCADE en NotificacionUsuario
 * - Al eliminar la notificación, se eliminan automáticamente todos los registros
 *   de lectura de esa notificación en NotificacionUsuario
 * 
 * @param {number} notificacionId - ID de la notificación
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export const eliminarNotificacion = async (notificacionId) => {
  try {
    await notificationApi.delete(`notificaciones/${notificacionId}/`);
    return {
      success: true
    };
  } catch (error) {
    console.error('Error al eliminar notificación:', error.response?.data);
    return {
      success: false,
      error: error.response?.data?.error || error.response?.data?.detail || 'Error al eliminar notificación'
    };
  }
};

// ============================================================================
// UTILIDADES
// ============================================================================

/**
 * Marcar todas las notificaciones como leídas
 * 
 * FUNCIONAMIENTO:
 * ---------------
 * Itera sobre todas las notificaciones no leídas y las marca como leídas.
 * Crea registros en NotificacionUsuario para cada una.
 * 
 * USO:
 * ----
 * Botón "Marcar todas como leídas" en el panel de notificaciones
 * 
 * @returns {Promise<{success: boolean, marcadas: number, error?: string}>}
 */
export const marcarTodasLeidas = async () => {
  try {
    // Obtener todas las notificaciones
    const { success, data } = await fetchNotificaciones();
    
    if (!success) {
      return {
        success: false,
        marcadas: 0,
        error: 'Error al obtener notificaciones'
      };
    }
    
    // Filtrar las no leídas
    const noLeidas = data.filter(n => !n.leido);
    
    // Marcar cada una como leída
    const promesas = noLeidas.map(notif => marcarNotificacionLeida(notif.id));
    await Promise.all(promesas);
    
    return {
      success: true,
      marcadas: noLeidas.length
    };
  } catch (error) {
    console.error('Error al marcar todas como leídas:', error);
    return {
      success: false,
      marcadas: 0,
      error: 'Error al marcar todas como leídas'
    };
  }
};

/**
 * Obtener nivel de urgencia como número
 * Útil para ordenar notificaciones por prioridad
 * 
 * @param {string} nivel - 'urgente', 'alerta', 'informativa'
 * @returns {number} 1 (urgente), 2 (alerta), 3 (informativa)
 */
export const getNivelPrioridad = (nivel) => {
  const prioridades = {
    'urgente': 1,
    'alerta': 2,
    'informativa': 3
  };
  return prioridades[nivel] || 3;
};

/**
 * Obtener ícono según el nivel de la notificación
 * 
 * @param {string} nivel - 'urgente', 'alerta', 'informativa'
 * @returns {string} Emoji o caracterthema según el nivel
 */
export const getIconoNivel = (nivel) => {
  const iconos = {
    'urgente': '🚨',
    'alerta': '⚠️',
    'informativa': 'ℹ️'
  };
  return iconos[nivel] || 'ℹ️';
};

/**
 * Obtener color según el nivel de la notificación
 * 
 * @param {string} nivel - 'urgente', 'alerta', 'informativa'
 * @returns {string} Color hex o clase CSS
 */
export const getColorNivel = (nivel) => {
  const colores = {
    'urgente': '#ef4444',   // rojo
    'alerta': '#f59e0b',    // naranja/amarillo
    'informativa': '#3b82f6' // azul
  };
  return colores[nivel] || '#3b82f6';
};

// ============================================================================
// EXPORTACIÓN DEFAULT (Para importar todo el servicio)
// ============================================================================

export default {
  fetchNotificaciones,
  fetchNotificacionesNoLeidas,
  marcarNotificacionLeida,
  crearLecturaNotificacion,
  fetchMisLecturas,
  fetchNotificacionById,
  crearNotificacion,
  actualizarNotificacion,
  eliminarNotificacion,
  marcarTodasLeidas,
  getNivelPrioridad,
  getIconoNivel,
  getColorNivel
};
