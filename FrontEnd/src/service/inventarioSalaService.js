import api from './api';

export default {
    getInventario(casinoId) {
        let url = 'inventario-sala/';
        if (casinoId) {
            url += `?casino=${casinoId}`;
        }
        return api.get(url).then(res => res.data);
    },

    save(articulo) {
        if (articulo.id) {
            return api.put(`inventario-sala/${articulo.id}/`, articulo);
        }
        return api.post('inventario-sala/', articulo);
    },

    toggleActivo(id, estadoActual) {
        // Invertimos el estado actual
        return api.patch(`inventario-sala/${id}/`, { esta_activo: !estadoActual });
    }
};