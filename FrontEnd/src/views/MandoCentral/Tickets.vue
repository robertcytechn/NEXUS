<script setup>
import { ref, onMounted, watch } from 'vue';
import api, { getUser } from '@/service/api';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';


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

        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los datos', life: 3000 });
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

const saveTicket = async () => {
    submitted.value = true;

    // Validaciones básicas
    if (ticket.value.maquina && ticket.value.categoria && ticket.value.descripcion_problema?.trim()) {
        loading.value = true;
        const payload = { ...ticket.value };
        
        // Si estamos creando un ticket nuevo, agregar el reportante del usuario logueado
        if (!ticket.value.id) {
            const user = getUser();
            if (user && user.id) {
                payload.reportante = user.id;
            }
            
            // Agregar UID de la máquina a la descripción
            const maquinaSeleccionada = maquinas.value.find(m => m.id === payload.maquina);
            if (maquinaSeleccionada && maquinaSeleccionada.uid_sala) {
                payload.descripcion_problema = `${payload.descripcion_problema} | Máquina: ${maquinaSeleccionada.uid_sala}`;
            }
        }

        try {
            // Guardar ticket (crear o actualizar)
            if (ticket.value.id) {
                await api.put(`tickets/${ticket.value.id}/`, payload);
            } else {
                const response = await api.post('tickets/', payload);
                
                // Incrementar contador de fallas de la máquina
                const maquinaId = payload.maquina;
                if (maquinaId) {
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
                            detail: `No se pudo actualizar el contador de fallas`, 
                            life: 4000 
                        });
                    }
                }
            }
            
            const accion = ticket.value.id ? 'actualizado' : 'creado';
            toast.add({ 
                severity: 'success', 
                summary: 'Éxito', 
                detail: `Ticket ${accion} correctamente`, 
                life: 3000 
            });
            
            ticketDialog.value = false;
            ticket.value = {};
            cargarDatos();
        } catch (error) {
            // Manejar error específico de validación de tickets abiertos
            if (error.response?.data?.error) {
                const errorData = error.response.data;
                toast.add({ 
                    severity: 'error', 
                    summary: errorData.error || 'Error de validación', 
                    detail: errorData.mensaje || 'No se pudo guardar el ticket', 
                    life: 5000 
                });
            } else {
                toast.add({ 
                    severity: 'error', 
                    summary: 'Error', 
                    detail: 'No se pudo guardar el ticket', 
                    life: 3000 
                });
            }
        } finally {
            loading.value = false;
        }
    }
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

                toast.add({ severity: 'error', summary: 'Error', detail: `No se pudo ${accion} el ticket`, life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

const verHistorial = async (ticketData) => {
    ticketSeleccionado.value = ticketData;
    historialDialog.value = true;
    await cargarHistorialBitacora(ticketData.id);
};

const cargarHistorialBitacora = async (ticketId) => {
    loadingHistorial.value = true;
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
        loadingHistorial.value = false;
    }
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
            <DataTableToolbar
                ref="toolbarRef"
                :dt="dt"
                :datos="tickets"
                titulo-reporte="Gestión de Tickets de Soporte"
                nombre-archivo="tickets"
                :columnas="columnas"
                :mostrar-exportacion="true"
                :mostrar-imprimir="true"
                :mostrar-refrescar="true"
                :mostrar-selector-columnas="true"
                :mostrar-buscador="true"
                @refrescar="cargarDatos"
                v-model:columnas-seleccionadas="columnas"
            >
                <template #acciones-extra>
                    <Button 
                        icon="pi pi-plus" 
                        label="Nuevo Ticket"
                        rounded
                        severity="primary"
                        @click="openNew"
                    />
                </template>
            </DataTableToolbar>
            
            <!-- DataTable -->
            <DataTable 
                ref="dt"
                :value="tickets" 
                :loading="loading"
                v-model:filters="filtros"
                :globalFilterFields="['folio', 'maquina_uid', 'categoria', 'subcategoria', 'descripcion_problema', 'reportante_nombre', 'reportante_rol']"
                paginator 
                :rows="10" 
                :rowsPerPageOptions="[5, 10, 20, 50]"
                dataKey="id"
                filterDisplay="menu"
                showGridlines
                stripedRows
                class="datatable-mobile"
            >
                <template #empty>
                    <div class="text-center p-4">No se encontraron tickets registrados.</div>
                </template>
                
                <template #loading>Cargando tickets...</template>
                
                <Column v-if="esColumnaVisible('folio')" field="folio" header="Folio" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <span 
                            class="font-bold font-mono text-primary-600 dark:text-primary-400 cursor-pointer hover:underline"
                            @click="verHistorial(data)"
                            v-tooltip.top="'Ver historial de bitácora'"
                        >
                            {{ data.folio || 'Pendiente' }}
                        </span>
                    </template>
                </Column>
                
                <Column v-if="esColumnaVisible('maquina_uid')" field="maquina_uid" header="Máquina" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <!-- Ajustar campo según lo que devuelva el backend (uid_sala, numero_serie, etc) -->
                        {{ data.maquina_uid || data.maquina }} 
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('categoria')" field="categoria" header="Categoría" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <span class="capitalize">{{ data.categoria }}</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('subcategoria')" field="subcategoria" header="Subcategoría" sortable style="min-width: 12rem" />

                <Column v-if="esColumnaVisible('prioridad')" field="prioridad" header="Prioridad" sortable style="min-width: 8rem">
                    <template #body="{ data }">
                        <Tag :value="data.prioridad.toUpperCase()" :severity="getPrioridadSeverity(data.prioridad)" />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('estado_ciclo')" field="estado_ciclo" header="Estado" sortable style="min-width: 8rem">
                    <template #body="{ data }">
                        <Tag :value="data.estado_ciclo.toUpperCase()" :severity="getEstadoSeverity(data.estado_ciclo)" />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('reportante_nombre')" field="reportante_nombre" header="Reportante" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2" v-if="data.reportante">
                            <i class="pi pi-user-edit text-primary"></i>
                            <div class="flex flex-col">
                                <span class="font-semibold">{{ data.reportante_nombre }} {{ data.reportante_apellidos }}</span>
                            </div>
                        </div>
                        <span v-else class="text-surface-400 italic">No especificado</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('reportante_rol')" field="reportante_rol" header="Rol" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <div v-if="data.reportante_rol" class="flex items-center gap-2">
                            <i class="pi pi-id-card text-surface-500"></i>
                            <span class="text-sm">{{ data.reportante_rol }}</span>
                        </div>
                        <span v-else class="text-surface-400 italic text-sm">-</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('creado_en')" field="creado_en" header="Fecha Creación" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="text-sm">{{ formatearFecha(data.creado_en) }}</div>
                    </template>
                </Column>
                
                <Column header="Acciones" :exportable="false" style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button 
                                icon="pi pi-pencil" 
                                size="small"
                                severity="info"
                                rounded 
                                outlined
                                @click="editarTicket(data)"
                                v-tooltip.top="'Editar / Gestionar'"
                            />
                            <Button 
                                :icon="data.esta_activo ? 'pi pi-ban' : 'pi pi-check-circle'" 
                                size="small"
                                :severity="data.esta_activo ? 'warning' : 'success'"
                                rounded 
                                outlined
                                @click="toggleActivarTicket(data)"
                                v-tooltip.top="data.esta_activo ? 'Archivar' : 'Restaurar'"
                            />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <!-- Dialogo de Edición/Creación -->
            <Dialog v-model:visible="ticketDialog" :style="{ width: '700px' }" header="Detalles del Ticket" :modal="true">
                <div class="flex flex-col gap-6">
                    
                    <!-- Fila 1: Identificación -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="folio" class="block font-bold mb-3">Folio</label>
                            <InputText id="folio" :value="ticket.folio || 'Se generará automáticamente'" disabled fluid class="bg-surface-100 dark:bg-surface-800 font-mono" />
                        </div>
                        <div>
                            <label for="estado_ciclo" class="block font-bold mb-3">Estado del Ciclo</label>
                            <Select id="estado_ciclo" v-model="ticket.estado_ciclo" :options="estadosCiclo" optionLabel="label" optionValue="value" fluid />
                        </div>
                    </div>

                    <!-- Fila 2: Relaciones -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="maquina" class="block font-bold mb-3">Máquina Afectada</label>
                            <Select 
                                id="maquina" 
                                v-model="ticket.maquina" 
                                :options="maquinas" 
                                optionLabel="uid_sala" 
                                optionValue="id" 
                                placeholder="Seleccione Máquina" 
                                filter
                                fluid 
                                :invalid="submitted && !ticket.maquina"
                            >
                                <template #option="slotProps">
                                    <div class="flex flex-col">
                                        <span class="font-bold">{{ slotProps.option.uid_sala }}</span>
                                        <span class="text-xs text-surface-500">{{ slotProps.option.casino_nombre }} - {{ slotProps.option.modelo_nombre }}</span>
                                    </div>
                                </template>
                            </Select>
                            <small class="text-red-500" v-if="submitted && !ticket.maquina">La máquina es obligatoria.</small>
                        </div>
                    </div>

                    <!-- Fila 3: Clasificación -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label for="categoria" class="block font-bold mb-3">Categoría</label>
                            <Select id="categoria" v-model="ticket.categoria" :options="categorias" optionLabel="label" optionValue="value" placeholder="Seleccione" fluid :invalid="submitted && !ticket.categoria" />
                            <small class="text-red-500" v-if="submitted && !ticket.categoria">Requerido.</small>
                        </div>
                        <div>
                            <label for="subcategoria" class="block font-bold mb-3">Subcategoría</label>
                            <InputText id="subcategoria" v-model="ticket.subcategoria" placeholder="Ej. Billetero, Pantalla..." fluid />
                        </div>
                        <div>
                            <label for="prioridad" class="block font-bold mb-3">Prioridad</label>
                            <Select id="prioridad" v-model="ticket.prioridad" :options="prioridades" optionLabel="label" optionValue="value" fluid />
                        </div>
                    </div>

                    <!-- Fila 4: Descripción -->
                    <div>
                        <label for="descripcion" class="block font-bold mb-3">Descripción del Problema</label>
                        <Textarea id="descripcion" v-model="ticket.descripcion_problema" rows="4" fluid :invalid="submitted && !ticket.descripcion_problema" />
                        <small class="text-red-500" v-if="submitted && !ticket.descripcion_problema">La descripción es obligatoria.</small>
                    </div>

                    <!-- Fila 5: Seguimiento (Solo visible si ya existe el ticket) -->
                    <div v-if="ticket.id" class="border-t border-surface-200 dark:border-surface-700 pt-4 flex flex-col gap-4">
                        <div class="font-bold text-surface-500">Seguimiento y Cierre</div>
                        
                        <div>
                            <label for="notas" class="block font-bold mb-3">Notas de Seguimiento</label>
                            <Textarea id="notas" v-model="ticket.notas_seguimiento" rows="3" fluid placeholder="Bitácora de acciones realizadas..." />
                        </div>

                        <div v-if="ticket.estado_ciclo === 'cerrado'">
                            <label for="cierre" class="block font-bold mb-3">Explicación de Cierre</label>
                            <Textarea id="cierre" v-model="ticket.explicacion_cierre" rows="3" fluid class="bg-green-50 dark:bg-green-900/20" placeholder="Solución final aplicada..." />
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                            <div>
                                <span class="font-bold text-surface-600">Reaperturas:</span> {{ ticket.contador_reaperturas }}
                            </div>
                            <div>
                                <span class="font-bold text-surface-600">Creado por:</span> {{ ticket.creado_por || 'Sistema' }}
                            </div>
                        </div>
                    </div>

                </div>

                <template #footer>
                    <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                    <Button label="Guardar" icon="pi pi-check" @click="saveTicket" />
                </template>
            </Dialog>

            <!-- Dialog de Historial de Bitácora -->
            <Dialog 
                v-model:visible="historialDialog" 
                :style="{ width: '900px' }" 
                header="Historial de Bitácora Técnica" 
                :modal="true"
                :maximizable="true"
            >
                <div v-if="ticketSeleccionado" class="flex flex-col gap-6">
                    <!-- Información del Ticket -->
                    <Card>
                        <template #content>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <p class="text-sm text-surface-600 dark:text-surface-400">Folio</p>
                                    <p class="font-bold font-mono text-lg">{{ ticketSeleccionado.folio }}</p>
                                </div>
                                <div>
                                    <p class="text-sm text-surface-600 dark:text-surface-400">Estado</p>
                                    <Tag :value="ticketSeleccionado.estado_ciclo.toUpperCase()" :severity="getEstadoSeverity(ticketSeleccionado.estado_ciclo)" />
                                </div>
                                <div>
                                    <p class="text-sm text-surface-600 dark:text-surface-400">Máquina</p>
                                    <p class="font-semibold">{{ ticketSeleccionado.maquina_uid }}</p>
                                </div>
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
                                <div class="col-span-2">
                                    <p class="text-sm text-surface-600 dark:text-surface-400">Descripción del Problema</p>
                                    <p>{{ ticketSeleccionado.descripcion_problema }}</p>
                                </div>
                            </div>
                        </template>
                    </Card>

                    <!-- Timeline de Bitácora -->
                    <div class="border-t border-surface-200 dark:border-surface-700 pt-4">
                        <h3 class="text-xl font-semibold mb-4">Historial de Intervenciones</h3>
                        
                        <div v-if="loadingHistorial" class="text-center py-8">
                            <i class="pi pi-spin pi-spinner text-4xl text-primary"></i>
                            <p class="mt-4 text-surface-500">Cargando historial...</p>
                        </div>

                        <Timeline v-else-if="historialBitacora.length > 0" :value="historialBitacora" align="alternate" class="w-full">
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

                        <div v-else class="text-center py-8 text-surface-500">
                            <i class="pi pi-info-circle text-4xl mb-3"></i>
                            <p>No hay entradas de bitácora para este ticket aún</p>
                        </div>
                    </div>
                </div>

                <template #footer>
                    <Button label="Cerrar" icon="pi pi-times" @click="historialDialog = false" />
                </template>
            </Dialog>
        </div>
    </div>
</template>

<style scoped>
:deep(.p-timeline-event-opposite) {
    flex: 0 0 auto;
    min-width: 150px;
}
</style>
