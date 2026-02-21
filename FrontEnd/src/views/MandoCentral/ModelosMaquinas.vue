<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api from '@/service/api';import { guardarModelo } from '@/service/modeloService';import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import Chart from 'primevue/chart';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

const modelos = ref([]);
const casinos = ref([]);
const proveedores = ref([]);
const loading = ref(false);
const dt = ref();
const toolbarRef = ref();

// Hacer el DataTable responsive en móvil
useResponsiveDataTable(dt);
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();
const confirm = useConfirm();
const modeloDialog = ref(false);
const modelo = ref({});
const submitted = ref(false);

// Variables para Gráficas
const chartDataFabricantes = ref();
const chartOptionsFabricantes = ref();

// Sincronizar buscador
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Columnas
const columnas = ref([
    { field: 'nombre_modelo', label: 'Modelo Técnico', visible: true },
    { field: 'nombre_producto', label: 'Nombre Producto', visible: true },
    { field: 'casino_nombre', label: 'Casino', visible: true },
    { field: 'proveedor_nombre', label: 'Fabricante', visible: true },
    { field: 'descripcion', label: 'Descripción', visible: true },
    { field: 'esta_activo', label: 'Estado', visible: true },
    { field: 'creado_en', label: 'Fecha Registro', visible: true }
]);

// Cargar datos
const cargarModelos = async () => {
    loading.value = true;
    try {
        const [resModelos, resProveedores] = await Promise.all([
            api.get('modelos/lista/'),
            api.get('proveedores/lista/')
        ]);

        // Actualizar lista de proveedores para el selector (solo activos)
        proveedores.value = resProveedores.data.filter(p => p.esta_activo);

        // Enriquecer modelos con nombre de casino
        modelos.value = resModelos.data.map(m => {
            const prov = resProveedores.data.find(p => p.id === m.proveedor);
            return {
                ...m,
                casino_nombre: prov ? (prov.casino_nombre || 'N/A') : 'N/A'
            };
        });

        actualizarGraficas();
    } catch (error) {

        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudo cargar la lista de modelos', life: 3000 });
    } finally {
        loading.value = false;
    }
};

const cargarCasinos = async () => {
    try {
        const response = await api.get('casinos/');
        casinos.value = response.data;
    } catch (error) {

    }
};

// Proveedores filtrados por casino seleccionado
const proveedoresFiltrados = computed(() => {
    if (!modelo.value.casino_id) return [];
    return proveedores.value.filter(p => p.casino === modelo.value.casino_id);
});

// Gráficas
const actualizarGraficas = () => {
    if (!modelos.value.length) return;

    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--p-text-color') || '#334155';

    const conteo = {};
    modelos.value.filter(m => m.esta_activo).forEach(m => {
        const nombre = m.proveedor_nombre || 'Desconocido';
        conteo[nombre] = (conteo[nombre] || 0) + 1;
    });

    chartDataFabricantes.value = {
        labels: Object.keys(conteo),
        datasets: [{
            data: Object.values(conteo),
            backgroundColor: [
                '#3b82f6', '#ef4444', '#22c55e', '#eab308', '#a855f7', 
                '#06b6d4', '#f97316', '#14b8a6', '#6366f1', '#ec4899',
                '#84cc16', '#10b981', '#0ea5e9', '#8b5cf6', '#d946ef',
                '#f43f5e', '#f59e0b', '#64748b', '#71717a', '#78716c'
            ]
        }]
    };

    chartOptionsFabricantes.value = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: { usePointStyle: true, color: textColor }
            }
        }
    };
};

// Helpers
const formatearFecha = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleString('es-MX', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit'
    });
};

const esColumnaVisible = (field) => {
    const columna = columnas.value.find(c => c.field === field);
    return columna ? columna.visible : true;
};

// CRUD
const openNew = () => {
    modelo.value = { esta_activo: true, casino_id: null };
    submitted.value = false;
    modeloDialog.value = true;
};

const editarModelo = (data) => {
    modelo.value = { ...data };
    // Buscar el casino al que pertenece el proveedor actual para pre-llenar el select
    const prov = proveedores.value.find(p => p.id === data.proveedor);
    if (prov) {
        modelo.value.casino_id = prov.casino;
    }
    modeloDialog.value = true;
};

const hideDialog = () => {
    modeloDialog.value = false;
    submitted.value = false;
};

const saveModelo = async () => {
    submitted.value = true;

    if (modelo.value.nombre_modelo?.trim() && modelo.value.nombre_producto?.trim() && modelo.value.proveedor) {
        loading.value = true;
        
        const esEdicion = !!modelo.value.id;
        const resultado = await guardarModelo(modelo.value, esEdicion);
        
        if (!resultado.exito) {
            toast.add({ 
                severity: 'error', 
                summary: resultado.error, 
                detail: resultado.detalle, 
                life: 5000 
            });
            loading.value = false;
            return;
        }

        toast.add({ 
            severity: 'success', 
            summary: 'Éxito', 
            detail: resultado.mensaje, 
            life: 3000 
        });
        
        modeloDialog.value = false;
        modelo.value = {};
        cargarModelos();
        loading.value = false;
    }
};

const toggleActivarModelo = (data) => {
    const accion = data.esta_activo ? 'desactivar' : 'activar';
    confirm.require({
        message: `¿Estás seguro de que deseas ${accion} el modelo "${data.nombre_modelo}"?`,
        header: 'Confirmar Acción',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: { label: 'Cancelar', severity: 'secondary', outlined: true },
        acceptProps: { label: 'Confirmar', severity: data.esta_activo ? 'danger' : 'success' },
        accept: async () => {
            loading.value = true;
            try {
                await api.patch(`modelos/${data.id}/switch-estado/`, {});
                toast.add({ severity: 'success', summary: 'Éxito', detail: `Modelo ${accion === 'activar' ? 'activado' : 'desactivado'} correctamente`, life: 3000 });
                cargarModelos();
            } catch (error) {
                toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.error || error?.response?.data?.detail || `No se pudo ${accion} el modelo`, life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

onMounted(() => {
    cargarModelos();
    cargarCasinos();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <!-- Estadísticas -->
        <div class="card flex flex-col items-center justify-center">
            <div class="font-semibold text-xl mb-4">Modelos por Fabricante</div>
            <div class="relative w-full h-[250px] flex justify-center">
                <Chart v-if="chartDataFabricantes" type="pie" :data="chartDataFabricantes" :options="chartOptionsFabricantes" class="h-full w-full" />
                <div v-else class="flex items-center justify-center h-full text-surface-500">Cargando datos...</div>
            </div>
        </div>

        <div class="card">
            <Toast />
            <ConfirmDialog />
            
            <DataTableToolbar
                ref="toolbarRef"
                :dt="dt"
                :datos="modelos"
                titulo-reporte="Catálogo de Modelos de Máquinas"
                nombre-archivo="modelos_maquinas"
                :columnas="columnas"
                @refrescar="cargarModelos"
                v-model:columnas-seleccionadas="columnas"
            >
                <template #acciones-extra>
                    <Button icon="pi pi-plus" label="Nuevo Modelo" rounded severity="primary" @click="openNew" />
                </template>
            </DataTableToolbar>
            
            <DataTable 
                ref="dt" :value="modelos" :loading="loading" v-model:filters="filtros"
                :globalFilterFields="['nombre_modelo', 'nombre_producto', 'casino_nombre', 'proveedor_nombre', 'descripcion']"
                paginator :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]"
                dataKey="id" showGridlines stripedRows
                class="datatable-mobile"
            >
                <template #empty><div class="text-center p-4">No se encontraron modelos registrados.</div></template>
                
                <Column v-if="esColumnaVisible('nombre_modelo')" field="nombre_modelo" header="Modelo Técnico" sortable style="min-width: 14rem">
                    <template #body="{ data }"><span class="font-bold">{{ data.nombre_modelo }}</span></template>
                </Column>
                <Column v-if="esColumnaVisible('nombre_producto')" field="nombre_producto" header="Nombre Producto" sortable style="min-width: 14rem" />
                <Column v-if="esColumnaVisible('casino_nombre')" field="casino_nombre" header="Casino" sortable style="min-width: 12rem">
                    <template #body="{ data }"><span class="text-sm">{{ data.casino_nombre }}</span></template>
                </Column>
                <Column v-if="esColumnaVisible('proveedor_nombre')" field="proveedor_nombre" header="Fabricante" sortable style="min-width: 12rem" />
                <Column v-if="esColumnaVisible('descripcion')" field="descripcion" header="Descripción" sortable style="min-width: 18rem" />
                <Column v-if="esColumnaVisible('esta_activo')" field="esta_activo" header="Estado" sortable style="min-width: 8rem">
                    <template #body="{ data }"><Tag :value="data.esta_activo ? 'Activo' : 'Inactivo'" :severity="data.esta_activo ? 'success' : 'danger'" /></template>
                </Column>
                <Column v-if="esColumnaVisible('creado_en')" field="creado_en" header="Fecha Registro" sortable style="min-width: 12rem">
                    <template #body="{ data }"><div class="text-sm">{{ formatearFecha(data.creado_en) }}</div></template>
                </Column>
                
                <Column header="Acciones" :exportable="false" style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button icon="pi pi-pencil" size="small" severity="info" rounded outlined @click="editarModelo(data)" v-tooltip.top="'Editar'" />
                            <Button :icon="data.esta_activo ? 'pi pi-ban' : 'pi pi-check-circle'" size="small" :severity="data.esta_activo ? 'warning' : 'success'" rounded outlined @click="toggleActivarModelo(data)" v-tooltip.top="data.esta_activo ? 'Desactivar' : 'Activar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <Dialog v-model:visible="modeloDialog" :style="{ width: '500px' }" header="Detalles del Modelo" :modal="true">
                <div class="flex flex-col gap-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="nombre_modelo" class="block font-bold mb-3">Nombre del Modelo</label>
                            <InputText id="nombre_modelo" v-model.trim="modelo.nombre_modelo" required="true" autofocus :invalid="submitted && !modelo.nombre_modelo" fluid />
                            <small class="text-red-500" v-if="submitted && !modelo.nombre_modelo">El modelo es obligatorio.</small>
                        </div>
                        <div>
                            <label for="nombre_producto" class="block font-bold mb-3">Nombre Producto</label>
                            <InputText id="nombre_producto" v-model.trim="modelo.nombre_producto" required="true" :invalid="submitted && !modelo.nombre_producto" fluid />
                            <small class="text-red-500" v-if="submitted && !modelo.nombre_producto">El producto es obligatorio.</small>
                        </div>
                    </div>
                    <div>
                        <label for="casino" class="block font-bold mb-3">Casino</label>
                        <Select id="casino" v-model="modelo.casino_id" :options="casinos" optionLabel="nombre" optionValue="id" placeholder="Seleccione un Casino" fluid @change="modelo.proveedor = null" />
                    </div>
                    <div>
                        <label for="proveedor" class="block font-bold mb-3">Fabricante / Proveedor</label>
                        <Select id="proveedor" v-model="modelo.proveedor" :options="proveedoresFiltrados" optionLabel="nombre" optionValue="id" placeholder="Seleccione un Fabricante" fluid :invalid="submitted && !modelo.proveedor" :disabled="!modelo.casino_id" />
                        <small class="text-red-500" v-if="submitted && !modelo.proveedor">El fabricante es obligatorio.</small>
                        <small v-if="!modelo.casino_id" class="text-surface-500 block mt-1">Seleccione un casino primero.</small>
                    </div>
                    <div>
                        <label for="descripcion" class="block font-bold mb-3">Descripción / Características</label>
                        <Textarea id="descripcion" v-model="modelo.descripcion" rows="3" fluid placeholder="Tipo de gabinete, características especiales..." />
                    </div>
                    <div class="flex items-center mt-2">
                        <Checkbox v-model="modelo.esta_activo" :binary="true" inputId="esta_activo" />
                        <label for="esta_activo" class="ml-2">¿Modelo Activo?</label>
                    </div>
                </div>
                <template #footer>
                    <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                    <Button label="Guardar" icon="pi pi-check" @click="saveModelo" />
                </template>
            </Dialog>
        </div>
    </div>
</template>