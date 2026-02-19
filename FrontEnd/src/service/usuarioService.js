import api from './api';

/**
 * Servicio para gestión de Usuarios del casino
 */

/**
 * Guarda (crea o actualiza) un usuario
 * @param {Object} usuarioData - Datos del usuario
 * @param {boolean} esEdicion - Si es edición (true) o creación (false)
 * @returns {Promise<Object>} Respuesta con el resultado
 */
export async function guardarUsuario(usuarioData, esEdicion = false) {
    try {
        // Validaciones básicas
        if (!usuarioData.nombres?.trim()) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'El nombre del usuario es obligatorio'
            };
        }

        if (!usuarioData.apellido_paterno?.trim()) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'El apellido paterno es obligatorio'
            };
        }

        if (!usuarioData.username?.trim()) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'El nombre de usuario es obligatorio'
            };
        }

        if (!usuarioData.email?.trim()) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'El email es obligatorio'
            };
        }

        if (!usuarioData.casino) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'Debe tener un casino asignado'
            };
        }

        if (!usuarioData.rol) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'Debe seleccionar un rol'
            };
        }

        if (!esEdicion && !usuarioData.password?.trim()) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'La contraseña es obligatoria para nuevos usuarios'
            };
        }

        // Preparar payload
        const payload = { ...usuarioData };

        // Si es edición y no se cambió el password, no enviarlo
        if (esEdicion && payload.id && !payload.password) {
            delete payload.password;
        }

        // Guardar (crear o actualizar)
        let response;
        if (esEdicion && payload.id) {
            response = await api.put(`usuarios/${payload.id}/`, payload);
        } else {
            response = await api.post('usuarios/', payload);
        }

        return {
            exito: true,
            data: response.data,
            mensaje: esEdicion ? 'Usuario actualizado correctamente' : 'Usuario registrado correctamente'
        };

    } catch (error) {
        console.error('Error en guardarUsuario:', error);

        // Manejo de errores específicos
        if (error.response?.status === 400) {
            const errorData = error.response.data;

            if (errorData.username) {
                return {
                    exito: false,
                    error: 'Usuario Duplicado',
                    detalle: 'Ya existe un usuario con este nombre de usuario'
                };
            }
            if (errorData.email) {
                return {
                    exito: false,
                    error: 'Email Duplicado',
                    detalle: 'Ya existe un usuario con este correo electrónico'
                };
            }

            // Error genérico de validación
            const primerError = Object.values(errorData)[0];
            if (Array.isArray(primerError)) {
                return {
                    exito: false,
                    error: 'Error de validación',
                    detalle: primerError[0]
                };
            }
        }

        return {
            exito: false,
            error: 'Error al guardar',
            detalle: error.response?.data?.detail || 'No se pudo guardar el usuario'
        };
    }
}


/**
 * Obtener estadísticas del dashboard
 * @returns {Promise<Object>} Datos del dashboard
 */
export async function getDashboardStats() {
    try {
        const response = await api.get('usuarios/dashboard-stats/');
        return response.data;
    } catch (error) {
        throw error;
    }
}

/**
 * Subir avatar de usuario
 * @param {number} id - ID del usuario
 * @param {File} archivo - Archivo de imagen
 * @returns {Promise<Object>} Resultado de la operación
 */
export async function subirAvatar(id, archivo) {
    try {
        const formData = new FormData();
        formData.append('avatar', archivo);

        const response = await api.patch(`usuarios/${id}/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        return {
            exito: true,
            data: response.data,
            mensaje: 'Avatar actualizado correctamente'
        };
    } catch (error) {
        console.error('Error al subir avatar:', error);
        return {
            exito: false,
            error: 'Error al subir imagen',
            detalle: error.response?.data?.detail || 'No se pudo actualizar el avatar'
        };
    }
}

/**
 * Cambiar contraseña de usuario
 * @param {number} id - ID del usuario
 * @param {string} newPassword - Nueva contraseña
 * @returns {Promise<Object>} Resultado de la operación
 */
export async function cambiarPassword(id, newPassword) {
    try {
        const response = await api.patch(`usuarios/${id}/`, { password: newPassword });
        return {
            exito: true,
            data: response.data,
            mensaje: 'Contraseña actualizada correctamente'
        };
    } catch (error) {
        console.error('Error al cambiar password:', error);
        return {
            exito: false,
            error: 'Error al cambiar contraseña',
            detalle: error.response?.data?.detail || 'No se pudo actualizar la contraseña'
        };
    }
}

/**
 * Obtener estadísticas de perfil del usuario
 * @param {number} id - ID del usuario
 * @returns {Promise<Object>} Estadísticas del usuario (tickets, evoluciones, cuenta)
 */
export async function obtenerEstadisticasPerfil(id) {
    try {
        const response = await api.get(`usuarios/${id}/estadisticas-perfil/`);
        return {
            exito: true,
            data: response.data
        };
    } catch (error) {
        console.error('Error al obtener estadísticas de perfil:', error);
        return {
            exito: false,
            error: 'Error al cargar estadísticas',
            detalle: error.response?.data?.error || 'No se pudieron obtener las estadísticas'
        };
    }
}

export default {
    guardarUsuario,
    getDashboardStats,
    subirAvatar,
    cambiarPassword,
    obtenerEstadisticasPerfil
};
