<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api, { getUser } from '@/service/api';
import { guardarModelo } from '@/service/modeloService';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';

const modelos = ref([]);
const proveedores = ref([]);
const estadisticas = ref({ total: 0 });
const loading = ref(false);
const dt = ref();
const toolbarRef = ref();
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();
const confirm = useConfirm();
const modeloDialog = ref(false);
const modelo = ref({});
const submitted = ref(false);

// Modal de detalle
const detalleDialog = ref(false);
const modeloDetalle = ref(null);

// Obtener usuario actual y su rol
const usuario = computed(() => getUser());
const rolUsuario = computed(() => usuario.value?.rol_nombre || '');
const casinoUsuario = computed(() => usuario.value?.casino || null);

// Permisos basados en rol
const permisos = computed(() => ({
    puedeExportar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeAgregar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeEditar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeDesactivar: ['SUP SISTEMAS', 'ADMINISTRADOR'].includes(rolUsuario.value)
}));

// Sincronizar buscador
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Columnas
const columnas = ref([
    { field: 'nombre_modelo', label: 'Modelo', visible: true },
    { field: 'nombre_producto', label: 'Producto / Marca', visible: true },
    { field: 'proveedor_nombre', label: 'Proveedor', visible: true },
    { field: 'descripcion', label: 'Descripción', visible: true },
    { field: 'total_maquinas', label: 'Máquinas', visible: true }
]);

// Cargar Datos
const cargarDatos = async () => {
    loading.value = true;
    try {
        if (!casinoUsuario.value) {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: 'Usuario sin casino asignado. Contacte al administrador.',
                life: 5000
            });
            return;
        }

        const res = await api.get(`modelos/lista-por-casino/${casinoUsuario.value}/`);
        modelos.value = res.data.modelos;
        estadisticas.value = res.data.estadisticas;

        // Cargar proveedores del casino si puede agregar/editar
        if (permisos.value.puedeAgregar || permisos.value.puedeEditar) {
            const resProv = await api.get(`proveedores/lista-por-casino/${casinoUsuario.value}/`);
            proveedores.value = resProv.data.proveedores;
        }
    } catch (error) {
        console.error('Error al cargar datos:', error);
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los modelos', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// Helpers
const esColumnaVisible = (field) => {
    const col = columnas.value.find(c => c.field === field);
    return col ? col.visible : true;
};

// CRUD
const openNew = () => {
    modelo.value = {
        esta_activo: true
    };
    submitted.value = false;
    modeloDialog.value = true;
};

const editarModelo = (data) => {
    modelo.value = { ...data };
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
        cargarDatos();
        loading.value = false;
    }
};

const desactivarModelo = (data) => {
    confirm.require({
        message: `¿Estás seguro de que deseas desactivar el modelo "${data.nombre_modelo}"?`,
        header: 'Confirmar Acción',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: { label: 'Cancelar', severity: 'secondary', outlined: true },
        acceptProps: { label: 'Desactivar', severity: 'danger' },
        accept: async () => {
            loading.value = true;
            try {
                await api.patch(`modelos/${data.id}/switch-estado/`, {});
                toast.add({ severity: 'success', summary: 'Éxito', detail: 'Modelo desactivado correctamente', life: 3000 });
                cargarDatos();
            } catch (error) {
                toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo desactivar el modelo', life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

// Modal detalle
const verDetalleModelo = (data) => {
    modeloDetalle.value = { ...data };
    detalleDialog.value = true;
};

onMounted(() => {
    cargarDatos();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <!-- Estadísticas -->
        <div v-if="permisos.puedeExportar" class="card">
            <div class="font-bold text-xl mb-6 text-surface-900 dark:text-surface-0">
                Modelos de Máquinas - {{ usuario?.casino_nombre }}
            </div>
            <div class="grid grid-cols-1 gap-4">
                <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Total Modelos Registrados</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{ estadisticas.total }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-indigo-100 dark:bg-indigo-400/10 rounded-lg" style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-box text-indigo-500 dark:text-indigo-400 text-2xl"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <Toast />
            <ConfirmDialog />

            <DataTableToolbar
                ref="toolbarRef"
                :dt="dt"
                :datos="modelos"
                titulo-reporte="Modelos de Máquinas"
                nombre-archivo="modelos_maquinas"
                :columnas="columnas"
                @refrescar="cargarDatos"
                v-model:columnas-seleccionadas="columnas"
                :mostrar-exportacion="permisos.puedeExportar"
                :mostrar-imprimir="permisos.puedeExportar"
            >
                <template #acciones-extra>
                    <Button v-if="permisos.puedeAgregar" icon="pi pi-plus" label="Nuevo Modelo" rounded severity="primary" @click="openNew" />
                </template>
            </DataTableToolbar>

            <DataTable
                ref="dt" :value="modelos" :loading="loading" v-model:filters="filtros"
                :globalFilterFields="['nombre_modelo', 'nombre_producto', 'proveedor_nombre', 'descripcion']"
                paginator :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]"
                dataKey="id" showGridlines stripedRows
            >
                <template #empty><div class="text-center p-4">No se encontraron modelos registrados.</div></template>

                <Column v-if="esColumnaVisible('nombre_modelo')" field="nombre_modelo" header="Modelo" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <span class="font-bold text-primary-500 cursor-pointer hover:text-primary-700 hover:underline" @click="verDetalleModelo(data)">
                            {{ data.nombre_modelo }}
                        </span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('nombre_producto')" field="nombre_producto" header="Producto / Marca" sortable style="min-width: 12rem" />
                <Column v-if="esColumnaVisible('proveedor_nombre')" field="proveedor_nombre" header="Proveedor" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-briefcase text-surface-400 text-sm"></i>
                            <span>{{ data.proveedor_nombre }}</span>
                        </div>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('descripcion')" field="descripcion" header="Descripción" sortable style="min-width: 16rem">
                    <template #body="{ data }">
                        <span class="text-sm text-surface-600 dark:text-surface-300">{{ data.descripcion || 'Sin descripción' }}</span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('total_maquinas')" field="total_maquinas" header="Máquinas" sortable style="min-width: 8rem">
                    <template #body="{ data }">
                        <Tag :value="String(data.total_maquinas)" severity="info" rounded />
                    </template>
                </Column>

                <Column v-if="permisos.puedeEditar || permisos.puedeDesactivar" header="Acciones" :exportable="false" style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button v-if="permisos.puedeEditar" icon="pi pi-pencil" size="small" severity="info" rounded outlined @click="editarModelo(data)" v-tooltip.top="'Editar'" />
                            <Button v-if="permisos.puedeDesactivar" icon="pi pi-ban" size="small" severity="warning" rounded outlined @click="desactivarModelo(data)" v-tooltip.top="'Desactivar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <!-- Dialog Crear/Editar -->
            <Dialog v-model:visible="modeloDialog" :style="{ width: '600px' }" header="Datos del Modelo" :modal="true">
                <div class="flex flex-col gap-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="proveedor" class="block font-bold mb-3">Proveedor</label>
                            <Select id="proveedor" v-model="modelo.proveedor" :options="proveedores" optionLabel="nombre" optionValue="id" placeholder="Seleccione Proveedor" fluid :invalid="submitted && !modelo.proveedor" />
                            <small class="text-red-500" v-if="submitted && !modelo.proveedor">Requerido.</small>
                        </div>
                        <div>
                            <label for="nombre_modelo" class="block font-bold mb-3">Nombre del Modelo</label>
                            <InputText id="nombre_modelo" v-model.trim="modelo.nombre_modelo" fluid :invalid="submitted && !modelo.nombre_modelo" />
                            <small class="text-red-500" v-if="submitted && !modelo.nombre_modelo">Requerido.</small>
                        </div>
                    </div>
                    <div>
                        <label for="nombre_producto" class="block font-bold mb-3">Nombre del Producto / Marca</label>
                        <InputText id="nombre_producto" v-model.trim="modelo.nombre_producto" fluid :invalid="submitted && !modelo.nombre_producto" />
                        <small class="text-red-500" v-if="submitted && !modelo.nombre_producto">Requerido.</small>
                    </div>
                    <div>
                        <label for="descripcion" class="block font-bold mb-3">Descripción Técnica</label>
                        <Textarea id="descripcion" v-model="modelo.descripcion" rows="3" fluid placeholder="Detalles técnicos del modelo..." />
                    </div>
                </div>
                <template #footer>
                    <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                    <Button label="Guardar" icon="pi pi-check" @click="saveModelo" />
                </template>
            </Dialog>

            <!-- Modal de Detalle del Modelo -->
            <Dialog v-model:visible="detalleDialog" :style="{ width: '750px' }" header="Ficha del Modelo" :modal="true">
                <div v-if="modeloDetalle" class="flex flex-col gap-5">
                    <div class="surface-card border-2 border-primary-200 dark:border-primary-900 rounded-xl p-5 bg-gradient-to-br from-primary-50 to-white dark:from-primary-950 dark:to-surface-900">
                        <!-- Cabecera -->
                        <div class="flex items-center gap-4 mb-5">
                            <div class="flex items-center justify-center bg-primary-500 rounded-xl shadow-lg" style="width:3.5rem;height:3.5rem">
                                <i class="pi pi-box text-white text-2xl"></i>
                            </div>
                            <div class="flex-1">
                                <h3 class="text-2xl font-bold text-surface-900 dark:text-surface-0 mb-1">{{ modeloDetalle.nombre_modelo }}</h3>
                                <p class="text-surface-600 dark:text-surface-400 font-medium">
                                    {{ modeloDetalle.nombre_producto }}
                                    <span class="text-primary-500 mx-2">•</span>
                                    {{ modeloDetalle.casino_nombre }}
                                </p>
                            </div>
                        </div>

                        <div class="grid grid-cols-2 md:grid-cols-3 gap-6">
                            <!-- Proveedor -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-briefcase text-teal-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Proveedor</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{ modeloDetalle.proveedor_nombre }}</span>
                            </div>
                            <!-- Producto / Marca -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-tag text-purple-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Producto / Marca</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{ modeloDetalle.nombre_producto }}</span>
                            </div>
                            <!-- Máquinas Activas -->
                            <div class="bg-blue-50 dark:bg-blue-950 rounded-lg p-3 border border-blue-200 dark:border-blue-800">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-desktop text-blue-600 text-sm"></i>
                                    <span class="text-blue-700 dark:text-blue-400 text-xs font-semibold">Máquinas Activas</span>
                                </div>
                                <span class="font-bold text-blue-800 dark:text-blue-300 text-2xl">{{ modeloDetalle.total_maquinas }}</span>
                            </div>
                            <!-- Casino -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-building text-red-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Casino</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{ modeloDetalle.casino_nombre }}</span>
                            </div>
                            <!-- Descripción (ocupa 2 columnas) -->
                            <div class="col-span-2 bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-align-left text-indigo-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Descripción Técnica</span>
                                </div>
                                <p class="text-sm text-surface-700 dark:text-surface-300">{{ modeloDetalle.descripcion || 'Sin descripción registrada.' }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </Dialog>
        </div>
    </div>
</template>
