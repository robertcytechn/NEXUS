<script setup>
import { ref, onMounted, watch } from 'vue';
import api, { getUser } from '@/service/api';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';
import TicketFormDialog from '@/components/tickets/TicketFormDialog.vue';
import TicketDetalleDialog from '@/components/tickets/TicketDetalleDialog.vue';
import { parseServerError } from '@/utils/parseServerError';


const tickets = ref([]);
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

const ticketDialog = ref(false);
const ticket = ref({});
const submitted = ref(false);

// Para el historial de bitácora
const historialDialog = ref(false);
const ticketSeleccionado = ref(null);
const historialBitacora = ref([]);
const loadingHistorial = ref(false);

// --- Catálogos Estáticos (Basados en el Modelo Django) ---
const categorias = ref([
    { label: 'Hardware', value: 'hardware' },
    { label: 'Periféricos', value: 'perifericos' },
    { label: 'Software', value: 'software' },
    { label: 'Red / Comunicación', value: 'red' },
    { label: 'Otros', value: 'otros' }
]);

const prioridades = ref([
    { label: 'Baja', value: 'baja' },
    { label: 'Media', value: 'media' },
    { label: 'Alta', value: 'alta' },
    { label: 'Crítica', value: 'critica' },
    { label: 'Emergencia', value: 'emergencia' },
    { label: 'Sin Prioridad', value: 'sin_prioridad' }
]);

const estadosCiclo = ref([
    { label: 'Abierto', value: 'abierto' },
    { label: 'En Proceso', value: 'proceso' },
    { label: 'En Espera', value: 'espera' },
    { label: 'Cerrado', value: 'cerrado' },
    { label: 'Reabierto', value: 'reabierto' }
]);

// --- Sincronización del Buscador ---
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// --- Columnas Configurables ---
const columnas = ref([
    { field: 'folio', label: 'Folio', visible: true },
    { field: 'maquina_uid', label: 'Máquina', visible: true },
    { field: 'categoria', label: 'Categoría', visible: true },
    { field: 'subcategoria', label: 'Subcategoría', visible: false },
    { field: 'prioridad', label: 'Prioridad', visible: true },
    { field: 'estado_ciclo', label: 'Estado', visible: true },
    { field: 'reportante_nombre', label: 'Reportante', visible: true },
    { field: 'reportante_rol', label: 'Rol Reportante', visible: true },
    { field: 'creado_en', label: 'Fecha Creación', visible: true }
]);

// --- Carga de Datos ---
const cargarDatos = async () => {
    loading.value = true;
    try {
        const [resTickets, resMaquinas] = await Promise.all([
            api.get('tickets/'),
            api.get('maquinas/lista/')
        ]);

        tickets.value = resTickets.data;
        maquinas.value = resMaquinas.data;

    } catch (error) {

        toast.add({ severity: 'error', summary: 'Error', detail: parseServerError(error, 'No se pudieron cargar los datos'), life: 5000 });
    } finally {
        loading.value = false;
    }
};

// --- Helpers de Formato y Estilo ---
const formatearFecha = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleString('es-MX', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit'
    });
};

const getPrioridadSeverity = (prioridad) => {
    switch (prioridad) {
        case 'baja': return 'success';
        case 'media': return 'info';
        case 'alta': return 'warn';
        case 'critica': return 'danger';
        case 'emergencia': return 'danger'; // O un color más intenso si se personaliza
        default: return 'secondary';
    }
};

const getEstadoSeverity = (estado) => {
    switch (estado) {
        case 'abierto': return 'danger';
        case 'proceso': return 'warn';
        case 'espera': return 'info';
        case 'cerrado': return 'success';
        case 'reabierto': return 'secondary';
        default: return 'contrast';
    }
};

const esColumnaVisible = (field) => {
    const columna = columnas.value.find(c => c.field === field);
    return columna ? columna.visible : true;
};

// --- CRUD Actions ---
const openNew = () => {
    ticket.value = {
        prioridad: 'media',
        estado_ciclo: 'abierto',
        esta_activo: true,
        // El reportante idealmente se asigna en el backend con el usuario logueado
    };

    submitted.value = false;
    ticketDialog.value = true;
};

const editarTicket = (data) => {
    ticket.value = { ...data };

    ticketDialog.value = true;
};

const hideDialog = () => {
    ticketDialog.value = false;
    submitted.value = false;
    ticket.value = {};
};

const saveTicket = () => {
    // La logica de guardado y update de fallas la maneja TicketFormDialog.
    cargarDatos();
};

const toggleActivarTicket = (data) => {
    const accion = data.esta_activo ? 'desactivar' : 'activar';

    confirm.require({
        message: `¿Estás seguro de que deseas ${accion} el ticket ${data.folio}?`,
        header: 'Confirmar Acción',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: { label: 'Cancelar', severity: 'secondary', outlined: true },
        acceptProps: { label: 'Confirmar', severity: data.esta_activo ? 'danger' : 'success' },
        accept: async () => {
            loading.value = true;
            try {
                await api.patch(`tickets/${data.id}/switch-estado/`, {});
                toast.add({ severity: 'success', summary: 'Éxito', detail: `Ticket ${accion === 'activar' ? 'activado' : 'desactivado'} correctamente`, life: 3000 });
                cargarDatos();
            } catch (error) {

                toast.add({ severity: 'error', summary: 'Error', detail: parseServerError(error, `No se pudo ${accion} el ticket`), life: 5000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

const verHistorial = (ticketData) => {
    ticketSeleccionado.value = ticketData;
    historialDialog.value = true;
};

const formatearFechaCompleta = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleString('es-MX', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

const getResultadoSeverity = (resultado) => {
    const severities = {
        'exitosa': 'success',
        'parcial': 'warn',
        'fallida': 'danger',
        'espera_refaccion': 'info'
    };
    return severities[resultado] || 'info';
};

const getMarkerClass = (resultado) => {
    const classes = {
        'exitosa': 'bg-green-500 text-white',
        'parcial': 'bg-yellow-500 text-white',
        'fallida': 'bg-red-500 text-white',
        'espera_refaccion': 'bg-blue-500 text-white'
    };
    return classes[resultado] || 'bg-surface-300 text-surface-700';
};

const getMarkerIcon = (tipo) => {
    const icons = {
        'diagnostico': 'pi pi-search',
        'correctiva': 'pi pi-wrench',
        'ajuste': 'pi pi-sliders-h',
        'instalacion': 'pi pi-box',
        'actualización': 'pi pi-cloud-download'
    };
    return icons[tipo] || 'pi pi-circle';
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

            <!-- Toolbar -->
            <DataTableToolbar ref="toolbarRef" :dt="dt" :datos="tickets" titulo-reporte="Gestión de Tickets de Soporte"
                nombre-archivo="tickets" :columnas="columnas" :mostrar-exportacion="true" :mostrar-imprimir="true"
                :mostrar-refrescar="true" :mostrar-selector-columnas="true" :mostrar-buscador="true"
                @refrescar="cargarDatos" v-model:columnas-seleccionadas="columnas">
                <template #acciones-extra>
                    <Button icon="pi pi-plus" label="Nuevo Ticket" rounded severity="primary" @click="openNew" />
                </template>
            </DataTableToolbar>

            <!-- DataTable -->
            <DataTable ref="dt" :value="tickets" :loading="loading" v-model:filters="filtros"
                :globalFilterFields="['folio', 'maquina_uid', 'categoria', 'subcategoria', 'descripcion_problema', 'reportante_nombre', 'reportante_rol']"
                paginator :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]" dataKey="id" filterDisplay="menu"
                showGridlines stripedRows class="datatable-mobile">
                <template #empty>
                    <div class="text-center p-4">No se encontraron tickets registrados.</div>
                </template>

                <template #loading>Cargando tickets...</template>

                <Column v-if="esColumnaVisible('folio')" field="folio" header="Folio" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <span
                            class="font-bold font-mono text-primary-600 dark:text-primary-400 cursor-pointer hover:underline"
                            @click="verHistorial(data)" v-tooltip.top="'Ver historial de bitácora'">
                            {{ data.folio || 'Pendiente' }}
                        </span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('maquina_uid')" field="maquina_uid" header="Máquina" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <!-- Ajustar campo según lo que devuelva el backend (uid_sala, numero_serie, etc) -->
                        {{ data.maquina_uid || data.maquina }}
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('categoria')" field="categoria" header="Categoría" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <span class="capitalize">{{ data.categoria }}</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('subcategoria')" field="subcategoria" header="Subcategoría" sortable
                    style="min-width: 12rem" />

                <Column v-if="esColumnaVisible('prioridad')" field="prioridad" header="Prioridad" sortable
                    style="min-width: 8rem">
                    <template #body="{ data }">
                        <Tag :value="data.prioridad.toUpperCase()" :severity="getPrioridadSeverity(data.prioridad)" />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('estado_ciclo')" field="estado_ciclo" header="Estado" sortable
                    style="min-width: 8rem">
                    <template #body="{ data }">
                        <Tag :value="data.estado_ciclo.toUpperCase()"
                            :severity="getEstadoSeverity(data.estado_ciclo)" />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('reportante_nombre')" field="reportante_nombre" header="Reportante"
                    sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2" v-if="data.reportante">
                            <i class="pi pi-user-edit text-primary"></i>
                            <div class="flex flex-col">
                                <span class="font-semibold">{{ data.reportante_nombre }} {{ data.reportante_apellidos
                                }}</span>
                            </div>
                        </div>
                        <span v-else class="text-surface-400 italic">No especificado</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('reportante_rol')" field="reportante_rol" header="Rol" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <div v-if="data.reportante_rol" class="flex items-center gap-2">
                            <i class="pi pi-id-card text-surface-500"></i>
                            <span class="text-sm">{{ data.reportante_rol }}</span>
                        </div>
                        <span v-else class="text-surface-400 italic text-sm">-</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('creado_en')" field="creado_en" header="Fecha Creación" sortable
                    style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="text-sm">{{ formatearFecha(data.creado_en) }}</div>
                    </template>
                </Column>

                <Column header="Acciones" :exportable="false" style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button icon="pi pi-pencil" size="small" severity="info" rounded outlined
                                @click="editarTicket(data)" v-tooltip.top="'Editar / Gestionar'" />
                            <Button :icon="data.esta_activo ? 'pi pi-ban' : 'pi pi-check-circle'" size="small"
                                :severity="data.esta_activo ? 'warning' : 'success'" rounded outlined
                                @click="toggleActivarTicket(data)"
                                v-tooltip.top="data.esta_activo ? 'Archivar' : 'Restaurar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <!-- Dialogos Inteligentes -->
            <TicketFormDialog v-model:visible="ticketDialog" :ticketProp="ticket" @saved="cargarDatos" />

            <TicketDetalleDialog v-model:visible="historialDialog" :ticketProp="ticketSeleccionado" />
        </div>
    </div>
</template>
