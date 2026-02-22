import api from './api';

export const getTareasEspeciales = async () => {
    try {
        const response = await api.get('tareas/');
        return { success: true, data: response.data.results || response.data };
    } catch (error) {
        return { success: false, error: 'Error al obtener las tareas especiales' };
    }
};

export const createTareaEspecial = async (data) => {
    try {
        const response = await api.post('tareas/', data);
        return { success: true, data: response.data };
    } catch (error) {
        return { success: false, error: error.response?.data || 'Error al crear la tarea especial' };
    }
};

export const updateTareaEspecial = async (id, data) => {
    try {
        const response = await api.patch(`tareas/${id}/`, data);
        return { success: true, data: response.data };
    } catch (error) {
        return { success: false, error: error.response?.data || 'Error al actualizar la tarea especial' };
    }
};

export const deleteTareaEspecial = async (id) => {
    try {
        await api.delete(`tareas/${id}/`);
        return { success: true };
    } catch (error) {
        return { success: false, error: 'Error al eliminar la tarea especial' };
    }
};
