<script setup>
import { ref, computed, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import api, { getUser } from '@/service/api';

const props = defineProps({
    visible: {
        type: Boolean,
        required: true
    },
    maquina: {
        type: Object,
        default: null
    }
});

const emit = defineEmits(['update:visible', 'levantar-incidencia']);
const toast = useToast();

const isVisible = computed({
    get: () => props.visible,
    set: (value) => emit('update:visible', value)
});

// --- ESTADO HISTORIAL ---
const historialTickets = ref([]);
const loadingDetalle = ref(false);

const cargarHistorial = async () => {
    if (!props.maquina || !props.maquina.id) return;

    loadingDetalle.value = true;
    historialTickets.value = [];

    try {
        const res = await api.get(`tickets/historial-maquina/${props.maquina.id}/`);
        historialTickets.value = res.data.historial || [];
    } catch (e) {
        // Silencioso si no hay historial
    } finally {
        loadingDetalle.value = false;
    }
};

watch(() => props.visible, (newVal) => {
    if (newVal) {
        cargarHistorial();
    }
});

// --- AYUDANTES VISUALES ---
const getSeverity = (estado) => {
    const map = {
        OPERATIVA: 'success', DAÑADA_OPERATIVA: 'warn',
        DAÑADA: 'danger', MANTENIMIENTO: 'info',
        OBSERVACION: 'secondary', PRUEBAS: 'contrast'
    };
    return map[estado] || 'secondary';
};

const labelPiso = (val) => {
    if (!val) return 'Sin piso';
    const dict = {
        'PISO_1': 'Piso 1', 'PISO_2': 'Piso 2', 'PISO_3': 'Piso 3',
        'PLANTA_BAJA': 'Planta Baja', 'VIP': 'Área VIP', 'TERRAZA': 'Terraza'
    };
    return dict[val] || val;
};

const labelSala = (val) => {
    if (!val) return 'Sin sala';
    const dict = {
        'SALA_A': 'Sala A', 'SALA_B': 'Sala B', 'SALA_PRINCIPAL': 'Sala Principal',
        'ZONA_FUMADORES': 'Zona Fumadores', 'ZONA_NO_FUMADORES': 'Zona No Fumadores',
        'BAR': 'Bar / Restaurante', 'ENTRADA': 'Entrada / Lobby'
    };
    return dict[val] || val;
};

const diasDesdeMantenimiento = computed(() => {
    if (!props.maquina?.ultimo_mantenimiento) return 'N/A';
    const fecha = new Date(props.maquina.ultimo_mantenimiento);
    const diff = Math.floor((new Date() - fecha) / (1000 * 60 * 60 * 24));
    return `${diff} días`;
});

const handleLevantarIncidencia = () => {
    emit('levantar-incidencia', props.maquina);
};
</script>

<template>
    <Dialog v-model:visible="isVisible" :style="{ width: '1000px' }" :breakpoints="{ '960px': '95vw' }"
        header="Ficha Técnica y Operativa" :modal="true" :maximizable="true">
        <div v-if="maquina" class="flex flex-col gap-5">
            <!-- Cabecera -->
            <div
                class="surface-card border-2 border-primary-200 dark:border-primary-900 rounded-xl p-5 bg-gradient-to-br from-primary-50 to-white dark:from-primary-950 dark:to-surface-900">
                <div class="flex flex-col md:flex-row items-start md:items-center gap-3 mb-5">
                    <div class="flex items-center gap-3 flex-1">
                        <div class="flex items-center justify-center bg-primary-500 rounded-xl shadow-lg shrink-0"
                            style="width:3rem;height:3rem">
                            <i class="pi pi-desktop text-white text-xl"></i>
                        </div>
                        <div>
                            <h3 class="text-2xl font-bold text-surface-900 dark:text-surface-0">{{ maquina.uid_sala }}
                            </h3>
                            <p class="text-surface-500 text-sm">{{ maquina.modelo_nombre }} · {{ maquina.modelo_producto
                                }}</p>
                        </div>
                    </div>
                    <Tag :value="maquina.estado_actual" :severity="getSeverity(maquina.estado_actual)"
                        class="text-base px-4 py-2 font-bold" rounded />
                </div>

                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                    <!-- Casino -->
                    <div class="info-tile">
                        <div class="info-tile-label"><i class="pi pi-building text-blue-500"></i> Casino</div>
                        <span class="info-tile-value">{{ maquina.casino_nombre }}</span>
                    </div>
                    <!-- Piso / Sala -->
                    <div class="info-tile">
                        <div class="info-tile-label"><i class="pi pi-map-marker text-red-500"></i> Ubicación</div>
                        <span class="info-tile-value">{{ labelPiso(maquina.ubicacion_piso) }} / {{
                            labelSala(maquina.ubicacion_sala) }}</span>
                    </div>
                    <!-- Coordenadas -->
                    <div class="info-tile">
                        <div class="info-tile-label"><i class="pi pi-compass text-purple-500"></i> Coordenadas</div>
                        <Tag :value="`X: ${maquina.coordenada_x}, Y: ${maquina.coordenada_y}`" severity="secondary"
                            class="text-xs" />
                    </div>
                    <!-- IP -->
                    <div class="info-tile">
                        <div class="info-tile-label"><i class="pi pi-wifi text-green-500"></i> IP</div>
                        <Tag v-if="maquina.ip_maquina" :value="maquina.ip_maquina" severity="info"
                            class="text-xs font-mono" />
                        <span v-else class="text-surface-400 text-xs">Sin asignar</span>
                    </div>
                    <!-- Serie -->
                    <div class="info-tile">
                        <div class="info-tile-label"><i class="pi pi-hashtag text-indigo-500"></i> No. Serie</div>
                        <span class="info-tile-value">{{ maquina.numero_serie }}</span>
                    </div>
                    <!-- Juego -->
                    <div class="info-tile">
                        <div class="info-tile-label"><i class="pi pi-play text-pink-500"></i> Juego</div>
                        <span class="info-tile-value">{{ maquina.juego || 'N/A' }}</span>
                    </div>
                    <!-- Mantenimiento -->
                    <div class="info-tile bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
                        <div class="info-tile-label"><i class="pi pi-wrench text-blue-600"></i> Último Mtto.</div>
                        <span class="info-tile-value text-blue-800 dark:text-blue-300">{{ maquina.ultimo_mantenimiento
                            || 'Sin registro' }}</span>
                        <span v-if="maquina.ultimo_mantenimiento" class="text-xs text-blue-600">({{
                            diasDesdeMantenimiento }})</span>
                    </div>
                    <!-- Proveedor -->
                    <div class="info-tile">
                        <div class="info-tile-label"><i class="pi pi-briefcase text-teal-500"></i> Proveedor</div>
                        <span class="info-tile-value">{{ maquina.proveedor_nombre || 'N/A' }}</span>
                    </div>
                    <!-- Fallas -->
                    <div class="info-tile"
                        :class="maquina.contador_fallas > 5 ? 'bg-red-50 dark:bg-red-950 border-red-300' : 'bg-orange-50 dark:bg-orange-950 border-orange-200'">
                        <div class="info-tile-label"><i class="pi pi-exclamation-triangle text-orange-500"></i> Fallas
                            Históricas</div>
                        <span class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ maquina.contador_fallas
                            || 0 }}</span>
                    </div>
                    <!-- Instalación -->
                    <div class="info-tile">
                        <div class="info-tile-label"><i class="pi pi-calendar text-cyan-500"></i> Instalación</div>
                        <Tag v-if="maquina.fecha_instalacion" :value="maquina.fecha_instalacion" severity="contrast"
                            class="text-xs" />
                        <span v-else class="text-surface-400 text-xs">N/A</span>
                    </div>

                    <!-- Denominaciones (fila completa) -->
                    <div class="col-span-2 sm:col-span-2 md:col-span-2 info-tile">
                        <div class="info-tile-label"><i class="pi pi-dollar text-emerald-500"></i> Denominaciones</div>
                        <div class="flex flex-wrap gap-1 mt-1">
                            <Tag v-for="denom in maquina.denominaciones_info" :key="denom.id" :value="denom.etiqueta"
                                severity="success" class="text-xs" rounded />
                            <Tag v-if="!maquina.denominaciones_info || maquina.denominaciones_info.length === 0"
                                value="Sin configurar" severity="warn" class="text-xs" />
                        </div>
                    </div>
                </div>
            </div>

            <!-- Historial de Tickets / Intervenciones -->
            <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-5">
                <div class="flex items-center gap-2 mb-4">
                    <i class="pi pi-history text-xl text-surface-500"></i>
                    <h4 class="font-bold text-xl text-surface-900 dark:text-surface-0">Historial de Intervenciones
                        Ténicas</h4>
                </div>

                <div v-if="loadingDetalle" class="text-center py-8">
                    <ProgressSpinner style="width:50px;height:50px" />
                </div>
                <div v-else-if="historialTickets.length === 0" class="text-center py-8 text-surface-400">
                    <i class="pi pi-info-circle text-4xl mb-3 block"></i>
                    No hay tickets ni intervenciones registradas recintemente para esta máquina operativa.
                </div>

                <!-- TIMELINE PRIME VUE EXPORTADA DE MAPASALA.VUE -->
                <Timeline v-else :value="historialTickets" class="w-full hide-timeline-opposite">
                    <template #marker="slotProps">
                        <span class="flex w-8 h-8 items-center justify-center text-white rounded-full z-10 shadow-sm"
                            :class="{
                                'bg-green-500': slotProps.item.estado_ciclo === 'cerrado',
                                'bg-blue-500': slotProps.item.estado_ciclo === 'proceso',
                                'bg-orange-500': slotProps.item.estado_ciclo === 'espera',
                                'bg-red-500': slotProps.item.estado_ciclo === 'abierto'
                            }">
                            <i class="pi pi-wrench"></i>
                        </span>
                    </template>
                    <template #content="slotProps">
                        <div
                            class="surface-card border-2 border-blue-200 dark:border-blue-800 rounded-xl p-3 md:p-5 mb-4 bg-gradient-to-br from-blue-50 to-white dark:from-blue-950 dark:to-surface-900">
                            <!-- Cabecera del Ticket -->
                            <div class="flex flex-col sm:flex-row justify-between items-start gap-2 mb-4">
                                <div class="flex items-center gap-2 md:gap-3 flex-wrap">
                                    <div class="flex items-center justify-center bg-blue-500 rounded-lg shadow-md shrink-0"
                                        style="width:2rem;height:2rem">
                                        <i class="pi pi-ticket text-white text-sm"></i>
                                    </div>
                                    <div class="flex items-center gap-2 flex-wrap">
                                        <span class="font-bold text-lg md:text-2xl text-blue-600 dark:text-blue-400">{{
                                            slotProps.item.folio }}</span>
                                        <Tag :value="slotProps.item.estado_ciclo"
                                            :severity="slotProps.item.estado_ciclo === 'cerrado' ? 'success' : slotProps.item.estado_ciclo === 'proceso' ? 'info' : 'warn'" />
                                    </div>
                                </div>
                                <span class="text-surface-500 text-xs md:text-sm">{{ new
                                    Date(slotProps.item.fecha_creacion).toLocaleDateString('es-MX') }}</span>
                            </div>

                            <p
                                class="text-sm md:text-base font-medium text-blue-800 dark:text-blue-300 mb-4 pl-0 md:pl-12">
                                {{ slotProps.item.descripcion_problema }}
                            </p>

                            <div class="flex flex-wrap gap-3 md:gap-4 mb-4 pl-0 md:pl-12">
                                <div class="flex items-center gap-1">
                                    <i class="pi pi-tag text-surface-400 text-xs"></i>
                                    <span class="text-surface-500 text-sm">Categoría:</span>
                                    <span class="font-semibold text-surface-900 dark:text-surface-0 text-sm">{{
                                        slotProps.item.categoria }}</span>
                                </div>
                                <div class="flex items-center gap-1">
                                    <i class="pi pi-exclamation-circle text-surface-400 text-xs"></i>
                                    <span class="text-surface-500 text-sm">Prioridad:</span>
                                    <Tag :value="slotProps.item.prioridad"
                                        :severity="slotProps.item.prioridad === 'critica' || slotProps.item.prioridad === 'emergencia' ? 'danger' : slotProps.item.prioridad === 'alta' ? 'warn' : 'info'"
                                        class="text-xs" />
                                </div>
                                <div class="flex items-center gap-1">
                                    <i class="pi pi-user text-surface-400 text-xs"></i>
                                    <span class="text-surface-500 text-sm">Técnico:</span>
                                    <span class="font-semibold text-surface-900 dark:text-surface-0 text-sm">
                                        {{ slotProps.item.tecnico_asignado?.nombre || 'Sin asignar' }} {{
                                            slotProps.item.tecnico_asignado?.apellidos || '' }}
                                    </span>
                                </div>
                            </div>

                            <!-- Bitácoras -->
                            <div v-if="slotProps.item.bitacoras && slotProps.item.bitacoras.length > 0"
                                class="mt-4 pl-0 md:pl-12">
                                <div class="flex items-center gap-2 mb-3">
                                    <i class="pi pi-list text-surface-400 text-sm"></i>
                                    <span
                                        class="text-surface-600 dark:text-surface-400 text-xs md:text-sm font-bold uppercase tracking-wide">
                                        Acciones y Reportes ({{ slotProps.item.bitacoras.length }})
                                    </span>
                                </div>

                                <div
                                    class="relative pl-4 md:pl-6 border-l-2 border-blue-300 dark:border-blue-700 ml-1 md:ml-2">
                                    <div v-for="(bitacora, idx) in slotProps.item.bitacoras" :key="idx"
                                        class="relative mb-4 last:mb-0">
                                        <div
                                            class="absolute -left-[1.6rem] top-3 w-4 h-4 bg-blue-400 dark:bg-blue-600 rounded-full border-2 border-white dark:border-surface-900">
                                        </div>

                                        <div
                                            class="bg-white dark:bg-surface-800 rounded-lg p-3 md:p-4 shadow-sm border border-surface-200 dark:border-surface-700 hover:shadow-md transition-shadow">
                                            <div
                                                class="flex flex-col sm:flex-row justify-between items-start gap-1 mb-2">
                                                <div class="flex items-center gap-2">
                                                    <i class="pi pi-user-edit text-blue-500 text-sm"></i>
                                                    <span
                                                        class="text-xs md:text-sm font-bold text-surface-900 dark:text-surface-0">{{
                                                        bitacora.tecnico_nombre }}</span>
                                                </div>
                                                <span class="text-xs text-surface-500">{{ new
                                                    Date(bitacora.fecha_registro).toLocaleString('es-MX') }}</span>
                                            </div>
                                            <p
                                                class="text-xs md:text-sm text-surface-700 dark:text-surface-300 mb-3 pl-0 md:pl-6">
                                                {{ bitacora.descripcion_trabajo }}
                                            </p>
                                            <div class="flex flex-wrap gap-2 pl-0 md:pl-6">
                                                <Tag :value="bitacora.tipo_intervencion" severity="secondary"
                                                    class="text-xs" icon="pi pi-cog" />
                                                <Tag :value="bitacora.resultado_intervencion"
                                                    :severity="bitacora.resultado_intervencion === 'exitosa' ? 'success' : bitacora.resultado_intervencion === 'parcial' ? 'warn' : 'danger'"
                                                    class="text-xs"
                                                    :icon="bitacora.resultado_intervencion === 'exitosa' ? 'pi pi-check-circle' : 'pi pi-info-circle'" />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </template>
                </Timeline>
            </div>
        </div>

        <template #footer>
            <Button label="Reportar Avería Exprés" icon="pi pi-exclamation-triangle" severity="danger"
                @click="handleLevantarIncidencia" />
            <Button label="Cerrar Ficha" icon="pi pi-times" text @click="isVisible = false" />
        </template>
    </Dialog>
</template>

<style scoped>
/* Timeline: ocultar lado vacío */
:deep(.p-timeline-event-opposite) {
    display: none !important;
}

:deep(.p-timeline-event-content) {
    width: 100% !important;
    padding-left: 1rem !important;
}

/* Tiles de INFO */
.info-tile {
    background: white;
    border: 1px solid var(--p-surface-200, #e2e8f0);
    border-radius: 8px;
    padding: 10px 12px;
}

.dark .info-tile {
    background: var(--p-surface-800, #1e293b);
    border-color: var(--p-surface-700, #334155);
}

.info-tile-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 600;
    color: var(--p-surface-500, #64748b);
    margin-bottom: 4px;
}

.info-tile-label i {
    font-size: 12px;
}

.info-tile-value {
    font-size: 13px;
    font-weight: 600;
    color: var(--p-surface-900, #0f172a);
    display: block;
}

.dark .info-tile-value {
    color: var(--p-surface-0, #f8fafc);
}
</style>
