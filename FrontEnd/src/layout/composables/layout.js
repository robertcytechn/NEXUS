import { computed, reactive } from 'vue';

/**
 * Configuración global del layout de la aplicación
 * Estos valores se aplican por defecto en toda la aplicación
 * 
 * Configuración actual:
 * - Preset: Aura (tema de PrimeVue)
 * - Primary Color: cyan (color principal de la aplicación)
 * - Surface: slate (esquema de color de superficies)
 * - Dark Theme: desactivado por defecto
 * - Menu Mode: static (menú estático, no overlay)
 * 
 * Para cambiar estos valores, editar este archivo
 */
const layoutConfig = reactive({
    preset: 'Aura',          // Opciones: 'Aura', 'Lara', 'Nora'
    primary: 'cyan',         // Color primario - ver AppConfigurator.vue para opciones
    surface: 'slate',        // Esquema de superficies - opciones: 'slate', 'gray', 'zinc', 'neutral', 'stone', 'soho', 'viva', 'ocean'
    darkTheme: false,        // true para modo oscuro por defecto
    menuMode: 'static'       // 'static' o 'overlay'
});

const layoutState = reactive({
    staticMenuInactive: false,
    overlayMenuActive: false,
    profileSidebarVisible: false,
    configSidebarVisible: false,
    sidebarExpanded: false,
    menuHoverActive: false,
    activeMenuItem: null,
    activePath: null
});

export function useLayout() {
    const toggleDarkMode = () => {
        if (!document.startViewTransition) {
            executeDarkModeToggle();

            return;
        }

        document.startViewTransition(() => executeDarkModeToggle(event));
    };

    const executeDarkModeToggle = () => {
        layoutConfig.darkTheme = !layoutConfig.darkTheme;
        document.documentElement.classList.toggle('app-dark');
    };

    const toggleMenu = () => {
        if (isDesktop()) {
            if (layoutConfig.menuMode === 'static') {
                layoutState.staticMenuInactive = !layoutState.staticMenuInactive;
            }

            if (layoutConfig.menuMode === 'overlay') {
                layoutState.overlayMenuActive = !layoutState.overlayMenuActive;
            }
        } else {
            layoutState.mobileMenuActive = !layoutState.mobileMenuActive;
        }
    };

    const toggleConfigSidebar = () => {
        layoutState.configSidebarVisible = !layoutState.configSidebarVisible;
    };

    const hideMobileMenu = () => {
        layoutState.mobileMenuActive = false;
    };

    const changeMenuMode = (event) => {
        layoutConfig.menuMode = event.value;
        layoutState.staticMenuInactive = false;
        layoutState.mobileMenuActive = false;
        layoutState.sidebarExpanded = false;
        layoutState.menuHoverActive = false;
        layoutState.anchored = false;
    };

    const isDarkTheme = computed(() => layoutConfig.darkTheme);
    const isDesktop = () => window.innerWidth > 991;

    const hasOpenOverlay = computed(() => layoutState.overlayMenuActive);

    return {
        layoutConfig,
        layoutState,
        isDarkTheme,
        toggleDarkMode,
        toggleConfigSidebar,
        toggleMenu,
        hideMobileMenu,
        changeMenuMode,
        isDesktop,
        hasOpenOverlay
    };
}
