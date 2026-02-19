import api from '@/service/api';

export class InfraestructuraService {
    async getIncidencias() {
        const response = await api.get('infra-incidencias/');
        return response.data;
    }

    async getCasinos() {
        const response = await api.get('casinos/lista/');
        return response.data.map(c => ({
            label: c.nombre,
            value: c.id
        }));
    }

    async saveIncidencia(incidencia) {
        const payload = { ...incidencia };
        const user = JSON.parse(localStorage.getItem('user') || '{}');

        if (incidencia.id) {
            payload.modificado_por_id = user.id;
        } else {
            payload.creado_por_id = user.id;
        }

        if (payload.hora_inicio instanceof Date) {
            payload.hora_inicio = payload.hora_inicio.toISOString();
        }
        if (payload.hora_fin instanceof Date) {
            payload.hora_fin = payload.hora_fin.toISOString();
        }

        if (incidencia.id) {
            return await api.put(`infra-incidencias/${incidencia.id}/`, payload);
        } else {
            return await api.post('infra-incidencias/', payload);
        }
    }

    async toggleActivarIncidencia(incidencia) {
        const payload = { ...incidencia, esta_activo: !incidencia.esta_activo };
        return await api.patch(`infra-incidencias/${incidencia.id}/`, payload);
    }
}

export default new InfraestructuraService();
