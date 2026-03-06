<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api, { getUser } from '@/service/api';
import { crearBitacoraTecnica } from '@/service/ticketService';
import { mostrarToastPuntos } from '@/service/gamificacionUtils';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';
import TicketFormDialog from '@/components/tickets/TicketFormDialog.vue';
import TicketDetalleDialog from '@/components/tickets/TicketDetalleDialog.vue';
import { parseServerError } from '@/utils/parseServerError';

const tickets = ref([]);
const maquinas = ref([]);
const tecnicos = ref([]);
const estadisticas = ref({ total: 0, criticos: 0, sin_tecnico: 0 });
const loading = ref(false);
const dt = ref();
const toolbarRef = ref();

useResponsiveDataTable(dt);
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();
const confirm = useConfirm();

// Estado para el modal de formulario de ticket
const ticketFormDialogVisible = ref(false);
const ticketToEdit = ref({});

// Estado para el modal de detalle de ticket
const historialDialog = ref(false);
const ticketSeleccionado = ref(null);


// Obtener usuario actual y su rol
const usuario = computed(() => getUser());
const rolUsuario = computed(() => usuario.value?.rol_nombre || '');
const casinoUsuario = computed(() => usuario.value?.casino || null);

// Permisos basados en rol
const permisos = computed(() => ({
    puedeExportar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeAgregar: ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA'].includes(rolUsuario.value),
    puedeEditar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeDesactivar: ['SUP SISTEMAS', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeAgregarBitacora: ['SUP SISTEMAS', 'TECNICO', 'ADMINISTRADOR'].includes(rolUsuario.value)
}));

// Catálogos
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
    { label: 'Emergencia', value: 'emergencia' }
]);

const estadosCiclo = ref([
    { label: 'Abierto', value: 'abierto' },
    { label: 'En Proceso', value: 'proceso' },
    { label: 'En Espera', value: 'espera' },
    { label: 'Reabierto', value: 'reabierto' }
]);

const tiposIntervencion = ref([
    { label: 'Diagnóstico', value: 'diagnostico' },
    { label: 'Reparación Correctiva', value: 'correctiva' },
    { label: 'Ajuste / Calibración', value: 'ajuste' },
    { label: 'Instalación / Movimiento', value: 'instalacion' },
    { label: 'Actualización Software', value: 'actualización' }
]);

const resultadosIntervencion = ref([
    { label: 'Reparación Exitosa', value: 'exitosa' },
    { label: 'Reparación Parcial', value: 'parcial' },
    { label: 'Prueba Fallida', value: 'fallida' },
    { label: 'En espera de Refacción', value: 'espera_refaccion' }
]);

const estadosMaquina = ref([
    { label: 'Operativa', value: 'operativa' },
    { label: 'Dañada pero Operativa', value: 'dañada_operativa' },
    { label: 'Dañada', value: 'dañada' },
    { label: 'En Mantenimiento', value: 'mantenimiento' }
]);

// Sincronizar buscador
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Columnas
const columnas = ref([
    { field: 'folio', label: 'Folio', visible: true },
    { field: 'maquina_uid', label: 'Máquina', visible: true },
    { field: 'categoria', label: 'Categoría', visible: true },
    { field: 'prioridad', label: 'Prioridad', visible: true },
    { field: 'estado_ciclo', label: 'Estado', visible: true },
    { field: 'dias_abierto', label: 'Antigüedad', visible: true },
    { field: 'total_intervenciones', label: 'Intervenciones', visible: true },
    { field: 'tecnico_asignado_nombre', label: 'Técnico', visible: true }
]);

// Cargar Datos
const cargarTickets = async () => {
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

        const res = await api.get(`tickets/lista-por-casino/${casinoUsuario.value}/`);
        let listaTickets = res.data.tickets;
        let stats = res.data.estadisticas;

        // Filtro para ENCARGADO AREA: Solo ver sus propios tickets
        if (rolUsuario.value === 'ENCARGADO AREA') {
            const userId = usuario.value?.id;
            if (userId) {
                listaTickets = listaTickets.filter(t => {
                    const reportanteId = typeof t.reportante === 'object' ? t.reportante?.id : t.reportante;
                    return reportanteId === userId;
                });

                // Recalcular estadísticas para la vista filtrada
                stats = {
                    total: listaTickets.length,
                    criticos: listaTickets.filter(t => ['critica', 'emergencia'].includes(t.prioridad)).length,
                    sin_tecnico: listaTickets.filter(t => !t.tecnico_asignado).length
                };
            }
        }

        tickets.value = listaTickets;
        estadisticas.value = stats;

        // Cargar datos adicionales si puede agregar/editar
        if (permisos.value.puedeAgregar || permisos.value.puedeEditar) {
            const [resMaquinas, resTecnicos] = await Promise.all([
                api.get(`maquinas/lista-por-casino/${casinoUsuario.value}/`),
                api.get('usuarios/')
            ]);

            maquinas.value = resMaquinas.data.maquinas;
            // Filtrar solo técnicos activos
            tecnicos.value = resTecnicos.data.filter(u =>
                u.esta_activo && ['TECNICO', 'SUP SISTEMAS'].includes(u.rol_nombre)
            );
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: parseServerError(error, 'No se pudieron cargar los tickets'), life: 5000 });
    } finally {
        loading.value = false;
    }
};

// Helpers
const esColumnaVisible = (field) => {
    const col = columnas.value.find(c => c.field === field);
    return col ? col.visible : true;
};

const getPrioridadSeverity = (prioridad) => {
    switch (prioridad) {
        case 'baja': return 'success';
        case 'media': return 'info';
        case 'alta': return 'warn';
        case 'critica': return 'danger';
        case 'emergencia': return 'danger';
        default: return 'secondary';
    }
};

const getEstadoSeverity = (estado) => {
    switch (estado) {
        case 'abierto': return 'danger';
        case 'proceso': return 'info';
        case 'espera': return 'warn';
        case 'reabierto': return 'secondary';
        default: return 'contrast';
    }
};

// Semáforo de antigüedad
const getDiasClass = (dias) => {
    if (dias <= 3) return 'bg-green-100 dark:bg-green-950 text-green-700 dark:text-green-400 border-green-300 dark:border-green-800';
    if (dias <= 8) return 'bg-orange-100 dark:bg-orange-950 text-orange-700 dark:text-orange-400 border-orange-300 dark:border-orange-800';
    if (dias <= 15) return 'bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-400 border-red-300 dark:border-red-800';
    return 'bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-400 border-purple-300 dark:border-purple-800';
};

const getDiasIcon = (dias) => {
    if (dias <= 3) return 'pi-check-circle';
    if (dias <= 8) return 'pi-exclamation-triangle';
    if (dias <= 15) return 'pi-times-circle';
    return 'pi-ban';
};

const getDiasLabel = (dias) => {
    if (dias <= 3) return 'Reciente';
    if (dias <= 8) return 'Atención';
    if (dias <= 15) return 'Crítico';
    return 'Urgente';
};

// CRUD
const openNew = () => {
    ticketToEdit.value = {
        prioridad: 'media',
        estado_ciclo: 'abierto',
        esta_activo: true,
        reportante: usuario.value?.id
    };
    ticketFormDialogVisible.value = true;
};

const editarTicket = (data) => {
    ticketToEdit.value = { ...data };
    ticketFormDialogVisible.value = true;
};

const saveTicket = () => {
    // La logica de guardado y update de fallas la maneja TicketFormDialog.
    cargarTickets();
};

const desactivarTicket = (data) => {
    confirm.require({
        message: `¿Estás seguro de que deseas desactivar el ticket ${data.folio}?`,
        header: 'Confirmar Acción',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: { label: 'Cancelar', severity: 'secondary', outlined: true },
        acceptProps: { label: 'Desactivar', severity: 'danger' },
        accept: async () => {
            loading.value = true;
            try {
                await api.patch(`tickets/${data.id}/switch-estado/`, {});
                toast.add({ severity: 'success', summary: 'Éxito', detail: 'Ticket desactivado correctamente', life: 3000 });
                cargarTickets();
            } catch (error) {
                toast.add({ severity: 'error', summary: 'Error', detail: parseServerError(error, 'No se pudo desactivar el ticket'), life: 5000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

// Ver detalle con bitácoras
const verHistorial = (ticketData) => {
    ticketSeleccionado.value = ticketData;
    historialDialog.value = true;
};

const formatearFechaCompleta = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleString('es-MX', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
};

onMounted(() => {
    cargarTickets();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <!-- Estadísticas -->
        <div v-if="permisos.puedeExportar" class="card">
            <div class="font-bold text-xl mb-6 text-surface-900 dark:text-surface-0">
                Centro de Tickets - {{ usuario?.casino_nombre }}
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Tickets
                                Abiertos</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{ estadisticas.total
                                }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-lg"
                            style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-ticket text-blue-500 dark:text-blue-400 text-2xl"></i>
                        </div>
                    </div>
                </div>
                <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Críticos</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{
                                estadisticas.criticos }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-red-100 dark:bg-red-400/10 rounded-lg"
                            style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-exclamation-triangle text-red-500 dark:text-red-400 text-2xl"></i>
                        </div>
                    </div>
                </div>
                <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Sin
                                Técnico</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{
                                estadisticas.sin_tecnico }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-orange-100 dark:bg-orange-400/10 rounded-lg"
                            style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-user-minus text-orange-500 dark:text-orange-400 text-2xl"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <TicketFormDialog v-model:visible="ticketFormDialogVisible" :ticketProp="ticketToEdit" @saved="saveTicket" />
        <TicketDetalleDialog v-model:visible="historialDialog" :ticketProp="ticketSeleccionado" @ticket-cerrado="cargarTickets" />

        <div class="card">
            <Toast />
            <ConfirmDialog />

            <DataTableToolbar ref="toolbarRef" :dt="dt" :datos="tickets" titulo-reporte="Tickets Abiertos"
                nombre-archivo="tickets_abiertos" :columnas="columnas" @refrescar="cargarTickets"
                v-model:columnas-seleccionadas="columnas" :mostrar-exportacion="permisos.puedeExportar"
                :mostrar-imprimir="permisos.puedeExportar">
                <template #acciones-extra>
                    <Button v-if="permisos.puedeAgregar" icon="pi pi-plus" label="Nuevo Ticket" rounded
                        severity="primary" @click="openNew" />
                </template>
            </DataTableToolbar>

            <DataTable ref="dt" :value="tickets" :loading="loading" v-model:filters="filtros"
                :globalFilterFields="['folio', 'maquina_uid', 'categoria', 'descripcion_problema', 'tecnico_asignado_nombre']"
                paginator :rows="15" :rowsPerPageOptions="[10, 15, 25, 50]" dataKey="id" showGridlines stripedRows
                class="datatable-mobile">
                <template #empty>
                    <div class="text-center p-4">No hay tickets abiertos en este momento.</div>
                </template>

                <Column v-if="esColumnaVisible('folio')" field="folio" header="Folio" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <span
                            class="font-bold font-mono text-primary-600 dark:text-primary-400 cursor-pointer hover:underline text-base"
                            @click="verHistorial(data)" v-tooltip.top="'Ver detalle completo'">
                            {{ data.folio }}
                        </span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('maquina_uid')" field="maquina_uid" header="Máquina" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-desktop text-surface-400 text-sm"></i>
                            <span class="font-semibold">{{ data.maquina_uid }}</span>
                        </div>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('categoria')" field="categoria" header="Categoría" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <span class="capitalize text-sm">{{ data.categoria }}</span>
                    </template>
                </Column>

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

                <Column v-if="esColumnaVisible('dias_abierto')" field="dias_abierto" header="Antigüedad" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2 px-3 py-2 rounded-lg border-2"
                            :class="getDiasClass(data.dias_abierto)">
                            <i class="pi text-sm" :class="getDiasIcon(data.dias_abierto)"></i>
                            <div class="flex flex-col">
                                <span class="font-bold text-base">{{ data.dias_abierto }}d</span>
                                <span class="text-xs font-semibold">{{ getDiasLabel(data.dias_abierto) }}</span>
                            </div>
                        </div>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('total_intervenciones')" field="total_intervenciones"
                    header="Intervenciones" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2">
                            <Tag :value="String(data.total_intervenciones)"
                                :severity="data.total_intervenciones > 0 ? 'info' : 'secondary'" rounded>
                                <i class="pi pi-wrench mr-1"></i>
                                {{ data.total_intervenciones }}
                            </Tag>
                        </div>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('tecnico_asignado_nombre')" field="tecnico_asignado_nombre"
                    header="Técnico" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div v-if="data.tecnico_asignado_nombre" class="flex items-center gap-2">
                            <i class="pi pi-user text-primary-500 text-sm"></i>
                            <span class="text-sm">{{ data.tecnico_asignado_nombre }}</span>
                        </div>
                        <Tag v-else value="Sin asignar" severity="warn" class="text-xs" />
                    </template>
                </Column>

                <Column v-if="permisos.puedeEditar || permisos.puedeDesactivar" header="Acciones" :exportable="false"
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button v-if="permisos.puedeEditar" icon="pi pi-pencil" size="small" severity="info" rounded
                                outlined @click="editarTicket(data)" v-tooltip.top="'Editar'" />
                            <Button v-if="permisos.puedeDesactivar" icon="pi pi-ban" size="small" severity="warning"
                                rounded outlined @click="desactivarTicket(data)" v-tooltip.top="'Desactivar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>
        </div>
    </div>
</template>

<style scoped>
/* Timeline: ocultar lado vacío, mantener línea con marcadores */
:deep(.p-timeline-event-opposite) {
    display: none !important;
}

:deep(.p-timeline-event-content) {
    width: 100% !important;
    padding-left: 1rem !important;
}
</style>
