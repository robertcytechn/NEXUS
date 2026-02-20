<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api, { getUser } from '@/service/api';
import { crearTicket, TIPOS_TICKET } from '@/service/ticketService';
import { guardarMaquina } from '@/service/maquinaService';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

const maquinas = ref([]);
const casinos = ref([]);
const modelos = ref([]);
const denominaciones = ref([]);
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
const maquinaDialog = ref(false);
const maquina = ref({});
const submitted = ref(false);

// Modal de Detalles
const detalleDialog = ref(false);
const maquinaDetalle = ref(null);
const historialTickets = ref([]);
const loadingDetalle = ref(false);

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

// Opciones de Estado (Hardcoded según modelo Django)
const estados = ref([
    { label: 'Operativa', value: 'OPERATIVA' },
    { label: 'Dañada (Operativa)', value: 'DAÑADA_OPERATIVA' },
    { label: 'Dañada (No Operativa)', value: 'DAÑADA' },
    { label: 'Mantenimiento', value: 'MANTENIMIENTO' },
    { label: 'Observación', value: 'OBSERVACION' },
    { label: 'Pruebas', value: 'PRUEBAS' }
]);

// Choices de ubicación (deben coincidir con el modelo Django)
const pisosChoices = [
    { label: 'Piso 1', value: 'PISO_1' },
    { label: 'Piso 2', value: 'PISO_2' },
    { label: 'Piso 3', value: 'PISO_3' },
    { label: 'Área VIP', value: 'VIP' },
    { label: 'Terraza', value: 'TERRAZA' },
    { label: 'Sótano', value: 'SÓTANO' },
];
const salasChoices = [
    { label: 'Sala A', value: 'SALA_A' },
    { label: 'Sala B', value: 'SALA_B' },
    { label: 'Sala C', value: 'SALA_C' },
    { label: 'Sala D', value: 'SALA_D' },
    { label: 'Sala Principal', value: 'SALA_PRINCIPAL' },
    { label: 'Zona Fumadores', value: 'ZONA_FUMADORES' },
    { label: 'Zona No Fumadores', value: 'ZONA_NO_FUMADORES' },
];

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
const cargarDatos = async () => {
    loading.value = true;
    try {
        // Verificar que el usuario tenga un casino asignado
        if (!casinoUsuario.value) {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: 'Usuario sin casino asignado. Contacte al administrador.',
                life: 5000
            });
            return;
        }

        // Cargar máquinas filtradas por el casino del usuario usando el nuevo endpoint
        const resMaquinas = await api.get(`maquinas/lista-por-casino/${casinoUsuario.value}/`);

        maquinas.value = resMaquinas.data.maquinas;
        estadisticas.value = resMaquinas.data.estadisticas;

        // Solo cargar datos adicionales si el usuario puede agregar/editar
        if (permisos.value.puedeAgregar || permisos.value.puedeEditar) {
            const [resCasinos, resModelos, resProveedores, resDenominaciones] = await Promise.all([
                api.get('casinos/lista/'),
                api.get('modelos/lista/'),
                api.get('proveedores/lista/'),
                api.get('denominaciones/')
            ]);

            casinos.value = resCasinos.data;
            denominaciones.value = resDenominaciones.data;

            // Enriquecer modelos con el ID del casino de su proveedor para filtrar
            modelos.value = resModelos.data.map(m => {
                const prov = resProveedores.data.find(p => p.id === m.proveedor);
                return {
                    ...m,
                    casino_id: prov ? prov.casino : null,
                    proveedor_nombre: prov ? prov.nombre : 'N/A'
                };
            });
        }

    } catch (error) {

        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'No se pudieron cargar los datos necesarios',
            life: 3000
        });
    } finally {
        loading.value = false;
    }
};

// Filtrar modelos según el casino seleccionado
const modelosFiltrados = computed(() => {
    if (!maquina.value.casino) return [];
    return modelos.value.filter(m => m.casino_id === maquina.value.casino && m.esta_activo);
});

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

// CRUD
const openNew = () => {
    maquina.value = {
        esta_activo: true,
        estado_actual: 'OPERATIVA',
        coordenada_x: 0,
        coordenada_y: 0,
        contador_fallas: 0,
        denominaciones: [],
        casino: casinoUsuario.value // Pre-seleccionar el casino del usuario
    };
    submitted.value = false;
    maquinaDialog.value = true;
};

const editarMaquina = (data) => {
    maquina.value = { ...data };
    // Asegurar que denominaciones sea un array de IDs para el MultiSelect
    if (maquina.value.denominaciones && maquina.value.denominaciones.length > 0 && typeof maquina.value.denominaciones[0] === 'object') {
        maquina.value.denominaciones = maquina.value.denominaciones.map(d => d.id);
    }

    // Convertir fechas string a Date objects para DatePicker
    if (maquina.value.ultimo_mantenimiento) maquina.value.ultimo_mantenimiento = new Date(maquina.value.ultimo_mantenimiento);
    if (maquina.value.fecha_vencimiento_licencia) maquina.value.fecha_vencimiento_licencia = new Date(maquina.value.fecha_vencimiento_licencia);

    maquinaDialog.value = true;
};

const hideDialog = () => {
    maquinaDialog.value = false;
    submitted.value = false;
};

const saveMaquina = async () => {
    submitted.value = true;

    if (maquina.value.uid_sala?.trim() &&
        maquina.value.numero_serie?.trim() &&
        maquina.value.casino &&
        maquina.value.modelo &&
        maquina.value.ubicacion_piso &&
        maquina.value.ubicacion_sala &&
        maquina.value.coordenada_x != null &&
        maquina.value.coordenada_y != null) {

        loading.value = true;

        const esEdicion = !!maquina.value.id;
        const resultado = await guardarMaquina(maquina.value, esEdicion);

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

        maquinaDialog.value = false;
        maquina.value = {};
        cargarDatos();
        loading.value = false;
    }
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
                toast.add({ severity: 'error', summary: 'Error', detail: `No se pudo ${accion} la máquina`, life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

// Función para abrir modal de detalles y cargar historial
const verDetalleMaquina = async (data) => {
    maquinaDetalle.value = { ...data };
    detalleDialog.value = true;
    loadingDetalle.value = true;
    historialTickets.value = [];

    try {
        const response = await api.get(`tickets/historial-maquina/${data.id}/`);
        historialTickets.value = response.data.historial;
    } catch (error) {

        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'No se pudo cargar el historial de tickets',
            life: 3000
        });
    } finally {
        loadingDetalle.value = false;
    }
};

// Calcular días desde último mantenimiento
const diasDesdeMantenimiento = computed(() => {
    if (!maquinaDetalle.value?.ultimo_mantenimiento) return 'N/A';
    const fecha = new Date(maquinaDetalle.value.ultimo_mantenimiento);
    const hoy = new Date();
    const diff = Math.floor((hoy - fecha) / (1000 * 60 * 60 * 24));
    return `${diff} días`;
});

// Función para levantar incidencia (basada en botón de pánico)
const levantarIncidencia = async () => {
    if (!maquinaDetalle.value) return;

    // Validación 1: Verificar que existe información del casino
    if (!casinoUsuario.value) {
        toast.add({
            severity: 'error',
            summary: 'Casino no identificado',
            detail: 'No se encontró información del casino. Por favor cierre sesión y vuelva a iniciar sesión.',
            life: 5000
        });
        return;
    }

    // Validación 2: Verificar información del usuario
    if (!usuario.value || !usuario.value.id) {
        toast.add({
            severity: 'error',
            summary: 'Usuario no autenticado',
            detail: 'No se pudo obtener su información de usuario. Por favor inicie sesión nuevamente.',
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

        detalleDialog.value = false;
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

                <Column v-if="permisos.puedeEditar || permisos.puedeDesactivar" header="Acciones" :exportable="false"
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button v-if="permisos.puedeEditar" icon="pi pi-pencil" size="small" severity="info" rounded
                                outlined @click="editarMaquina(data)" v-tooltip.top="'Editar'" />
                            <Button v-if="permisos.puedeDesactivar" icon="pi pi-ban" size="small" severity="warning"
                                rounded outlined @click="toggleActivarMaquina(data)" v-tooltip.top="'Desactivar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <Dialog v-model:visible="maquinaDialog" :style="{ width: '800px' }" header="Detalles de la Máquina"
                :modal="true">
                <div class="flex flex-col gap-6">
                    <!-- Sección 1: Identificación y Ubicación -->
                    <div
                        class="font-bold text-lg text-surface-500 border-b border-surface-200 dark:border-surface-700 pb-2">
                        Identificación y Ubicación</div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="casino" class="block font-bold mb-3">Casino</label>
                            <Select id="casino" v-model="maquina.casino" :options="casinos" optionLabel="nombre"
                                optionValue="id" placeholder="Seleccione Casino" fluid
                                :invalid="submitted && !maquina.casino" @change="maquina.modelo = null"
                                :disabled="true" />
                            <small class="text-red-500" v-if="submitted && !maquina.casino">Requerido.</small>
                            <small class="text-surface-500">Casino asignado a tu usuario.</small>
                        </div>
                        <div>
                            <label for="modelo" class="block font-bold mb-3">Modelo</label>
                            <Select id="modelo" v-model="maquina.modelo" :options="modelosFiltrados"
                                optionLabel="nombre_modelo" optionValue="id" placeholder="Seleccione Modelo" fluid
                                :invalid="submitted && !maquina.modelo" :disabled="!maquina.casino" />
                            <small class="text-red-500" v-if="submitted && !maquina.modelo">Requerido.</small>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label for="uid_sala" class="block font-bold mb-3">UID Sala (Ej. A01)</label>
                            <InputText id="uid_sala" v-model.trim="maquina.uid_sala" required="true"
                                :invalid="submitted && !maquina.uid_sala" fluid />
                            <small class="text-red-500" v-if="submitted && !maquina.uid_sala">Requerido.</small>
                        </div>
                        <div>
                            <label for="numero_serie" class="block font-bold mb-3">No. Serie</label>
                            <InputText id="numero_serie" v-model.trim="maquina.numero_serie" required="true"
                                :invalid="submitted && !maquina.numero_serie" fluid />
                            <small class="text-red-500" v-if="submitted && !maquina.numero_serie">Requerido.</small>
                        </div>
                        <div>
                            <label for="ip_maquina" class="block font-bold mb-3">Dirección IP</label>
                            <InputText id="ip_maquina" v-model.trim="maquina.ip_maquina" fluid
                                placeholder="172.16.xx.xx" />
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="ubicacion_piso" class="block font-bold mb-3">Piso / Área</label>
                            <Select id="ubicacion_piso" v-model="maquina.ubicacion_piso" :options="pisosChoices"
                                optionLabel="label" optionValue="value" placeholder="Seleccione piso" showClear fluid
                                :invalid="submitted && !maquina.ubicacion_piso" />
                            <small class="text-red-500" v-if="submitted && !maquina.ubicacion_piso">Requerido.</small>
                        </div>
                        <div>
                            <label for="ubicacion_sala" class="block font-bold mb-3">Sala / Sección</label>
                            <Select id="ubicacion_sala" v-model="maquina.ubicacion_sala" :options="salasChoices"
                                optionLabel="label" optionValue="value" placeholder="Seleccione sala" showClear fluid
                                :invalid="submitted && !maquina.ubicacion_sala" />
                            <small class="text-red-500" v-if="submitted && !maquina.ubicacion_sala">Requerido.</small>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block font-bold mb-3">Coordenadas (X, Y)</label>
                            <div class="flex gap-2">
                                <InputNumber id="coordenada_x" name="coordenada_x" v-model="maquina.coordenada_x"
                                    showButtons :min="0" placeholder="X" fluid
                                    :invalid="submitted && maquina.coordenada_x == null" />
                                <InputNumber id="coordenada_y" name="coordenada_y" v-model="maquina.coordenada_y"
                                    showButtons :min="0" placeholder="Y" fluid
                                    :invalid="submitted && maquina.coordenada_y == null" />
                            </div>
                            <small class="text-red-500"
                                v-if="submitted && (maquina.coordenada_x == null || maquina.coordenada_y == null)">Ambas
                                coordenadas
                                son requeridas.</small>
                        </div>
                        <div>
                            <label for="juego" class="block font-bold mb-3">Juego / Título</label>
                            <InputText id="juego" v-model="maquina.juego" fluid />
                        </div>
                    </div>

                    <!-- Sección 2: Detalles Técnicos -->
                    <div
                        class="font-bold text-lg text-surface-500 border-b border-surface-200 dark:border-surface-700 pb-2 mt-2">
                        Detalles Técnicos</div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="estado_actual" class="block font-bold mb-3">Estado Actual</label>
                            <Select id="estado_actual" v-model="maquina.estado_actual" :options="estados"
                                optionLabel="label" optionValue="value" fluid />
                        </div>
                        <div>
                            <label for="denominaciones" class="block font-bold mb-3">Denominaciones</label>
                            <MultiSelect id="denominaciones" v-model="maquina.denominaciones" :options="denominaciones"
                                optionLabel="etiqueta" optionValue="id" placeholder="Seleccione Denominaciones"
                                display="chip" fluid />
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label for="contador_fallas" class="block font-bold mb-3">Contador Fallas</label>
                            <InputNumber id="contador_fallas" v-model="maquina.contador_fallas" showButtons :min="0"
                                fluid />
                        </div>
                        <div>
                            <label for="ultimo_mantenimiento" class="block font-bold mb-3">Último Mantenimiento</label>
                            <DatePicker id="ultimo_mantenimiento" v-model="maquina.ultimo_mantenimiento"
                                dateFormat="yy-mm-dd" showIcon fluid />
                        </div>
                        <div>
                            <label for="fecha_vencimiento_licencia" class="block font-bold mb-3">Vencimiento
                                Licencia</label>
                            <DatePicker id="fecha_vencimiento_licencia" v-model="maquina.fecha_vencimiento_licencia"
                                dateFormat="yy-mm-dd" showIcon fluid />
                        </div>
                    </div>

                </div>
                <template #footer>
                    <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                    <Button label="Guardar" icon="pi pi-check" @click="saveMaquina" />
                </template>
            </Dialog>

            <!-- Modal de Detalles de Máquina -->
            <Dialog v-model:visible="detalleDialog" :style="{ width: '1000px' }" :breakpoints="{ '960px': '95vw' }"
                header="Ficha Técnica Completa" :modal="true" :maximizable="true">
                <div v-if="maquinaDetalle" class="flex flex-col gap-5">
                    <!-- 1. FICHA TÉCNICA COMPLETA (TODO EN UNO) -->
                    <div
                        class="surface-card border-2 border-primary-200 dark:border-primary-900 rounded-xl p-5 bg-gradient-to-br from-primary-50 to-white dark:from-primary-950 dark:to-surface-900">
                        <div class="flex flex-col md:flex-row items-start md:items-center gap-3 md:gap-4 mb-5">
                            <div class="flex items-center gap-3 w-full md:w-auto">
                                <div class="flex items-center justify-center bg-primary-500 rounded-xl shadow-lg shrink-0"
                                    style="width:3rem;height:3rem">
                                    <i class="pi pi-desktop text-white text-xl"></i>
                                </div>
                                <div class="flex-1 min-w-0">
                                    <h3
                                        class="text-xl md:text-2xl font-bold text-surface-900 dark:text-surface-0 mb-1 truncate">
                                        {{
                                            maquinaDetalle.uid_sala }}</h3>
                                    <p
                                        class="text-surface-600 dark:text-surface-400 font-medium text-sm md:text-base truncate">
                                        {{
                                            maquinaDetalle.modelo_nombre }} <span class="text-primary-500">•</span> {{
                                            maquinaDetalle.modelo_producto }}</p>
                                </div>
                            </div>
                            <div class="shrink-0">
                                <Tag :value="maquinaDetalle.estado_actual"
                                    :severity="getEstadoSeverity(maquinaDetalle.estado_actual)"
                                    class="text-base px-4 py-2 font-bold" rounded />
                            </div>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
                            <!-- Información de Ubicación -->
                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-building text-blue-500 text-sm"></i>
                                    <span
                                        class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Casino</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{
                                    maquinaDetalle.casino_nombre
                                }}</span>
                            </div>
                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-map-marker text-red-500 text-sm"></i>
                                    <span
                                        class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Ubicación</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{
                                    maquinaDetalle.ubicacion_piso || 'N/A' }} / {{ maquinaDetalle.ubicacion_sala ||
                                        'N/A' }}</span>
                            </div>
                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-compass text-purple-500 text-sm"></i>
                                    <span
                                        class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Coordenadas</span>
                                </div>
                                <Tag :value="`X: ${maquinaDetalle.coordenada_x}, Y: ${maquinaDetalle.coordenada_y}`"
                                    severity="secondary" class="text-xs" />
                            </div>
                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-wifi text-green-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">IP
                                        Máquina</span>
                                </div>
                                <Tag v-if="maquinaDetalle.ip_maquina" :value="maquinaDetalle.ip_maquina" severity="info"
                                    class="text-xs font-mono" />
                                <span v-else class="text-surface-400 text-xs">Sin asignar</span>
                            </div>

                            <!-- Información Técnica -->
                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-hashtag text-indigo-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">No.
                                        Serie</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{
                                    maquinaDetalle.numero_serie
                                }}</span>
                            </div>
                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-play text-pink-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Juego /
                                        Título</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{
                                    maquinaDetalle.juego ||
                                    'N/A' }}</span>
                            </div>
                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-calendar text-cyan-500 text-sm"></i>
                                    <span
                                        class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Instalación</span>
                                </div>
                                <Tag v-if="maquinaDetalle.fecha_instalacion" :value="maquinaDetalle.fecha_instalacion"
                                    severity="contrast" class="text-xs" />
                                <span v-else class="text-surface-400 text-xs">N/A</span>
                            </div>
                            <div
                                class="bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-950 dark:to-red-950 rounded-lg p-3 border-2 border-orange-300 dark:border-orange-800">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-exclamation-triangle text-orange-600 text-sm"></i>
                                    <span class="text-orange-700 dark:text-orange-400 text-xs font-semibold">Contador
                                        Fallas</span>
                                </div>
                                <div class="flex items-center gap-2">
                                    <span class="font-bold text-orange-600 dark:text-orange-400 text-2xl">{{
                                        maquinaDetalle.contador_fallas || 0 }}</span>
                                    <Tag v-if="maquinaDetalle.contador_fallas > 5" value="Alto" severity="danger"
                                        class="text-xs" />
                                    <Tag v-else-if="maquinaDetalle.contador_fallas > 2" value="Medio" severity="warn"
                                        class="text-xs" />
                                </div>
                            </div>

                            <!-- Información del Proveedor -->
                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-briefcase text-teal-500 text-sm"></i>
                                    <span
                                        class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Proveedor</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{
                                    maquinaDetalle.proveedor_nombre || 'N/A' }}</span>
                            </div>
                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-id-card text-gray-500 text-sm"></i>
                                    <span
                                        class="text-surface-500 dark:text-surface-400 text-xs font-semibold">RFC</span>
                                </div>
                                <Tag v-if="maquinaDetalle.proveedor_rfc" :value="maquinaDetalle.proveedor_rfc"
                                    severity="secondary" class="text-xs" />
                                <span v-else class="text-surface-400 text-xs">N/A</span>
                            </div>
                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-envelope text-blue-500 text-sm"></i>
                                    <span
                                        class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Email</span>
                                </div>
                                <a v-if="maquinaDetalle.proveedor_email"
                                    :href="'mailto:' + maquinaDetalle.proveedor_email"
                                    class="text-primary-600 hover:text-primary-700 hover:underline text-xs font-medium">
                                    {{ maquinaDetalle.proveedor_email }}
                                </a>
                                <span v-else class="text-surface-400 text-xs">N/A</span>
                            </div>
                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-phone text-green-500 text-sm"></i>
                                    <span
                                        class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Teléfono</span>
                                </div>
                                <a v-if="maquinaDetalle.proveedor_telefono"
                                    :href="'tel:' + maquinaDetalle.proveedor_telefono"
                                    class="text-primary-600 hover:text-primary-700 hover:underline text-xs font-medium">
                                    {{ maquinaDetalle.proveedor_telefono }}
                                </a>
                                <span v-else class="text-surface-400 text-xs">N/A</span>
                            </div>

                            <!-- Mantenimiento y Licencia -->
                            <div
                                class="bg-blue-50 dark:bg-blue-950 rounded-lg p-3 border border-blue-200 dark:border-blue-800">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-wrench text-blue-600 text-sm"></i>
                                    <span class="text-blue-700 dark:text-blue-400 text-xs font-semibold">Último
                                        Mtto.</span>
                                </div>
                                <span class="font-bold text-blue-800 dark:text-blue-300 text-sm block">{{
                                    maquinaDetalle.ultimo_mantenimiento || 'Sin registro' }}</span>
                                <span v-if="maquinaDetalle.ultimo_mantenimiento"
                                    class="text-xs text-blue-600 dark:text-blue-400">({{ diasDesdeMantenimiento
                                    }})</span>
                            </div>
                            <div class="rounded-lg p-3 border-2" :class="maquinaDetalle.dias_licencia < 30 && maquinaDetalle.dias_licencia !== 'Indefinida'
                                ? 'bg-red-50 dark:bg-red-950 border-red-300 dark:border-red-800'
                                : 'bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800'">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-shield text-sm"
                                        :class="maquinaDetalle.dias_licencia < 30 && maquinaDetalle.dias_licencia !== 'Indefinida' ? 'text-red-600' : 'text-green-600'"></i>
                                    <span class="text-xs font-semibold"
                                        :class="maquinaDetalle.dias_licencia < 30 && maquinaDetalle.dias_licencia !== 'Indefinida' ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'">Licencia</span>
                                </div>
                                <span class="font-bold text-sm block"
                                    :class="maquinaDetalle.dias_licencia < 30 && maquinaDetalle.dias_licencia !== 'Indefinida' ? 'text-red-800 dark:text-red-300' : 'text-green-800 dark:text-green-300'">
                                    {{ maquinaDetalle.fecha_vencimiento_licencia || 'Indefinida' }}
                                </span>
                                <Tag v-if="maquinaDetalle.dias_licencia && maquinaDetalle.dias_licencia !== 'Indefinida'"
                                    :value="`${maquinaDetalle.dias_licencia} días`"
                                    :severity="maquinaDetalle.dias_licencia < 30 ? 'danger' : 'success'"
                                    class="text-xs mt-1" />
                            </div>
                            <div
                                class="col-span-1 sm:col-span-2 md:col-span-4 bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-dollar text-emerald-500 text-sm"></i>
                                    <span
                                        class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Denominaciones</span>
                                </div>
                                <div class="flex flex-wrap gap-1">
                                    <Tag v-for="denom in maquinaDetalle.denominaciones_info" :key="denom.id"
                                        :value="denom.etiqueta" severity="success" class="text-xs" rounded />
                                    <Tag v-if="!maquinaDetalle.denominaciones_info || maquinaDetalle.denominaciones_info.length === 0"
                                        value="Sin configurar" severity="warn" class="text-xs" />
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 2. HISTORIAL DE INTERVENCIONES -->
                    <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                        <div class="flex items-center gap-2 mb-4">
                            <i class="pi pi-history text-xl text-surface-500"></i>
                            <h4 class="font-bold text-xl text-surface-900 dark:text-surface-0">Historial de
                                Intervenciones</h4>
                        </div>

                        <div v-if="loadingDetalle" class="text-center py-8">
                            <ProgressSpinner style="width: 50px; height: 50px" />
                            <p class="text-surface-500 mt-4">Cargando historial...</p>
                        </div>

                        <div v-else-if="historialTickets.length === 0" class="text-center py-8">
                            <i class="pi pi-info-circle text-4xl text-surface-400 mb-4"></i>
                            <p class="text-surface-500">No hay tickets registrados para esta máquina</p>
                        </div>

                        <Timeline v-else :value="historialTickets" class="w-full">
                            <template #marker="slotProps">
                                <span
                                    class="flex w-8 h-8 items-center justify-center text-white rounded-full z-10 shadow-sm"
                                    :class="{
                                        'bg-green-500': slotProps.item.estado_ciclo === 'cerrado',
                                        'bg-blue-500': slotProps.item.estado_ciclo === 'proceso',
                                        'bg-orange-500': slotProps.item.estado_ciclo === 'espera',
                                        'bg-red-500': slotProps.item.estado_ciclo === 'abierto'
                                    }">
                                    <i class="pi pi-wrench"></i>
                                </span>
                            </template>
                            <template #content="slotProps">
                                <div
                                    class="surface-card border-2 border-blue-200 dark:border-blue-800 rounded-xl p-3 md:p-5 mb-4 bg-gradient-to-br from-blue-50 to-white dark:from-blue-950 dark:to-surface-900">
                                    <!-- Cabecera del Ticket - Más grande y destacada -->
                                    <div class="flex flex-col sm:flex-row justify-between items-start gap-2 mb-4">
                                        <div class="flex items-center gap-2 md:gap-3 flex-wrap">
                                            <div class="flex items-center justify-center bg-blue-500 rounded-lg shadow-md shrink-0"
                                                style="width:2rem;height:2rem">
                                                <i class="pi pi-ticket text-white text-sm"></i>
                                            </div>
                                            <div class="flex items-center gap-2 flex-wrap">
                                                <span
                                                    class="font-bold text-lg md:text-2xl text-blue-600 dark:text-blue-400">{{
                                                        slotProps.item.folio }}</span>
                                                <Tag :value="slotProps.item.estado_ciclo"
                                                    :severity="slotProps.item.estado_ciclo === 'cerrado' ? 'success' : slotProps.item.estado_ciclo === 'proceso' ? 'info' : 'warn'" />
                                            </div>
                                        </div>
                                        <span class="text-surface-500 text-xs md:text-sm">{{ new
                                            Date(slotProps.item.fecha_creacion).toLocaleDateString('es-MX') }}</span>
                                    </div>

                                    <!-- Descripción del problema - Más grande -->
                                    <p
                                        class="text-sm md:text-base font-medium text-blue-800 dark:text-blue-300 mb-4 pl-0 md:pl-12">
                                        {{ slotProps.item.descripcion_problema }}</p>

                                    <!-- Información del ticket -->
                                    <div class="flex flex-wrap gap-3 md:gap-4 mb-4 pl-0 md:pl-12">
                                        <div class="flex items-center gap-1">
                                            <i class="pi pi-tag text-surface-400 text-xs"></i>
                                            <span class="text-surface-500 text-sm">Categoría:</span>
                                            <span class="font-semibold text-surface-900 dark:text-surface-0 text-sm">{{
                                                slotProps.item.categoria }}</span>
                                        </div>
                                        <div class="flex items-center gap-1">
                                            <i class="pi pi-exclamation-circle text-surface-400 text-xs"></i>
                                            <span class="text-surface-500 text-sm">Prioridad:</span>
                                            <Tag :value="slotProps.item.prioridad"
                                                :severity="slotProps.item.prioridad === 'critica' || slotProps.item.prioridad === 'emergencia' ? 'danger' : slotProps.item.prioridad === 'alta' ? 'warn' : 'info'"
                                                class="text-xs" />
                                        </div>
                                        <div class="flex items-center gap-1">
                                            <i class="pi pi-user text-surface-400 text-xs"></i>
                                            <span class="text-surface-500 text-sm">Técnico:</span>
                                            <span class="font-semibold text-surface-900 dark:text-surface-0 text-sm">
                                                {{ slotProps.item.tecnico_asignado.nombre }} {{
                                                    slotProps.item.tecnico_asignado.apellidos }}
                                            </span>
                                        </div>
                                    </div>

                                    <!-- Bitácoras del Ticket - Diseño de árbol jerárquico -->
                                    <div v-if="slotProps.item.bitacoras && slotProps.item.bitacoras.length > 0"
                                        class="mt-4 pl-0 md:pl-12">
                                        <div class="flex items-center gap-2 mb-3">
                                            <i class="pi pi-list text-surface-400 text-sm"></i>
                                            <span
                                                class="text-surface-600 dark:text-surface-400 text-xs md:text-sm font-bold uppercase tracking-wide">Intervenciones
                                                ({{ slotProps.item.bitacoras.length }})</span>
                                        </div>

                                        <!-- Contenedor con línea vertical conectora -->
                                        <div
                                            class="relative pl-4 md:pl-6 border-l-2 border-blue-300 dark:border-blue-700 ml-1 md:ml-2">
                                            <div v-for="(bitacora, idx) in slotProps.item.bitacoras" :key="idx"
                                                class="relative mb-4 last:mb-0">
                                                <!-- Punto de conexión -->
                                                <div
                                                    class="absolute -left-[1.6rem] top-3 w-4 h-4 bg-blue-400 dark:bg-blue-600 rounded-full border-2 border-white dark:border-surface-900">
                                                </div>

                                                <!-- Tarjeta de bitácora -->
                                                <div
                                                    class="bg-white dark:bg-surface-800 rounded-lg p-3 md:p-4 shadow-sm border border-surface-200 dark:border-surface-700 hover:shadow-md transition-shadow">
                                                    <div
                                                        class="flex flex-col sm:flex-row justify-between items-start gap-1 mb-2">
                                                        <div class="flex items-center gap-2">
                                                            <i class="pi pi-user-edit text-blue-500 text-sm"></i>
                                                            <span
                                                                class="text-xs md:text-sm font-bold text-surface-900 dark:text-surface-0">{{
                                                                    bitacora.tecnico_nombre }}</span>
                                                        </div>
                                                        <span class="text-xs text-surface-500">{{ new
                                                            Date(bitacora.fecha_registro).toLocaleString('es-MX')
                                                        }}</span>
                                                    </div>
                                                    <p
                                                        class="text-xs md:text-sm text-surface-700 dark:text-surface-300 mb-3 pl-0 md:pl-6">
                                                        {{ bitacora.descripcion_trabajo }}</p>
                                                    <div class="flex flex-wrap gap-2 pl-0 md:pl-6">
                                                        <Tag :value="bitacora.tipo_intervencion" severity="secondary"
                                                            class="text-xs" icon="pi pi-cog" />
                                                        <Tag :value="bitacora.resultado_intervencion"
                                                            :severity="bitacora.resultado_intervencion === 'exitosa' ? 'success' : bitacora.resultado_intervencion === 'parcial' ? 'warn' : 'danger'"
                                                            class="text-xs"
                                                            :icon="bitacora.resultado_intervencion === 'exitosa' ? 'pi pi-check-circle' : 'pi pi-info-circle'" />
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </template>
                        </Timeline>
                    </div>

                    <!-- 3. BOTÓN DE ACCIÓN -->
                    <div class="flex justify-center gap-3">
                        <Button label="Levantar Incidencia" icon="pi pi-exclamation-circle" severity="danger"
                            size="large" @click="levantarIncidencia" class="px-6" />
                    </div>
                </div>
            </Dialog>
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
