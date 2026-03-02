<script setup>
/**
 * CardFama.vue
 * ============
 * Componente que muestra a un técnico con estilo "Carta de Héroe" (StarCraft / HOTS)
 * usando el sistema de gamificación de NEXUS.
 */
import { computed } from 'vue';
import InsigniaRangoAnimada from '@/components/InsigniaRangoAnimada.vue';
import api from '@/service/api';

const props = defineProps({
    tecnico: {
        type: Object,
        required: true
    }
});

// Extraer info de forma más amigable
const fullName = computed(() => {
    return `${props.tecnico.nombres || ''} ${props.tecnico.apellido_paterno || ''}`.trim();
});

const rango = computed(() => props.tecnico.rango || {});
const nivel = computed(() => rango.value.nivel || 1);
const progresoPct = computed(() => rango.value.progreso_pct || 0);

const avatarUrl = computed(() => {
    if (props.tecnico.avatar) {
        if (props.tecnico.avatar.startsWith('http')) return props.tecnico.avatar;
        // Obtenemos la baseURL de la instancia de axios (ej. http://localhost:8000/api/)
        // y le quitamos el '/api/' del final si lo tiene para construir la ruta al medio.
        const baseUrl = api.defaults.baseURL || '';
        const serverUrl = baseUrl.replace(/\/api\/?$/, '');
        return props.tecnico.avatar.startsWith('/') ? `${serverUrl}${props.tecnico.avatar}` : props.tecnico.avatar;
    }
    // Fallback imagen por defecto
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(fullName.value)}&background=222&color=fff&size=150`;
});

// Mapear el nivel a estilos específicos de la carta (bordes y sombras) basándonos 
// en InsigniaRangoAnimada.vue
const cardStylesByLevel = {
    1: 'border-surface-600 shadow-[0_0_15px_rgba(0,0,0,0.8)] shadow-surface-900', // Novato (metálico oscuro)
    2: 'border-surface-400 shadow-[0_0_15px_rgba(255,255,255,0.1)]', // Aprendiz (pulido)
    3: 'border-blue-500 shadow-[0_0_20px_rgba(30,144,255,0.4)]', // Soporte
    4: 'border-green-500 shadow-[0_0_20px_rgba(0,255,102,0.4)]', // Operador
    5: 'border-yellow-600 shadow-[0_0_20px_rgba(245,196,0,0.4)]', // Especialista Hardware
    6: 'border-cyan-500 shadow-[0_0_25px_rgba(0,255,255,0.5)]', // Técnico Élite
    7: 'border-fuchsia-500 shadow-[0_0_25px_rgba(204,0,255,0.5)]', // Maestro Electrónico
    8: 'border-red-600 shadow-[0_0_30px_rgba(204,0,0,0.6)]', // Arquitecto de Sala
    9: 'border-yellow-400 shadow-[0_0_30px_rgba(255,215,0,0.6)]', // Guardián del Casino
    10: 'border-yellow-300 shadow-[0_0_40px_rgba(255,215,0,0.8)]', // Leyenda
};

const borderColorClass = computed(() => cardStylesByLevel[nivel.value] || cardStylesByLevel[1]);
const badgeNameClass = computed(() => 'insignia-nombre-' + nivel.value);

</script>

<template>
    <div
        class="relative w-full max-w-[280px] mx-auto mt-4 mb-10 transition-transform duration-300 hover:-translate-y-2 hover:scale-105 group perspective">
        <!-- Contenedor Principal de la Carta -->
        <div class="bg-surface-900 rounded-xl border-2 overflow-hidden flex flex-col relative" :class="borderColorClass"
            style="min-height: 380px;" :style="{ transformStyle: 'preserve-3d' }">
            <!-- Overlay Estético (Gradiente superior) -->
            <div
                class="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-black/60 to-transparent z-10 pointer-events-none">
            </div>

            <!-- Imagen de Perfil -->
            <div class="h-48 w-full relative bg-surface-800 flex items-center justify-center overflow-hidden">
                <img :src="avatarUrl" :alt="fullName"
                    class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                    @error="$event.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(fullName)}&background=222&color=fff&size=200`" />

                <!-- Efecto Scanline / Overlay decorativo en la imagen -->
                <div
                    class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSJyZ2JhKDAsMCwwLDApIj48L3JlY3Q+CjxyZWN0IHdpZHRoPSI0IiBoZWlnaHQ9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wNSkiPjwvcmVjdD4KPC9zdmc+')] pointer-events-none opacity-50">
                </div>

                <!-- Filtro tintado según rango -->
                <div class="absolute inset-0 mix-blend-overlay opacity-30 pointer-events-none ring-rango"
                    :class="`ring-rango-${nivel}`"></div>
            </div>

            <!-- Información del Técnico -->
            <div
                class="relative bg-gradient-to-b from-surface-800 to-surface-900 border-t border-surface-700 p-4 pt-5 pb-12 flex-1 flex flex-col justify-between items-center text-center shadow-inner z-20">
                <div class="w-full">
                    <h3 class="text-xl font-bold text-white mb-1 uppercase tracking-wider drop-shadow-md">
                        {{ fullName }}
                    </h3>
                    <div class="text-surface-400 text-sm font-semibold tracking-widest uppercase mb-4">
                        <i class="pi pi-map-marker text-xs mr-1 opacity-70"></i> {{ tecnico.casino_nombre || 'NEXUS' }}
                    </div>
                </div>

                <!-- Estadísticas / Puntos -->
                <div
                    class="w-full bg-black/40 rounded border border-surface-700 p-3 mb-6 relative overflow-hidden group-hover:border-surface-600 transition-colors">
                    <div class="text-xs text-surface-400 uppercase tracking-widest mb-1">XP Histórico</div>
                    <div
                        class="text-2xl font-black text-amber-400 font-mono tracking-tighter drop-shadow-[0_0_8px_rgba(251,191,36,0.5)]">
                        {{ tecnico.puntos_gamificacion_historico.toLocaleString() }}
                    </div>

                    <!-- Barra de progreso miniatura -->
                    <div
                        class="w-full h-1.5 bg-surface-800 rounded-full mt-2 overflow-hidden border border-surface-700 relative">
                        <!-- Destello de fondo si está lleno -->
                        <div v-if="progresoPct === 100" class="absolute inset-0 bg-yellow-500/20 animate-pulse"></div>
                        <div class="h-full bg-gradient-to-r from-surface-600 via-surface-400 to-surface-200 transition-all duration-1000 ease-out"
                            :class="{ '!from-yellow-600 !via-yellow-400 !to-yellow-200': progresoPct >= 100 }"
                            :style="{ width: `${progresoPct}%` }"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Insignia de Rango Superpuesta (Rompiendo el borde inferior) -->
        <!-- absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 -->
        <div
            class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 z-30 drop-shadow-[0_10px_15px_rgba(0,0,0,0.8)]">
            <div
                class="transform scale-125 md:scale-150 transform-origin-top transition-transform duration-500 hover:scale-[1.6]">
                <InsigniaRangoAnimada :nivel="nivel" :nombreRango="rango.titulo" />
            </div>
            <!-- Brillo detrás de la insignia -->
            <div class="absolute inset-0 bg-white/20 blur-xl rounded-full -z-10 animate-pulse"></div>
        </div>
    </div>
</template>

<style scoped>
/* Filtros extra aplicados a la foto de perfil dependiendo el rango */
.ring-rango-1 {
    background-color: rgba(100, 100, 100, 0.4);
}

.ring-rango-2 {
    background-color: rgba(200, 200, 200, 0.3);
}

.ring-rango-3 {
    background-color: rgba(30, 144, 255, 0.3);
}

.ring-rango-4 {
    background-color: rgba(0, 255, 102, 0.3);
}

.ring-rango-5 {
    background-color: rgba(245, 196, 0, 0.3);
}

.ring-rango-6 {
    background-color: rgba(0, 255, 255, 0.4);
}

.ring-rango-7 {
    background-color: rgba(204, 0, 255, 0.4);
}

.ring-rango-8 {
    background-color: rgba(204, 0, 0, 0.4);
}

.ring-rango-9 {
    background-color: rgba(255, 215, 0, 0.4);
}

.ring-rango-10 {
    background-color: rgba(255, 165, 0, 0.5);
}
</style>
