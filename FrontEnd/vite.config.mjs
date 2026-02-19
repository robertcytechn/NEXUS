import { fileURLToPath, URL } from 'node:url';

import { PrimeVueResolver } from '@primevue/auto-import-resolver';
import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';
import Components from 'unplugin-vue-components/vite';
import { defineConfig } from 'vite';

// https://vitejs.dev/config/
export default defineConfig({
    optimizeDeps: {
        noDiscovery: true
    },
    plugins: [
        vue(),
        tailwindcss(),
        Components({
            resolvers: [PrimeVueResolver()]
        })
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    css: {
        preprocessorOptions: {
            scss: {
                api: 'modern-compiler'
            }
        }
    },
    build: {
        sourcemap: false // Deshabilitar source maps en producción
    },
    server: {
        host: '0.0.0.0', // Permite conexiones desde cualquier IP
        port: 5173,
        strictPort: true,
        allowedHosts: ['localhost', 'cytechn.ddns.net'], // Dominios permitidos para acceso
        // Suprimir advertencias de source maps en desarrollo
        hmr: {
            overlay: true,
            clientPort: 5173
        }
    }
});
