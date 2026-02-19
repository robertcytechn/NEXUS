<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api, { getUser } from '@/service/api';

const router = useRouter();
const visible = ref(false);
const searchQuery = ref('');
const searchResults = ref([]);
const activeIndex = ref(0);
const isLoading = ref(false);
let debounceTimeout = null;


// =============================================================================
// MENU LOCAL
// =============================================================================

// =============================================================================
// SEGURIDAD FRONT-END
// =============================================================================
// Definimos qué tipos de resultados puede ver cada rol.
// Los tipos coinciden con las claves 'type' del backend.
const ALL_TYPES = ['user', 'machine', 'ticket', 'supplier', 'model', 'inventory', 'evolution', 'casino', 'audit', 'infra', 'task', 'wiki'];
const BASIC_TYPES = ['machine', 'ticket', 'inventory', 'evolution', 'wiki', 'task', 'infra'];

const SEARCH_PERMISSIONS = {
    'ADMINISTRADOR': ALL_TYPES,
    'SUP SISTEMAS': ALL_TYPES,
    'GERENCIA': ['machine', 'ticket', 'supplier', 'casino', 'audit', 'infra', 'task', 'evolution'],
    'TECNICO': BASIC_TYPES,
    'SUPERVISOR SALA': BASIC_TYPES,
    'DEFAULT': BASIC_TYPES // Fallback
};

const menuItems = [
    { label: 'Dashboard', route: '/', icon: 'pi pi-home', keywords: 'inicio casa escritorio home' },
    { label: 'Notificaciones', route: '/notificaciones/lista', icon: 'pi pi-bell', keywords: 'alertas mensajes' },
    { label: 'Mi Perfil', route: '/profile', icon: 'pi pi-user', keywords: 'configuracion cuenta' },
    
    // Mando Central
    { label: 'Usuarios (Admin)', route: '/admin/usuarios', icon: 'pi pi-users', keywords: 'personal cuentas empleados' },
    { label: 'Casinos', route: '/admin/casinos', icon: 'pi pi-building', keywords: 'salas sucursales' },
    { label: 'Máquinas (Admin)', route: '/admin/maquinas', icon: 'pi pi-cog', keywords: 'slots tragamonedas' },
    
    // Centro de Servicios
    { label: 'Máquinas (Técnicos)', route: '/centro-servicios/maquinas', icon: 'pi pi-cog', keywords: 'slots maquinas' },
    { label: 'Tickets', route: '/centro-servicios/tickets', icon: 'pi pi-ticket', keywords: 'incidencias reportes fallas' },
    { label: 'Inventario de Sala', route: '/centro-servicios/inventario', icon: 'pi pi-box', keywords: 'refacciones partes' },
    { label: 'Proveedores', route: '/centro-servicios/proveedores', icon: 'pi pi-truck', keywords: 'vendedores externos' },
    { label: 'Wiki Técnica', route: '/centro-servicios/wiki', icon: 'pi pi-book', keywords: 'manuales guias ayuda' },
    
    // Operatividad
    { label: 'Auditorías', route: '/operatividad/auditorias-externas', icon: 'pi pi-file-check', keywords: 'revisiones externos' },
    { label: 'Incidencias Infraestructura', route: '/operatividad/incidencias-infraestructura', icon: 'pi pi-exclamation-triangle', keywords: 'goteras luz agua' },
    { label: 'Tareas Especiales', route: '/operatividad/tareas-especiales', icon: 'pi pi-check-square', keywords: 'pendientes extra' },
    
    // Evolución
    { label: 'Evolución NEXUS', route: '/evolucion-nexus', icon: 'pi pi-bolt', keywords: 'mejoras ideas nuevas funciones' },
];

const openSearch = () => {
    visible.value = true;
    searchQuery.value = '';
    searchResults.value = [];
    activeIndex.value = 0;
};

const closeSearch = () => {
    visible.value = false;
};

const onKeydown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        visible.value ? closeSearch() : openSearch();
    }
    
    if (visible.value) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (activeIndex.value < searchResults.value.length - 1) activeIndex.value++;
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (activeIndex.value > 0) activeIndex.value--;
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (searchResults.value.length > 0) {
                selectItem(searchResults.value[activeIndex.value]);
            }
        }
    }
};

const performSearch = async () => {
    const query = searchQuery.value.toLowerCase().trim();
    if (!query) {
        searchResults.value = [];
        return;
    }

    isLoading.value = true;
    
    // 1. Obtener Rol del Usuario y sus Permisos
    const currentUser = getUser();
    const userRole = currentUser?.rol?.nombre || 'DEFAULT';
    // Si el rol no existe exactamente, usamos DEFAULT
    const allowedTypes = SEARCH_PERMISSIONS[userRole] || SEARCH_PERMISSIONS['DEFAULT'];

    // 2. Búsqueda Local (Menú)
    const localResults = menuItems.filter(item => 
        item.label.toLowerCase().includes(query) || 
        item.keywords.includes(query)
    ).map(item => ({
        ...item,
        type: 'menu',
        sublabel: 'Opción de Menú'
    }));

    // 3. Búsqueda Remota (API) con Filtro de Tipos
    let remoteResults = [];
    if (query.length >= 2) {
        try {
            // Enviamos los tipos permitidos al backend
            const typesParam = allowedTypes.join(',');
            const response = await api.get(`usuarios/global-search/?q=${query}&types=${typesParam}`);
            if (response.status === 200 && Array.isArray(response.data)) {
                remoteResults = response.data;
            }
        } catch (error) {
            console.error("Error en búsqueda global:", error);
        }
    }

    // Combinar y limitar
    searchResults.value = [...localResults, ...remoteResults];
    activeIndex.value = 0;
    isLoading.value = false;
};

const onInput = () => {
    if (debounceTimeout) clearTimeout(debounceTimeout);
    isLoading.value = true; // Feedback inmediato
    debounceTimeout = setTimeout(performSearch, 300);
};

const selectItem = (item) => {
    if (item.route) {
        router.push(item.route);
        closeSearch();
    }
};

onMounted(() => {
    window.addEventListener('keydown', onKeydown);
});

onUnmounted(() => {
    window.removeEventListener('keydown', onKeydown);
});

defineExpose({ openSearch });
</script>

<template>
    <Dialog 
        v-model:visible="visible" 
        modal 
        :dismissableMask="true" 
        :showHeader="false"
        :closeOnEscape="true"
        class="search-dialog"
        :style="{ width: '50rem', maxWidth: '90vw' }"
        :contentStyle="{ padding: '0', borderRadius: '12px' }"
    >
        <div class="flex flex-col h-full bg-surface-0 dark:bg-surface-900 rounded-xl overflow-hidden">
            <!-- Header / Input -->
            <div class="flex items-center border-b border-surface-200 dark:border-surface-700 p-4 gap-3">
                <i class="pi pi-search text-xl text-primary-500"></i>
                <input 
                    ref="inputRef"
                    v-model="searchQuery"
                    @input="onInput"
                    type="text" 
                    placeholder="Buscar usuarios (Admin), máquinas, tickets o menú..." 
                    class="flex-1 bg-transparent border-none outline-none text-lg text-surface-900 dark:text-surface-0 placeholder-surface-400"
                    autofocus
                    autocomplete="off"
                />
                <div class="flex items-center gap-2">
                    <span class="hidden md:inline-flex items-center justify-center bg-surface-100 dark:bg-surface-800 rounded px-2 py-1 text-xs text-surface-500 font-mono border border-surface-200 dark:border-surface-700">ESC</span>
                </div>
            </div>

            <!-- Resultados -->
            <div class="max-h-[60vh] overflow-y-auto custom-scrollbar p-2">
                <div v-if="isLoading" class="flex justify-center items-center py-8">
                    <i class="pi pi-spinner pi-spin text-3xl text-primary-500"></i>
                </div>

                <div v-else-if="searchResults.length > 0" class="flex flex-col gap-1">
                    <div 
                        v-for="(item, index) in searchResults" 
                        :key="index"
                        @click="selectItem(item)"
                        class="flex items-center p-3 rounded-lg cursor-pointer transition-all duration-200 gap-4 group"
                        :class="[
                            index === activeIndex 
                                ? 'bg-primary-50 dark:bg-primary-900/20 border-l-4 border-primary-500' 
                                : 'hover:bg-surface-50 dark:hover:bg-surface-800 border-l-4 border-transparent'
                        ]"
                        @mouseenter="activeIndex = index"
                    >
                        <div 
                            class="flex items-center justify-center w-10 h-10 rounded-full"
                            :class="[
                                item.type === 'user' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' :
                                item.type === 'machine' ? 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400' :
                                item.type === 'ticket' ? 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400' :
                                item.type === 'supplier' ? 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400' :
                                item.type === 'model' ? 'bg-cyan-100 text-cyan-600 dark:bg-cyan-900/30 dark:text-cyan-400' :
                                item.type === 'inventory' ? 'bg-teal-100 text-teal-600 dark:bg-teal-900/30 dark:text-teal-400' :
                                item.type === 'evolution' ? 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400' :
                                item.type === 'casino' ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400' :
                                item.type === 'audit' ? 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300' : 
                                item.type === 'infra' ? 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400' :
                                item.type === 'task' ? 'bg-rose-100 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400' :
                                item.type === 'wiki' ? 'bg-lime-100 text-lime-600 dark:bg-lime-900/30 dark:text-lime-400' :
                                'bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-400'
                            ]"
                        >
                            <i :class="item.icon"></i>
                        </div>
                        
                        <div class="flex-1 min-w-0">
                            <div class="font-medium text-surface-900 dark:text-surface-0 truncate" :class="{ 'text-primary-600 dark:text-primary-400': index === activeIndex }">
                                {{ item.label }}
                            </div>
                            <div class="text-sm text-surface-500 dark:text-surface-400 truncate">
                                {{ item.sublabel }}
                            </div>
                        </div>

                        <i v-if="index === activeIndex" class="pi pi-arrow-left text-primary-500"></i>
                    </div>
                </div>

                <div v-else-if="searchQuery" class="flex flex-col items-center justify-center py-12 text-surface-500">
                    <i class="pi pi-search text-4xl mb-3 opacity-50"></i>
                    <p>No hay resultados para "{{ searchQuery }}"</p>
                </div>

                <div v-else class="flex flex-col items-center justify-center py-12 text-surface-500 opacity-60">
                    <i class="pi pi-compass text-4xl mb-3"></i>
                    <p>Escribe para buscar en todo NEXUS</p>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="bg-surface-50 dark:bg-surface-900 border-t border-surface-200 dark:border-surface-700 p-2 px-4 flex justify-between items-center text-xs text-surface-500">
                <div class="flex gap-4">
                    <span class="flex items-center gap-1"><i class="pi pi-arrow-up"></i> <i class="pi pi-arrow-down"></i> Navegar</span>
                    <span class="flex items-center gap-1"><i class="pi pi-arrow-left"></i> Seleccionar</span>
                </div>
                <span>NEXUS Spotlight</span>
            </div>
        </div>
    </Dialog>
</template>

<style scoped>
/* Eliminar estilos por defecto del input number si hubiera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
