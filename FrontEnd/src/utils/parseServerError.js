/**
 * Extrae un mensaje de error legible desde una respuesta de error de Axios / Django REST Framework.
 *
 * DRF puede retornar errores en varios formatos:
 *  - { detail: "mensaje" }                        → errores de permiso / 404
 *  - { mensaje: "mensaje" }                       → errores personalizados del proyecto
 *  - { message: "mensaje" }                       → variante en inglés
 *  - { error: "mensaje" }                         → variante genérica
 *  - { non_field_errors: ["msg1", "msg2"] }       → errores no ligados a un campo
 *  - { campo: ["error1", "error2"], ... }         → errores de validación por campo
 *
 * @param {unknown} error        El objeto de error capturado en el catch
 * @param {string}  fallback     Mensaje genérico si no se puede extraer nada del servidor
 * @returns {string}             Mensaje resultado, listo para mostrar en un toast
 */
export function parseServerError(error, fallback = 'Ocurrió un error inesperado.') {
    const data = error?.response?.data;

    if (!data) return fallback;

    // Formatos planos de un solo campo
    if (typeof data === 'string') return data;
    if (data.detail) return String(data.detail);
    if (data.mensaje) return String(data.mensaje);
    if (data.message) return String(data.message);
    if (data.error) return String(data.error);

    // non_field_errors (array)
    if (Array.isArray(data.non_field_errors) && data.non_field_errors.length) {
        return data.non_field_errors.join(' | ');
    }

    // Errores de validación por campo: { campo: ["msg"], otro: ["msg"] }
    if (typeof data === 'object') {
        const lineas = [];
        for (const [campo, valor] of Object.entries(data)) {
            const msgs = Array.isArray(valor) ? valor.join(', ') : String(valor);
            const etiqueta = campo === 'non_field_errors' ? '' : `${campo}: `;
            lineas.push(`${etiqueta}${msgs}`);
        }
        if (lineas.length) return lineas.join(' | ');
    }

    return fallback;
}
