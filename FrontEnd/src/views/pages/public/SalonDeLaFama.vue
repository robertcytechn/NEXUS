<script setup>
/**
 * SalonDeLaFama.vue
 * =================
 * Vista pública que muestra a los técnicos ordenados por su puntaje histórico
 * en un diseño de "Cartas de Héroe", importando el CardFama.vue para cada uno.
 */
import { ref, onMounted } from 'vue';
import CardFama from '@/components/CardFama.vue';
import { useToast } from 'primevue/usetoast';
import api from '@/service/api';

const toast = useToast();
const loading = ref(true);
const tecnicosGenerales = ref([]);

// ─────────────────────────────────────────────────────────────────────────────
// CONFIGURACIÓN DE TESTING (Fantasmas)
// ─────────────────────────────────────────────────────────────────────────────
// Cambiar a `false` en producción o mediante una variable de entorno.
const mostrarFantasmas = ref(true);

const datosFantasma = [
    {
        id: 'ghost-1',
        nombres: 'Jim',
        apellido_paterno: 'Raynor',
        casino_nombre: 'Mar Sara',
        avatar: 'https://ui-avatars.com/api/?name=Jim+Raynor&background=333&color=ddd&size=200',
        puntos_gamificacion_historico: 50,
        rango: { nivel: 1, titulo: 'Novato de Mantenimiento', progreso_pct: 50.0 }
    },
    {
        id: 'ghost-2',
        nombres: 'Gabriel',
        apellido_paterno: 'Tosh',
        casino_nombre: 'Tarsonis',
        avatar: 'https://ui-avatars.com/api/?name=Gabriel+Tosh&background=444&color=ddd&size=200',
        puntos_gamificacion_historico: 200,
        rango: { nivel: 2, titulo: 'Aprendiz de Sala', progreso_pct: 50.0 }
    },
    {
        id: 'ghost-3',
        nombres: 'Sarah',
        apellido_paterno: 'Kerrigan',
        casino_nombre: 'Antiga Prime',
        avatar: 'https://ui-avatars.com/api/?name=Sarah+Kerrigan&background=1e90ff&color=fff&size=200',
        puntos_gamificacion_historico: 450,
        rango: { nivel: 3, titulo: 'Técnico de Soporte', progreso_pct: 50.0 }
    },
    {
        id: 'ghost-4',
        nombres: 'Nova',
        apellido_paterno: 'Terra',
        casino_nombre: 'Korhal',
        avatar: 'https://ui-avatars.com/api/?name=Nova+Terra&background=00ff66&color=111&size=200',
        puntos_gamificacion_historico: 800,
        rango: { nivel: 4, titulo: 'Operador de Máquinas', progreso_pct: 50.0 }
    },
    {
        id: 'ghost-5',
        nombres: 'Rory',
        apellido_paterno: 'Swann',
        casino_nombre: 'Hyperion',
        avatar: 'https://ui-avatars.com/api/?name=Rory+Swann&background=f5c400&color=111&size=200',
        puntos_gamificacion_historico: 1250,
        rango: { nivel: 5, titulo: 'Especialista en Hardware', progreso_pct: 50.0 }
    },
    {
        id: 'ghost-6',
        nombres: 'Zeratul',
        apellido_paterno: 'Nerazim',
        casino_nombre: 'Shakuras',
        avatar: 'https://ui-avatars.com/api/?name=Zeratul&background=00ffff&color=111&size=200',
        puntos_gamificacion_historico: 1800,
        rango: { nivel: 6, titulo: 'Técnico Élite', progreso_pct: 50.0 }
    },
    {
        id: 'ghost-7',
        nombres: 'Artanis',
        apellido_paterno: 'Hierarch',
        casino_nombre: 'Aiur',
        avatar: 'https://ui-avatars.com/api/?name=Artanis&background=cc00ff&color=fff&size=200',
        puntos_gamificacion_historico: 2450,
        rango: { nivel: 7, titulo: 'Maestro Electrónico', progreso_pct: 50.0 }
    },
    {
        id: 'ghost-8',
        nombres: 'Alarak',
        apellido_paterno: 'Tal\'darim',
        casino_nombre: 'Slayn',
        avatar: 'https://ui-avatars.com/api/?name=Alarak&background=cc0000&color=fff&size=200',
        puntos_gamificacion_historico: 3200,
        rango: { nivel: 8, titulo: 'Arquitecto de Sala', progreso_pct: 50.0 }
    },
    {
        id: 'ghost-9',
        nombres: 'Tassadar',
        apellido_paterno: 'Adun',
        casino_nombre: 'Gantrithor',
        avatar: 'https://ui-avatars.com/api/?name=Tassadar&background=ffd700&color=111&size=200',
        puntos_gamificacion_historico: 4050,
        rango: { nivel: 9, titulo: 'Guardián del Casino', progreso_pct: 50.0 }
    },
    {
        id: 'ghost-10',
        nombres: 'Amon',
        apellido_paterno: 'Xel\'Naga',
        casino_nombre: 'Void',
        avatar: 'https://ui-avatars.com/api/?name=Amon&background=ff8800&color=111&size=200',
        puntos_gamificacion_historico: 9999,
        rango: { nivel: 10, titulo: 'Leyenda de NEXUS', progreso_pct: 100.0 }
    }
];

// ─────────────────────────────────────────────────────────────────────────────

const loadTecnicos = async () => {
    loading.value = true;
    try {
        const response = await api.get('gamificacion/salon-fama/');

        let dataReal = response.data || [];

        // Integración Segura de los datos reales con los fantasmas
        if (mostrarFantasmas.value) {
            tecnicosGenerales.value = [...datosFantasma, ...dataReal];
            // Reordenar por puntos después de mezclar para mantener coherencia
            tecnicosGenerales.value.sort((a, b) => b.puntos_gamificacion_historico - a.puntos_gamificacion_historico);
        } else {
            tecnicosGenerales.value = dataReal;
        }

    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'No se pudo cargar el Salón de la Fama',
            life: 3000
        });

        // Fallback a fantasmas si falla la API pero estamos en modo ghost
        if (mostrarFantasmas.value) {
            tecnicosGenerales.value = [...datosFantasma].sort((a, b) => b.puntos_gamificacion_historico - a.puntos_gamificacion_historico);
        }
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    loadTecnicos();
});

</script>

<template>
    <div class="salon-fama-container bg-surface-950 min-h-screen text-surface-0 pb-20 pt-10">

        <!-- Header -->
        <div class="text-center mb-16 relative z-10">
            <h1
                class="text-5xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-b from-yellow-300 via-amber-500 to-yellow-700 tracking-tighter uppercase drop-shadow-[0_0_15px_rgba(245,158,11,0.5)] mb-2 mt-4">
                SALÓN DE LA FAMA
            </h1>
            <p class="text-surface-400 uppercase tracking-[0.3em] font-semibold text-sm md:text-base">
                Los mejores técnicos de NEXUS
            </p>

            <!-- Controls fantasma (solo en dev) -->
            <div class="mt-4 flex justify-center items-center gap-2 text-surface-400 text-xs">
                <span>Modo Pruebas (Ghosts):</span>
                <button @click="mostrarFantasmas = !mostrarFantasmas; loadTecnicos();"
                    class="p-1 px-3 rounded text-white font-bold transition-colors"
                    :class="mostrarFantasmas ? 'bg-green-600 hover:bg-green-500' : 'bg-surface-700 hover:bg-surface-600'">
                    {{ mostrarFantasmas ? 'ON ✓' : 'OFF ✗' }}
                </button>
            </div>
        </div>

        <!-- Skeleton Loading -->
        <div v-if="loading"
            class="max-w-7xl mx-auto px-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-8 gap-y-20 justify-items-center">
            <div v-for="i in 8" :key="i" class="w-full max-w-[280px]">
                <div class="bg-surface-800 animate-pulse rounded-xl h-[380px] w-full border border-surface-700"></div>
                <!-- skeleton badge -->
                <div class="h-16 w-32 bg-surface-700 animate-pulse rounded-lg mx-auto -mt-8 relative z-20"></div>
            </div>
        </div>

        <!-- Results Grid -->
        <div v-else-if="tecnicosGenerales.length > 0"
            class="max-w-7xl mx-auto px-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-8 gap-y-24 justify-items-center">

            <CardFama v-for="tecnico in tecnicosGenerales" :key="tecnico.id" :tecnico="tecnico" />

        </div>

        <!-- Empty State -->
        <div v-else class="text-center text-surface-500 py-20">
            <i class="pi pi-users text-6xl mb-4 opacity-50"></i>
            <h3 class="text-2xl font-bold">Aún no hay técnicos clasificados.</h3>
            <p>Comienza a entregar recompensas y puntos para poblar el Salón de la Fama.</p>
        </div>

    </div>
</template>

<style scoped>
/* Fondo general inspirado en void / espacio */
.salon-fama-container {
    background-image: radial-gradient(circle at 50% 0%, #17171e 0%, #0a0a0f 100%);
    position: relative;
    overflow: hidden;
}

.salon-fama-container::before {
    content: "";
    position: absolute;
    inset: 0;
    background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSJyZ2JhKDAsMCwwLDApIj48L3JlY3Q+CjxyZWN0IHdpZHRoPSI0IiBoZWlnaHQ9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wNSkiPjwvcmVjdD4KPC9zdmc+') repeat;
    opacity: 0.2;
    pointer-events: none;
    z-index: 1;
}

.salon-fama-container>* {
    position: relative;
    z-index: 2;
}
</style>
