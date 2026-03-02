<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api, { getUser } from '@/service/api';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';

// --- NUEVOS COMPONENTES INTELIGENTES ---
import ModeloFormDialog from '@/components/modelos/ModeloFormDialog.vue';
import ModeloDetalleDialog from '@/components/modelos/ModeloDetalleDialog.vue';

const modelos = ref([]);
const proveedores = ref([]); // Necesario si hay otra logica en la tabla
const estadisticas = ref({ total: 0 });
const loading = ref(false);
const dt = ref();
const toolbarRef = ref();
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();
const confirm = useConfirm();

// --- ESTADOS DE COMPONENTES INTELIGENTES ---
const dialogFormVisible = ref(false);
const dialogDetalleVisible = ref(false);
const idModeloActivo = ref(null);
const objModeloDetalle = ref(null);

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
                detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'Usuario sin casino asignado. Contacte al administrador.',
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

        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudieron cargar los modelos', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// Helpers
const esColumnaVisible = (field) => {
    const col = columnas.value.find(c => c.field === field);
    return col ? col.visible : true;
};

// Funciones de Componentes Reactivos
const openNew = () => {
    idModeloActivo.value = null;
    dialogFormVisible.value = true;
};

const editarModelo = (data) => {
    idModeloActivo.value = data.id;
    dialogFormVisible.value = true;
};

const verDetalleModelo = (data) => {
    objModeloDetalle.value = { ...data };
    dialogDetalleVisible.value = true;
};

const onModeloGuardado = () => {
    cargarDatos();
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
                toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudo desactivar el modelo', life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
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
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Total Modelos
                                Registrados</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{ estadisticas.total
                            }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-indigo-100 dark:bg-indigo-400/10 rounded-lg"
                            style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-box text-indigo-500 dark:text-indigo-400 text-2xl"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <Toast />
            <ConfirmDialog />

            <DataTableToolbar ref="toolbarRef" :dt="dt" :datos="modelos" titulo-reporte="Modelos de Máquinas"
                nombre-archivo="modelos_maquinas" :columnas="columnas" @refrescar="cargarDatos"
                v-model:columnas-seleccionadas="columnas" :mostrar-exportacion="permisos.puedeExportar"
                :mostrar-imprimir="permisos.puedeExportar">
                <template #acciones-extra>
                    <Button v-if="permisos.puedeAgregar" icon="pi pi-plus" label="Nuevo Modelo" rounded
                        severity="primary" @click="openNew" />
                </template>
            </DataTableToolbar>

            <DataTable ref="dt" :value="modelos" :loading="loading" v-model:filters="filtros"
                :globalFilterFields="['nombre_modelo', 'nombre_producto', 'proveedor_nombre', 'descripcion']" paginator
                :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]" dataKey="id" showGridlines stripedRows>
                <template #empty>
                    <div class="text-center p-4">No se encontraron modelos registrados.</div>
                </template>

                <Column v-if="esColumnaVisible('nombre_modelo')" field="nombre_modelo" header="Modelo" sortable
                    style="min-width: 12rem">
                    <template #body="{ data }">
                        <span class="font-bold text-primary-500 cursor-pointer hover:text-primary-700 hover:underline"
                            @click="verDetalleModelo(data)">
                            {{ data.nombre_modelo }}
                        </span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('nombre_producto')" field="nombre_producto" header="Producto / Marca"
                    sortable style="min-width: 12rem" />
                <Column v-if="esColumnaVisible('proveedor_nombre')" field="proveedor_nombre" header="Proveedor" sortable
                    style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-briefcase text-surface-400 text-sm"></i>
                            <span>{{ data.proveedor_nombre }}</span>
                        </div>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('descripcion')" field="descripcion" header="Descripción" sortable
                    style="min-width: 16rem">
                    <template #body="{ data }">
                        <span class="text-sm text-surface-600 dark:text-surface-300">{{ data.descripcion || 'Sin descripción' }}</span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('total_maquinas')" field="total_maquinas" header="Máquinas" sortable
                    style="min-width: 8rem">
                    <template #body="{ data }">
                        <Tag :value="String(data.total_maquinas)" severity="info" rounded />
                    </template>
                </Column>

                <Column v-if="permisos.puedeEditar || permisos.puedeDesactivar" header="Acciones" :exportable="false"
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button v-if="permisos.puedeEditar" icon="pi pi-pencil" size="small" severity="info" rounded
                                outlined @click="editarModelo(data)" v-tooltip.top="'Editar'" />
                            <Button v-if="permisos.puedeDesactivar" icon="pi pi-ban" size="small" severity="warning"
                                rounded outlined @click="desactivarModelo(data)" v-tooltip.top="'Desactivar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <!-- Dialog Componentes Inteligentes -->
            <ModeloFormDialog v-model:visible="dialogFormVisible" :modeloId="idModeloActivo"
                @saved="onModeloGuardado" />

            <ModeloDetalleDialog v-model:visible="dialogDetalleVisible" :modelo="objModeloDetalle" />
        </div>
    </div>
</template>
