import axios from 'axios';

// URL base del backend Django construida dinámicamente
// Detecta el hostname actual y construye la URL con el puerto 8000 de Django
const BASE_URL = `http://${window.location.hostname}:8000/api/`;

// Crear instancia de axios
const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el token a cada petición
api.interceptors.request.use(
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
api.interceptors.response.use(
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

// Funciones auxiliares para manejar localStorage

// Token de acceso
export const setAuthToken = (token) => {
    localStorage.setItem('token', token);
};

export const getAuthToken = () => {
    return localStorage.getItem('token');
};

export const removeAuthToken = () => {
    localStorage.removeItem('token');
};

// Refresh token
export const setRefreshToken = (refreshToken) => {
    localStorage.setItem('refresh_token', refreshToken);
};

export const getRefreshToken = () => {
    return localStorage.getItem('refresh_token');
};

export const removeRefreshToken = () => {
    localStorage.removeItem('refresh_token');
};

// Usuario
export const setUser = (user) => {
    localStorage.setItem('user', JSON.stringify(user));
};

export const getUser = () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
};

export const removeUser = () => {
    localStorage.removeItem('user');
};

/**
 * Devuelve el rango de gamificación del usuario desde localStorage.
 * El backend ya lo incluye en la respuesta del login (UsuariosSerializer),
 * por lo que no requiere ninguna petición adicional al servidor.
 *
 * @returns {{ nivel: number, titulo: string, insignia: string, puntos_min: number, puntos_sig: number|null, progreso_pct: number }}
 */
export const getRangoUsuario = () => {
    const user = getUser();
    if (!user || !user.rango_gamificacion) {
        return { nivel: 1, titulo: 'Novato de Mantenimiento', insignia: '🔩', puntos_min: 0, puntos_sig: 100, progreso_pct: 0 };
    }
    return user.rango_gamificacion;
};

/**
 * Actualiza sólo el rango en el objeto usuario del localStorage
 * y despacha el evento `nexus:rango-actualizado` para que componentes
 * como AppTopbar actualicen InsigniaRangoAnimada en tiempo real.
 * @param {{ nivel: number, titulo: string }} rango
 */
export const actualizarRangoLocal = (rango) => {
    const user = getUser();
    if (user && rango) {
        user.rango_gamificacion = { ...user.rango_gamificacion, ...rango };
        setUser(user);
        // Notificar a todos los componentes que escuchan (AppTopbar, Dashboard, etc.)
        window.dispatchEvent(new CustomEvent('nexus:rango-actualizado', { detail: user.rango_gamificacion }));
    }
};

// Función para guardar todos los datos del login
export const saveLoginData = (loginResponse) => {
    const { token, refresh_token, usuario } = loginResponse;
    
    if (token) setAuthToken(token);
    if (refresh_token) setRefreshToken(refresh_token);
    if (usuario) setUser(usuario);
};

// Función para limpiar todos los datos de sesión
export const logout = () => {
    removeAuthToken();
    removeRefreshToken();
    removeUser();
    removeRoles(); // Limpiar roles del localStorage
};

// Roles - Gestión de lista de roles
export const setRoles = (roles) => {
    localStorage.setItem('roles', JSON.stringify(roles));
};

export const getRoles = () => {
    const roles = localStorage.getItem('roles');
    return roles ? JSON.parse(roles) : [];
};

export const removeRoles = () => {
    localStorage.removeItem('roles');
};

// Función para obtener la lista de roles desde el backend
export const fetchRoles = async () => {
    try {
        const response = await api.get('roles/lista/');
        const roles = response.data;
        
        // Guardar en localStorage para uso offline
        setRoles(roles);
        
        return {
            success: true,
            data: roles
        };
    } catch (error) {
        return {
            success: false,
            error: error.response?.data?.message || 'Error al obtener los roles'
        };
    }
};

// Función auxiliar para verificar si un usuario tiene acceso basado en roles
export const hasRoleAccess = (requiredRoles) => {
    // Si no se especifican roles requeridos, o es 'all', permitir acceso
    if (!requiredRoles || requiredRoles.includes('all')) {
        return true;
    }
    
    const user = getUser();
    if (!user || !user.rol_nombre) {
        return false;
    }
    
    // Verificar si el rol del usuario está en la lista de roles requeridos
    return requiredRoles.includes(user.rol_nombre);
};

// Función de login
export const login = async (credentials) => {
    try {
        const response = await api.post('usuarios/login/', credentials);
        const { data } = response;
        
        // Guardar todos los datos en localStorage
        saveLoginData(data);
        
        return {
            success: true,
            data: data,
            user: data.usuario
        };
    } catch (error) {
        return {
            success: false,
            error: error.response?.data?.message || 'Datos no validos, verifica tu usuario y contraseña'
        };
    }
};

// Función para aceptar la EULA (Términos y Condiciones)
export const acceptEULA = async () => {
    try {
        // Obtener el ID del usuario actual desde localStorage
        const currentUser = getUser();
        if (!currentUser || !currentUser.id) {
            throw new Error('Usuario no encontrado en la sesión');
        }
        
        const response = await api.patch(`usuarios/${currentUser.id}/aceplisencia/`);
        const { data } = response;
        
        // Actualizar el usuario en localStorage con el nuevo valor
        if (currentUser) {
            currentUser.EULAAceptada = true;
            setUser(currentUser);
        }
        
        return {
            success: true,
            data: data
        };
    } catch (error) {
        return {
            success: false,
            error: error.response?.data?.message || 'Error al aceptar los términos y condiciones'
        };
    }
};

export default api;

/*
===============================================================================
  EJEMPLOS DE USO DE LA API
===============================================================================

1. USAR LA FUNCIÓN LOGIN (RECOMENDADO):
   -----------------------------------
   import { login } from '@/service/api';
   
   const handleLogin = async () => {
       const result = await login({
           username: 'robertcyby',
           password: 'miPassword123'
       });
       
       if (result.success) {
           console.log('Usuario:', result.user);
           console.log('Token guardado automáticamente');
           router.push('/dashboard');
       } else {
           console.error('Error:', result.error);
       }
   };

2. PETICIÓN DIRECTA CON API (MANUAL):
   ----------------------------------
   import api, { saveLoginData } from '@/service/api';
   
   const manualLogin = async () => {
       try {
           const response = await api.post('usuarios/login/', {
               username: 'robertcyby',
               password: 'miPassword123'
           });
           
           console.log('Respuesta completa:', response.data);
           // response.data contiene: { message, token, refresh_token, usuario }
           
           // Guardar manualmente
           saveLoginData(response.data);
           
           // O guardar individualmente
           // setAuthToken(response.data.token);
           // setRefreshToken(response.data.refresh_token);
           // setUser(response.data.usuario);
           
       } catch (error) {
           console.error('Error:', error.response?.data);
       }
   };

3. OTRAS PETICIONES A LA API:
   --------------------------
   import api from '@/service/api';
   
   // GET - Obtener todos los tickets
   const getTickets = async () => {
       try {
           const response = await api.get('tickets/');
           return response.data;
       } catch (error) {
           console.error('Error:', error);
       }
   };
   
   // GET - Obtener un ticket específico
   const getTicket = async (id) => {
       const response = await api.get(`tickets/${id}/`);
       return response.data;
   };
   
   // POST - Crear un nuevo ticket
   const createTicket = async (ticketData) => {
       const response = await api.post('tickets/', ticketData);
       return response.data;
   };
   
   // PUT - Actualizar ticket completo
   const updateTicket = async (id, ticketData) => {
       const response = await api.put(`tickets/${id}/`, ticketData);
       return response.data;
   };
   
   // PATCH - Actualizar campos específicos
   const patchTicket = async (id, partialData) => {
       const response = await api.patch(`tickets/${id}/`, partialData);
       return response.data;
   };
   
   // DELETE - Eliminar ticket
   const deleteTicket = async (id) => {
       const response = await api.delete(`tickets/${id}/`);
       return response.data;
   };

4. MANEJO DE RESPUESTA DEL LOGIN:
   ------------------------------
   La respuesta de usuarios/login/ incluye:
   {
       "message": "Login exitoso",
       "token": "06567153-156a-42ec-b8a5-a7fa2eecf3ee",
       "refresh_token": "72b2704a-3b44-447d-9cda-d571fdbf778d",
       "usuario": {
           "id": 1,
           "username": "robertcyby",
           "email": "robert-cyby@hotmail.com",
           "nombres": "Cy",
           "apellido_paterno": "Tamayo",
           "apellido_materno": "Montejano",
           "nombre_completo": "Cy Tamayo Montejano",
           "casino": 1,
           "casino_nombre": "Pruebas",
           "rol": 1,
           "rol_nombre": "ADMINISTRADOR",
           "esta_activo": true,
           ...
       }
   }

5. ACCEDER A DATOS DEL USUARIO:
   ----------------------------
   import { getUser, getAuthToken, hasRoleAccess } from '@/service/api';
   
   const user = getUser();
   if (user) {
       console.log('Usuario:', user.nombre_completo);
       console.log('Rol:', user.rol_nombre);
       console.log('Casino:', user.casino_nombre);
   }
   
   // Verificar acceso por rol
   if (hasRoleAccess(['ADMINISTRADOR', 'SUP SISTEMAS'])) {
       console.log('Usuario tiene acceso administrativo');
   }
   
   const token = getAuthToken();
   console.log('Token actual:', token);

6. LOGOUT:
   -------
   import { logout } from '@/service/api';
   import { useRouter } from 'vue-router';
   
   const router = useRouter();
   
   const handleLogout = () => {
       logout(); // Limpia token, refresh_token y usuario
       router.push('/auth/login');
   };

7. NOTIFICACIONES:
   ---------------
   Las notificaciones ahora están en un servicio separado.
   Ver: @/service/notificationService.js
   
   import notificationService from '@/service/notificationService';
   // o
   import { fetchNotificaciones, marcarNotificacionLeida } from '@/service/notificationService';

===============================================================================
*/
