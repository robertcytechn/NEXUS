import api from './api';

/**
 * Servicio para el Mapa Interactivo de Sala (Digital Twin)
 */

/**
 * Obtiene la configuración del grid y las máquinas de un casino.
 * @param {number|string} casinoId  - ID del casino
 * @param {string} [piso]           - Clave de piso para filtrar (opcional)
 * @param {string} [area]           - Clave de área/sala para filtrar (opcional)
 * @returns {Promise<Object>} { casino, pisos_disponibles, areas_disponibles, piso_choices, sala_choices, maquinas, total }
 */
export async function obtenerMapaCasino(casinoId, piso = null, area = null) {
    try {
        const params = { casino_id: casinoId };
        if (piso) params.piso = piso;
        if (area) params.area = area;

        const response = await api.get('maquinas/mapa-completo/', { params });
        return {
            exito: true,
            data: response.data
        };
    } catch (error) {
        console.error('Error al obtener el mapa del casino:', error);
        return {
            exito: false,
            error: error.response?.data?.error || 'No se pudo cargar el mapa del casino'
        };
    }
}

/**
 * Actualiza las coordenadas X e Y de una máquina en el mapa.
 * @param {number} maquinaId  - PK de la máquina
 * @param {number} x          - Nueva coordenada X (>= 0)
 * @param {number} y          - Nueva coordenada Y (>= 0)
 * @returns {Promise<Object>} { exito, data, error }
 */
export async function actualizarCoordenadas(maquinaId, x, y) {
    try {
        const response = await api.patch(`maquinas/${maquinaId}/actualizar-coordenadas/`, {
            coordenada_x: x,
            coordenada_y: y
        });
        return {
            exito: true,
            data: response.data,
            mensaje: 'Coordenadas actualizadas correctamente'
        };
    } catch (error) {
        console.error('Error al actualizar coordenadas:', error);
        const status = error.response?.status;
        let mensaje = 'No se pudieron actualizar las coordenadas';
        if (status === 409) {
            mensaje = 'Ya existe una máquina en esa posición de la sala';
        } else if (status === 400) {
            mensaje = error.response?.data?.error || 'Datos inválidos';
        }
        return {
            exito: false,
            error: mensaje
        };
    }
}

export default {
    obtenerMapaCasino,
    actualizarCoordenadas
};
