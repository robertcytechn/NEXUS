import api from './api';

export const getAuditoriaHistorial = async (filtros) => {
    try {
        const response = await api.get('auditoria-sistema/', { params: filtros });
        return response.data; // Retorna results (paginado)
    } catch (error) {
        console.error('Error al obtener el historial de auditoría:', error);
        throw error;
    }
};

export const getTablasAfectadas = async () => {
    try {
        const response = await api.get('auditoria-sistema/tablas_afectadas/');
        return response.data; // Lista string array
    } catch (error) {
        console.error('Error al obtener la lista de tablas:', error);
        throw error;
    }
};

export default {
    getAuditoriaHistorial,
    getTablasAfectadas
};
