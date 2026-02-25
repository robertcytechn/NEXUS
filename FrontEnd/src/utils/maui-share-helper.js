/**
 * Helper JavaScript para integración MAUI WebView
 * Incluye este archivo en tu aplicación Vue para habilitar compartir/descargar archivos
 *
 * Jerarquía de métodos (del más al menos confiable):
 *   1. window.NexusApp (JavascriptInterface nativo de Android) — primario
 *   2. nexus:// URL scheme (Navigating event de MAUI)               — fallback MAUI
 *   3. <a download> tradicional del navegador                       — fallback web
 */

class MauiShareHelper {
    /**
     * Detecta si la aplicación está corriendo en MAUI WebView con JS Bridge disponible
     * @returns {boolean}
     */
    static isBridgeAvailable() {
        return typeof window.NexusApp !== 'undefined' &&
               typeof window.NexusApp.shareFile === 'function';
    }

    /**
     * Detecta si está corriendo en MAUI WebView (por user-agent o protocolo)
     * @returns {boolean}
     */
    static isMauiWebView() {
        return window.navigator.userAgent.includes('MAUI') ||
               window.location.protocol === 'app:' ||
               this.isBridgeAvailable();
    }

    /**
     * Comparte un archivo PDF o cualquier blob generado en Vue.
     * En MAUI abre el menú nativo "Compartir con..."; en web descarga directamente.
     * @param {Blob} blob - El blob del archivo a compartir
     * @param {string} filename - Nombre del archivo (ej: "reporte.pdf")
     * @param {string} mimeType - Tipo MIME (ej: "application/pdf")
     * @returns {Promise<boolean>} true si fue a MAUI, false si usó descarga web
     */
    static async shareFile(blob, filename = 'archivo.pdf', mimeType = 'application/pdf') {
        // En escritorio/navegador web usar descarga tradicional directamente
        if (!this.isMauiWebView()) {
            this.downloadFallback(blob, filename);
            return false;
        }

        try {
            const base64Data = await this._blobToBase64Data(blob);

            // Método 1: JS Bridge nativo (más confiable, sin límite de URL)
            if (this.isBridgeAvailable()) {
                window.NexusApp.shareFile(filename, base64Data, mimeType);
                return true;
            }

            // Método 2: URL scheme nexus:// (fallback para MAUI sin bridge)
            const url = `nexus://share?filename=${encodeURIComponent(filename)}&data=${encodeURIComponent(base64Data)}&mimetype=${encodeURIComponent(mimeType)}`;
            window.location.href = url;
            return true;

        } catch (error) {
            console.error('[MauiShareHelper] Error al compartir archivo:', error);
            this.downloadFallback(blob, filename);
            return false;
        }
    }

    /**
     * Descarga/guarda un archivo localmente.
     * En MAUI guarda en almacenamiento y ofrece compartir; en web descarga directamente.
     * @param {Blob} blob - El blob del archivo a descargar
     * @param {string} filename - Nombre del archivo
     * @returns {Promise<boolean>}
     */
    static async downloadFile(blob, filename = 'archivo.pdf') {
        // En escritorio/navegador web usar descarga tradicional directamente
        if (!this.isMauiWebView()) {
            this.downloadFallback(blob, filename);
            return false;
        }

        try {
            const base64Data = await this._blobToBase64Data(blob);

            // Método 1: JS Bridge nativo
            if (this.isBridgeAvailable() && typeof window.NexusApp.downloadFile === 'function') {
                window.NexusApp.downloadFile(filename, base64Data);
                return true;
            }

            // Método 2: URL scheme nexus://download
            const url = `nexus://download?filename=${encodeURIComponent(filename)}&data=${encodeURIComponent(base64Data)}`;
            window.location.href = url;
            return true;

        } catch (error) {
            console.error('[MauiShareHelper] Error al descargar archivo:', error);
            this.downloadFallback(blob, filename);
            return false;
        }
    }

    /**
     * Convierte un Blob a string Base64 puro (sin el prefijo data:...)
     * @param {Blob} blob
     * @returns {Promise<string>}
     */
    static _blobToBase64Data(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                const result = reader.result;
                // Remover prefijo "data:mime/type;base64,"
                const base64 = result.split(',')[1] || result;
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }

    /**
     * Convierte un Blob a Base64 completo (con prefijo data:...)
     * @param {Blob} blob
     * @returns {Promise<string>}
     */
    static blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }

    /**
     * Fallback: descarga tradicional del navegador mediante <a download>
     * @param {Blob} blob
     * @param {string} filename
     */
    static downloadFallback(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Exportar como módulo ES6 (requerido por Vite/Vue)
export default MauiShareHelper;

// Hacer disponible globalmente (útil para scripts externos o MAUI)
if (typeof window !== 'undefined') {
    window.MauiShareHelper = MauiShareHelper;
}
