<script setup>
import FloatingConfigurator from '@/components/FloatingConfigurator.vue';
import { onMounted, nextTick } from 'vue';
import { useLayout } from '@/layout/composables/layout';
import { $t } from '@primeuix/themes';
import Aura from '@primeuix/themes/aura';

const { layoutConfig } = useLayout();

const primaryColors = {
    orange: { 50: '#fff7ed', 100: '#ffedd5', 200: '#fed7aa', 300: '#fdba74', 400: '#fb923c', 500: '#f97316', 600: '#ea580c', 700: '#c2410c', 800: '#9a3412', 900: '#7c2d12', 950: '#431407' }
};

const surfaces = {
    slate: { 0: '#ffffff', 50: '#f8fafc', 100: '#f1f5f9', 200: '#e2e8f0', 300: '#cbd5e1', 400: '#94a3b8', 500: '#64748b', 600: '#475569', 700: '#334155', 800: '#1e293b', 900: '#0f172a', 950: '#020617' }
};

function getPresetExt() {
    const primaryPalette = primaryColors.orange;
    
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

onMounted(async () => {
    const surfacePalette = surfaces[layoutConfig.surface];
    
    $t()
        .preset(Aura)
        .preset(getPresetExt())
        .surfacePalette(surfacePalette)
        .use({ useDefaultOptions: true });
    
    await nextTick();
});
</script>

<template>
    <FloatingConfigurator />
    <div class="bg-surface-50 dark:bg-surface-950 flex items-center justify-center min-h-screen min-w-[100vw] overflow-hidden relative">
        <!-- Decoradores de fondo -->
        <div class="absolute w-full h-full overflow-hidden pointer-events-none">
            <div class="absolute top-[10%] left-[10%] w-96 h-96 bg-[var(--primary-color)] opacity-20 rounded-full blur-[100px]"></div>
            <div class="absolute bottom-[10%] right-[10%] w-96 h-96 bg-[var(--primary-color)] opacity-20 rounded-full blur-[100px]"></div>
        </div>

        <div class="flex flex-col items-center justify-center relative z-10">
            <div style="border-radius: 56px; padding: 0.3rem; background: linear-gradient(180deg, var(--primary-color) 10%, rgba(33, 150, 243, 0) 30%)">
                <div class="w-full bg-surface-0 dark:bg-surface-900 py-20 px-8 sm:px-20 flex flex-col items-center" style="border-radius: 53px">
                    <div class="gap-4 flex flex-col items-center">
                        <div class="flex justify-center items-center border-2 border-[var(--primary-color)] rounded-full" style="width: 3.2rem; height: 3.2rem">
                            <i class="text-[var(--primary-color)] pi pi-fw pi-lock text-2xl!"></i>
                        </div>
                        <h1 class="text-surface-900 dark:text-surface-0 font-bold text-4xl lg:text-5xl mb-2">Acceso Denegado</h1>
                        <span class="text-muted-color mb-8">No tienes los permisos necesarios. Por favor contacta al administrador.</span>
                        <img src="/demo/images/access/asset-access.svg" alt="Access denied" class="mb-8" width="80%" />
                        <div class="col-span-12 mt-8 text-center">
                            <Button as="router-link" label="Ir al Inicio" to="/" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
