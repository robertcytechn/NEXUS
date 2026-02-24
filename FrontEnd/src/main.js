import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import Aura from '@primeuix/themes/aura';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';

import '@/assets/tailwind.css';
import '@/assets/styles.scss';

const app = createApp(App);

app.use(router);
app.use(PrimeVue, {
    // ========== CONFIGURACIÓN DEL TEMA ==========
    theme: {
        preset: Aura, // Preset del tema (Aura, Lara, Nora, etc.)
        options: {
            darkModeSelector: '.app-dark', // Selector CSS para activar modo oscuro (ej: '.app-dark', 'class', 'system')
            cssLayer: false // Habilita CSS @layer para mejor control de especificidad
        }
    },

    // ========== EFECTOS VISUALES ==========
    ripple: true, // Habilita el efecto ripple (onda) al hacer clic en botones y componentes

    // ========== ESTILOS DE INPUT ==========
    inputStyle: 'outlined', // Estilo de los campos de entrada: 'outlined' (con borde) o 'filled' (con fondo)
    inputVariant: 'outlined', // Variante de input (alternativa moderna a inputStyle): 'outlined' o 'filled'

    // ========== CONFIGURACIÓN REGIONAL ==========
    locale: {
        // Configuración de idioma para componentes (Calendar, DataTable, etc.)
        startsWith: 'Empieza con',
        contains: 'Contiene',
        notContains: 'No contiene',
        endsWith: 'Termina con',
        equals: 'Igual a',
        notEquals: 'Diferente de',
        noFilter: 'Sin filtro',
        lt: 'Menor que',
        lte: 'Menor o igual que',
        gt: 'Mayor que',
        gte: 'Mayor o igual que',
        dateIs: 'Fecha es',
        dateIsNot: 'Fecha no es',
        dateBefore: 'Fecha antes de',
        dateAfter: 'Fecha después de',
        clear: 'Limpiar',
        apply: 'Aplicar',
        matchAll: 'Coincidir todo',
        matchAny: 'Coincidir cualquiera',
        addRule: 'Agregar regla',
        removeRule: 'Eliminar regla',
        accept: 'Sí',
        reject: 'No',
        choose: 'Elegir',
        upload: 'Subir',
        cancel: 'Cancelar',
        dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
        dayNamesShort: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
        dayNamesMin: ['D', 'L', 'M', 'X', 'J', 'V', 'S'],
        monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        monthNamesShort: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
        today: 'Hoy',
        weekHeader: 'Sm',
        firstDayOfWeek: 1,
        dateFormat: 'dd/mm/yy',
        weak: 'Débil',
        medium: 'Medio',
        strong: 'Fuerte',
        passwordPrompt: 'Escribe una contraseña',
        emptyFilterMessage: 'No se encontraron resultados',
        emptyMessage: 'No hay opciones disponibles'
    },

    // ========== OPCIONES DE FILTRADO ==========
    filterMatchModeOptions: {
        // Define qué modos de coincidencia están disponibles para cada tipo de dato
        text: ['startsWith', 'contains', 'notContains', 'endsWith', 'equals', 'notEquals'],
        numeric: ['equals', 'notEquals', 'lt', 'lte', 'gt', 'gte'],
        date: ['dateIs', 'dateIsNot', 'dateBefore', 'dateAfter']
    },

    // ========== Z-INDEX (CAPAS) ==========
    zIndex: {
        // Controla el orden de apilamiento de los componentes overlay
        modal: 1100,        // Diálogos modales
        overlay: 1000,      // Overlays en general (OverlayPanel, etc.)
        menu: 1000,         // Menús desplegables
        tooltip: 1100,      // Tooltips
        toast: 1200         // Notificaciones toast
    },

    // ========== PASS THROUGH (PT) ==========
    // Permite personalizar las props de cualquier componente a nivel global
    pt: undefined, // Objeto con personalizaciones globales para componentes (ej: { button: { root: { class: 'mi-clase' } } })
    
    // ========== OPCIONES DE PASS THROUGH ==========
    ptOptions: {
        // Opciones para el sistema PassThrough
        mergeSections: true,     // Combina secciones PT en lugar de sobrescribirlas
        mergeProps: false        // Combina props PT en lugar de sobrescribirlas
    },

    // ========== MODO SIN ESTILOS ==========
    unstyled: false, // Deshabilita todos los estilos por defecto (útil para UI totalmente personalizada)

    // ========== CONTENT SECURITY POLICY ==========
    csp: {
        // Configuración para entornos con políticas de seguridad estrictas
        nonce: undefined // Nonce para estilos inline cuando se usa CSP (ej: 'random-nonce-123')
    }
});
app.use(ToastService);
app.use(ConfirmationService);

app.mount('#app');


/**
 * app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: '.app-dark'
        }
    }
});
 */