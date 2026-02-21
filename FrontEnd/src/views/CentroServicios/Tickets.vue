<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api, { getUser } from '@/service/api';
import { crearBitacoraTecnica } from '@/service/ticketService';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

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
const ticketDialog = ref(false);
const ticket = ref({});
const submitted = ref(false);

// Modal de detalle con bitácoras
const detalleDialog = ref(false);
const ticketDetalle = ref(null);
const bitacoras = ref([]);
const loadingDetalle = ref(false);
const guardandoBitacora = ref(false);
const submittedBitacora = ref(false);

// Nueva entrada de bitácora
const nuevaBitacora = ref({
    tipo_intervencion: null,
    descripcion_trabajo: '',
    resultado_intervencion: null,
    estado_maquina_resultante: null,
    finaliza_ticket: false,
    explicacion_cierre: ''
});

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
        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudieron cargar los tickets', life: 3000 });
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

// Computed para validación de cierre de ticket
const puedeSerCerrado = computed(() => {
    if (!nuevaBitacora.value.finaliza_ticket) return false;
    return nuevaBitacora.value.estado_maquina_resultante === 'operativa'
        && nuevaBitacora.value.resultado_intervencion === 'exitosa';
});

const ticketEstaCerrado = computed(() => {
    return ticketDetalle.value?.estado_ciclo === 'cerrado';
});

// CRUD
const openNew = () => {
    ticket.value = {
        prioridad: 'media',
        estado_ciclo: 'abierto',
        esta_activo: true,
        reportante: usuario.value?.id
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

const saveTicket = async () => {
    submitted.value = true;

    if (ticket.value.maquina && ticket.value.categoria && ticket.value.descripcion_problema?.trim()) {
        loading.value = true;
        try {
            const payload = { ...ticket.value };

            if (!payload.reportante && usuario.value?.id) {
                payload.reportante = usuario.value.id;
            }

            if (ticket.value.id) {
                await api.put(`tickets/${ticket.value.id}/`, payload);
                toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Ticket actualizado correctamente', life: 3000 });
            } else {
                const response = await api.post('tickets/', payload);
                const ticketCreado = response.data;

                toast.add({ severity: 'success', summary: 'Creado', detail: 'Ticket creado correctamente', life: 3000 });

                // Incrementar contador de fallas de la máquina
                const maquinaId = payload.maquina;

                if (!maquinaId) {
                    throw new Error('ID de máquina no válido');
                }

                try {
                    const fallasResponse = await api.post(`maquinas/${maquinaId}/incrementar-fallas/`);

                    toast.add({
                        severity: 'info',
                        summary: 'Contador Actualizado',
                        detail: `Contador de fallas: ${fallasResponse.data.contador_fallas}`,
                        life: 2000
                    });
                } catch (errorFallas) {
                    toast.add({
                        severity: 'warn',
                        summary: 'Advertencia',
                        detail: `No se pudo actualizar el contador de fallas: ${errorFallas.response?.data?.error || errorFallas.message}`,
                        life: 4000
                    });
                }
            }

            ticketDialog.value = false;
            ticket.value = {};
            cargarDatos();
        } catch (error) {
            const detalle = error.response?.data?.mensaje || error.response?.data?.detail || 'Error al guardar el ticket';
            toast.add({ severity: 'error', summary: 'Error', detail: detalle, life: 5000 });
        } finally {
            loading.value = false;
        }
    }
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
                cargarDatos();
            } catch (error) {
                toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudo desactivar el ticket', life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

// Ver detalle con bitácoras
const verDetalleTicket = async (data) => {
    ticketDetalle.value = { ...data };
    detalleDialog.value = true;
    cancelarFormularioBitacora();
    await cargarBitacoras(data.id);
};

const cargarBitacoras = async (ticketId) => {
    loadingDetalle.value = true;
    try {
        const response = await api.get(`bitacora-tecnica/?ticket=${ticketId}`);
        bitacoras.value = response.data.sort((a, b) =>
            new Date(b.fecha_registro) - new Date(a.fecha_registro)
        );
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudo cargar el historial de intervenciones',
            life: 3000
        });
    } finally {
        loadingDetalle.value = false;
    }
};

const formatearFecha = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleString('es-MX', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
};

const cancelarFormularioBitacora = () => {
    nuevaBitacora.value = {
        tipo_intervencion: null,
        descripcion_trabajo: '',
        resultado_intervencion: null,
        estado_maquina_resultante: null,
        finaliza_ticket: false,
        explicacion_cierre: ''
    };
    submittedBitacora.value = false;
};

const guardarBitacora = async () => {
    submittedBitacora.value = true;

    if (!usuario.value || !usuario.value.id) {
        toast.add({
            severity: 'error',
            summary: 'Sesión No Válida',
            detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No hay una sesión activa. Por favor, inicia sesión nuevamente.',
            life: 5000
        });
        return;
    }

    // Validaciones
    if (!nuevaBitacora.value.tipo_intervencion ||
        !nuevaBitacora.value.descripcion_trabajo?.trim() ||
        !nuevaBitacora.value.resultado_intervencion ||
        !nuevaBitacora.value.estado_maquina_resultante) {
        toast.add({
            severity: 'warn',
            summary: 'Campos Incompletos',
            detail: 'Complete todos los campos obligatorios',
            life: 3000
        });
        return;
    }

    if (nuevaBitacora.value.finaliza_ticket && !nuevaBitacora.value.explicacion_cierre?.trim()) {
        toast.add({
            severity: 'warn',
            summary: 'Explicación Requerida',
            detail: 'Debe proporcionar una explicación del cierre',
            life: 3000
        });
        return;
    }

    guardandoBitacora.value = true;

    try {
        // Usar el servicio global para crear la bitácora
        const resultado = await crearBitacoraTecnica({
            ticketId: ticketDetalle.value.id,
            maquinaId: ticketDetalle.value.maquina,
            usuarioTecnicoId: usuario.value.id,
            tipoIntervencion: nuevaBitacora.value.tipo_intervencion,
            descripcionTrabajo: nuevaBitacora.value.descripcion_trabajo,
            resultadoIntervencion: nuevaBitacora.value.resultado_intervencion,
            estadoMaquinaResultante: nuevaBitacora.value.estado_maquina_resultante,
            finalizaTicket: nuevaBitacora.value.finaliza_ticket,
            explicacionCierre: nuevaBitacora.value.explicacion_cierre || '',
            ticketActual: ticketDetalle.value
        });

        // Manejar el resultado
        if (!resultado.exito) {
            toast.add({
                severity: 'error',
                summary: resultado.error,
                detail: resultado.detalle,
                life: 4000
            });
            guardandoBitacora.value = false;
            return;
        }

        toast.add({
            severity: 'success',
            summary: 'Guardado',
            detail: resultado.mensaje,
            life: 3000
        });

        // Recargar bitácoras y actualizar el detalle del ticket
        await cargarBitacoras(ticketDetalle.value.id);
        cancelarFormularioBitacora();

        // Recargar la lista de tickets para actualizar contadores
        await cargarDatos();

        // Si se cerró el ticket, cerrar el modal después de un momento
        if (nuevaBitacora.value.finaliza_ticket) {
            setTimeout(() => {
                detalleDialog.value = false;
            }, 1500);
        } else {
            // Si no se cerró, cerrar el modal inmediatamente
            detalleDialog.value = false;
        }

    } catch (error) {
        const detalle = error.response?.data?.detail || error.response?.data?.usuario_tecnico?.[0] || 'No se pudo guardar la entrada de bitácora';
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: detalle,
            life: 4000
        });
    } finally {
        guardandoBitacora.value = false;
    }
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

onMounted(() => {
    cargarDatos();
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

        <div class="card">
            <Toast />
            <ConfirmDialog />

            <DataTableToolbar ref="toolbarRef" :dt="dt" :datos="tickets" titulo-reporte="Tickets Abiertos"
                nombre-archivo="tickets_abiertos" :columnas="columnas" @refrescar="cargarDatos"
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
                            @click="verDetalleTicket(data)" v-tooltip.top="'Ver detalle completo'">
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

            <!-- Dialog Crear/Editar -->
            <Dialog v-model:visible="ticketDialog" :style="{ width: '700px' }" :breakpoints="{ '768px': '95vw' }"
                header="Datos del Ticket" :modal="true">
                <div class="flex flex-col gap-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="folio" class="block font-bold mb-3">Folio</label>
                            <InputText id="folio" name="folio" :value="ticket.folio || 'Se generará automáticamente'"
                                disabled fluid class="bg-surface-100 dark:bg-surface-800 font-mono" />
                        </div>
                        <div>
                            <label for="estado_ciclo" class="block font-bold mb-3">Estado</label>
                            <Select id="estado_ciclo" name="estado_ciclo" v-model="ticket.estado_ciclo"
                                :options="estadosCiclo" optionLabel="label" optionValue="value" fluid />
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="maquina" class="block font-bold mb-3">Máquina</label>
                            <Select id="maquina" name="maquina" v-model="ticket.maquina" :options="maquinas"
                                optionLabel="uid_sala" optionValue="id" placeholder="Seleccione Máquina" filter fluid
                                :invalid="submitted && !ticket.maquina">
                                <template #option="slotProps">
                                    <div class="flex flex-col">
                                        <span class="font-bold">{{ slotProps.option.uid_sala }}</span>
                                        <span class="text-xs text-surface-500">{{ slotProps.option.modelo_nombre
                                            }}</span>
                                    </div>
                                </template>
                            </Select>
                            <small class="text-red-500" v-if="submitted && !ticket.maquina">Requerido.</small>
                        </div>
                        <div>
                            <label for="tecnico_asignado" class="block font-bold mb-3">Técnico Asignado</label>
                            <Select id="tecnico_asignado" name="tecnico_asignado" v-model="ticket.tecnico_asignado"
                                :options="tecnicos" optionLabel="nombres" optionValue="id" placeholder="Sin asignar"
                                filter fluid>
                                <template #option="slotProps">
                                    <div class="flex flex-col">
                                        <span class="font-bold">{{ slotProps.option.nombres }} {{
                                            slotProps.option.apellido_paterno }}</span>
                                        <span class="text-xs text-surface-500">{{ slotProps.option.rol_nombre }}</span>
                                    </div>
                                </template>
                            </Select>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label for="categoria" class="block font-bold mb-3">Categoría</label>
                            <Select id="categoria" name="categoria" v-model="ticket.categoria" :options="categorias"
                                optionLabel="label" optionValue="value" fluid
                                :invalid="submitted && !ticket.categoria" />
                            <small class="text-red-500" v-if="submitted && !ticket.categoria">Requerido.</small>
                        </div>
                        <div>
                            <label for="subcategoria" class="block font-bold mb-3">Subcategoría</label>
                            <InputText id="subcategoria" name="subcategoria" v-model="ticket.subcategoria" fluid
                                placeholder="Ej: Billetero trabado" />
                        </div>
                        <div>
                            <label for="prioridad" class="block font-bold mb-3">Prioridad</label>
                            <Select id="prioridad" name="prioridad" v-model="ticket.prioridad" :options="prioridades"
                                optionLabel="label" optionValue="value" fluid />
                        </div>
                    </div>

                    <div>
                        <label for="descripcion_problema" class="block font-bold mb-3">Descripción del Problema</label>
                        <Textarea id="descripcion_problema" name="descripcion_problema"
                            v-model="ticket.descripcion_problema" rows="4" fluid
                            :invalid="submitted && !ticket.descripcion_problema" />
                        <small class="text-red-500" v-if="submitted && !ticket.descripcion_problema">Requerido.</small>
                    </div>

                    <div>
                        <label for="notas_seguimiento" class="block font-bold mb-3">Notas de Seguimiento</label>
                        <Textarea id="notas_seguimiento" name="notas_seguimiento" v-model="ticket.notas_seguimiento"
                            rows="2" fluid />
                    </div>
                </div>
                <template #footer>
                    <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                    <Button label="Guardar" icon="pi pi-check" @click="saveTicket" />
                </template>
            </Dialog>

            <!-- Modal de Detalle con Bitácoras -->
            <Dialog v-model:visible="detalleDialog" :style="{ width: '1000px' }" :breakpoints="{ '960px': '95vw' }"
                header="Detalle del Ticket" :modal="true" :maximizable="true">
                <div v-if="ticketDetalle" class="flex flex-col gap-5">
                    <!-- Ficha del Ticket -->
                    <div
                        class="surface-card border-2 border-primary-200 dark:border-primary-900 rounded-xl p-5 bg-gradient-to-br from-primary-50 to-white dark:from-primary-950 dark:to-surface-900">
                        <div class="flex flex-col md:flex-row items-start md:items-center gap-3 md:gap-4 mb-5">
                            <div class="flex items-center gap-3 w-full md:w-auto">
                                <div class="flex items-center justify-center bg-primary-500 rounded-xl shadow-lg shrink-0"
                                    style="width:3rem;height:3rem">
                                    <i class="pi pi-ticket text-white text-xl"></i>
                                </div>
                                <div class="flex-1 min-w-0">
                                    <h3
                                        class="text-xl md:text-2xl font-bold text-surface-900 dark:text-surface-0 mb-1 truncate">
                                        {{
                                        ticketDetalle.folio }}</h3>
                                    <p
                                        class="text-surface-600 dark:text-surface-400 font-medium text-sm md:text-base truncate">
                                        {{ ticketDetalle.maquina_uid }}
                                        <span class="text-primary-500 mx-2">•</span>
                                        {{ ticketDetalle.categoria }}
                                    </p>
                                </div>
                            </div>
                            <div class="flex gap-2 shrink-0">
                                <Tag :value="ticketDetalle.prioridad.toUpperCase()"
                                    :severity="getPrioridadSeverity(ticketDetalle.prioridad)"
                                    class="text-sm md:text-base px-3 md:px-4 py-1.5 md:py-2 font-bold" rounded />
                                <Tag :value="ticketDetalle.estado_ciclo.toUpperCase()"
                                    :severity="getEstadoSeverity(ticketDetalle.estado_ciclo)"
                                    class="text-sm md:text-base px-3 md:px-4 py-1.5 md:py-2 font-bold" rounded />
                            </div>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
                            <div class="rounded-lg p-3 border-2" :class="getDiasClass(ticketDetalle.dias_abierto)">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi text-sm" :class="getDiasIcon(ticketDetalle.dias_abierto)"></i>
                                    <span class="text-xs font-semibold">Antigüedad</span>
                                </div>
                                <span class="font-bold text-2xl block">{{ ticketDetalle.dias_abierto }}d</span>
                                <span class="text-xs font-semibold">{{ getDiasLabel(ticketDetalle.dias_abierto)
                                    }}</span>
                            </div>

                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-wrench text-indigo-500 text-sm"></i>
                                    <span
                                        class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Intervenciones</span>
                                </div>
                                <span class="font-bold text-indigo-700 dark:text-indigo-400 text-2xl">{{
                                    ticketDetalle.total_intervenciones }}</span>
                            </div>

                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-user text-teal-500 text-sm"></i>
                                    <span
                                        class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Técnico</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{
                                    ticketDetalle.tecnico_asignado_nombre || 'Sin asignar' }}</span>
                            </div>

                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-calendar text-blue-500 text-sm"></i>
                                    <span
                                        class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Creado</span>
                                </div>
                                <span class="text-xs text-surface-700 dark:text-surface-300">{{
                                    formatearFecha(ticketDetalle.creado_en) }}</span>
                            </div>

                            <div
                                class="col-span-1 sm:col-span-2 md:col-span-4 bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-align-left text-surface-500 text-sm"></i>
                                    <span
                                        class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Descripción
                                        del
                                        Problema</span>
                                </div>
                                <p class="text-sm text-surface-700 dark:text-surface-300">{{
                                    ticketDetalle.descripcion_problema }}
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Historial de Intervenciones -->
                    <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                        <div class="flex items-center gap-2 mb-4">
                            <i class="pi pi-history text-xl text-surface-500"></i>
                            <h4 class="font-bold text-xl text-surface-900 dark:text-surface-0">Historial de
                                Intervenciones ({{
                                bitacoras.length }})</h4>
                        </div>

                        <div v-if="loadingDetalle" class="text-center py-8">
                            <ProgressSpinner style="width: 50px; height: 50px" />
                            <p class="text-surface-500 mt-4">Cargando intervenciones...</p>
                        </div>

                        <div v-else-if="bitacoras.length === 0" class="text-center py-8">
                            <i class="pi pi-info-circle text-4xl text-surface-400 mb-4"></i>
                            <p class="text-surface-500">No hay intervenciones registradas para este ticket</p>
                        </div>

                        <div v-else class="space-y-4">
                            <div v-for="(bitacora, idx) in bitacoras" :key="idx"
                                class="bg-blue-50 dark:bg-blue-950 rounded-lg p-3 md:p-4 border-l-4 border-blue-500">
                                <div class="flex flex-col sm:flex-row justify-between items-start gap-1 mb-2">
                                    <div class="flex items-center gap-2">
                                        <i class="pi pi-user-edit text-blue-600 text-sm"></i>
                                        <span class="font-bold text-surface-900 dark:text-surface-0">{{
                                            bitacora.tecnico_nombre
                                            }}</span>
                                    </div>
                                    <span class="text-xs text-surface-500">{{ formatearFecha(bitacora.fecha_registro)
                                        }}</span>
                                </div>
                                <p class="text-xs md:text-sm text-surface-700 dark:text-surface-300 mb-3">{{
                                    bitacora.descripcion_trabajo }}</p>
                                <div class="flex flex-wrap gap-2">
                                    <Tag :value="bitacora.tipo_intervencion" severity="secondary" class="text-xs"
                                        icon="pi pi-cog" />
                                    <Tag :value="bitacora.resultado_intervencion"
                                        :severity="getResultadoSeverity(bitacora.resultado_intervencion)"
                                        class="text-xs"
                                        :icon="bitacora.resultado_intervencion === 'exitosa' ? 'pi pi-check-circle' : 'pi pi-info-circle'" />
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Formulario Nueva Bitácora -->
                    <div v-if="!ticketEstaCerrado && permisos.puedeAgregarBitacora"
                        class="surface-card border-2 border-primary-200 dark:border-primary-800 rounded-lg p-6">
                        <div class="flex items-center gap-2 mb-5">
                            <i class="pi pi-plus-circle text-2xl text-primary-500"></i>
                            <h4 class="font-bold text-xl text-surface-900 dark:text-surface-0">Nueva Intervención</h4>
                        </div>

                        <div class="grid grid-cols-1 gap-5">
                            <!-- Tipo de Intervención -->
                            <div>
                                <label class="block font-bold mb-3">Tipo de Intervención *</label>
                                <div class="flex flex-wrap gap-2">
                                    <Chip v-for="tipo in tiposIntervencion" :key="tipo.value" :label="tipo.label"
                                        :class="[
                                            'cursor-pointer transition-all duration-200 border-2',
                                            nuevaBitacora.tipo_intervencion === tipo.value
                                                ? 'bg-blue-600 dark:bg-blue-500 text-white border-blue-700 dark:border-blue-400 shadow-xl scale-110 font-bold'
                                                : 'bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 border-surface-300 dark:border-surface-600 hover:border-blue-400 hover:bg-surface-200 dark:hover:bg-surface-700'
                                        ]" @click="nuevaBitacora.tipo_intervencion = tipo.value" />
                                </div>
                                <small v-if="submittedBitacora && !nuevaBitacora.tipo_intervencion"
                                    class="text-red-500">
                                    Debe seleccionar un tipo de intervención
                                </small>
                            </div>

                            <!-- Descripción del Trabajo -->
                            <div>
                                <label for="descripcion" class="block font-bold mb-3">Descripción del Trabajo *</label>
                                <Textarea id="descripcion" name="descripcion"
                                    v-model="nuevaBitacora.descripcion_trabajo" rows="4"
                                    placeholder="Detalle las acciones realizadas, pruebas ejecutadas y componentes revisados..."
                                    :invalid="submittedBitacora && !nuevaBitacora.descripcion_trabajo" class="w-full" />
                                <small v-if="submittedBitacora && !nuevaBitacora.descripcion_trabajo"
                                    class="text-red-500">
                                    La descripción del trabajo es obligatoria
                                </small>
                            </div>

                            <!-- Resultado de la Intervención -->
                            <div>
                                <label class="block font-bold mb-3">Resultado de la Intervención *</label>
                                <div class="flex flex-wrap gap-2">
                                    <Chip v-for="resultado in resultadosIntervencion" :key="resultado.value"
                                        :label="resultado.label" :class="[
                                            'cursor-pointer transition-all duration-200 border-2',
                                            nuevaBitacora.resultado_intervencion === resultado.value
                                                ? 'bg-green-600 dark:bg-green-500 text-white border-green-700 dark:border-green-400 shadow-xl scale-110 font-bold'
                                                : 'bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 border-surface-300 dark:border-surface-600 hover:border-green-400 hover:bg-surface-200 dark:hover:bg-surface-700'
                                        ]" @click="nuevaBitacora.resultado_intervencion = resultado.value" />
                                </div>
                                <small v-if="submittedBitacora && !nuevaBitacora.resultado_intervencion"
                                    class="text-red-500">
                                    Debe seleccionar un resultado
                                </small>
                            </div>

                            <!-- Estado de Máquina Resultante -->
                            <div>
                                <label class="block font-bold mb-3">Estado de Máquina Resultante *</label>
                                <div class="flex flex-wrap gap-2">
                                    <Chip v-for="estado in estadosMaquina" :key="estado.value" :label="estado.label"
                                        :class="[
                                            'cursor-pointer transition-all duration-200 border-2',
                                            nuevaBitacora.estado_maquina_resultante === estado.value
                                                ? 'bg-teal-600 dark:bg-teal-500 text-white border-teal-700 dark:border-teal-400 shadow-xl scale-110 font-bold'
                                                : 'bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 border-surface-300 dark:border-surface-600 hover:border-teal-400 hover:bg-surface-200 dark:hover:bg-surface-700'
                                        ]" @click="nuevaBitacora.estado_maquina_resultante = estado.value" />
                                </div>
                                <small v-if="submittedBitacora && !nuevaBitacora.estado_maquina_resultante"
                                    class="text-red-500">
                                    Debe seleccionar el estado de la máquina
                                </small>
                            </div>

                            <!-- Finaliza Ticket -->
                            <div
                                class="border-2 border-dashed border-surface-300 dark:border-surface-600 rounded-lg p-4">
                                <div class="flex items-center gap-3 mb-3">
                                    <Checkbox v-model="nuevaBitacora.finaliza_ticket" :binary="true"
                                        inputId="finaliza" />
                                    <label for="finaliza" class="font-bold text-lg cursor-pointer">
                                        ¿Esta intervención cierra el ticket?
                                    </label>
                                </div>

                                <!-- Validación para cerrar ticket -->
                                <div v-if="nuevaBitacora.finaliza_ticket">
                                    <div v-if="!puedeSerCerrado"
                                        class="bg-red-50 dark:bg-red-900/20 border border-red-500 rounded p-3">
                                        <p class="text-red-700 dark:text-red-400 font-semibold flex items-center gap-2">
                                            <i class="pi pi-exclamation-triangle"></i>
                                            No se puede cerrar el ticket
                                        </p>
                                        <ul class="mt-2 ml-6 text-sm text-red-600 dark:text-red-300">
                                            <li v-if="nuevaBitacora.estado_maquina_resultante !== 'operativa'">
                                                • La máquina debe quedar en estado OPERATIVA
                                            </li>
                                            <li v-if="nuevaBitacora.resultado_intervencion !== 'exitosa'">
                                                • El resultado de la intervención debe ser EXITOSA
                                            </li>
                                        </ul>
                                    </div>
                                    <div v-else
                                        class="bg-green-50 dark:bg-green-900/20 border border-green-500 rounded p-3">
                                        <p
                                            class="text-green-700 dark:text-green-400 font-semibold flex items-center gap-2">
                                            <i class="pi pi-check-circle"></i>
                                            Al guardar se realizará:
                                        </p>
                                        <ul class="mt-2 ml-6 text-sm text-green-600 dark:text-green-300">
                                            <li>✓ Cerrar el ticket (estado_ciclo = cerrado)</li>
                                            <li>✓ Cambiar máquina a estado OPERATIVA</li>
                                            <li>✓ Guardar bitácora con timestamp</li>
                                        </ul>
                                    </div>

                                    <!-- Campo de explicación de cierre -->
                                    <div class="mt-4">
                                        <label for="explicacion_cierre" class="block font-bold mb-3">Explicación del
                                            Cierre
                                            *</label>
                                        <Textarea id="explicacion_cierre" name="explicacion_cierre"
                                            v-model="nuevaBitacora.explicacion_cierre" rows="3"
                                            placeholder="Resumen de la solución aplicada y confirmación de que el problema quedó resuelto..."
                                            :invalid="submittedBitacora && nuevaBitacora.finaliza_ticket && !nuevaBitacora.explicacion_cierre"
                                            class="w-full" />
                                        <small
                                            v-if="submittedBitacora && nuevaBitacora.finaliza_ticket && !nuevaBitacora.explicacion_cierre"
                                            class="text-red-500">
                                            La explicación de cierre es obligatoria
                                        </small>
                                    </div>
                                </div>
                            </div>

                            <!-- Botones -->
                            <div class="flex flex-col-reverse sm:flex-row gap-3 justify-end">
                                <Button label="Cancelar" icon="pi pi-times" @click="cancelarFormularioBitacora"
                                    severity="secondary" outlined />
                                <Button label="Guardar Intervención" icon="pi pi-save" @click="guardarBitacora"
                                    :loading="guardandoBitacora"
                                    :disabled="nuevaBitacora.finaliza_ticket && !puedeSerCerrado" />
                            </div>
                        </div>
                    </div>

                    <!-- Mensaje cuando el ticket está cerrado -->
                    <div v-else-if="ticketEstaCerrado"
                        class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                        <div class="text-center py-8">
                            <i class="pi pi-lock text-6xl text-surface-400 mb-4"></i>
                            <p class="text-xl font-semibold mb-2 text-surface-900 dark:text-surface-0">Ticket Cerrado
                            </p>
                            <p class="text-surface-600 dark:text-surface-400">
                                No se pueden agregar más intervenciones a un ticket cerrado.
                            </p>
                        </div>
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
