<script setup>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { mostrarToastPuntos } from '@/service/gamificacionUtils';
import api, { getUser, hasRoleAccess } from '@/service/api';

const toast = useToast();

// Estados
const loading = ref(false);
const relevos = ref([]);
const relevoDialog = ref(false);
const deleteDialog = ref(false);
const relevo = ref({});
const submitted = ref(false);
const filteredUsuarios = ref([]);
const usuario = ref(null);

// Opciones de Estado de Sala
const estadosSala = [
    { label: 'Sin Pendientes / Todo Operativo', value: 'limpia', icon: 'pi-check-circle', color: 'success' },
    { label: 'Con Pendientes Menores', value: 'con_pendientes', icon: 'pi-exclamation-circle', color: 'warn' },
    { label: 'Situación Crítica / Urgente', value: 'critica', icon: 'pi-times-circle', color: 'danger' }
];

// Computed Properties
const casinoId = computed(() => usuario.value?.casino || null);

// Permisos: Pueden crear
const canCreate = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO']));

// Permisos: Pueden editar/eliminar
const canEditOrDelete = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS']));

onMounted(async () => {
    usuario.value = getUser();
    if (casinoId.value) {
        await cargarRelevos();
    } else {
        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No tiene un casino asignado.', life: 3000 });
    }
});

const cargarRelevos = async () => {
    if (!casinoId.value) return;
    
    loading.value = true;
    try {
        const response = await api.get('relevos-turnos/', {
            params: { 
                casino: casinoId.value,
                page_size: 10,
                ordering: '-hora_salida_real'
            }
        });
        relevos.value = (response.data.results || response.data).slice(0, 10);
    } catch (error) {

        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudieron cargar los relevos', life: 3000 });
    } finally {
        loading.value = false;
    }
};

const buscarUsuarios = async (event) => {
    try {
        const query = event.query;
        const response = await api.get('usuarios/', {
            params: {
                search: query,
                casino: casinoId.value,
                page_size: 20
            }
        });
        
        const resultados = response.data.results || response.data;
        filteredUsuarios.value = resultados.map(u => ({
            id: u.id,
            label: `${u.username} - ${u.rol_nombre || 'Sin Rol'}`,
            username: u.username
        }));
    } catch (error) {

    }
};

const openNew = () => {
    relevo.value = {
        estado_entrega: 'limpia'
    };
    submitted.value = false;
    relevoDialog.value = true;
};

const hideDialog = () => {
    relevoDialog.value = false;
    submitted.value = false;
};

const saveRelevo = async () => {
    submitted.value = true;

    if (!relevo.value.tecnico_entrante) {
        toast.add({ severity: 'warn', summary: 'Validación', detail: 'Complete los campos requeridos', life: 3000 });
        return;
    }

    loading.value = true;
    try {
        const payload = {
            casino: casinoId.value,
            tecnico_saliente: usuario.value.id, // El usuario actual es quien entrega
            tecnico_entrante: getTecnicoId(relevo.value.tecnico_entrante),
            estado_entrega: relevo.value.estado_entrega,
            pendientes_detallados: relevo.value.pendientes_detallados || '',
            novedades_generales: relevo.value.novedades_generales || ''
            // hora_salida_real se establece automáticamente en el backend
        };

        if (relevo.value.id) {
            await api.put(`relevos-turnos/${relevo.value.id}/`, payload);
            toast.add({ severity: 'success', summary: 'Éxito', detail: 'Relevo actualizado', life: 3000 });
        } else {
            const resRelevo = await api.post('relevos-turnos/', payload);
            toast.add({ severity: 'success', summary: 'Éxito', detail: 'Relevo de turno registrado correctamente', life: 3000 });
            mostrarToastPuntos(toast, resRelevo.data?.puntos_nexus);
        }

        relevoDialog.value = false;
        relevo.value = {};
        await cargarRelevos();
    } catch (error) {

        
        // Manejar errores de validación específicos del backend
        let errorDetail = 'Error al guardar el relevo';
        if (error.response?.data) {
            if (error.response.data.tecnico_entrante) {
                errorDetail = error.response.data.tecnico_entrante[0] || error.response.data.tecnico_entrante;
            } else if (error.response.data.tecnico_saliente) {
                errorDetail = error.response.data.tecnico_saliente[0] || error.response.data.tecnico_saliente;
            } else if (typeof error.response.data === 'object' && Object.keys(error.response.data).length > 0) {
                const firstKey = Object.keys(error.response.data)[0];
                errorDetail = error.response.data[firstKey][0] || error.response.data[firstKey];
            }
        }
        
        toast.add({ severity: 'error', summary: 'Error', detail: errorDetail, life: 5000 });
    } finally {
        loading.value = false;
    }
};

const editRelevo = (item) => {
    relevo.value = { 
        ...item
    };
    
    // Reconstruir objeto técnico entrante para el autocomplete
    if (item.tecnico_entrante) {
        relevo.value.tecnico_entrante = {
            id: item.tecnico_entrante,
            label: item.nombre_entrante,
            username: item.nombre_entrante
        };
    }

    relevoDialog.value = true;
};

const confirmDeleteRelevo = (item) => {
    relevo.value = item;
    deleteDialog.value = true;
};

const deleteRelevo = async () => {
    loading.value = true;
    try {
        await api.delete(`relevos-turnos/${relevo.value.id}/`);
        toast.add({ severity: 'success', summary: 'Éxito', detail: 'Relevo eliminado', life: 3000 });
        deleteDialog.value = false;
        relevo.value = {};
        await cargarRelevos();
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudo eliminar el registro', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// Helpers
const getTecnicoId = (tecnicoObj) => {
    return tecnicoObj?.id || tecnicoObj;
};

const formatDateTimeForApi = (datetime) => {
    if (!datetime) return null;
    return datetime.toISOString();
};

const getEstadoInfo = (estado) => {
    const info = estadosSala.find(e => e.value === estado);
    return info || { icon: 'pi-circle', color: 'secondary' };
};

const formatFecha = (fecha) => {
    return new Date(fecha).toLocaleString('es-MX', { 
        dateStyle: 'medium', 
        timeStyle: 'short' 
    });
};
</script>

<template>
    <div class="grid grid-cols-12 gap-8">
        <div class="col-span-12">
            <div class="card">
                <div class="flex justify-between items-center mb-6">
                    <div>
                        <h2 class="text-2xl font-bold text-surface-900 dark:text-surface-0">
                            <i class="pi pi-sync mr-2"></i>
                            Historial de Relevos de Turno
                        </h2>
                        <p class="text-surface-600 dark:text-surface-400 mt-1">
                            Últimos 10 cambios de guardia registrados
                        </p>
                    </div>
                    <div class="flex gap-2">
                        <Button 
                            icon="pi pi-refresh" 
                            rounded 
                            outlined 
                            @click="cargarRelevos"
                            :loading="loading"
                        />
                        <Button 
                            v-if="canCreate"
                            label="Registrar Relevo" 
                            icon="pi pi-plus" 
                            severity="primary" 
                            @click="openNew" 
                        />
                    </div>
                </div>

                <!-- Timeline de Relevos -->
                <div v-if="loading" class="flex justify-center items-center py-12">
                    <ProgressSpinner />
                </div>

                <Timeline 
                    v-else-if="relevos.length > 0" 
                    :value="relevos" 
                    align="alternate" 
                    class="customized-timeline"
                >
                    <template #marker="slotProps">
                        <div 
                            class="flex w-8 h-8 items-center justify-center text-white rounded-full z-10 shadow-lg"
                            :class="`bg-${getEstadoInfo(slotProps.item.estado_entrega).color}-500`"
                        >
                            <i :class="`pi ${getEstadoInfo(slotProps.item.estado_entrega).icon}`"></i>
                        </div>
                    </template>
                    
                    <template #content="slotProps">
                        <Card class="mt-3">
                            <template #header>
                                <div class="bg-surface-50 dark:bg-surface-800 p-4 border-b border-surface-200 dark:border-surface-700">
                                    <div class="flex justify-between items-start">
                                        <div>
                                            <div class="flex items-center gap-2 mb-2">
                                                <Tag 
                                                    :value="slotProps.item.estado_entrega" 
                                                    :severity="getEstadoInfo(slotProps.item.estado_entrega).color"
                                                    icon="pi pi-flag"
                                                />
                                            </div>
                                            <div class="text-sm text-surface-600 dark:text-surface-400">
                                                <i class="pi pi-clock mr-2"></i>
                                                {{ formatFecha(slotProps.item.hora_salida_real) }}
                                            </div>
                                        </div>
                                        <div v-if="canEditOrDelete" class="flex gap-2">
                                            <Button 
                                                icon="pi pi-pencil" 
                                                rounded 
                                                outlined 
                                                severity="success" 
                                                size="small"
                                                @click="editRelevo(slotProps.item)" 
                                            />
                                            <Button 
                                                icon="pi pi-trash" 
                                                rounded 
                                                outlined 
                                                severity="danger" 
                                                size="small"
                                                @click="confirmDeleteRelevo(slotProps.item)" 
                                            />
                                        </div>
                                    </div>
                                </div>
                            </template>
                            
                            <template #content>
                                <div class="space-y-3">
                                    <!-- Transición de Técnicos -->
                                    <div class="flex items-center justify-between bg-surface-50 dark:bg-surface-900 p-3 rounded-lg">
                                        <div class="flex items-center gap-2">
                                            <i class="pi pi-user text-red-500"></i>
                                            <div>
                                                <div class="text-xs text-surface-500">Sale</div>
                                                <div class="font-semibold">{{ slotProps.item.nombre_saliente }}</div>
                                            </div>
                                        </div>
                                        <i class="pi pi-arrow-right text-surface-400 text-2xl"></i>
                                        <div class="flex items-center gap-2">
                                            <i class="pi pi-user text-green-500"></i>
                                            <div>
                                                <div class="text-xs text-surface-500">Entra</div>
                                                <div class="font-semibold">{{ slotProps.item.nombre_entrante }}</div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Pendientes -->
                                    <div v-if="slotProps.item.pendientes_detallados" class="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg">
                                        <div class="flex items-start gap-2">
                                            <i class="pi pi-exclamation-triangle text-yellow-600 mt-1"></i>
                                            <div>
                                                <div class="font-semibold text-yellow-800 dark:text-yellow-400 mb-1">
                                                    Pendientes Técnicos
                                                </div>
                                                <div class="text-sm text-surface-700 dark:text-surface-300 whitespace-pre-line">
                                                    {{ slotProps.item.pendientes_detallados }}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Novedades -->
                                    <div v-if="slotProps.item.novedades_generales" class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                                        <div class="flex items-start gap-2">
                                            <i class="pi pi-info-circle text-blue-600 mt-1"></i>
                                            <div>
                                                <div class="font-semibold text-blue-800 dark:text-blue-400 mb-1">
                                                    Novedades del Turno
                                                </div>
                                                <div class="text-sm text-surface-700 dark:text-surface-300 whitespace-pre-line">
                                                    {{ slotProps.item.novedades_generales }}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </template>
                        </Card>
                    </template>
                </Timeline>

                <div v-else class="text-center py-12">
                    <i class="pi pi-inbox text-6xl text-surface-300 dark:text-surface-600 mb-4"></i>
                    <p class="text-surface-600 dark:text-surface-400 text-lg">
                        No hay relevos de turno registrados
                    </p>
                    <Button 
                        v-if="canCreate"
                        label="Registrar el primer relevo" 
                        icon="pi pi-plus" 
                        class="mt-4"
                        @click="openNew" 
                    />
                </div>
            </div>
        </div>

        <!-- Dialog de Registro/Edición -->
        <Dialog v-model:visible="relevoDialog" :style="{ width: '650px' }" header="Registro de Relevo de Turno" :modal="true" class="p-fluid">
            <div class="flex flex-col gap-4">
                <!-- Técnico que Recibe -->
                <div class="flex flex-col gap-2">
                    <label for="entrante" class="font-bold">Técnico que Recibe el Turno *</label>
                    <AutoComplete
                        id="entrante"
                        name="entrante"
                        v-model="relevo.tecnico_entrante"
                        :suggestions="filteredUsuarios"
                        @complete="buscarUsuarios"
                        optionLabel="label"
                        placeholder="Buscar técnico..."
                        dropdown
                        :invalid="submitted && !relevo.tecnico_entrante"
                    />
                    <small class="text-red-500" v-if="submitted && !relevo.tecnico_entrante">El técnico entrante es requerido.</small>
                </div>

                <!-- Estado de la Sala -->
                <div class="flex flex-col gap-2">
                    <label for="estado" class="font-bold">Estado de la Sala *</label>
                    <Select 
                        id="estado" 
                        name="estado" 
                        v-model="relevo.estado_entrega" 
                        :options="estadosSala" 
                        optionLabel="label" 
                        optionValue="value" 
                        placeholder="Seleccione estado"
                    >
                        <template #value="slotProps">
                            <div v-if="slotProps.value" class="flex items-center gap-2">
                                <i :class="`pi ${getEstadoInfo(slotProps.value).icon} text-${getEstadoInfo(slotProps.value).color}-500`"></i>
                                <span>{{ estadosSala.find(e => e.value === slotProps.value)?.label }}</span>
                            </div>
                        </template>
                        <template #option="slotProps">
                            <div class="flex items-center gap-2">
                                <i :class="`pi ${slotProps.option.icon} text-${slotProps.option.color}-500`"></i>
                                <span>{{ slotProps.option.label }}</span>
                            </div>
                        </template>
                    </Select>
                </div>

                <!-- Pendientes Detallados -->
                <div class="flex flex-col gap-2">
                    <label for="pendientes" class="font-bold">Pendientes Técnicos</label>
                    <Textarea 
                        id="pendientes" 
                        name="pendientes" 
                        v-model="relevo.pendientes_detallados" 
                        rows="4" 
                        placeholder="Lista de máquinas o tareas que quedaron sin concluir (ej: Máquina A05 con contador trabado, reintentar mañana...)"
                    />
                    <small class="text-xs text-surface-500">Opcional - Detallar tareas pendientes</small>
                </div>

                <!-- Novedades Generales -->
                <div class="flex flex-col gap-2">
                    <label for="novedades" class="font-bold">Novedades del Turno</label>
                    <Textarea 
                        id="novedades" 
                        name="novedades" 
                        v-model="relevo.novedades_generales" 
                        rows="4" 
                        placeholder="Cualquier comentario relevante sobre el personal o la sala (ej: Mayor afluencia de jugadores por evento especial...)"
                    />
                    <small class="text-xs text-surface-500">Opcional - Información adicional del turno</small>
                </div>

                <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                    <div class="flex items-start gap-2">
                        <i class="pi pi-info-circle text-blue-500 mt-1"></i>
                        <div class="text-sm text-blue-700 dark:text-blue-300">
                            <strong>Nota:</strong> Usted (<strong>{{ usuario?.username }}</strong>) quedará registrado como el técnico que entrega el turno. La hora de salida se registrará automáticamente.
                        </div>
                    </div>
                </div>
            </div>

            <template #footer>
                <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                <Button label="Registrar Relevo" icon="pi pi-check" @click="saveRelevo" :loading="loading" />
            </template>
        </Dialog>

        <!-- Dialog de Confirmación de Eliminación -->
        <Dialog v-model:visible="deleteDialog" :style="{ width: '450px' }" header="Confirmar" :modal="true">
            <div class="flex items-center gap-4">
                <i class="pi pi-exclamation-triangle !text-3xl text-red-500" />
                <span v-if="relevo">
                    ¿Está seguro de eliminar el relevo de <b>{{ relevo.nombre_saliente }}</b> a <b>{{ relevo.nombre_entrante }}</b>?
                </span>
            </div>
            <template #footer>
                <Button label="No" icon="pi pi-times" text @click="deleteDialog = false" />
                <Button label="Sí" icon="pi pi-check" severity="danger" @click="deleteRelevo" :loading="loading" />
            </template>
        </Dialog>
    </div>
</template>

<style scoped>
.customized-timeline :deep(.p-timeline-event-content) {
    line-height: 1;
}

.customized-timeline :deep(.p-timeline-event-opposite) {
    line-height: 1;
    min-width: 0;
}
</style>
