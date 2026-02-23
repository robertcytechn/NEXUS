/**
 * gamificacionUtils.js
 * ====================
 * Utilidades para mostrar notificaciones de puntos NEXUS en el frontend.
 *
 * Uso:
 *   import { mostrarToastPuntos } from '@/service/gamificacionUtils'
 *   mostrarToastPuntos(toast, respuesta.data?.puntos_nexus)
 */

/**
 * Muestra un toast con el detalle de los puntos NEXUS obtenidos.
 *
 * @param {object} toast       - Instancia de useToast() de PrimeVue.
 * @param {object|null} puntos - Objeto puntos_nexus devuelto por el servidor, o null/undefined.
 * @param {number} [life=5000] - Duración del toast en milisegundos.
 */
export function mostrarToastPuntos(toast, puntos, life = 5000) {
    if (!puntos || !puntos.puntos_otorgados || puntos.puntos_otorgados <= 0) return;

    const rangoTexto = puntos.rango_titulo
        ? ` | ${puntos.rango_titulo}`
        : '';

    toast.add({
        severity: 'success',
        summary: '🏅 ¡Puntos NEXUS!',
        detail: `${puntos.mensaje_nexus || `+${puntos.puntos_otorgados} puntos`}${rangoTexto} (Total: ${puntos.puntos_totales})`,
        life,
        group: 'nexus-puntos',
    });
}

/**
 * Combina dos objetos puntos_nexus acumulando los puntos_otorgados.
 * Útil cuando una sola acción genera dos llamadas API (ej. bitácora + cierre de ticket).
 *
 * @param {object|null} base      - Primer resultado de puntos_nexus (puede ser null).
 * @param {object|null} adicional - Segundo resultado a acumular.
 * @returns {object|null}
 */
export function acumularPuntos(base, adicional) {
    if (!base && !adicional) return null;
    if (!base) return adicional;
    if (!adicional) return base;

    return {
        ...adicional,                            // por defecto usamos los datos más recientes
        puntos_otorgados: (base.puntos_otorgados || 0) + (adicional.puntos_otorgados || 0),
        mensaje_nexus: `🏅 +${(base.puntos_otorgados || 0) + (adicional.puntos_otorgados || 0)} puntos NEXUS acumulados en esta acción`,
    };
}
