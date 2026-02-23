import api from './api';

// ─────────────────────────────────────────────────────────────────────────────
// WIKI — Centro de Mando (Admin)
// ─────────────────────────────────────────────────────────────────────────────
export const wikiAdmin = {
    /** Todas las guías (cualquier estado) */
    listar: () => api.get('wiki/centro-mando/'),

    /** Solo las pendientes de revisión */
    pendientes: () => api.get('wiki/centro-mando/pendientes/'),

    /** Aprobar una guía */
    aprobar: (id, payload) => api.post(`wiki/centro-mando/${id}/aprobar/`, payload),

    /** Publicar + otorgar puntos */
    publicar: (id, payload) => api.post(`wiki/centro-mando/${id}/publicar/`, payload),

    /** Rechazar con nota obligatoria */
    rechazar: (id, payload) => api.post(`wiki/centro-mando/${id}/rechazar/`, payload),

    /** Eliminar físicamente */
    eliminar: (id) => api.delete(`wiki/centro-mando/${id}/`),
};

// ─────────────────────────────────────────────────────────────────────────────
// WIKI — Centro de Servicios (Técnicos / Todos los roles autorizados)
// ─────────────────────────────────────────────────────────────────────────────
export const wikiPublica = {
    /** Guías publicadas */
    listar: () => api.get('wiki/centro-servicios/'),

    /** Reglas del centro */
    reglas: () => api.get('wiki/centro-servicios/reglas/'),

    /** Enviar nueva propuesta (técnico) */
    enviarPropuesta: (formData) =>
        api.post('wiki/centro-servicios/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        }),

    /** Mis propuestas (técnico logueado) */
    misPropuestas: () => api.get('wiki/centro-servicios/mis-propuestas/'),
};

// ─────────────────────────────────────────────────────────────────────────────
// GAMIFICACIÓN — Tienda (Gerencia)
// ─────────────────────────────────────────────────────────────────────────────
export const tiendaGerencia = {
    listarRecompensas: () => api.get('gamificacion/tienda/'),
    crearRecompensa: (data) => api.post('gamificacion/tienda/', data),
    editarRecompensa: (id, data) => api.put(`gamificacion/tienda/${id}/`, data),
    toggleActivo: (id) => api.post(`gamificacion/tienda/${id}/toggle-activo/`),
    eliminar: (id) => api.delete(`gamificacion/tienda/${id}/`),
    historialCanjes: () => api.get('gamificacion/tienda/canjes/'),
    entregarCanje: (recompensaId, canjeId, payload) =>
        api.post(`gamificacion/tienda/${recompensaId}/canjes/${canjeId}/entregar/`, payload),
};

// ─────────────────────────────────────────────────────────────────────────────
// GAMIFICACIÓN — Tienda Técnico (lectura + canje)
// ─────────────────────────────────────────────────────────────────────────────
export const tiendaTecnico = {
    listarRecompensas: () => api.get('gamificacion/tienda-tecnico/'),
    miRango: () => api.get('gamificacion/tienda-tecnico/mi-rango/'),
    misCanjes: () => api.get('gamificacion/tienda-tecnico/mis-canjes/'),
    canjear: (id) => api.post(`gamificacion/tienda-tecnico/${id}/canjear/`),
};

// ─────────────────────────────────────────────────────────────────────────────
// Helpers de catálogos compartidos
// ─────────────────────────────────────────────────────────────────────────────
export const wikiCatalogos = {
    modelos: () => api.get('modelos/'),
};
