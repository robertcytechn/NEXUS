<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const home = { icon: 'pi pi-home', route: '/' };

const segmentMap = {
    'admin': 'Mando Central',
    'centro-servicios': 'Centro de Servicios',
    'operatividad': 'Operatividad',
    'evolucion-nexus': 'Evolución NEXUS',
    'auth': 'Autenticación',
    'pages': 'Páginas'
};

const breadcrumbs = computed(() => {
    const path = route.path;
    if (path === '/') return [];

    const segments = path.split('/').filter(item => item);
    const crumbs = [];
    let currentPath = '';

    segments.forEach((segment, index) => {
        currentPath += `/${segment}`;
        
        // Determine label
        let label = segmentMap[segment] || segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');
        
        // For the last item, try to use meta title if available
        if (index === segments.length - 1 && route.meta.title) {
            label = route.meta.title;
        }

        // Determine if it's a clickable link
        // In this app, intermediate paths like /admin or /centro-servicios often don't have a direct route
        // So we disable them unless we know they exist. 
        // For now, we'll assume only the last item is the "page" and 'home' is a link.
        // Actually, if we are at /admin/usuarios, /admin might not be a valid page.
        // But if we are at /admin, it might be.
        // Given the router config, /admin doesn't exist.
        // So strict path based: check if standard known parents.
        // Or simpler: disable all intermediate nodes for now as requested "visual aid" mostly, 
        // but user said "permitiendo retroceder fácilmente". 
        // If the parent doesn't exist, we can't go back to it.
        // But we can go back to "Inicio".
        
        crumbs.push({
            label: label,
            route: currentPath,
            disabled: index !== segments.length - 1 && !isKnownRoute(currentPath) // Disable if not last and not a known route
        });
    });

    return crumbs;
});

// Helper to check if a path might be valid (simplified)
// Since we don't have the full router list easily accessible as a flat list here without iterating router.getRoutes()
// and even then, '/admin' is not a route.
// So for now, we disabled intermediate paths to avoid 404s.
const isKnownRoute = (path) => {
    // Add paths here if they actually exist as summaries/dashboards
    return false; 
};
</script>

<template>
    <div class="flex items-center gap-2 text-sm text-surface-500 dark:text-surface-400 my-2">
        <router-link to="/" class="hover:text-primary transition-colors flex items-center">
            <i class="pi pi-home mr-1"></i>
            <span class="hidden sm:inline">Inicio</span>
        </router-link>
        
        <template v-for="(item, index) in breadcrumbs" :key="index">
            <i class="pi pi-chevron-right text-xs opacity-60"></i>
            <template v-if="!item.disabled">
                <router-link :to="item.route" class="hover:text-primary transition-colors">
                    {{ item.label }}
                </router-link>
            </template>
            <span v-else class="font-medium text-surface-900 dark:text-surface-0">
                {{ item.label }}
            </span>
        </template>
    </div>
</template>
