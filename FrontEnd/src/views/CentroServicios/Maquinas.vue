<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api, { getUser } from '@/service/api';
import { crearTicket, TIPOS_TICKET } from '@/service/ticketService';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

// --- COMPONENTES INTELIGENTES ---
import MaquinaFormDialog from '@/components/maquinas/MaquinaFormDialog.vue';
import MaquinaDetalleDialog from '@/components/maquinas/MaquinaDetalleDialog.vue';

const maquinas = ref([]);
const estadisticas = ref({ total: 0, danadas: 0, porcentaje_danadas: 0 });
const loading = ref(false);
const dt = ref();
const toolbarRef = ref();

useResponsiveDataTable(dt);
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();
const confirm = useConfirm();

// --- ESTADOS DE MODALES ---
const formDialogVisible = ref(false);
const maquinaSeleccionadaId = ref(null);
const detalleDialogVisible = ref(false);
const maquinaDetalle = ref(null);

// Obtener usuario actual y su rol
const usuario = computed(() => getUser());
const rolUsuario = computed(() => usuario.value?.rol_nombre || '');
const casinoUsuario = computed(() => usuario.value?.casino || null);

// Permisos basados en rol
const permisos = computed(() => ({
    puedeExportar: ['SUP SISTEMAS', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeAgregar: ['SUP SISTEMAS', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeEditar: ['SUP SISTEMAS', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeDesactivar: ['SUP SISTEMAS', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeVerGrafica: ['SUP SISTEMAS', 'ADMINISTRADOR'].includes(rolUsuario.value)
}));

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
    { field: 'estado_actual', label: 'Estado', visible: true }
]);

// Cargar Datos Iniciales
// Cargar Datos Iniciales (Solo lista, los Choices los carga el Componente Inteligente Form)
const cargarDatos = async () => {
    loading.value = true;
    try {
        if (!casinoUsuario.value) {
            toast.add({ severity: 'error', summary: 'Error', detail: 'Usuario sin casino asignado. Contacte al administrador.', life: 5000 });
            return;
        }

        const resMaquinas = await api.get(`maquinas/lista-por-casino/${casinoUsuario.value}/`);
        maquinas.value = resMaquinas.data.maquinas;
        estadisticas.value = resMaquinas.data.estadisticas;
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || 'No se pudieron cargar los datos necesarios', life: 3000 });
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

// CRUD VIA COMPONENTES INTELIGENTES
const openNew = () => {
    maquinaSeleccionadaId.value = null;
    formDialogVisible.value = true;
};

const editarMaquina = (data) => {
    maquinaSeleccionadaId.value = data.id;
    formDialogVisible.value = true;
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
                toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.error || error?.response?.data?.detail || `No se pudo ${accion} la máquina`, life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

// Función para abrir modal inteligente de detalles y cargar historial
const verDetalleMaquina = async (maquinaRow) => {
    try {
        loading.value = true;
        const res = await api.get(`maquinas/${maquinaRow.id}/`);
        maquinaDetalle.value = res.data;
        detalleDialogVisible.value = true;
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar el detalle completo de la máquina.', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// Función para levantar incidencia (basada en botón de pánico)
const levantarIncidencia = async () => {
    if (!maquinaDetalle.value) return;

    // Validación 1: Verificar que existe información del casino
    if (!casinoUsuario.value) {
        toast.add({
            severity: 'error',
            summary: 'Casino no identificado',
            detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se encontró información del casino. Por favor cierre sesión y vuelva a iniciar sesión.',
            life: 5000
        });
        return;
    }

    // Validación 2: Verificar información del usuario
    if (!usuario.value || !usuario.value.id) {
        toast.add({
            severity: 'error',
            summary: 'Usuario no autenticado',
            detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudo obtener su información de usuario. Por favor inicie sesión nuevamente.',
            life: 5000
        });
        return;
    }

    loading.value = true;

    try {
        const maquina = maquinaDetalle.value;

        // Usar el servicio global para crear el ticket
        const resultado = await crearTicket({
            maquinaId: maquina.id,
            maquinaUid: maquina.uid_sala,
            ...TIPOS_TICKET.INCIDENCIA_RAPIDA,
            reportanteId: usuario.value.id,
            estadoMaquina: 'DAÑADA',
            incrementarContador: true,
            actualizarEstado: true
        });

        // Manejar el resultado
        if (!resultado.exito) {
            toast.add({
                severity: 'error',
                summary: resultado.error,
                detail: resultado.detalle,
                life: 6000
            });
            loading.value = false;
            return;
        }

        // Mostrar éxito
        const mensajeContador = resultado.contadorFallas
            ? ` | Contador de fallas: ${resultado.contadorFallas}`
            : '';

        toast.add({
            severity: 'success',
            summary: '✓ Incidencia Creada',
            detail: `Ticket #${resultado.ticket.folio || resultado.ticket.id} creado para la máquina "${maquina.uid_sala}"${mensajeContador}.`,
            life: 6000
        });

        if (resultado.advertencia) {
            toast.add({
                severity: 'warn',
                summary: 'Advertencia',
                detail: resultado.advertencia,
                life: 5000
            });
        }

        detalleDialogVisible.value = false;
        cargarDatos();

    } catch (error) {


        const mensajesError = {
            'ECONNABORTED': 'No se pudo conectar con el servidor.',
            'ERR_NETWORK': 'Error de conexión. Verifique su conexión a internet.',
            400: error.response?.data?.detail || 'Los datos enviados no son válidos',
            401: 'Su sesión ha expirado. Por favor inicie sesión nuevamente.',
            403: 'No tiene permisos para crear tickets.',
            500: 'Error del servidor. Intente nuevamente más tarde.'
        };

        const status = error.response?.status;
        const detalle = mensajesError[error.code] || mensajesError[status]
            || error.response?.data?.error
            || 'Ocurrió un error inesperado al crear el ticket.';

        toast.add({
            severity: 'error',
            summary: 'Error al crear ticket',
            detail: detalle,
            life: 6000
        });
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    cargarDatos();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <!-- Gráfica de Máquinas Dañadas (solo para SUP SISTEMAS y ADMINISTRADOR) -->
        <div v-if="permisos.puedeVerGrafica" class="card">
            <div class="font-bold text-xl mb-6 text-surface-900 dark:text-surface-0">
                Estado de Máquinas - {{ usuario?.casino_nombre }}
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Total de
                                Máquinas</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{ estadisticas.total
                            }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-lg"
                            style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-desktop text-blue-500 dark:text-blue-400 text-2xl"></i>
                        </div>
                    </div>
                </div>

                <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Máquinas
                                Dañadas</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{
                                estadisticas.danadas }}</div>
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
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Porcentaje
                                Dañadas</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{
                                estadisticas.porcentaje_danadas }}%</div>
                        </div>
                        <div class="flex items-center justify-center bg-orange-100 dark:bg-orange-400/10 rounded-lg"
                            style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-chart-pie text-orange-500 dark:text-orange-400 text-2xl"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <Toast />
            <ConfirmDialog />

            <DataTableToolbar ref="toolbarRef" :dt="dt" :datos="maquinas" titulo-reporte="Inventario de Máquinas"
                nombre-archivo="maquinas" :columnas="columnas" @refrescar="cargarDatos"
                v-model:columnas-seleccionadas="columnas" :mostrar-exportacion="permisos.puedeExportar"
                :mostrar-imprimir="permisos.puedeExportar">
                <template #acciones-extra>
                    <Button v-if="permisos.puedeAgregar" icon="pi pi-plus" label="Nueva Máquina" rounded
                        severity="primary" @click="openNew" />
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
                    <template #body="{ data }">
                        <span class="font-bold text-primary-500 cursor-pointer hover:text-primary-700 hover:underline"
                            @click="verDetalleMaquina(data)">
                            {{ data.uid_sala }}
                        </span>
                    </template>
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

                <Column v-if="permisos.puedeEditar || permisos.puedeDesactivar || true" header="Acciones"
                    :exportable="false" style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button icon="pi pi-eye" size="small" severity="secondary" rounded outlined
                                @click="verDetalleMaquina(data)" v-tooltip.top="'Ver Detalle Completo e Historial'" />
                            <Button v-if="permisos.puedeEditar" icon="pi pi-pencil" size="small" severity="info" rounded
                                outlined @click="editarMaquina(data)" v-tooltip.top="'Editar'" />
                            <Button v-if="permisos.puedeDesactivar" icon="pi pi-ban" size="small" severity="warning"
                                rounded outlined @click="toggleActivarMaquina(data)" v-tooltip.top="'Desactivar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <!-- COMPONENTES INTELIGENTES INYECTADOS -->
            <MaquinaFormDialog v-model:visible="formDialogVisible" :maquinaId="maquinaSeleccionadaId"
                @saved="onMaquinaGuardada" />

            <MaquinaDetalleDialog v-model:visible="detalleDialogVisible" :maquina="maquinaDetalle"
                @levantar-incidencia="levantarIncidencia" />
        </div>
    </div>
</template>
