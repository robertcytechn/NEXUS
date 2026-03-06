<script setup>
import { ref, watch, computed } from 'vue';
import api, { getUser } from '@/service/api';
import { crearBitacoraTecnica } from '@/service/ticketService';
import { mostrarToastPuntos } from '@/service/gamificacionUtils';
import { useToast } from 'primevue/usetoast';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    ticketProp: {
        type: Object,
        default: () => ({})
    }
});

const emit = defineEmits(['update:visible', 'ticket-cerrado']);

const toast = useToast();
const historialBitacora = ref([]);
const loadingHistorial = ref(false);

const guardandoBitacora = ref(false);
const submittedBitacora = ref(false);

const usuario = computed(() => getUser());

// Permisos para ver si puede agregar (dependiente de rol, asumiendo lo del componente original)
const puedeAgregarBitacora = computed(() => {
    return ['SUP SISTEMAS', 'TECNICO', 'ADMINISTRADOR'].includes(usuario.value?.rol_nombre || '');
});

const ticketEstaCerrado = computed(() => props.ticketProp?.estado_ciclo === 'cerrado');

const nuevaBitacora = ref({
    tipo_intervencion: null,
    descripcion_trabajo: '',
    resultado_intervencion: null,
    estado_maquina_resultante: null,
    finaliza_ticket: false,
    explicacion_cierre: ''
});

// Catalogos quemados para opciones rapidas de Bitacora
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

const puedeSerCerrado = computed(() => {
    if (!nuevaBitacora.value.finaliza_ticket) return false;
    return nuevaBitacora.value.estado_maquina_resultante === 'operativa'
        && nuevaBitacora.value.resultado_intervencion === 'exitosa';
});

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
        case 'proceso': return 'warn';
        case 'espera': return 'info';
        case 'cerrado': return 'success';
        case 'reabierto': return 'secondary';
        default: return 'contrast';
    }
};

const formatearFechaCompleta = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleString('es-MX', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
};

const getResultadoSeverity = (resultado) => {
    const severities = { 'exitosa': 'success', 'parcial': 'warn', 'fallida': 'danger', 'espera_refaccion': 'info' };
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

const cargarHistorialBitacora = async (ticketId) => {
    loadingHistorial.value = true;
    historialBitacora.value = [];
    try {
        const response = await api.get(`bitacora-tecnica/?ticket=${ticketId}`);
        historialBitacora.value = response.data.sort((a, b) => new Date(b.fecha_registro) - new Date(a.fecha_registro));
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'No se pudo cargar el historial logístico de la máquina',
            life: 3000
        });
    } finally {
        loadingHistorial.value = false;
    }
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
            detail: 'No hay una sesión activa. Por favor, inicia sesión nuevamente.',
            life: 5000
        });
        return;
    }

    if (!nuevaBitacora.value.tipo_intervencion ||
        !nuevaBitacora.value.descripcion_trabajo?.trim() ||
        !nuevaBitacora.value.resultado_intervencion ||
        !nuevaBitacora.value.estado_maquina_resultante) {
        toast.add({ severity: 'warn', summary: 'Campos Incompletos', detail: 'Complete todos los campos obligatorios', life: 3000 });
        return;
    }

    if (nuevaBitacora.value.finaliza_ticket && !nuevaBitacora.value.explicacion_cierre?.trim()) {
        toast.add({ severity: 'warn', summary: 'Explicación Requerida', detail: 'Debe proporcionar una explicación del cierre', life: 3000 });
        return;
    }

    guardandoBitacora.value = true;

    try {
        const resultado = await crearBitacoraTecnica({
            ticketId: props.ticketProp.id,
            maquinaId: props.ticketProp.maquina,
            usuarioTecnicoId: usuario.value.id,
            tipoIntervencion: nuevaBitacora.value.tipo_intervencion,
            descripcionTrabajo: nuevaBitacora.value.descripcion_trabajo,
            resultadoIntervencion: nuevaBitacora.value.resultado_intervencion,
            estadoMaquinaResultante: nuevaBitacora.value.estado_maquina_resultante,
            finalizaTicket: nuevaBitacora.value.finaliza_ticket,
            explicacionCierre: nuevaBitacora.value.explicacion_cierre || '',
            ticketActual: props.ticketProp
        });

        if (!resultado.exito) {
            toast.add({ severity: 'error', summary: resultado.error, detail: resultado.detalle, life: 4000 });
            return;
        }

        toast.add({ severity: 'success', summary: 'Guardado', detail: resultado.mensaje, life: 3000 });
        mostrarToastPuntos(toast, resultado.puntos_nexus);

        // Capturar antes del reset si el ticket fue cerrado
        const seFinalizoTicket = nuevaBitacora.value.finaliza_ticket;

        await cargarHistorialBitacora(props.ticketProp.id);
        cancelarFormularioBitacora();

        if (seFinalizoTicket) {
            setTimeout(() => {
                emit('update:visible', false);
                emit('ticket-cerrado');
            }, 1500);
        }
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'No se pudo guardar la intervención',
            life: 4000
        });
    } finally {
        guardandoBitacora.value = false;
    }
};

watch(
    () => props.visible,
    async (newVal) => {
        if (newVal && props.ticketProp?.id) {
            await cargarHistorialBitacora(props.ticketProp.id);
        }
    }
);

</script>

<template>
    <Dialog :visible="visible" @update:visible="(val) => emit('update:visible', val)" :style="{ width: '900px' }"
        header="Historial de Ticket y Bitácora Técnica" :modal="true" :maximizable="true">
        <div v-if="ticketProp" class="flex flex-col gap-6">
            <!-- Información Base -->
            <Card>
                <template #content>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div>
                            <p class="text-sm text-surface-600 dark:text-surface-400">Folio</p>
                            <p class="font-bold font-mono text-lg text-primary">{{ ticketProp.folio }}</p>
                        </div>
                        <div>
                            <p class="text-sm text-surface-600 dark:text-surface-400">Estado</p>
                            <Tag :value="ticketProp.estado_ciclo?.toUpperCase()"
                                :severity="getEstadoSeverity(ticketProp.estado_ciclo)" />
                        </div>
                        <div>
                            <p class="text-sm text-surface-600 dark:text-surface-400">Prioridad</p>
                            <Tag :value="ticketProp.prioridad?.toUpperCase()"
                                :severity="getPrioridadSeverity(ticketProp.prioridad)" />
                        </div>
                        <div>
                            <p class="text-sm text-surface-600 dark:text-surface-400">Máquina</p>
                            <p class="font-semibold">{{ ticketProp.maquina_uid }}</p>
                        </div>
                        <div>
                            <p class="text-sm text-surface-600 dark:text-surface-400">Categoría / Subcategoría</p>
                            <p class="font-semibold capitalize">{{ ticketProp.categoria }} <span
                                    v-if="ticketProp.subcategoria">- {{ ticketProp.subcategoria }}</span></p>
                        </div>
                        <div>
                            <p class="text-sm text-surface-600 dark:text-surface-400">Reportante</p>
                            <p class="font-semibold">{{ ticketProp.reportante_nombre || 'No Especificado' }}</p>
                        </div>
                        <div class="col-span-1 md:col-span-2 lg:col-span-3">
                            <p class="text-sm text-surface-600 dark:text-surface-400">Descripción Original</p>
                            <p class="border-l-4 border-surface-200 dark:border-surface-700 pl-3 py-1 italic">{{
                                ticketProp.descripcion_problema }}</p>
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Timeline Extractivo de Intervenciones -->
            <div class="border-t border-surface-200 dark:border-surface-700 pt-4">
                <h3 class="text-xl font-semibold mb-4">Intervenciones del Historial</h3>

                <div v-if="loadingHistorial" class="text-center py-8">
                    <i class="pi pi-spin pi-spinner text-4xl text-primary"></i>
                    <p class="mt-4 text-surface-500">Cargando bitácoras asociadas...</p>
                </div>

                <Timeline v-else-if="historialBitacora.length > 0" :value="historialBitacora" align="alternate"
                    class="w-full custom-timeline">
                    <template #opposite="slotProps">
                        <small class="text-surface-500 dark:text-surface-400 block font-semibold">
                            {{ formatearFechaCompleta(slotProps.item.fecha_registro) }}
                        </small>
                    </template>
                    <template #content="slotProps">
                        <Card class="mb-4">
                            <template #title>
                                <div class="flex items-center gap-2">
                                    <Tag :value="slotProps.item.tipo_intervencion" severity="info" />
                                    <Tag :value="slotProps.item.resultado_intervencion"
                                        :severity="getResultadoSeverity(slotProps.item.resultado_intervencion)" />
                                </div>
                            </template>
                            <template #subtitle>
                                <i class="pi pi-user mr-1 text-xs"></i> Técnico: {{ slotProps.item.tecnico_nombre }}
                            </template>
                            <template #content>
                                <p class="mb-3 text-sm">{{ slotProps.item.descripcion_trabajo }}</p>
                                <div
                                    class="flex items-center gap-2 mt-2 pt-2 border-t border-surface-100 dark:border-surface-800">
                                    <span class="text-xs font-semibold uppercase text-surface-500">Estado Máquina
                                        Resultante:</span>
                                    <Tag :value="slotProps.item.estado_maquina_resultante" class="text-xs" />
                                </div>
                                <div v-if="slotProps.item.finaliza_ticket" class="mt-2 text-right">
                                    <Tag value="CIERRA TICKET" severity="success" icon="pi pi-check-circle" />
                                </div>
                            </template>
                        </Card>
                    </template>
                    <template #marker="slotProps">
                        <span class="flex items-center justify-center p-3 rounded-full z-10 shadow-sm"
                            :class="getMarkerClass(slotProps.item.resultado_intervencion)">
                            <i :class="getMarkerIcon(slotProps.item.tipo_intervencion)"></i>
                        </span>
                    </template>
                </Timeline>

                <div v-else
                    class="text-center py-8 bg-surface-50 dark:bg-surface-900 rounded-border border border-surface-200 dark:border-surface-800">
                    <i class="pi pi-clock text-4xl mb-3 text-surface-400"></i>
                    <p class="text-surface-500 font-semibold">El Ticket aún no posee bitácoras de seguimiento técnicas.
                    </p>
                </div>
            </div>

            <!-- Formulario Nueva Bitácora -->
            <div v-if="!ticketEstaCerrado && puedeAgregarBitacora"
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
                            <Chip v-for="tipo in tiposIntervencion" :key="tipo.value" :label="tipo.label" :class="[
                                'cursor-pointer transition-all duration-200 border-2',
                                nuevaBitacora.tipo_intervencion === tipo.value
                                    ? 'bg-blue-600 dark:bg-blue-500 text-white border-blue-700 dark:border-blue-400 shadow-xl scale-110 font-bold'
                                    : 'bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 border-surface-300 dark:border-surface-600 hover:border-blue-400 hover:bg-surface-200 dark:hover:bg-surface-700'
                            ]" @click="nuevaBitacora.tipo_intervencion = tipo.value" />
                        </div>
                        <small v-if="submittedBitacora && !nuevaBitacora.tipo_intervencion" class="text-red-500">
                            Debe seleccionar un tipo de intervención
                        </small>
                    </div>

                    <!-- Descripción del Trabajo -->
                    <div>
                        <label for="descripcion" class="block font-bold mb-3">Descripción del Trabajo *</label>
                        <Textarea id="descripcion" name="descripcion" v-model="nuevaBitacora.descripcion_trabajo"
                            rows="4"
                            placeholder="Detalle las acciones realizadas, pruebas ejecutadas y componentes revisados..."
                            :invalid="submittedBitacora && !nuevaBitacora.descripcion_trabajo" class="w-full" />
                        <small v-if="submittedBitacora && !nuevaBitacora.descripcion_trabajo" class="text-red-500">
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
                        <small v-if="submittedBitacora && !nuevaBitacora.resultado_intervencion" class="text-red-500">
                            Debe seleccionar un resultado
                        </small>
                    </div>

                    <!-- Estado de Máquina Resultante -->
                    <div>
                        <label class="block font-bold mb-3">Estado de Máquina Resultante *</label>
                        <div class="flex flex-wrap gap-2">
                            <Chip v-for="estado in estadosMaquina" :key="estado.value" :label="estado.label" :class="[
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
                    <div class="border-2 border-dashed border-surface-300 dark:border-surface-600 rounded-lg p-4">
                        <div class="flex items-center gap-3 mb-3">
                            <Checkbox v-model="nuevaBitacora.finaliza_ticket" :binary="true" inputId="finaliza" />
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
                            <div v-else class="bg-green-50 dark:bg-green-900/20 border border-green-500 rounded p-3">
                                <p class="text-green-700 dark:text-green-400 font-semibold flex items-center gap-2">
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
                    <div class="flex flex-col-reverse sm:flex-row gap-3 justify-end mt-4">
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
                    <p class="text-xl font-semibold mb-2 text-surface-900 dark:text-surface-0">Ticket Cerrado</p>
                    <p class="text-surface-600 dark:text-surface-400">No se pueden agregar más intervenciones a un
                        ticket cerrado.
                    </p>
                </div>
            </div>
        </div>

        <template #footer>
            <Button label="Cerrar Ficha" icon="pi pi-times" variant="outlined" @click="emit('update:visible', false)" />
        </template>
    </Dialog>
</template>

<style scoped>
:deep(.custom-timeline .p-timeline-event-opposite) {
    flex: 0 0 auto;
    min-width: 150px;
}
</style>
