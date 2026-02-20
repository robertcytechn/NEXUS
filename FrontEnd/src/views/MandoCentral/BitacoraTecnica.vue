<template>
    <div class="card">
        <h2 class="text-3xl font-bold mb-6">Bitácora Técnica</h2>

        <!-- Panel de Tickets Abiertos -->
        <div v-if="!ticketSeleccionado" class="mb-6">
            <h3 class="text-xl font-semibold mb-4">Tickets Abiertos</h3>
            
            <DataTable 
                ref="dt"
                :value="ticketsAbiertos" 
                :loading="loading"
                paginator 
                :rows="10"
                :rowsPerPageOptions="[5, 10, 20, 50]"
                dataKey="id"
                filterDisplay="row"
                v-model:filters="filtros"
                :globalFilterFields="['folio', 'maquina_uid', 'categoria', 'estado_ciclo']"
                class="datatable-mobile"
            >
                <template #empty>No hay tickets abiertos</template>
                <template #loading>Cargando tickets...</template>

                <Column field="folio" header="Folio" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <span 
                            class="font-mono font-semibold text-primary-600 dark:text-primary-400 cursor-pointer hover:underline"
                            @click="seleccionarTicket(data)"
                        >
                            {{ data.folio }}
                        </span>
                    </template>
                </Column>

                <Column field="maquina_uid" header="Máquina" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <span class="font-semibold">{{ data.maquina_uid }}</span>
                    </template>
                </Column>

                <Column field="estado_ciclo" header="Estado" sortable style="min-width: 8rem">
                    <template #body="{ data }">
                        <Tag :value="data.estado_ciclo.toUpperCase()" :severity="getEstadoSeverity(data.estado_ciclo)" />
                    </template>
                </Column>

                <Column field="categoria" header="Categoría" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <span class="capitalize">{{ data.categoria }}</span>
                    </template>
                </Column>

                <Column field="prioridad" header="Prioridad" sortable style="min-width: 8rem">
                    <template #body="{ data }">
                        <Tag :value="data.prioridad.toUpperCase()" :severity="getPrioridadSeverity(data.prioridad)" />
                    </template>
                </Column>

                <Column field="tecnico_asignado" header="Técnico" style="min-width: 12rem">
                    <template #body="{ data }">
                        <span v-if="data.tecnico_asignado_nombre">{{ data.tecnico_asignado_nombre }}</span>
                        <Tag v-else value="SIN ASIGNAR" severity="warn" />
                    </template>
                </Column>

                <Column field="creado_en" header="Fecha Reporte" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        {{ formatearFecha(data.creado_en) }}
                    </template>
                </Column>
            </DataTable>
        </div>

        <!-- Panel de Historial de Bitácora (Timeline) -->
        <div v-else>
            <!-- Botón Volver -->
            <Button 
                label="Volver a Tickets" 
                icon="pi pi-arrow-left" 
                @click="volverATickets" 
                class="mb-4"
                severity="secondary"
            />

            <!-- Información del Ticket -->
            <Card class="mb-6">
                <template #title>
                    <div class="flex justify-between items-center">
                        <span>{{ ticketSeleccionado.folio }} - {{ ticketSeleccionado.maquina_uid }}</span>
                        <Tag :value="ticketSeleccionado.estado_ciclo.toUpperCase()" :severity="getEstadoSeverity(ticketSeleccionado.estado_ciclo)" />
                    </div>
                </template>
                <template #content>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <p class="text-sm text-surface-600 dark:text-surface-400">Categoría</p>
                            <p class="font-semibold capitalize">{{ ticketSeleccionado.categoria }}</p>
                        </div>
                        <div>
                            <p class="text-sm text-surface-600 dark:text-surface-400">Prioridad</p>
                            <Tag :value="ticketSeleccionado.prioridad.toUpperCase()" :severity="getPrioridadSeverity(ticketSeleccionado.prioridad)" />
                        </div>
                        <div>
                            <p class="text-sm text-surface-600 dark:text-surface-400">Reportante</p>
                            <p class="font-semibold">{{ ticketSeleccionado.reportante_nombre || 'N/A' }}</p>
                        </div>
                        <div>
                            <p class="text-sm text-surface-600 dark:text-surface-400">Técnico Asignado</p>
                            <p class="font-semibold">{{ ticketSeleccionado.tecnico_asignado_nombre || 'Sin asignar' }}</p>
                        </div>
                        <div class="col-span-2">
                            <p class="text-sm text-surface-600 dark:text-surface-400">Descripción del Problema</p>
                            <p>{{ ticketSeleccionado.descripcion_problema }}</p>
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Timeline de Bitácora -->
            <Card class="mb-6">
                <template #title>Historial de Intervenciones</template>
                <template #content>
                    <Timeline :value="historialBitacora" align="alternate" class="w-full">
                        <template #opposite="slotProps">
                            <small class="text-surface-500 dark:text-surface-400">
                                {{ formatearFechaCompleta(slotProps.item.fecha_registro) }}
                            </small>
                        </template>
                        <template #content="slotProps">
                            <Card class="mb-4">
                                <template #title>
                                    <div class="flex items-center gap-2">
                                        <Tag :value="slotProps.item.tipo_intervencion" severity="info" />
                                        <Tag :value="slotProps.item.resultado_intervencion" :severity="getResultadoSeverity(slotProps.item.resultado_intervencion)" />
                                    </div>
                                </template>
                                <template #subtitle>
                                    Técnico: {{ slotProps.item.tecnico_nombre }}
                                </template>
                                <template #content>
                                    <p class="mb-3">{{ slotProps.item.descripcion_trabajo }}</p>
                                    <div class="flex items-center gap-2">
                                        <span class="text-sm font-semibold">Estado resultante:</span>
                                        <Tag :value="slotProps.item.estado_maquina_resultante" />
                                    </div>
                                    <div v-if="slotProps.item.finaliza_ticket" class="mt-2">
                                        <Tag value="TICKET CERRADO" severity="success" />
                                    </div>
                                </template>
                            </Card>
                        </template>
                        <template #marker="slotProps">
                            <span class="flex items-center justify-center p-3 rounded-full z-10" 
                                  :class="getMarkerClass(slotProps.item.resultado_intervencion)">
                                <i :class="getMarkerIcon(slotProps.item.tipo_intervencion)"></i>
                            </span>
                        </template>
                    </Timeline>

                    <div v-if="historialBitacora.length === 0" class="text-center py-8 text-surface-500">
                        <i class="pi pi-info-circle text-4xl mb-3"></i>
                        <p>No hay entradas de bitácora para este ticket aún</p>
                    </div>
                </template>
            </Card>

            <!-- Formulario Nueva Entrada -->
            <Card v-if="!ticketEstaCerrado">
                <template #title>Nueva Entrada de Bitácora</template>
                <template #content>
                    <div class="grid grid-cols-1 gap-4">
                        <!-- Tipo de Intervención -->
                        <div>
                            <label class="block font-bold mb-3">Tipo de Intervención *</label>
                            <div class="flex flex-wrap gap-2">
                                <Chip 
                                    v-for="tipo in tiposIntervencion" 
                                    :key="tipo.value"
                                    :label="tipo.label"
                                    :class="[
                                        'cursor-pointer transition-all duration-200 border-2',
                                        nuevaEntrada.tipo_intervencion === tipo.value 
                                            ? 'bg-blue-600 dark:bg-blue-500 text-white border-blue-700 dark:border-blue-400 shadow-xl scale-110 font-bold' 
                                            : 'bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 border-surface-300 dark:border-surface-600 hover:border-blue-400 hover:bg-surface-200 dark:hover:bg-surface-700'
                                    ]"
                                    @click="nuevaEntrada.tipo_intervencion = tipo.value"
                                />
                            </div>
                            <small v-if="submitted && !nuevaEntrada.tipo_intervencion" class="text-red-500">
                                Debe seleccionar un tipo de intervención
                            </small>
                        </div>

                        <!-- Descripción del Trabajo -->
                        <div>
                            <label for="descripcion" class="block font-bold mb-3">Descripción del Trabajo *</label>
                            <Textarea 
                                id="descripcion"
                                v-model="nuevaEntrada.descripcion_trabajo"
                                rows="4"
                                placeholder="Detalle las acciones realizadas, pruebas ejecutadas y componentes revisados..."
                                :invalid="submitted && !nuevaEntrada.descripcion_trabajo"
                                class="w-full"
                            />
                            <small v-if="submitted && !nuevaEntrada.descripcion_trabajo" class="text-red-500">
                                La descripción del trabajo es obligatoria
                            </small>
                        </div>

                        <!-- Resultado de la Intervención -->
                        <div>
                            <label class="block font-bold mb-3">Resultado de la Intervención *</label>
                            <div class="flex flex-wrap gap-2">
                                <Chip 
                                    v-for="resultado in resultadosIntervencion" 
                                    :key="resultado.value"
                                    :label="resultado.label"
                                    :class="[
                                        'cursor-pointer transition-all duration-200 border-2',
                                        nuevaEntrada.resultado_intervencion === resultado.value 
                                            ? 'bg-green-600 dark:bg-green-500 text-white border-green-700 dark:border-green-400 shadow-xl scale-110 font-bold' 
                                            : 'bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 border-surface-300 dark:border-surface-600 hover:border-green-400 hover:bg-surface-200 dark:hover:bg-surface-700'
                                    ]"
                                    @click="nuevaEntrada.resultado_intervencion = resultado.value"
                                />
                            </div>
                            <small v-if="submitted && !nuevaEntrada.resultado_intervencion" class="text-red-500">
                                Debe seleccionar un resultado
                            </small>
                        </div>

                        <!-- Estado de Máquina Resultante -->
                        <div>
                            <label class="block font-bold mb-3">Estado de Máquina Resultante *</label>
                            <div class="flex flex-wrap gap-2">
                                <Chip 
                                    v-for="estado in estadosMaquina" 
                                    :key="estado.value"
                                    :label="estado.label"
                                    :class="[
                                        'cursor-pointer transition-all duration-200 border-2',
                                        nuevaEntrada.estado_maquina_resultante === estado.value 
                                            ? 'bg-teal-600 dark:bg-teal-500 text-white border-teal-700 dark:border-teal-400 shadow-xl scale-110 font-bold' 
                                            : 'bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 border-surface-300 dark:border-surface-600 hover:border-teal-400 hover:bg-surface-200 dark:hover:bg-surface-700'
                                    ]"
                                    @click="nuevaEntrada.estado_maquina_resultante = estado.value"
                                />
                            </div>
                            <small v-if="submitted && !nuevaEntrada.estado_maquina_resultante" class="text-red-500">
                                Debe seleccionar el estado de la máquina
                            </small>
                        </div>

                        <!-- Finaliza Ticket -->
                        <div class="border-2 border-dashed border-surface-300 dark:border-surface-600 rounded-lg p-4">
                            <div class="flex items-center gap-3 mb-3">
                                <Checkbox 
                                    v-model="nuevaEntrada.finaliza_ticket" 
                                    :binary="true" 
                                    inputId="finaliza"
                                />
                                <label for="finaliza" class="font-bold text-lg cursor-pointer">
                                    ¿Esta intervención cierra el ticket?
                                </label>
                            </div>
                            
                            <!-- Validación para cerrar ticket -->
                            <div v-if="nuevaEntrada.finaliza_ticket">
                                <div v-if="!puedeSerCerrado" class="bg-red-50 dark:bg-red-900/20 border border-red-500 rounded p-3">
                                    <p class="text-red-700 dark:text-red-400 font-semibold flex items-center gap-2">
                                        <i class="pi pi-exclamation-triangle"></i>
                                        No se puede cerrar el ticket
                                    </p>
                                    <ul class="mt-2 ml-6 text-sm text-red-600 dark:text-red-300">
                                        <li v-if="nuevaEntrada.estado_maquina_resultante !== 'operativa'">
                                            • La máquina debe quedar en estado OPERATIVA
                                        </li>
                                        <li v-if="nuevaEntrada.resultado_intervencion !== 'exitosa'">
                                            • El resultado de la intervención debe ser EXITOSA
                                        </li>
                                    </ul>
                                </div>
                                <div v-else class="bg-green-50 dark:bg-green-900/20 border border-green-500 rounded p-3">
                                    <p class="text-green-700 dark:text-green-400 font-semibold flex items-center gap-2">
                                        <i class="pi pi-check-circle"></i>
                                        Al guardar se realizará en cascada:
                                    </p>
                                    <ul class="mt-2 ml-6 text-sm text-green-600 dark:text-green-300">
                                        <li>✓ Cerrar el ticket (estado_ciclo = cerrado)</li>
                                        <li>✓ Cambiar máquina a estado OPERATIVA</li>
                                        <li>✓ Guardar bitácora con timestamp</li>
                                        <li>✓ Actualizar explicación de cierre</li>
                                    </ul>
                                </div>

                                <!-- Campo de explicación de cierre -->
                                <div class="mt-4">
                                    <label for="explicacion_cierre" class="block font-bold mb-3">Explicación del Cierre *</label>
                                    <Textarea 
                                        id="explicacion_cierre"
                                        v-model="nuevaEntrada.explicacion_cierre"
                                        rows="3"
                                        placeholder="Resumen de la solución aplicada y confirmación de que el problema quedó resuelto..."
                                        :invalid="submitted && nuevaEntrada.finaliza_ticket && !nuevaEntrada.explicacion_cierre"
                                        class="w-full"
                                    />
                                    <small v-if="submitted && nuevaEntrada.finaliza_ticket && !nuevaEntrada.explicacion_cierre" class="text-red-500">
                                        La explicación de cierre es obligatoria
                                    </small>
                                </div>
                            </div>
                        </div>

                        <!-- Botones -->
                        <div class="flex gap-3 justify-end mt-4">
                            <Button 
                                label="Cancelar" 
                                icon="pi pi-times" 
                                @click="cancelarFormulario"
                                severity="secondary"
                                outlined
                            />
                            <Button 
                                label="Guardar Entrada" 
                                icon="pi pi-save" 
                                @click="guardarEntrada"
                                :loading="guardando"
                                :disabled="nuevaEntrada.finaliza_ticket && !puedeSerCerrado"
                            />
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Mensaje cuando el ticket está cerrado -->
            <Card v-else>
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-lock text-2xl"></i>
                        <span>Ticket Cerrado</span>
                    </div>
                </template>
                <template #content>
                    <div class="text-center py-8">
                        <i class="pi pi-check-circle text-6xl text-green-500 mb-4"></i>
                        <p class="text-xl font-semibold mb-2">Este ticket ha sido cerrado</p>
                        <p class="text-surface-600 dark:text-surface-400">
                            No se pueden agregar más entradas de bitácora a un ticket cerrado.
                        </p>
                    </div>
                </template>
            </Card>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { FilterMatchMode } from '@primevue/core/api';
import api, { getUser } from '@/service/api';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

const toast = useToast();

// Estado
const loading = ref(false);
const guardando = ref(false);
const submitted = ref(false);
const ticketsAbiertos = ref([]);
const ticketSeleccionado = ref(null);
const historialBitacora = ref([]);
const dt = ref();

useResponsiveDataTable(dt);

const filtros = ref({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS }
});

// Catálogos
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

// Nueva entrada inicial
const nuevaEntrada = ref({
    tipo_intervencion: null,
    descripcion_trabajo: '',
    resultado_intervencion: null,
    estado_maquina_resultante: null,
    finaliza_ticket: false,
    explicacion_cierre: ''
});

// Computed
const puedeSerCerrado = computed(() => {
    if (!nuevaEntrada.value.finaliza_ticket) return false;
    return nuevaEntrada.value.estado_maquina_resultante === 'operativa' 
        && nuevaEntrada.value.resultado_intervencion === 'exitosa';
});

const ticketEstaCerrado = computed(() => {
    return ticketSeleccionado.value?.estado_ciclo === 'cerrado';
});

// Métodos
const cargarTicketsAbiertos = async () => {
    loading.value = true;
    try {
        const response = await api.get('tickets/', {
            params: { 
                esta_activo: true
            }
        });
        // Mostrar los tickets abiertos o en proceso (excluir cerrados)
        ticketsAbiertos.value = response.data.filter(ticket => ticket.estado_ciclo !== 'cerrado');
    } catch (error) {

        toast.add({ 
            summary: 'Error', 
            detail: 'No se pudieron cargar los tickets abiertos', 
            life: 3000 
        });
    } finally {
        loading.value = false;
    }
};

const seleccionarTicket = async (ticket) => {
    ticketSeleccionado.value = ticket;
    await cargarHistorialBitacora(ticket.id);
};

const cargarHistorialBitacora = async (ticketId) => {
    loading.value = true;
    try {
        const response = await api.get(`bitacora-tecnica/?ticket=${ticketId}`);
        historialBitacora.value = response.data.sort((a, b) => 
            new Date(b.fecha_registro) - new Date(a.fecha_registro)
        );
    } catch (error) {

        toast.add({ 
            severity: 'error', 
            summary: 'Error', 
            detail: 'No se pudo cargar el historial de bitácora', 
            life: 3000 
        });
    } finally {
        loading.value = false;
    }
};

const volverATickets = () => {
    ticketSeleccionado.value = null;
    historialBitacora.value = [];
    cancelarFormulario();
};

const cancelarFormulario = () => {
    nuevaEntrada.value = {
        tipo_intervencion: null,
        descripcion_trabajo: '',
        resultado_intervencion: null,
        estado_maquina_resultante: null,
        finaliza_ticket: false,
        explicacion_cierre: ''
    };
    submitted.value = false;
};

const guardarEntrada = async () => {
    submitted.value = true;

    // Obtener usuario de localStorage
    const user = getUser();
    
    if (!user || !user.id) {
        toast.add({ 
            severity: 'error', 
            summary: 'Sesión No Válida', 
            detail: 'No hay una sesión activa. Por favor, inicia sesión nuevamente.', 
            life: 5000 
        });
        setTimeout(() => {
            window.location.href = '/auth/login';
        }, 2000);
        return;
    }

    // Validaciones de campos obligatorios
    if (!nuevaEntrada.value.tipo_intervencion || 
        !nuevaEntrada.value.descripcion_trabajo?.trim() ||
        !nuevaEntrada.value.resultado_intervencion ||
        !nuevaEntrada.value.estado_maquina_resultante) {
        toast.add({ 
            severity: 'warn', 
            summary: 'Campos Incompletos', 
            detail: 'Complete todos los campos obligatorios', 
            life: 3000 
        });
        return;
    }

    if (nuevaEntrada.value.finaliza_ticket && !nuevaEntrada.value.explicacion_cierre?.trim()) {
        toast.add({ 
            severity: 'warn', 
            summary: 'Explicación Requerida', 
            detail: 'Debe proporcionar una explicación del cierre', 
            life: 3000 
        });
        return;
    }

    guardando.value = true;

    try {
        // Usar el servicio global para crear la bitácora
        const resultado = await crearBitacoraTecnica({
            ticketId: ticketSeleccionado.value.id,
            maquinaId: ticketSeleccionado.value.maquina,
            usuarioTecnicoId: user.id,
            tipoIntervencion: nuevaEntrada.value.tipo_intervencion,
            descripcionTrabajo: nuevaEntrada.value.descripcion_trabajo,
            resultadoIntervencion: nuevaEntrada.value.resultado_intervencion,
            estadoMaquinaResultante: nuevaEntrada.value.estado_maquina_resultante,
            finalizaTicket: nuevaEntrada.value.finaliza_ticket,
            explicacionCierre: nuevaEntrada.value.explicacion_cierre || '',
            ticketActual: ticketSeleccionado.value
        });

        // Manejar el resultado
        if (!resultado.exito) {
            toast.add({
                severity: 'error',
                summary: resultado.error,
                detail: resultado.detalle,
                life: 4000
            });
            guardando.value = false;
            return;
        }

        // Auto-asignación del técnico si no está asignado o cambió
        const actualizacionTicket = {};
        
        if (!ticketSeleccionado.value.tecnico_asignado || 
            ticketSeleccionado.value.tecnico_asignado !== user.id) {
            actualizacionTicket.tecnico_asignado = user.id;
            
            // Si hay algo que actualizar y NO se cierra el ticket, hacerlo
            if (Object.keys(actualizacionTicket).length > 0 && !nuevaEntrada.value.finaliza_ticket) {
                await api.patch(`tickets/${ticketSeleccionado.value.id}/`, actualizacionTicket);
            }
        }

        // Éxito completo
        toast.add({ 
            severity: 'success', 
            summary: 'Éxito', 
            detail: resultado.mensaje, 
            life: 3000 
        });

        // Recargar datos
        await cargarHistorialBitacora(ticketSeleccionado.value.id);
        cancelarFormulario();

        // Actualizar información del ticket seleccionado SIEMPRE
        const ticketActualizado = await api.get(`tickets/${ticketSeleccionado.value.id}/`);
        ticketSeleccionado.value = ticketActualizado.data;


        // Si se cerró el ticket, volver a la lista después de un momento
        if (nuevaEntrada.value.finaliza_ticket) {
            setTimeout(() => {
                volverATickets();
                cargarTicketsAbiertos();
            }, 2000);
        }

    } catch (error) {

        toast.add({ 
            severity: 'error', 
            summary: 'Error', 
            detail: error.response?.data?.detail || error.response?.data?.usuario_tecnico?.[0] || 'No se pudo guardar la entrada de bitácora', 
            life: 4000 
        });
    } finally {
        guardando.value = false;
    }
};

// Utilidades
const formatearFecha = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleDateString('es-MX', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
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

const getEstadoSeverity = (estado) => {
    const severities = {
        'abierto': 'info',
        'proceso': 'warn',
        'espera': 'secondary',
        'cerrado': 'success',
        'reabierto': 'danger'
    };
    return severities[estado] || 'info';
};

const getPrioridadSeverity = (prioridad) => {
    const severities = {
        'baja': 'success',
        'media': 'info',
        'alta': 'warn',
        'critica': 'danger',
        'emergencia': 'danger'
    };
    return severities[prioridad] || 'info';
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

// Lifecycle
onMounted(() => {
    // Verificar que haya usuario en localStorage
    const user = getUser();
    
    if (!user || !user.id) {
        toast.add({ 
            severity: 'error', 
            summary: 'Sesión No Válida', 
            detail: 'Debes iniciar sesión para acceder a esta página', 
            life: 3000 
        });
        setTimeout(() => {
            window.location.href = '/auth/login';
        }, 2000);
        return;
    }
    
    cargarTicketsAbiertos();
});
</script>

<style scoped>
.cursor-pointer {
    cursor: pointer;
}

:deep(.p-timeline-event-opposite) {
    flex: 0 0 auto;
    min-width: 150px;
}

/* Animación suave para chips */
:deep(.p-chip) {
    transition: all 0.2s ease-in-out;
}
</style>
