import api from './api';

export default class EvolucionService {
    getEvoluciones() {
        return api.get('evolucion-nexus/').then(res => res.data);
    }

    getEvolucion(id) {
        return api.get(`evolucion-nexus/${id}/`).then(res => res.data);
    }

    createEvolucion(evolucion) {
        return api.post('evolucion-nexus/', evolucion).then(res => res.data);
    }

    updateEvolucion(evolucion) {
        return api.put(`evolucion-nexus/${evolucion.id}/`, evolucion).then(res => res.data);
    }

    deleteEvolucion(id) {
        return api.delete(`evolucion-nexus/${id}/`).then(res => res.data);
    }
}
