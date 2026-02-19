import api from './api';

/**
 * Servicio para gestión de Proveedores
 */

/**
 * Guarda (crea o actualiza) un proveedor
 * @param {Object} proveedorData - Datos del proveedor
 * @param {boolean} esEdicion - Si es edición (true) o creación (false)
 * @returns {Promise<Object>} Respuesta con el resultado
 */
export async function guardarProveedor(proveedorData, esEdicion = false) {
    try {
        // Validaciones básicas
        if (!proveedorData.nombre?.trim()) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'El nombre del proveedor es obligatorio'
            };
        }

        if (!proveedorData.casino) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'Debe seleccionar un casino'
            };
        }

        // Preparar payload
        const payload = { ...proveedorData };
        
        // Si es edición y no se cambió el password, no enviarlo
        if (esEdicion && payload.id && !payload.password) {
            delete payload.password;
        }

        // Guardar (crear o actualizar)
        let response;
        if (esEdicion && payload.id) {
            response = await api.put(`proveedores/${payload.id}/`, payload);
        } else {
            response = await api.post('proveedores/', payload);
        }

        return {
            exito: true,
            data: response.data,
            mensaje: esEdicion ? 'Proveedor actualizado correctamente' : 'Proveedor registrado correctamente'
        };

    } catch (error) {
        console.error('Error en guardarProveedor:', error);
        
        // Manejo de errores específicos
        if (error.response?.status === 400) {
            const errorData = error.response.data;
            
            if (errorData.nombre) {
                return {
                    exito: false,
                    error: 'Nombre Duplicado',
                    detalle: 'Ya existe un proveedor con este nombre en el casino'
                };
            }
            if (errorData.email) {
                return {
                    exito: false,
                    error: 'Email Duplicado',
                    detalle: 'Ya existe un proveedor con este email'
                };
            }
        }

        return {
            exito: false,
            error: 'Error al guardar',
            detalle: error.response?.data?.detail || 'No se pudo guardar el proveedor'
        };
    }
}

export default {
    guardarProveedor
};
