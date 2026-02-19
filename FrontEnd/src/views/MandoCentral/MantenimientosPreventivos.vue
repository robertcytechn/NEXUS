<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api from '@/service/api';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import Chart from 'primevue/chart';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

const mantenimientos = ref([]);
const loading = ref(false);
const dt = ref();
const toolbarRef = ref();

useResponsiveDataTable(dt);
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();

// Sincronizar buscador del toolbar con filtros del DataTable
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Columnas configurables
const columnas = ref([
    { field: 'maquina_uid', label: 'Máquina', visible: true },
    { field: 'casino_nombre', label: 'Casino', visible: true },
    { field: 'tecnico_nombre', label: 'Técnico', visible: true },
    { field: 'fecha_mantenimiento', label: 'Fecha Mantenimiento', visible: true },
    { field: 'estado_final_maquina', label: 'Estado Final', visible: true },
    { field: 'observaciones', label: 'Observaciones', visible: true },
    { field: 'creado_en', label: 'Fecha Registro', visible: true }
]);

// Cargar mantenimientos desde la API
const cargarMantenimientos = async () => {
    loading.value = true;
    try {
        const response = await api.get('mantenimientos-preventivos/');
        mantenimientos.value = response.data;
    } catch (error) {
        console.error('Error al cargar mantenimientos:', error);
        toast.add({ 
            severity: 'error', 
            summary: 'Error', 
            detail: 'No se pudo cargar la lista de mantenimientos', 
            life: 3000 
        });
    } finally {
        loading.value = false;
    }
};

// Formatear fecha
const formatearFecha = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleDateString('es-MX', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
};

const formatearFechaCompleta = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleString('es-MX', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// Función para verificar si una columna está visible
const esColumnaVisible = (field) => {
    const columna = columnas.value.find(c => c.field === field);
    return columna ? columna.visible : true;
};

// Severity para estados
const getEstadoSeverity = (estado) => {
    const severities = {
        'operativa': 'success',
        'dañada_operativa': 'warn',
        'dañada': 'danger',
        'observacion': 'info'
    };
    return severities[estado] || 'secondary';
};

// Computed para estadísticas
const mantenimientosPorTecnico = computed(() => {
    const conteo = {};
    mantenimientos.value.forEach(m => {
        const tecnico = m.tecnico_nombre || 'Sin asignar';
        conteo[tecnico] = (conteo[tecnico] || 0) + 1;
    });
    return Object.entries(conteo)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10); // Top 10 técnicos
});

const mantenimientosPorCasino = computed(() => {
    const conteo = {};
    mantenimientos.value.forEach(m => {
        const casino = m.casino_nombre || 'Sin definir';
        conteo[casino] = (conteo[casino] || 0) + 1;
    });
    return Object.entries(conteo)
        .sort((a, b) => b[1] - a[1]);
});

// Datos para gráfica de técnicos
const chartDataTecnicos = computed(() => ({
    labels: mantenimientosPorTecnico.value.map(([tecnico]) => tecnico),
    datasets: [
        {
            label: 'Mantenimientos Realizados',
            data: mantenimientosPorTecnico.value.map(([, cantidad]) => cantidad),
            backgroundColor: [
                '#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6',
                '#06b6d4', '#ec4899', '#14b8a6', '#f97316', '#6366f1'
            ],
            borderColor: '#ffffff',
            borderWidth: 2
        }
    ]
}));

// Datos para gráfica de casinos
const chartDataCasinos = computed(() => {
    const coloresCasinos = [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#06b6d4', '#ec4899', '#14b8a6', '#f97316', '#6366f1',
        '#84cc16', '#f43f5e', '#0ea5e9', '#a855f7', '#22c55e'
    ];
    
    return {
        labels: mantenimientosPorCasino.value.map(([casino]) => casino),
        datasets: [
            {
                label: 'Mantenimientos',
                data: mantenimientosPorCasino.value.map(([, cantidad]) => cantidad),
                backgroundColor: coloresCasinos,
                borderColor: '#ffffff',
                borderWidth: 2
            }
        ]
    };
});

// Opciones para las gráficas
const chartOptions = ref({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: true,
            position: 'bottom'
        },
        tooltip: {
            callbacks: {
                label: function(context) {
                    return `${context.label}: ${context.parsed.y || context.parsed} mantenimientos`;
                }
            }
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            ticks: {
                stepSize: 1
            }
        }
    }
});

const chartOptionsPie = ref({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: true,
            position: 'right'
        },
        tooltip: {
            callbacks: {
                label: function(context) {
                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                    const percentage = ((context.parsed / total) * 100).toFixed(1);
                    return `${context.label}: ${context.parsed} (${percentage}%)`;
                }
            }
        }
    }
});

onMounted(() => {
    cargarMantenimientos();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <!-- Gráficas -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Gráfica de Técnicos -->
            <Card>
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-user text-2xl text-primary"></i>
                        <span>Mantenimientos por Técnico</span>
                    </div>
                </template>
                <template #subtitle>Top 10 técnicos con más mantenimientos realizados</template>
                <template #content>
                    <div style="height: 400px">
                        <Chart 
                            type="bar" 
                            :data="chartDataTecnicos" 
                            :options="chartOptions"
                            v-if="mantenimientos.length > 0"
                        />
                        <div v-else class="text-center py-8 text-surface-500">
                            <i class="pi pi-chart-bar text-4xl mb-3"></i>
                            <p>No hay datos para mostrar</p>
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Gráfica de Casinos -->
            <Card>
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-building text-2xl text-primary"></i>
                        <span>Mantenimientos por Casino</span>
                    </div>
                </template>
                <template #subtitle>Distribución de mantenimientos por ubicación</template>
                <template #content>
                    <div style="height: 400px">
                        <Chart 
                            type="pie" 
                            :data="chartDataCasinos" 
                            :options="chartOptionsPie"
                            v-if="mantenimientos.length > 0"
                        />
                        <div v-else class="text-center py-8 text-surface-500">
                            <i class="pi pi-chart-pie text-4xl mb-3"></i>
                            <p>No hay datos para mostrar</p>
                        </div>
                    </div>
                </template>
            </Card>
        </div>

        <!-- DataTable -->
        <div class="card">
            <Toast />
            
            <!-- Toolbar -->
            <DataTableToolbar
                ref="toolbarRef"
                :dt="dt"
                :datos="mantenimientos"
                titulo-reporte="Registro de Mantenimientos Preventivos"
                nombre-archivo="mantenimientos-preventivos"
                :columnas="columnas"
                :mostrar-exportacion="true"
                :mostrar-imprimir="true"
                :mostrar-refrescar="true"
                :mostrar-selector-columnas="true"
                :mostrar-buscador="true"
                @refrescar="cargarMantenimientos"
                v-model:columnas-seleccionadas="columnas"
            />
            
            <!-- DataTable -->
            <DataTable 
                ref="dt"
                :value="mantenimientos" 
                :loading="loading"
                v-model:filters="filtros"
                :globalFilterFields="['maquina_uid', 'casino_nombre', 'tecnico_nombre', 'fecha_mantenimiento', 'estado_final_maquina', 'observaciones']"
                paginator 
                :rows="10" 
                :rowsPerPageOptions="[5, 10, 20, 50]"
                dataKey="id"
                filterDisplay="menu"
                showGridlines
                stripedRows
                class="datatable-mobile"
            >
                <template #empty>
                    <div class="text-center p-4">No se encontraron mantenimientos registrados.</div>
                </template>
                
                <template #loading>Cargando mantenimientos...</template>
                
                <Column v-if="esColumnaVisible('maquina_uid')" field="maquina_uid" header="Máquina" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-desktop text-primary"></i>
                            <span class="font-semibold">{{ data.maquina_uid }}</span>
                        </div>
                    </template>
                </Column>
                
                <Column v-if="esColumnaVisible('casino_nombre')" field="casino_nombre" header="Casino" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-building text-primary"></i>
                            <span class="font-semibold">{{ data.casino_nombre }}</span>
                        </div>
                    </template>
                </Column>
                
                <Column v-if="esColumnaVisible('tecnico_nombre')" field="tecnico_nombre" header="Técnico" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-user text-surface-500"></i>
                            <span class="font-semibold">{{ data.tecnico_nombre }}</span>
                        </div>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('fecha_mantenimiento')" field="fecha_mantenimiento" header="Fecha Mantenimiento" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-calendar text-blue-500"></i>
                            <span>{{ formatearFecha(data.fecha_mantenimiento) }}</span>
                        </div>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('estado_final_maquina')" field="estado_final_maquina" header="Estado Final" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <Tag 
                            :value="data.estado_final_maquina.replace('_', ' ').toUpperCase()" 
                            :severity="getEstadoSeverity(data.estado_final_maquina)" 
                        />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('observaciones')" field="observaciones" header="Observaciones" style="min-width: 20rem">
                    <template #body="{ data }">
                        <span v-if="data.observaciones" class="text-sm">{{ data.observaciones }}</span>
                        <span v-else class="text-surface-400 italic text-sm">Sin observaciones</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('creado_en')" field="creado_en" header="Fecha Registro" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="text-sm text-surface-600">
                            {{ formatearFechaCompleta(data.creado_en) }}
                        </div>
                    </template>
                </Column>
            </DataTable>
        </div>
    </div>
</template>

<style scoped>
:deep(.p-card-body) {
    padding: 1.5rem;
}

:deep(.p-chart) {
    height: 100%;
}
</style>
