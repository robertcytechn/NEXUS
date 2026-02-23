<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import { mostrarToastPuntos } from '@/service/gamificacionUtils';
import { useConfirm } from 'primevue/useconfirm';
import api, { getUser, hasRoleAccess } from '@/service/api';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

const toast = useToast();
const confirm = useConfirm();

// Estados
const loading = ref(false);
const mantenimientos = ref([]);
const mantenimientoDialog = ref(false);
const deleteDialog = ref(false);
const mantenimiento = ref({});
const submitted = ref(false);
const filteredMaquinas = ref([]);
const usuario = ref(null);

// Configuración de columnas para el Toolbar
const columnas = ref([
    { field: 'id', label: 'ID', visible: false },
    { field: 'maquina_uid', label: 'Máquina (UID)', visible: true },
    { field: 'fecha_mantenimiento', label: 'Fecha Mantenimiento', visible: true },
    { field: 'estado_final_maquina', label: 'Estado Resultante', visible: true },
    { field: 'tecnico_nombre', label: 'Técnico Responsable', visible: true },
    { field: 'observaciones', label: 'Observaciones', visible: false }
]);

// Referencias para Toolbar
const dt = ref();
const toolbarRef = ref();
const filters = ref({
    global: { value: null, matchMode: 'contains' }
});

useResponsiveDataTable(dt);

// Opciones de Estado de Máquina (coincide con el backend)
const estadosMaquina = [
    { label: 'Operativa', value: 'operativa' },
    { label: 'Dañada pero Operativa', value: 'dañada_operativa' },
    { label: 'Dañada', value: 'dañada' },
    { label: 'En Observación', value: 'observacion' }
];

// Computed Properties
const casinoId = computed(() => usuario.value?.casino || null);

// Permisos de creación: pueden agregar nuevos mantenimientos
const canCreate = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO']));

// Permisos de edición y eliminación: solo estos roles pueden modificar o eliminar
const canEditOrDelete = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS']));

onMounted(async () => {
    usuario.value = getUser();
    if (casinoId.value) {
        await cargarMantenimientos();
    } else {
        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No tiene un casino asignado para ver mantenimientos.', life: 3000 });
    }
});

const cargarMantenimientos = async () => {
    if (!casinoId.value) return;
    
    loading.value = true;
    try {
        // Filtramos por el casino del usuario
        const response = await api.get('mantenimientos-preventivos/', {
            params: { casino: casinoId.value }
        });
        mantenimientos.value = response.data.results || response.data;
    } catch (error) {

        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudieron cargar los mantenimientos', life: 3000 });
    } finally {
        loading.value = false;
    }
};

const buscarMaquinas = async (event) => {
    if (!casinoId.value) return;
    
    try {
        const query = event.query;
        const response = await api.get('maquinas/', {
            params: {
                casino: casinoId.value, // Filtramos máquinas por el casino del usuario
                search: query,
                page_size: 20
            }
        });
        
        const resultados = response.data.results || response.data;
        filteredMaquinas.value = resultados.map(m => ({
            id: m.id,
            label: `${m.uid_sala} - ${m.numero_serie || 'Sin Serie'} (${m.modelo_nombre || 'Sin Modelo'})`,
            uid: m.uid_sala,
            modelo: m.modelo_nombre
        }));
    } catch (error) {

    }
};

const openNew = () => {
    mantenimiento.value = {
        estado_final_maquina: 'operativa',
        fecha_mantenimiento: new Date() // Bloqueada a hoy
    };
    submitted.value = false;
    mantenimientoDialog.value = true;
};

const hideDialog = () => {
    mantenimientoDialog.value = false;
    submitted.value = false;
};

const saveMantenimiento = async () => {
    submitted.value = true;

    if (!mantenimiento.value.maquina || !mantenimiento.value.fecha_mantenimiento) {
        return;
    }

    loading.value = true;
    try {
        const payload = {
            maquina: maintenanceMachineId(mantenimiento.value.maquina),
            tecnico_responsable: usuario.value.id, // ID del usuario logueado
            fecha_mantenimiento: formatDateForApi(mantenimiento.value.fecha_mantenimiento),
            estado_final_maquina: mantenimiento.value.estado_final_maquina,
            observaciones: mantenimiento.value.observaciones || ''
        };

        if (mantenimiento.value.id) {
            await api.put(`mantenimientos-preventivos/${mantenimiento.value.id}/`, payload);
            toast.add({ severity: 'success', summary: 'Éxito', detail: 'Mantenimiento actualizado', life: 3000 });
        } else {
            const resNuevo = await api.post('mantenimientos-preventivos/', payload);
            toast.add({ severity: 'success', summary: 'Éxito', detail: 'Mantenimiento creado', life: 3000 });
            mostrarToastPuntos(toast, resNuevo.data?.puntos_nexus);
        }

        mantenimientoDialog.value = false;
        mantenimiento.value = {};
        await cargarMantenimientos();
    } catch (error) {

        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'Error al guardar el mantenimiento', life: 3000 });
    } finally {
        loading.value = false;
    }
};

const editMantenimiento = (item) => {
    mantenimiento.value = { 
        ...item,
        fecha_mantenimiento: item.fecha_mantenimiento ? new Date(item.fecha_mantenimiento) : new Date()
    };
    
    // Reconstruir objeto máquina para el autocomplete si viene solo el ID
    if (item.maquina) {
        mantenimiento.value.maquina = {
            id: item.maquina,
            label: `${item.maquina_uid}`,
            uid: item.maquina_uid
        };
    }

    mantenimientoDialog.value = true;
};

const confirmDeleteMantenimiento = (item) => {
    mantenimiento.value = item;
    deleteDialog.value = true;
};

const deleteMantenimiento = async () => {
    loading.value = true;
    try {
        await api.delete(`mantenimientos-preventivos/${mantenimiento.value.id}/`);
        toast.add({ severity: 'success', summary: 'Éxito', detail: 'Mantenimiento eliminado', life: 3000 });
        deleteDialog.value = false;
        mantenimiento.value = {};
        await cargarMantenimientos();
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudo eliminar el registro', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// Helpers
const maintenanceMachineId = (maquinaObj) => {
    return maquinaObj?.id || maquinaObj;
};

const formatDateForApi = (date) => {
    if (!date) return null;
    return date.toISOString().split('T')[0];
};

const getEstadoSeverity = (estado) => {
    switch (estado) {
        case 'operativa': return 'success';
        case 'dañada_operativa': return 'warn';
        case 'dañada': return 'danger';
        case 'observacion': return 'info';
        default: return 'secondary';
    }
};

// Sincronizar búsqueda del toolbar
watch(() => toolbarRef.value?.busquedaGlobal, (val) => {
    if (filters.value.global) filters.value.global.value = val;
});
</script>

<template>
    <div class="grid grid-cols-12 gap-8">
        <div class="col-span-12">
            <div class="card">
                <DataTableToolbar
                    ref="toolbarRef"
                    :dt="dt"
                    :datos="mantenimientos"
                    titulo-reporte="Mantenimientos Preventivos"
                    nombre-archivo="mantenimientos_preventivos"
                    :columnas="columnas"
                    @refrescar="cargarMantenimientos"
                    v-model:columnas-seleccionadas="columnas"
                >
                    <template #acciones-extra>
                        <Button 
                            v-if="canCreate"
                            label="Nuevo" 
                            icon="pi pi-plus" 
                            severity="primary" 
                            class="mr-2" 
                            @click="openNew" 
                        />
                    </template>
                </DataTableToolbar>

                <DataTable
                    ref="dt"
                    :value="mantenimientos"
                    :loading="loading"
                    v-model:filters="filters"
                    dataKey="id"
                    :paginator="true"
                    :rows="10"
                    :rowsPerPageOptions="[5, 10, 25]"
                    paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
                    currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} registros"
                    :globalFilterFields="['maquina_uid', 'tecnico_nombre', 'observaciones']"
                    stripedRows
                    showGridlines
                    class="datatable-mobile"
                >
                    <template #empty>No se encontraron mantenimientos.</template>

                    <Column field="maquina_uid" header="Máquina (UID)" sortable style="min-width: 10rem">
                        <template #body="slotProps">
                            <span class="font-bold">{{ slotProps.data.maquina_uid }}</span>
                        </template>
                    </Column>

                    <Column field="fecha_mantenimiento" header="Fecha Mantenimiento" sortable style="min-width: 12rem">
                        <template #body="slotProps">
                            {{ new Date(slotProps.data.fecha_mantenimiento).toLocaleDateString() }}
                        </template>
                    </Column>

                    <Column field="estado_final_maquina" header="Estado Resultante" sortable style="min-width: 12rem">
                        <template #body="slotProps">
                            <Tag :value="slotProps.data.estado_final_maquina" :severity="getEstadoSeverity(slotProps.data.estado_final_maquina)" />
                        </template>
                    </Column>

                    <Column field="tecnico_nombre" header="Técnico Responsable" sortable style="min-width: 10rem"></Column>

                    <Column header="Acciones" :exportable="false" style="min-width: 8rem" v-if="canEditOrDelete">
                        <template #body="slotProps">
                            <Button icon="pi pi-pencil" outlined rounded severity="success" class="mr-2" @click="editMantenimiento(slotProps.data)" />
                            <Button icon="pi pi-trash" outlined rounded severity="danger" @click="confirmDeleteMantenimiento(slotProps.data)" />
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>

        <!-- Dialog de Creación/Edición -->
        <Dialog v-model:visible="mantenimientoDialog" :style="{ width: '550px' }" header="Detalles de Mantenimiento" :modal="true" class="p-fluid">
            <div class="flex flex-col gap-4">
                <!-- Selección de Máquina -->
                <div class="flex flex-col gap-2">
                    <label for="maquina" class="font-bold">Máquina</label>
                    <AutoComplete
                        id="maquina"
                        v-model="mantenimiento.maquina"
                        :suggestions="filteredMaquinas"
                        @complete="buscarMaquinas"
                        optionLabel="label"
                        placeholder="Buscar por UID o Serie..."
                        dropdown
                        :disabled="!!mantenimiento.id" 
                        :invalid="submitted && !mantenimiento.maquina"
                    />
                    <small class="text-red-500" v-if="submitted && !mantenimiento.maquina">La máquina es requerida.</small>
                </div>

                <!-- Estado y Fecha -->
                <div class="grid grid-cols-2 gap-4">
                    <div class="flex flex-col gap-2">
                        <label for="estado" class="font-bold">Estado Resultante</label>
                        <Select 
                            id="estado" 
                            v-model="mantenimiento.estado_final_maquina" 
                            :options="estadosMaquina" 
                            optionLabel="label" 
                            optionValue="value" 
                            placeholder="Seleccione Estado"
                        />
                    </div>
                    <div class="flex flex-col gap-2">
                        <label for="fecha_mant" class="font-bold">Fecha de Mantenimiento</label>
                        <DatePicker 
                            id="fecha_mant" 
                            v-model="mantenimiento.fecha_mantenimiento" 
                            showIcon 
                            dateFormat="dd/mm/yy"
                            :maxDate="new Date()"
                            :invalid="submitted && !mantenimiento.fecha_mantenimiento"
                            disabled
                        />
                        <small class="text-xs text-surface-500">El mantenimiento se registra con la fecha actual</small>
                    </div>
                </div>

                <!-- Observaciones -->
                <div class="flex flex-col gap-2">
                    <label for="observaciones" class="font-bold">Observaciones Técnicas</label>
                    <Textarea id="observaciones" v-model="mantenimiento.observaciones" rows="4" cols="20" placeholder="Notas adicionales sobre el mantenimiento realizado..." />
                </div>
            </div>

            <template #footer>
                <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                <Button label="Guardar" icon="pi pi-check" @click="saveMantenimiento" :loading="loading" />
            </template>
        </Dialog>

        <!-- Dialog de Confirmación de Eliminación -->
        <Dialog v-model:visible="deleteDialog" :style="{ width: '450px' }" header="Confirmar" :modal="true">
            <div class="flex items-center gap-4">
                <i class="pi pi-exclamation-triangle !text-3xl text-red-500" />
                <span v-if="mantenimiento">
                    ¿Está seguro de eliminar el mantenimiento de la máquina <b>{{ mantenimiento.maquina_uid }}</b>?
                </span>
            </div>
            <template #footer>
                <Button label="No" icon="pi pi-times" text @click="deleteDialog = false" />
                <Button label="Sí" icon="pi pi-check" severity="danger" @click="deleteMantenimiento" :loading="loading" />
            </template>
        </Dialog>
    </div>
</template>