<script setup>
import { ref, watch, onMounted } from 'vue';
import api from '@/service/api';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';
import { parseServerError } from '@/utils/parseServerError';

// --- NUEVOS COMPONENTES INTELIGENTES ---
import MaquinaFormDialog from '@/components/maquinas/MaquinaFormDialog.vue';
import MaquinaDetalleDialog from '@/components/maquinas/MaquinaDetalleDialog.vue';

const maquinas = ref([]);
const loading = ref(false);
const dt = ref();
const toolbarRef = ref();

useResponsiveDataTable(dt);
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();
const confirm = useConfirm();

// --- ESTADOS DE LOS MODALES ---
const formDialogVisible = ref(false);
const detalleDialogVisible = ref(false);
const maquinaSeleccionadaId = ref(null);
const maquinaDetalle = ref(null);

// Sincronizar buscador
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Columnas
const columnas = ref([
    { field: 'uid_sala', label: 'UID Sala', visible: true },
    { field: 'numero_serie', label: 'No. Serie', visible: true },
    { field: 'casino_nombre', label: 'Casino', visible: true },
    { field: 'modelo_nombre', label: 'Modelo', visible: true },
    { field: 'juego', label: 'Juego', visible: true },
    { field: 'ip_maquina', label: 'IP', visible: true },
    { field: 'ubicacion_piso', label: 'Piso', visible: false },
    { field: 'ubicacion_sala', label: 'Sala', visible: false },
    { field: 'estado_actual', label: 'Estado', visible: true },
    { field: 'esta_activo', label: 'Activo', visible: true }
]);

// Cargar Datos Iniciales (Solo lista de máquinas, el resto lo carga el FormComponent)
const cargarDatos = async () => {
    loading.value = true;
    try {
        const resMaquinas = await api.get('maquinas/lista/');
        maquinas.value = resMaquinas.data;
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: parseServerError(error, 'No se pudieron cargar los datos de las máquinas'), life: 5000 });
    } finally {
        loading.value = false;
    }
};

// Helpers
const getEstadoSeverity = (estado) => {
    switch (estado) {
        case 'OPERATIVA': return 'success';
        case 'DAÑADA_OPERATIVA': return 'warn';
        case 'DAÑADA': return 'danger';
        case 'MANTENIMIENTO': return 'info';
        case 'OBSERVACION': return 'secondary';
        case 'PRUEBAS': return 'contrast';
        default: return 'secondary';
    }
};

const esColumnaVisible = (field) => {
    const columna = columnas.value.find(c => c.field === field);
    return columna ? columna.visible : true;
};

// --- CRUD VIA COMPONENTES INTELIGENTES ---
const openNew = () => {
    maquinaSeleccionadaId.value = null;
    formDialogVisible.value = true;
};

const editarMaquina = (data) => {
    maquinaSeleccionadaId.value = data.id;
    formDialogVisible.value = true;
};

const verDetalleMaquina = async (data) => {
    // Para ver el detalle visual con su historial
    try {
        loading.value = true;
        const res = await api.get(`maquinas/${data.id}/`);
        maquinaDetalle.value = res.data;
        detalleDialogVisible.value = true;
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: parseServerError(error, 'No se pudo cargar el detalle completo de la máquina.'), life: 5000 });
    } finally {
        loading.value = false;
    }
};

const onMaquinaGuardada = () => {
    toast.add({ severity: 'success', summary: 'Éxito', detail: 'Máquina guardada correctamente', life: 3000 });
    cargarDatos();
};

const toggleActivarMaquina = (data) => {
    const accion = data.esta_activo ? 'desactivar' : 'activar';
    confirm.require({
        message: `¿Estás seguro de que deseas ${accion} la máquina "${data.uid_sala}"?`,
        header: 'Confirmar Acción',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: { label: 'Cancelar', severity: 'secondary', outlined: true },
        acceptProps: { label: 'Confirmar', severity: data.esta_activo ? 'danger' : 'success' },
        accept: async () => {
            loading.value = true;
            try {
                await api.patch(`maquinas/${data.id}/switch-estado/`, {});
                toast.add({ severity: 'success', summary: 'Éxito', detail: `Máquina ${accion === 'activar' ? 'activada' : 'desactivada'} correctamente`, life: 3000 });
                cargarDatos();
            } catch (error) {
                toast.add({ severity: 'error', summary: 'Error', detail: parseServerError(error, `No se pudo ${accion} la máquina`), life: 5000 });
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
        <div class="card">
            <Toast />
            <ConfirmDialog />

            <DataTableToolbar ref="toolbarRef" :dt="dt" :datos="maquinas" titulo-reporte="Inventario de Máquinas"
                nombre-archivo="maquinas" :columnas="columnas" @refrescar="cargarDatos"
                v-model:columnas-seleccionadas="columnas">
                <template #acciones-extra>
                    <Button icon="pi pi-plus" label="Nueva Máquina" rounded severity="primary" @click="openNew" />
                </template>
            </DataTableToolbar>

            <DataTable ref="dt" :value="maquinas" :loading="loading" v-model:filters="filtros"
                :globalFilterFields="['uid_sala', 'numero_serie', 'casino_nombre', 'modelo_nombre', 'juego', 'ip_maquina']"
                paginator :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]" dataKey="id" showGridlines stripedRows
                class="datatable-mobile">
                <template #empty>
                    <div class="text-center p-4">No se encontraron máquinas registradas.</div>
                </template>

                <Column v-if="esColumnaVisible('uid_sala')" field="uid_sala" header="UID Sala" sortable
                    style="min-width: 8rem">
                    <template #body="{ data }"><span class="font-bold">{{ data.uid_sala }}</span></template>
                </Column>
                <Column v-if="esColumnaVisible('numero_serie')" field="numero_serie" header="No. Serie" sortable
                    style="min-width: 10rem" />
                <Column v-if="esColumnaVisible('casino_nombre')" field="casino_nombre" header="Casino" sortable
                    style="min-width: 12rem" />
                <Column v-if="esColumnaVisible('modelo_nombre')" field="modelo_nombre" header="Modelo" sortable
                    style="min-width: 12rem" />
                <Column v-if="esColumnaVisible('juego')" field="juego" header="Juego" sortable
                    style="min-width: 12rem" />
                <Column v-if="esColumnaVisible('ip_maquina')" field="ip_maquina" header="IP" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }"><span class="font-mono text-sm">{{ data.ip_maquina || 'N/A'
                    }}</span></template>
                </Column>
                <Column v-if="esColumnaVisible('ubicacion_piso')" field="ubicacion_piso" header="Piso" sortable
                    style="min-width: 8rem" />
                <Column v-if="esColumnaVisible('ubicacion_sala')" field="ubicacion_sala" header="Sala" sortable
                    style="min-width: 10rem" />

                <Column v-if="esColumnaVisible('estado_actual')" field="estado_actual" header="Estado Técnico" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <Tag :value="data.estado_actual" :severity="getEstadoSeverity(data.estado_actual)" />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('esta_activo')" field="esta_activo" header="Activo" sortable
                    style="min-width: 6rem">
                    <template #body="{ data }">
                        <i
                            :class="[data.esta_activo ? 'pi pi-check-circle text-green-500' : 'pi pi-times-circle text-red-500']"></i>
                    </template>
                </Column>

                <Column header="Acciones" :exportable="false" style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button icon="pi pi-eye" size="small" severity="secondary" rounded outlined
                                @click="verDetalleMaquina(data)" v-tooltip.top="'Ver Detalle Completo e Historial'" />
                            <Button icon="pi pi-pencil" size="small" severity="info" rounded outlined
                                @click="editarMaquina(data)" v-tooltip.top="'Editar'" />
                            <Button :icon="data.esta_activo ? 'pi pi-ban' : 'pi pi-check-circle'" size="small"
                                :severity="data.esta_activo ? 'warning' : 'success'" rounded outlined
                                @click="toggleActivarMaquina(data)"
                                v-tooltip.top="data.esta_activo ? 'Desactivar' : 'Activar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <!-- COMPONENTES INTELIGENTES INYECTADOS -->
            <MaquinaFormDialog v-model:visible="formDialogVisible" :maquinaId="maquinaSeleccionadaId"
                :permitirElegirCasino="true" @saved="onMaquinaGuardada" />

            <MaquinaDetalleDialog v-model:visible="detalleDialogVisible" :maquina="maquinaDetalle"
                @levantar-incidencia="() => { toast.add({ severity: 'info', summary: 'Aviso', detail: 'Redirigiendo a incidentes...' }) }" />
        </div>
    </div>
</template>