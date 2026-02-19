<script setup>
import { useLayout } from '@/layout/composables/layout';
import { computed, onMounted, nextTick } from 'vue';
import AppFooter from './AppFooter.vue';
import AppSidebar from './AppSidebar.vue';
import AppTopbar from './AppTopbar.vue';
import AppBreadcrumb from '@/components/AppBreadcrumb.vue';
import { $t, updatePreset, updateSurfacePalette } from '@primeuix/themes';
import Aura from '@primeuix/themes/aura';

const { layoutConfig, layoutState, hideMobileMenu } = useLayout();

const containerClass = computed(() => {
    return {
        'layout-overlay': layoutConfig.menuMode === 'overlay',
        'layout-static': layoutConfig.menuMode === 'static',
        'layout-overlay-active': layoutState.overlayMenuActive,
        'layout-mobile-active': layoutState.mobileMenuActive,
        'layout-static-inactive': layoutState.staticMenuInactive
    };
});

// Paletas de colores
const primaryColors = {
    cyan: { 50: '#ecfeff', 100: '#cffafe', 200: '#a5f3fc', 300: '#67e8f9', 400: '#22d3ee', 500: '#06b6d4', 600: '#0891b2', 700: '#0e7490', 800: '#155e75', 900: '#164e63', 950: '#083344' }
};

const surfaces = {
    slate: { 0: '#ffffff', 50: '#f8fafc', 100: '#f1f5f9', 200: '#e2e8f0', 300: '#cbd5e1', 400: '#94a3b8', 500: '#64748b', 600: '#475569', 700: '#334155', 800: '#1e293b', 900: '#0f172a', 950: '#020617' }
};

// Función para obtener la extensión del preset con el color primario
function getPresetExt() {
    const primaryPalette = primaryColors[layoutConfig.primary];
    
    return {
        semantic: {
            primary: primaryPalette,
            colorScheme: {
                light: {
                    primary: {
                        color: '{primary.500}',
                        contrastColor: '#ffffff',
                        hoverColor: '{primary.600}',
                        activeColor: '{primary.700}'
                    },
                    highlight: {
                        background: '{primary.50}',
                        focusBackground: '{primary.100}',
                        color: '{primary.700}',
                        focusColor: '{primary.800}'
                    }
                },
                dark: {
                    primary: {
                        color: '{primary.400}',
                        contrastColor: '{surface.900}',
                        hoverColor: '{primary.300}',
                        activeColor: '{primary.200}'
                    },
                    highlight: {
                        background: 'color-mix(in srgb, {primary.400}, transparent 84%)',
                        focusBackground: 'color-mix(in srgb, {primary.400}, transparent 76%)',
                        color: 'rgba(255,255,255,.87)',
                        focusColor: 'rgba(255,255,255,.87)'
                    }
                }
            }
        }
    };
}

// Inicializar el tema con los colores configurados
onMounted(async () => {
    const surfacePalette = surfaces[layoutConfig.surface];
    
    // Aplicar el preset Aura con los colores primarios y surface personalizados
    $t()
        .preset(Aura)
        .preset(getPresetExt())
        .surfacePalette(surfacePalette)
        .use({ useDefaultOptions: true });
    
    // Esperar a que el DOM se actualice con las nuevas variables CSS
    await nextTick();
    
    // Esperar un momento adicional para que las variables CSS se apliquen completamente
    setTimeout(() => {
        // Forzar actualización disparando los watchers con una re-asignación
        const tempPrimary = layoutConfig.primary;
        const tempSurface = layoutConfig.surface;
        
        layoutConfig.primary = '';
        layoutConfig.surface = '';
        
        nextTick(() => {
            layoutConfig.primary = tempPrimary;
            layoutConfig.surface = tempSurface;
        });
    }, 100);
});
</script>

<template>
    <div class="layout-wrapper" :class="containerClass">
        <AppTopbar />
        <AppSidebar />
        <div class="layout-main-container">
            <div class="layout-main">
                <AppBreadcrumb />
                <router-view />
            </div>
            <AppFooter />
        </div>
        <div class="layout-mask animate-fadein" @click="hideMobileMenu" />
    </div>
    <Toast />
</template>
