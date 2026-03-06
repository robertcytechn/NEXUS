import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
    login as apiLogin,
    logout as apiLogout,
    fetchRoles as apiFetchRoles,
    getUser,
    getRoles,
    getAuthToken,
    setUser,
    actualizarRangoLocal,
} from '@/service/api';

/**
 * Store de autenticación usando Pinia.
 * Es la fuente de verdad reactiva para el usuario, token y roles.
 * Se inicializa desde localStorage (sesión persistida) y se mantiene
 * sincronizado con él a través de las acciones.
 */
export const useAuthStore = defineStore('auth', () => {
    // ── Estado ────────────────────────────────────────────────────────────────
    // Se inicializa desde localStorage para restaurar sesiones previas
    const user  = ref(getUser());
    const token = ref(getAuthToken());
    const roles = ref(getRoles());

    // ── Getters ───────────────────────────────────────────────────────────────
    const isAuthenticated = computed(() => !!token.value && !!user.value);
    const rolNombre       = computed(() => user.value?.rol_nombre ?? '');
    const casinoId        = computed(() => user.value?.casino ?? null);
    const rango           = computed(() => user.value?.rango_gamificacion ?? null);

    /** Verifica si el usuario tiene acceso según los roles requeridos */
    function hasRoleAccess(requiredRoles) {
        if (!requiredRoles || requiredRoles.includes('all')) return true;
        if (!user.value?.rol_nombre) return false;
        return requiredRoles.includes(user.value.rol_nombre);
    }

    // ── Acciones ──────────────────────────────────────────────────────────────

    /**
     * Inicia sesión: llama al API, persiste en localStorage y actualiza el store.
     * @param {{ username: string, password: string }} credentials
     */
    async function login(credentials) {
        const result = await apiLogin(credentials);
        if (result.success) {
            // apiLogin ya guardó en localStorage via saveLoginData; sincronizamos
            user.value  = result.user;
            token.value = getAuthToken();
            roles.value = getRoles();
        }
        return result;
    }

    /** Cierra sesión: limpia localStorage y resetea el estado reactivo. */
    function logout() {
        apiLogout();
        user.value  = null;
        token.value = null;
        roles.value = [];
    }

    /**
     * Carga los roles disponibles desde el backend y los guarda en el store.
     */
    async function fetchRoles() {
        const result = await apiFetchRoles();
        if (result.success) {
            roles.value = result.data;
        }
        return result;
    }

    /**
     * Actualiza el rango de gamificación del usuario en localStorage y en el store.
     * Sustituye el patrón de window.dispatchEvent('nexus:rango-actualizado').
     * @param {object} nuevoRango
     */
    function actualizarRango(nuevoRango) {
        actualizarRangoLocal(nuevoRango); // escribe en localStorage
        user.value = getUser();           // vuelve a leer para mantener reactividad
    }

    /**
     * Actualiza el objeto usuario completo (ej. tras editar perfil).
     * @param {object} nuevoUsuario
     */
    function actualizarUsuario(nuevoUsuario) {
        setUser(nuevoUsuario);
        user.value = nuevoUsuario;
    }

    /**
     * Re-sincroniza el estado del store desde localStorage.
     * Útil tras el refresco automático de token en el interceptor de axios.
     */
    function syncFromStorage() {
        user.value  = getUser();
        token.value = getAuthToken();
        roles.value = getRoles();
    }

    return {
        // estado
        user,
        token,
        roles,
        // getters
        isAuthenticated,
        rolNombre,
        casinoId,
        rango,
        // acciones
        hasRoleAccess,
        login,
        logout,
        fetchRoles,
        actualizarRango,
        actualizarUsuario,
        syncFromStorage,
    };
});
