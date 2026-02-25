/**
 * useContactLinks — Tarea 7: Links de contacto seguros para WebView
 *
 * Problema: Los esquemas directos `tel:` y `mailto:` pueden romper el WebView
 * de Android/iOS al intentar lanzar apps externas sin el puente nativo adecuado.
 *
 * Solución: Detectar el entorno (móvil/WebView vs escritorio) y actuar distinto:
 *  - Escritorio → abre el link nativo (mailto: / tel:) en una nueva pestaña.
 *  - Móvil/WebView → copia el valor al portapapeles y muestra un Toast/alerta.
 */

/**
 * Detecta si estamos en un entorno móvil o WebView.
 * Combina user-agent con el ancho de pantalla para mayor precisión.
 */
export function isMobileOrWebView() {
    const ua = navigator.userAgent || '';
    const isMobileUA = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua);
    const isSmallScreen = window.innerWidth <= 768;
    // navigator.share disponible indica que estamos en un contexto móvil/PWA
    const hasShareAPI = typeof navigator.share === 'function';
    return isMobileUA || isSmallScreen || hasShareAPI;
}

/**
 * Copia un texto al portapapeles de forma compatible con WebView.
 * Usa la Clipboard API moderna con fallback a execCommand para entornos antiguos.
 * @param {string} text
 * @returns {Promise<boolean>} true si tuvo éxito
 */
export async function copiarAlPortapapeles(text) {
    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(text);
            return true;
        }
        // Fallback para WebViews sin clipboard API
        const el = document.createElement('textarea');
        el.value = text;
        el.style.cssText = 'position:fixed;top:-9999px;left:-9999px;opacity:0;';
        document.body.appendChild(el);
        el.select();
        const exito = document.execCommand('copy');
        document.body.removeChild(el);
        return exito;
    } catch {
        return false;
    }
}

/**
 * Composable principal para manejar links de contacto de forma segura.
 *
 * @example
 * const { abrirTelefono, abrirEmail } = useContactLinks(toast);
 * // En template: @click="abrirTelefono(data.telefono_soporte)"
 */
export function useContactLinks(toast) {
    /**
     * Maneja un enlace telefónico (tel:).
     * - Escritorio → abre la app de llamadas/Skype via window.open.
     * - Móvil/WebView → copia el número al portapapeles + toast.
     * @param {string} numero
     */
    const abrirTelefono = async (numero) => {
        if (!numero) return;
        if (isMobileOrWebView()) {
            const exito = await copiarAlPortapapeles(numero);
            if (toast) {
                toast.add({
                    severity: exito ? 'success' : 'info',
                    summary: exito ? 'Número copiado' : 'Número de teléfono',
                    detail: exito ? `${numero} copiado al portapapeles.` : numero,
                    life: 3500
                });
            }
        } else {
            window.open(`tel:${numero}`, '_blank');
        }
    };

    /**
     * Maneja un enlace de email (mailto:).
     * - Escritorio → abre el cliente de correo via window.open.
     * - Móvil/WebView → copia el email al portapapeles + toast.
     * @param {string} email
     */
    const abrirEmail = async (email) => {
        if (!email) return;
        if (isMobileOrWebView()) {
            const exito = await copiarAlPortapapeles(email);
            if (toast) {
                toast.add({
                    severity: exito ? 'success' : 'info',
                    summary: exito ? 'Email copiado' : 'Dirección de email',
                    detail: exito ? `${email} copiado al portapapeles.` : email,
                    life: 3500
                });
            }
        } else {
            window.open(`mailto:${email}`, '_blank');
        }
    };

    return { abrirTelefono, abrirEmail, isMobileOrWebView };
}
