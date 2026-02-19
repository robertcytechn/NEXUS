import api from './api';

/**
 * Servicio para gestión de Modelos de Máquinas
 */

/**
 * Guarda (crea o actualiza) un modelo de máquina
 * @param {Object} modeloData - Datos del modelo
 * @param {boolean} esEdicion - Si es edición (true) o creación (false)
 * @returns {Promise<Object>} Respuesta con el resultado
 */
export async function guardarModelo(modeloData, esEdicion = false) {
    try {
        // Validaciones básicas
        if (!modeloData.nombre_modelo?.trim()) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'El nombre del modelo es obligatorio'
            };
        }

        if (!modeloData.nombre_producto?.trim()) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'El nombre del producto es obligatorio'
            };
        }

        if (!modeloData.proveedor) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'Debe seleccionar un proveedor'
            };
        }

        // Preparar payload
        const payload = { ...modeloData };

        // Guardar (crear o actualizar)
        let response;
        if (esEdicion && payload.id) {
            response = await api.put(`modelos/${payload.id}/`, payload);
        } else {
            response = await api.post('modelos/', payload);
        }

        return {
            exito: true,
            data: response.data,
            mensaje: esEdicion ? 'Modelo actualizado correctamente' : 'Modelo creado correctamente'
        };

    } catch (error) {
        console.error('Error en guardarModelo:', error);
        
        // Manejo de errores específicos
        if (error.response?.status === 400) {
            const errorData = error.response.data;
            
            if (errorData.nombre_modelo) {
                return {
                    exito: false,
                    error: 'Modelo Duplicado',
                    detalle: 'Ya existe un modelo con este nombre para el proveedor seleccionado'
                };
            }
        }

        return {
            exito: false,
            error: 'Error al guardar',
            detalle: error.response?.data?.detail || 'No se pudo guardar el modelo'
        };
    }
}

export default {
    guardarModelo
};
