/**
 * Helper JavaScript para integración MAUI WebView
 * Incluye este archivo en tu aplicación Vue para habilitar compartir/descargar archivos
 */

class MauiShareHelper {
    /**
     * Comparte un archivo PDF o cualquier blob generado en Vue
     * @param {Blob} blob - El blob del archivo a compartir
     * @param {string} filename - Nombre del archivo (ej: "reporte.pdf")
     * @param {string} mimeType - Tipo MIME (ej: "application/pdf")
     */
    static async shareFile(blob, filename = 'archivo.pdf', mimeType = 'application/pdf') {
        // En escritorio/navegador web usar descarga tradicional directamente
        if (!this.isMauiWebView()) {
            this.downloadFallback(blob, filename);
            return false;
        }

        try {
            // Convertir Blob a Base64
            const base64 = await this.blobToBase64(blob);
            
            // Remover el prefijo "data:mime/type;base64," si existe
            const base64Data = base64.split(',')[1] || base64;
            
            // Construir URL personalizada
            const url = `nexus://share?filename=${encodeURIComponent(filename)}&data=${encodeURIComponent(base64Data)}&mimetype=${encodeURIComponent(mimeType)}`;
            
            // Navegar a la URL personalizada (será interceptada por MAUI)
            window.location.href = url;
            
            return true;
        } catch (error) {
            console.error('Error al compartir archivo:', error);
            
            // Fallback: usar descarga tradicional del navegador
            this.downloadFallback(blob, filename);
            return false;
        }
    }
    
    /**
     * Descarga un archivo (lo guarda localmente en MAUI)
     * @param {Blob} blob - El blob del archivo a descargar
     * @param {string} filename - Nombre del archivo
     */
    static async downloadFile(blob, filename = 'archivo.pdf') {
        // En escritorio/navegador web usar descarga tradicional directamente
        if (!this.isMauiWebView()) {
            this.downloadFallback(blob, filename);
            return false;
        }

        try {
            // Convertir Blob a Base64
            const base64 = await this.blobToBase64(blob);
            
            // Remover el prefijo si existe
            const base64Data = base64.split(',')[1] || base64;
            
            // Construir URL personalizada
            const url = `nexus://download?filename=${encodeURIComponent(filename)}&data=${encodeURIComponent(base64Data)}`;
            
            // Navegar a la URL personalizada
            window.location.href = url;
            
            return true;
        } catch (error) {
            console.error('Error al descargar archivo:', error);
            
            // Fallback: usar descarga tradicional
            this.downloadFallback(blob, filename);
            return false;
        }
    }
    
    /**
     * Convierte un Blob a Base64
     * @param {Blob} blob - El blob a convertir
     * @returns {Promise<string>} String Base64
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
     * Fallback: descarga tradicional del navegador
     * @param {Blob} blob - El blob a descargar
     * @param {string} filename - Nombre del archivo
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
    
    /**
     * Detecta si la aplicación está corriendo en MAUI WebView
     * @returns {boolean}
     */
    static isMauiWebView() {
        return window.navigator.userAgent.includes('MAUI') || 
               window.location.protocol === 'app:';
    }
}

// Exportar para usar en Vue
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MauiShareHelper;
}

// Hacer disponible globalmente
if (typeof window !== 'undefined') {
    window.MauiShareHelper = MauiShareHelper;
}
