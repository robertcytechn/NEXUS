<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import infraestructuraService from '@/service/infraestructuraService';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import Chart from 'primevue/chart';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

const incidencias = ref([]);
const casinos = ref([]);
const loading = ref(false);
const dt = ref();
const toolbarRef = ref();

useResponsiveDataTable(dt);
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();
const confirm = useConfirm();
const incidenciaDialog = ref(false);
const incidencia = ref({});
const submitted = ref(false);

// Sincronizar buscador del toolbar con filtros del DataTable
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Columnas configurables
const columnas = ref([
    { field: 'casino_nombre', label: 'Casino', visible: true },
    { field: 'titulo', label: 'Título', visible: true },
    { field: 'categoria', label: 'Categoría', visible: true },
    { field: 'severidad', label: 'Severidad', visible: true },
    { field: 'afecta_operacion', label: 'Afecta Operación', visible: true },
    { field: 'hora_inicio', label: 'Hora Inicio', visible: true },
    { field: 'hora_fin', label: 'Hora Fin', visible: true },
    { field: 'esta_activo', label: 'Estado', visible: true },
    { field: 'creado_en', label: 'Fecha Registro', visible: true }
]);

// Opciones para categorías
const categorias = [
    { label: 'Falla Eléctrica / Luz', value: 'electrica' },
    { label: 'Filtración / Agua / Gotera', value: 'agua' },
    { label: 'Climatización / Aire Acondicionado', value: 'clima' },
    { label: 'Proveedor de Internet / Enlace', value: 'red_externa' },
    { label: 'Estructura / Paredes / Techos', value: 'obra_civil' },
    { label: 'Otros Eventos Externos', value: 'otros' }
];

// Opciones para severidad
const severidades = [
    { label: 'Baja (Sin afectación)', value: 'baja' },
    { label: 'Media (Afectación parcial)', value: 'media' },
    { label: 'Alta (Riesgo operativo)', value: 'alta' },
    { label: 'Crítica (Cierre de sala/área)', value: 'critica' }
];

// Cargar incidencias desde la API
const cargarIncidencias = async () => {
    loading.value = true;
    try {
        incidencias.value = await infraestructuraService.getIncidencias();
    } catch (error) {

        toast.add({ 
            severity: 'error', 
            summary: 'Error', 
            detail: 'No se pudo cargar la lista de incidencias', 
            life: 3000 
        });
    } finally {
        loading.value = false;
    }
};

// Cargar casinos para el dropdown
const cargarCasinos = async () => {
    try {
        casinos.value = await infraestructuraService.getCasinos();
    } catch (error) {

    }
};

// Formatear fecha
const formatearFecha = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleDateString('es-MX', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
};

const formatearFechaHora = (fecha) => {
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
const getSeveridadSeverity = (severidad) => {
    const severities = {
        'baja': 'info',
        'media': 'warn',
        'alta': 'danger',
        'critica': 'danger'
    };
    return severities[severidad] || 'secondary';
};

const getCategoriaNombre = (categoria) => {
    const cat = categorias.find(c => c.value === categoria);
    return cat ? cat.label : categoria;
};

const getSeveridadNombre = (severidad) => {
    const sev = severidades.find(s => s.value === severidad);
    return sev ? sev.label.split(' ')[0] : severidad;
};

// Computed para gráficas
const incidenciasPorCasino = computed(() => {
    const conteo = {};
    incidencias.value
        .filter(i => i.esta_activo)
        .forEach(i => {
            const casino = i.casino_nombre || 'Sin definir';
            conteo[casino] = (conteo[casino] || 0) + 1;
        });
    return Object.entries(conteo)
        .sort((a, b) => b[1] - a[1]);
});

const incidenciasPorCategoria = computed(() => {
    const conteo = {};
    incidencias.value
        .filter(i => i.esta_activo)
        .forEach(i => {
            const categoria = getCategoriaNombre(i.categoria);
            conteo[categoria] = (conteo[categoria] || 0) + 1;
        });
    return Object.entries(conteo)
        .sort((a, b) => b[1] - a[1]);
});

// Datos para gráfica de casinos
const chartDataCasinos = computed(() => ({
    labels: incidenciasPorCasino.value.map(([casino]) => casino),
    datasets: [
        {
            label: 'Incidencias Reportadas',
            data: incidenciasPorCasino.value.map(([, cantidad]) => cantidad),
            backgroundColor: '#ef4444',
            borderColor: '#dc2626',
            borderWidth: 2
        }
    ]
}));

// Datos para gráfica de categorías
const chartDataCategorias = computed(() => {
    const coloresCategorias = [
        '#f59e0b', '#3b82f6', '#10b981', '#ef4444', '#8b5cf6', '#ec4899'
    ];
    
    return {
        labels: incidenciasPorCategoria.value.map(([cat]) => cat),
        datasets: [
            {
                label: 'Incidencias',
                data: incidenciasPorCategoria.value.map(([, cantidad]) => cantidad),
                backgroundColor: coloresCategorias,
                borderColor: '#ffffff',
                borderWidth: 2
            }
        ]
    };
});

// Opciones para las gráficas
const chartOptionsCasinos = ref({
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
                    return `${context.label}: ${context.parsed.y} incidencias`;
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

// Acciones CRUD
const openNew = () => {
    incidencia.value = {
        esta_activo: true,
        afecta_operacion: false,
        severidad: 'media'
    };
    submitted.value = false;
    incidenciaDialog.value = true;
};

const editarIncidencia = (data) => {
    incidencia.value = { ...data };
    
    // Convertir strings de fecha a Date objects para DatePicker
    if (incidencia.value.hora_inicio) {
        incidencia.value.hora_inicio = new Date(incidencia.value.hora_inicio);
    }
    if (incidencia.value.hora_fin) {
        incidencia.value.hora_fin = new Date(incidencia.value.hora_fin);
    }
    
    incidenciaDialog.value = true;
};

const hideDialog = () => {
    incidenciaDialog.value = false;
    submitted.value = false;
};

const saveIncidencia = async () => {
    submitted.value = true;

    if (incidencia.value.titulo?.trim() && incidencia.value.casino && incidencia.value.hora_inicio) {
        loading.value = true;
        try {
            await infraestructuraService.saveIncidencia(incidencia.value);
            toast.add({ 
                severity: 'success', 
                summary: 'Éxito', 
                detail: `Incidencia ${incidencia.value.id ? 'actualizada' : 'registrada'} correctamente`, 
                life: 3000 
            });
            incidenciaDialog.value = false;
            incidencia.value = {};
            cargarIncidencias();
        } catch (error) {

            toast.add({ 
                severity: 'error', 
                summary: 'Error', 
                detail: 'No se pudo guardar la incidencia', 
                life: 3000 
            });
        } finally {
            loading.value = false;
        }
    }
};

const toggleActivarIncidencia = (data) => {
    const accion = data.esta_activo ? 'desactivar' : 'activar';
    
    confirm.require({
        message: `¿Estás seguro de que deseas ${accion} la incidencia "${data.titulo}"?`,
        header: 'Confirmar Acción',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: {
            label: 'Cancelar',
            severity: 'secondary',
            outlined: true
        },
        acceptProps: {
            label: 'Confirmar',
            severity: data.esta_activo ? 'danger' : 'success'
        },
        accept: async () => {
            loading.value = true;
            try {
                await infraestructuraService.toggleActivarIncidencia(data);
                toast.add({ 
                    severity: 'success', 
                    summary: 'Éxito', 
                    detail: `Incidencia ${accion === 'activar' ? 'activada' : 'desactivada'} correctamente`, 
                    life: 3000 
                });
                cargarIncidencias();
            } catch (error) {

                toast.add({ 
                    severity: 'error', 
                    summary: 'Error', 
                    detail: `No se pudo ${accion} la incidencia`, 
                    life: 3000 
                });
            } finally {
                loading.value = false;
            }
        }
    });
};

onMounted(() => {
    cargarIncidencias();
    cargarCasinos();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <!-- Gráficas -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Gráfica de Casinos -->
            <Card>
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-building text-2xl text-danger"></i>
                        <span>Incidencias por Casino</span>
                    </div>
                </template>
                <template #subtitle>Casinos con más reportes de infraestructura</template>
                <template #content>
                    <div style="height: 400px">
                        <Chart 
                            type="bar" 
                            :data="chartDataCasinos" 
                            :options="chartOptionsCasinos"
                            v-if="incidencias.length > 0"
                        />
                        <div v-else class="text-center py-8 text-surface-500">
                            <i class="pi pi-chart-bar text-4xl mb-3"></i>
                            <p>No hay datos para mostrar</p>
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Gráfica de Categorías -->
            <Card>
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-tags text-2xl text-primary"></i>
                        <span>Incidencias por Categoría</span>
                    </div>
                </template>
                <template #subtitle>Distribución por tipo de incidente</template>
                <template #content>
                    <div style="height: 400px">
                        <Chart 
                            type="pie" 
                            :data="chartDataCategorias" 
                            :options="chartOptionsPie"
                            v-if="incidencias.length > 0"
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
            <ConfirmDialog />
            
            <!-- Toolbar -->
            <DataTableToolbar
                ref="toolbarRef"
                :dt="dt"
                :datos="incidencias"
                titulo-reporte="Registro de Incidencias de Infraestructura"
                nombre-archivo="incidencias-infraestructura"
                :columnas="columnas"
                :mostrar-exportacion="true"
                :mostrar-imprimir="true"
                :mostrar-refrescar="true"
                :mostrar-selector-columnas="true"
                :mostrar-buscador="true"
                @refrescar="cargarIncidencias"
                v-model:columnas-seleccionadas="columnas"
            >
                <template #acciones-extra>
                    <Button 
                        icon="pi pi-plus" 
                        label="Nueva Incidencia"
                        rounded
                        severity="danger"
                        @click="openNew"
                    />
                </template>
            </DataTableToolbar>
            
            <!-- DataTable -->
            <DataTable 
                ref="dt"
                :value="incidencias" 
                :loading="loading"
                v-model:filters="filtros"
                :globalFilterFields="['casino_nombre', 'titulo', 'categoria', 'severidad', 'descripcion']"
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
                    <div class="text-center p-4">No se encontraron incidencias registradas.</div>
                </template>
                
                <template #loading>Cargando incidencias...</template>
                
                <Column v-if="esColumnaVisible('casino_nombre')" field="casino_nombre" header="Casino" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-building text-primary"></i>
                            <span class="font-semibold">{{ data.casino_nombre }}</span>
                        </div>
                    </template>
                </Column>
                
                <Column v-if="esColumnaVisible('titulo')" field="titulo" header="Título" sortable style="min-width: 15rem">
                    <template #body="{ data }">
                        <span class="font-semibold">{{ data.titulo }}</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('categoria')" field="categoria" header="Categoría" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <Tag :value="getCategoriaNombre(data.categoria)" severity="secondary" />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('severidad')" field="severidad" header="Severidad" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <Tag 
                            :value="getSeveridadNombre(data.severidad)" 
                            :severity="getSeveridadSeverity(data.severidad)" 
                        />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('afecta_operacion')" field="afecta_operacion" header="Afecta Operación" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <Tag 
                            :value="data.afecta_operacion ? 'SÍ' : 'NO'" 
                            :severity="data.afecta_operacion ? 'danger' : 'success'" 
                        />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('hora_inicio')" field="hora_inicio" header="Hora Inicio" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-calendar text-blue-500"></i>
                            <span>{{ formatearFechaHora(data.hora_inicio) }}</span>
                        </div>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('hora_fin')" field="hora_fin" header="Hora Fin" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div v-if="data.hora_fin" class="flex items-center gap-2">
                            <i class="pi pi-calendar-minus text-green-500"></i>
                            <span>{{ formatearFechaHora(data.hora_fin) }}</span>
                        </div>
                        <span v-else class="text-surface-400 italic text-sm">En curso</span>
                    </template>
                </Column>
                
                <Column v-if="esColumnaVisible('esta_activo')" field="esta_activo" header="Estado" sortable style="min-width: 8rem">
                    <template #body="{ data }">
                        <Tag 
                            :value="data.esta_activo ? 'Activo' : 'Inactivo'" 
                            :severity="data.esta_activo ? 'success' : 'danger'" 
                        />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('creado_en')" field="creado_en" header="Fecha Registro" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="text-sm text-surface-600">
                            {{ formatearFechaHora(data.creado_en) }}
                        </div>
                    </template>
                </Column>

                <Column header="Acciones" :exportable="false" style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button 
                                icon="pi pi-pencil" 
                                size="small"
                                severity="info"
                                rounded 
                                outlined
                                @click="editarIncidencia(data)"
                                v-tooltip.top="'Editar'"
                            />
                            <Button 
                                :icon="data.esta_activo ? 'pi pi-ban' : 'pi pi-check-circle'" 
                                size="small"
                                :severity="data.esta_activo ? 'warning' : 'success'"
                                rounded 
                                outlined
                                @click="toggleActivarIncidencia(data)"
                                v-tooltip.top="data.esta_activo ? 'Desactivar' : 'Activar'"
                            />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <!-- Dialog para crear/editar -->
            <Dialog 
                v-model:visible="incidenciaDialog" 
                :style="{ width: '650px' }" 
                header="Detalles de la Incidencia" 
                :modal="true"
                class="p-fluid"
            >
                <div class="flex flex-col gap-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="casino" class="block font-bold mb-3">Casino Afectado *</label>
                            <Select 
                                id="casino" 
                                v-model="incidencia.casino" 
                                :options="casinos" 
                                optionLabel="label" 
                                optionValue="value"
                                placeholder="Selecciona un casino"
                                :invalid="submitted && !incidencia.casino"
                                fluid
                            />
                            <small class="text-red-500" v-if="submitted && !incidencia.casino">El casino es obligatorio.</small>
                        </div>

                        <div>
                            <label for="severidad" class="block font-bold mb-3">Severidad *</label>
                            <Select 
                                id="severidad" 
                                v-model="incidencia.severidad" 
                                :options="severidades" 
                                optionLabel="label" 
                                optionValue="value"
                                placeholder="Selecciona severidad"
                                fluid
                            />
                        </div>
                    </div>

                    <div>
                        <label for="titulo" class="block font-bold mb-3">Título del Evento *</label>
                        <InputText 
                            id="titulo" 
                            v-model.trim="incidencia.titulo" 
                            required="true" 
                            autofocus 
                            :invalid="submitted && !incidencia.titulo" 
                            fluid 
                            placeholder="Ej: Apagón zona sur, Gotera fila 5"
                        />
                        <small class="text-red-500" v-if="submitted && !incidencia.titulo">El título es obligatorio.</small>
                    </div>

                    <div>
                        <label for="categoria" class="block font-bold mb-3">Categoría *</label>
                        <Select 
                            id="categoria" 
                            v-model="incidencia.categoria" 
                            :options="categorias" 
                            optionLabel="label" 
                            optionValue="value"
                            placeholder="Selecciona la categoría"
                            fluid
                        />
                    </div>
                    
                    <div>
                        <label for="descripcion" class="block font-bold mb-3">Descripción Detallada</label>
                        <Textarea 
                            id="descripcion" 
                            v-model="incidencia.descripcion" 
                            rows="4" 
                            fluid 
                            placeholder="Relato completo de lo ocurrido y afectaciones visibles..."
                        />
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="hora_inicio" class="block font-bold mb-3">Hora de Inicio *</label>
                            <DatePicker 
                                id="hora_inicio" 
                                v-model="incidencia.hora_inicio" 
                                showTime 
                                hourFormat="24"
                                fluid
                                :invalid="submitted && !incidencia.hora_inicio"
                                dateFormat="dd/mm/yy"
                            />
                            <small class="text-red-500" v-if="submitted && !incidencia.hora_inicio">La hora de inicio es obligatoria.</small>
                        </div>
                        <div>
                            <label for="hora_fin" class="block font-bold mb-3">Hora de Finalización</label>
                            <DatePicker 
                                id="hora_fin" 
                                v-model="incidencia.hora_fin" 
                                showTime 
                                hourFormat="24"
                                fluid
                                dateFormat="dd/mm/yy"
                            />
                        </div>
                    </div>

                    <div class="flex items-center gap-4 mt-2">
                        <div class="flex items-center">
                            <Checkbox v-model="incidencia.afecta_operacion" :binary="true" inputId="afecta_operacion" />
                            <label for="afecta_operacion" class="ml-2">¿Afecta Operación?</label>
                        </div>

                        <div class="flex items-center">
                            <Checkbox v-model="incidencia.esta_activo" :binary="true" inputId="esta_activo" />
                            <label for="esta_activo" class="ml-2">¿Está Activo?</label>
                        </div>
                    </div>

                    <div v-if="incidencia.id" class="border-t border-surface-200 dark:border-surface-700 pt-4">
                        <div class="font-bold mb-3 text-surface-500 dark:text-surface-400">Auditoría</div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Creado por</label>
                                <InputText id="creado_por" name="creado_por" :value="incidencia.creado_por || 'Sistema'" disabled fluid class="opacity-100" />
                            </div>
                            <div>
                                <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Fecha Registro</label>
                                <InputText id="creado_en" name="creado_en" :value="formatearFechaHora(incidencia.creado_en)" disabled fluid class="opacity-100" />
                            </div>
                        </div>
                    </div>
                </div>

                <template #footer>
                    <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                    <Button label="Guardar" icon="pi pi-check" @click="saveIncidencia" />
                </template>
            </Dialog>
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
