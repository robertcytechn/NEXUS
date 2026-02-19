import api from './api';

/**
 * Servicio para gestión de Máquinas
 */

/**
 * Guarda (crea o actualiza) una máquina
 * @param {Object} maquinaData - Datos de la máquina
 * @param {boolean} esEdicion - Si es edición (true) o creación (false)
 * @returns {Promise<Object>} Respuesta con el resultado
 */
export async function guardarMaquina(maquinaData, esEdicion = false) {
    try {
        // Validaciones básicas
        if (!maquinaData.uid_sala?.trim()) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'El UID de sala es obligatorio'
            };
        }

        if (!maquinaData.numero_serie?.trim()) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'El número de serie es obligatorio'
            };
        }

        if (!maquinaData.casino) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'Debe seleccionar un casino'
            };
        }

        if (!maquinaData.modelo) {
            return {
                exito: false,
                error: 'Campo requerido',
                detalle: 'Debe seleccionar un modelo'
            };
        }

        // Preparar payload
        const payload = { ...maquinaData };
        
        // Formatear fechas a YYYY-MM-DD
        const formatDate = (date) => {
            if (!date) return null;
            if (date instanceof Date) {
                return date.toISOString().split('T')[0];
            }
            return date;
        };

        if (payload.ultimo_mantenimiento) {
            payload.ultimo_mantenimiento = formatDate(payload.ultimo_mantenimiento);
        }
        if (payload.fecha_vencimiento_licencia) {
            payload.fecha_vencimiento_licencia = formatDate(payload.fecha_vencimiento_licencia);
        }

        // Guardar (crear o actualizar)
        let response;
        if (esEdicion && payload.id) {
            response = await api.put(`maquinas/${payload.id}/`, payload);
        } else {
            response = await api.post('maquinas/', payload);
        }

        return {
            exito: true,
            data: response.data,
            mensaje: esEdicion ? 'Máquina actualizada correctamente' : 'Máquina registrada correctamente'
        };

    } catch (error) {
        console.error('Error en guardarMaquina:', error);
        
        // Manejo de errores específicos
        if (error.response?.status === 400) {
            const errorData = error.response.data;
            
            // Errores de duplicados
            if (errorData.ip_maquina) {
                return {
                    exito: false,
                    error: 'IP Duplicada',
                    detalle: 'Ya existe una máquina con esta dirección IP'
                };
            }
            if (errorData.numero_serie) {
                return {
                    exito: false,
                    error: 'Serie Duplicada',
                    detalle: 'Ya existe una máquina con este número de serie'
                };
            }
            if (errorData.uid_sala) {
                return {
                    exito: false,
                    error: 'UID Duplicado',
                    detalle: 'Ya existe una máquina con este UID de sala'
                };
            }
        }

        return {
            exito: false,
            error: 'Error al guardar',
            detalle: error.response?.data?.message || error.response?.data?.detail || 'No se pudo guardar la máquina'
        };
    }
}

/**
 * Formatea una fecha a formato YYYY-MM-DD
 * @param {Date|string} fecha - Fecha a formatear
 * @returns {string|null} Fecha formateada o null
 */
export function formatearFecha(fecha) {
    if (!fecha) return null;
    if (fecha instanceof Date) {
        return fecha.toISOString().split('T')[0];
    }
    return fecha;
}

export default {
    guardarMaquina,
    formatearFecha
};
