<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import { getDashboardChartsData } from '@/service/ticketService';
import { useToast } from 'primevue/usetoast';

const props = defineProps({
    casinoId: {
        type: Number,
        required: true
    }
});

const toast = useToast();
const loading = ref(false);

// Filtros de fecha dinámicos
const filtroTipo = ref('mes'); // 'dia', 'semana', 'mes'
const tiposFiltro = ref([
    { label: 'Día', value: 'dia' },
    { label: 'Semana', value: 'semana' },
    { label: 'Mes', value: 'mes' }
]);

const fechaSeleccionada = ref(new Date());

const meses = ref([
    { label: 'Enero', value: 1 }, { label: 'Febrero', value: 2 }, { label: 'Marzo', value: 3 },
    { label: 'Abril', value: 4 }, { label: 'Mayo', value: 5 }, { label: 'Junio', value: 6 },
    { label: 'Julio', value: 7 }, { label: 'Agosto', value: 8 }, { label: 'Septiembre', value: 9 },
    { label: 'Octubre', value: 10 }, { label: 'Noviembre', value: 11 }, { label: 'Diciembre', value: 12 }
]);
const mesSeleccionado = ref(new Date().getMonth() + 1);

const semanas = ref([
    { label: 'Semana 1', value: 1 }, { label: 'Semana 2', value: 2 },
    { label: 'Semana 3', value: 3 }, { label: 'Semana 4', value: 4 }
]);
const semanaSeleccionada = ref(1);

const randoFechaLabel = ref('');

// Datos para gráficas
const fallasData = ref(null);
const fallasOptions = ref(null);
const resolucionData = ref(null);
const resolucionOptions = ref(null);
const salaData = ref(null);
const salaOptions = ref(null);

// Nuevos Datos Analíticos
const topMaquinasData = ref(null);
const topMaquinasOptions = ref(null);
const mantenimientosData = ref(null);
const mantenimientosOptions = ref(null);
const mttrKPI = ref(0);

const tecnicosActivos = ref([]);
const incidenciasInfra = ref(0);

const initCharts = () => {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--p-text-color');
    const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

    fallasOptions.value = {
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: { color: textColor, usePointStyle: true }
            }
        }
    };

    resolucionOptions.value = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: textColor, usePointStyle: true } }
        },
        scales: {
            x: { ticks: { color: textColor }, grid: { color: surfaceBorder } },
            y: { ticks: { color: textColor }, grid: { color: surfaceBorder } }
        }
    };

    salaOptions.value = {
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: { color: textColor, usePointStyle: true }
            }
        }
    };

    topMaquinasOptions.value = {
        indexAxis: 'y', // Hace que sea barra horizontal
        maintainAspectRatio: false,
        responsive: true,
        plugins: {
            legend: { display: false } // No necesitamos leyenda porque los labels lo dicen todo
        },
        scales: {
            x: { ticks: { color: textColor }, grid: { color: surfaceBorder } },
            y: { ticks: { color: textColor }, grid: { color: surfaceBorder } }
        }
    };

    mantenimientosOptions.value = {
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: { color: textColor, usePointStyle: true }
            }
        }
    };
};

const formatDate = (date) => {
    if (!date) return null;
    return date.toISOString().split('T')[0];
};

const loadData = async () => {
    if (!props.casinoId) return;

    loading.value = true;
    try {
        const filtros = {
            filtroTipo: filtroTipo.value,
            anio: new Date().getFullYear(),
        };

        if (filtroTipo.value === 'dia') {
            filtros.fecha = formatDate(fechaSeleccionada.value);
        } else if (filtroTipo.value === 'semana') {
            filtros.mes = mesSeleccionado.value;
            filtros.semana = semanaSeleccionada.value;
        } else if (filtroTipo.value === 'mes') {
            filtros.mes = mesSeleccionado.value;
        }

        const data = await getDashboardChartsData(props.casinoId, filtros);

        randoFechaLabel.value = data.periodo?.rango || '';

        // 1. Fallas por Categoría (Pie Chart)
        const categoriasColores = {
            hardware: '--p-orange-500',
            software: '--p-blue-500',
            perifericos: '--p-teal-500',
            red: '--p-indigo-500',
            otros: '--p-gray-500'
        };

        const documentStyle = getComputedStyle(document.documentElement);

        if (data.fallas_categoria && data.fallas_categoria.length > 0) {
            fallasData.value = {
                labels: data.fallas_categoria.map(item => item.label),
                datasets: [
                    {
                        data: data.fallas_categoria.map(item => item.total),
                        backgroundColor: data.fallas_categoria.map(item =>
                            documentStyle.getPropertyValue(categoriasColores[item.categoria] || '--p-primary-500')
                        )
                    }
                ]
            };
        } else {
            fallasData.value = null; // Para mostrar empty state
        }

        // 1b. Top Máquinas Problemáticas (Bar Chart Horizontal)
        if (data.top_maquinas && data.top_maquinas.length > 0) {
            topMaquinasData.value = {
                labels: data.top_maquinas.map(item => `${item.uid_sala} (${item.modelo})`),
                datasets: [
                    {
                        label: 'Fallos',
                        backgroundColor: documentStyle.getPropertyValue('--p-red-500'),
                        data: data.top_maquinas.map(item => item.total)
                    }
                ]
            };
        } else {
            topMaquinasData.value = null;
        }

        // 2. Resolución de Tickets (Bar Chart)
        resolucionData.value = {
            labels: ['Tickets'],
            datasets: [
                {
                    label: 'Creados (Acumulado Fecha)',
                    backgroundColor: documentStyle.getPropertyValue('--p-orange-500'),
                    data: [data.resolucion?.creados || 0]
                },
                {
                    label: 'Resueltos (Acumulado Fecha)',
                    backgroundColor: documentStyle.getPropertyValue('--p-green-500'),
                    data: [data.resolucion?.cerrados || 0]
                }
            ]
        };

        // 3. Técnico más activo
        tecnicosActivos.value = data.tecnicos_activos || [];

        // 4. Estado de la Sala (Doughnut Chart - Snapshot Global)
        const estadoColores = {
            OPERATIVA: '--p-green-500',
            DAÑADA: '--p-red-500',
            DAÑADA_OPERATIVA: '--p-orange-500',
            MANTENIMIENTO: '--p-blue-500'
        };
        const estadoLabels = {
            OPERATIVA: 'Operativa',
            DAÑADA: 'Dañada',
            DAÑADA_OPERATIVA: 'Dañada Operativa',
            MANTENIMIENTO: 'Mantenimiento'
        };

        if (data.estado_sala && data.estado_sala.length > 0) {
            salaData.value = {
                labels: data.estado_sala.map(item => estadoLabels[item.estado_actual] || item.estado_actual),
                datasets: [
                    {
                        data: data.estado_sala.map(item => item.total),
                        backgroundColor: data.estado_sala.map(item =>
                            documentStyle.getPropertyValue(estadoColores[item.estado_actual] || '--p-gray-500')
                        )
                    }
                ]
            };
        } else {
            salaData.value = null;
        }

        // 5. Infraestructura
        incidenciasInfra.value = data.incidencias_infra || 0;

        // 6. MTTR (KPI Numerico)
        mttrKPI.value = data.mttr_horas || 0;

        // 7. Preventivos vs Correctivos (Doughnut)
        const preventivos = data.mantenimientos?.preventivos || 0;
        const correctivos = data.mantenimientos?.correctivos || 0;

        if (preventivos > 0 || correctivos > 0) {
            mantenimientosData.value = {
                labels: ['Preventivos', 'Correctivos'],
                datasets: [
                    {
                        data: [preventivos, correctivos],
                        backgroundColor: [
                            documentStyle.getPropertyValue('--p-teal-500'),
                            documentStyle.getPropertyValue('--p-red-400')
                        ]
                    }
                ]
            };
        } else {
            mantenimientosData.value = null;
        }

    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los datos de las gráficas', life: 3000 });
    } finally {
        loading.value = false;
    }
};

watch(() => props.casinoId, (newId) => {
    if (newId) loadData();
});

// Reseteamos valores al cambiar el tipo de filtro, para UX más limpia
watch(filtroTipo, (nuevoTipo) => {
    if (nuevoTipo === 'dia' && !fechaSeleccionada.value) {
        fechaSeleccionada.value = new Date();
    }
    // No auto-recargamos aquí, forzamos usar el botón "Filtrar"
});

onMounted(() => {
    initCharts();
    loadData();
});
</script>

<template>
    <div class="card relative min-h-[500px]">
        <div v-if="loading"
            class="absolute inset-0 z-10 bg-surface-0/70 dark:bg-surface-900/70 flex items-center justify-center rounded-xl backdrop-blur-sm">
            <i class="pi pi-spin pi-spinner text-4xl text-primary"></i>
        </div>

        <!-- ENCABEZADO Y FILTROS -->
        <div class="flex flex-col xl:flex-row justify-between items-start xl:items-center mb-6 gap-6">
            <div>
                <div class="font-semibold text-xl">Análisis y Métricas Completas</div>
                <div class="text-surface-500 text-sm mt-1">Filtro aplicado: {{ randoFechaLabel }}</div>
            </div>

            <div
                class="flex flex-col md:flex-row items-center gap-3 bg-surface-50 dark:bg-surface-800/50 p-2 rounded-lg border border-surface-200 dark:border-surface-700">
                <!-- Tipo de Filtro -->
                <SelectButton v-model="filtroTipo" :options="tiposFiltro" optionLabel="label" optionValue="value"
                    :allowEmpty="false" />

                <div class="h-8 w-px bg-surface-300 dark:bg-surface-600 hidden md:block mx-1"></div>

                <!-- Controles Condicionales -->
                <div class="flex items-center gap-2">
                    <!-- Día -->
                    <template v-if="filtroTipo === 'dia'">
                        <DatePicker v-model="fechaSeleccionada" dateFormat="dd/mm/yy" placeholder="Selecciona Fecha"
                            class="w-40" />
                    </template>

                    <!-- Semana -->
                    <template v-if="filtroTipo === 'semana'">
                        <Select v-model="mesSeleccionado" :options="meses" optionLabel="label" optionValue="value"
                            placeholder="Mes" class="w-36" />
                        <Select v-model="semanaSeleccionada" :options="semanas" optionLabel="label" optionValue="value"
                            placeholder="Semana" class="w-32" />
                    </template>

                    <!-- Mes -->
                    <template v-if="filtroTipo === 'mes'">
                        <Select v-model="mesSeleccionado" :options="meses" optionLabel="label" optionValue="value"
                            placeholder="Mes" class="w-36" />
                    </template>
                </div>

                <Button label="Aplicar" icon="pi pi-filter" @click="loadData" severity="secondary" />
            </div>
        </div>

        <!-- SISTEMA DE PESTAÑAS (TABS) -->
        <Tabs value="0">
            <TabList>
                <Tab value="0"><i class="pi pi-home mr-2"></i> General</Tab>
                <Tab value="1"><i class="pi pi-desktop mr-2"></i> Hardware (Top 5)</Tab>
                <Tab value="2"><i class="pi pi-users mr-2"></i> Equipo Técnico & MTTR</Tab>
            </TabList>
            <TabPanels>

                <!-- PESTAÑA 0: GENERAL -->
                <TabPanel value="0">
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <!-- Eficiencia -->
                        <div
                            class="border border-surface-200 dark:border-surface-700 rounded-xl p-4 bg-surface-50 dark:bg-surface-800/50">
                            <div class="font-medium mb-3 flex items-center gap-2">
                                <i class="pi pi-chart-bar text-primary"></i> Eficiencia Técnica (Tickets)
                            </div>
                            <Chart type="bar" :data="resolucionData" :options="resolucionOptions" class="h-[250px]" />
                        </div>

                        <!-- Fallas Pie -->
                        <div
                            class="border border-surface-200 dark:border-surface-700 rounded-xl p-4 bg-surface-50 dark:bg-surface-800/50 flex flex-col">
                            <div class="font-medium mb-3 flex items-center gap-2">
                                <i class="pi pi-chart-pie text-orange-500"></i> Fallas por Categoría
                            </div>
                            <div class="relative h-[250px] w-full flex items-center justify-center">
                                <Chart v-if="fallasData" type="pie" :data="fallasData" :options="fallasOptions"
                                    class="w-full h-full" />
                                <div v-else class="text-surface-500 flex flex-col items-center">
                                    <i class="pi pi-inbox text-3xl mb-2"></i>
                                    <span>No hay fallas reportadas</span>
                                </div>
                            </div>
                        </div>

                        <!-- Estado Sala (Global instantaneous) -->
                        <div
                            class="border border-surface-200 dark:border-surface-700 rounded-xl p-4 bg-surface-50 dark:bg-surface-800/50 flex flex-col">
                            <div class="font-medium mb-3 flex items-center gap-2">
                                <i class="pi pi-cog text-green-500"></i> Estado Actual Máquinas
                            </div>
                            <div class="relative h-[250px] w-full flex items-center justify-center">
                                <Chart v-if="salaData" type="doughnut" :data="salaData" :options="salaOptions"
                                    class="w-full h-full" />
                                <div v-else class="text-surface-500 flex flex-col items-center">
                                    <i class="pi pi-inbox text-3xl mb-2"></i>
                                    <span>Sin datos de máquinas</span>
                                </div>
                            </div>
                        </div>

                        <!-- Panel Adicional: Técnicos e Incidencias -->
                        <div class="md:col-span-2 lg:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-6 mt-2">
                            <div class="p-4 rounded-xl border border-surface-200 dark:border-surface-700 flex flex-col">
                                <div class="font-medium mb-4 flex items-center gap-2">
                                    <i class="pi pi-star-fill text-yellow-500"></i> Técnicos más activos
                                </div>
                                <ul class="p-0 m-0 list-none flex-1">
                                    <li v-for="(t, index) in tecnicosActivos" :key="index"
                                        class="flex items-center justify-between py-2 border-b border-surface-200 dark:border-surface-700 last:border-0 last:pb-0">
                                        <div class="flex items-center gap-3">
                                            <div
                                                class="w-8 h-8 rounded-full bg-primary/10 text-primary font-bold flex items-center justify-center text-sm">
                                                {{ index + 1 }}
                                            </div>
                                            <span class="font-medium">{{ t.nombre }}</span>
                                        </div>
                                        <Badge :value="t.total" severity="success" class="text-xs"></Badge>
                                    </li>
                                    <li v-if="tecnicosActivos.length === 0" class="text-center text-surface-500 py-4">
                                        Sin actividad reportada en el periodo
                                    </li>
                                </ul>
                            </div>

                            <!-- KPI Incidencias -->
                            <div
                                class="p-4 rounded-xl bg-orange-500/10 border border-orange-500/20 flex flex-col justify-center items-center text-center">
                                <i class="pi pi-exclamation-triangle text-orange-500 text-4xl mb-3"></i>
                                <div class="text-surface-500 font-medium mb-1">Acontecimientos de Infraestructura</div>
                                <div class="text-4xl font-bold text-orange-600 dark:text-orange-400">{{ incidenciasInfra
                                }}
                                </div>
                                <div class="text-sm text-surface-500 mt-2">Afectaciones en sala durante el periodo
                                    reportado
                                </div>
                            </div>
                        </div>
                    </div>
                </TabPanel>

                <!-- PESTAÑA 1: HARDWARE (TOP 5) -->
                <TabPanel value="1">
                    <div class="grid grid-cols-1">
                        <div
                            class="border border-surface-200 dark:border-surface-700 rounded-xl p-4 bg-surface-50 dark:bg-surface-800/50">
                            <div class="font-medium mb-3 flex items-center gap-2">
                                <i class="pi pi-sort-amount-down-alt text-red-500"></i> Máquinas con Mayor Incidencia de
                                Fallos
                                (Top 5)
                            </div>
                            <p class="text-surface-500 text-sm mb-4">Muestra las máquinas que más tickets de falla han
                                acumulado
                                durante el periodo filtrado.</p>
                            <div class="relative min-h-[350px] w-full flex items-center justify-center">
                                <Chart v-if="topMaquinasData" type="bar" :data="topMaquinasData"
                                    :options="topMaquinasOptions" class="w-full h-full" />
                                <div v-else class="text-surface-500 flex flex-col items-center">
                                    <i class="pi pi-check-circle text-4xl mb-2 text-green-500"></i>
                                    <span>Excelente: No hay reportes de fallas en sala durante este lapso.</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </TabPanel>

                <!-- PESTAÑA 2: MTTR Y EQUIPO TECNICO -->
                <TabPanel value="2">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <!-- KPI MTTR -->
                        <div
                            class="border border-surface-200 dark:border-surface-700 rounded-xl p-6 bg-surface-50 dark:bg-surface-800/50 flex flex-col justify-center items-center text-center shrink-0 min-h-[300px]">
                            <i class="pi pi-stopwatch text-indigo-500 text-5xl mb-4"></i>
                            <div class="text-surface-900 font-bold mb-1 text-2xl">MTTR</div>
                            <div class="text-surface-500 font-medium mb-2 text-sm">(Mean Time To Repair / Tiempo Medio
                                Reparación)</div>
                            <div class="text-6xl font-black text-indigo-600 dark:text-indigo-400 my-4">{{ mttrKPI }}
                                <span class="text-2xl font-semibold">hrs</span>
                            </div>
                            <div class="text-sm text-surface-500 max-w-[80%]">Promedio de tiempo transcurrido desde que
                                se
                                reporta un fallo hasta que se cierra el ticket exitosamente.</div>
                        </div>

                        <!-- PvsC Doughnut -->
                        <div
                            class="border border-surface-200 dark:border-surface-700 rounded-xl p-4 bg-surface-50 dark:bg-surface-800/50 flex flex-col">
                            <div class="font-medium mb-3 flex items-center gap-2">
                                <i class="pi pi-wrench text-teal-500"></i> Balance de Mantenimientos
                            </div>
                            <p class="text-surface-500 text-sm mb-4">Relación entre trabajos Correctivos (solución de
                                fallas de
                                tickets/bitácoras) vs. Preventivos (rutinas programadas).</p>
                            <div class="relative h-[250px] w-full flex items-center justify-center">
                                <Chart v-if="mantenimientosData" type="doughnut" :data="mantenimientosData"
                                    :options="mantenimientosOptions" class="w-full h-full" />
                                <div v-else class="text-surface-500 flex flex-col items-center">
                                    <i class="pi pi-inbox text-3xl mb-2"></i>
                                    <span>No hay mantenimientos concluidos registrados.</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </TabPanel>

            </TabPanels>
        </Tabs>
    </div>
</template>
