<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import api, { getUser, hasRoleAccess } from '@/service/api';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

const toast = useToast();

// Estados
const loading = ref(false);
const auditorias = ref([]);
const auditoriaDialog = ref(false);
const deleteDialog = ref(false);
const auditoria = ref({});
const submitted = ref(false);
const filteredProveedores = ref([]);
const usuario = ref(null);

// Configuración de columnas para el Toolbar
const columnas = ref([
    { field: 'id', label: 'ID', visible: false },
    { field: 'proveedor_nombre', label: 'Empresa', visible: true },
    { field: 'nombre_tecnico_externo', label: 'Técnico Externo', visible: true },
    { field: 'area_acceso_display', label: 'Área de Acceso', visible: true },
    { field: 'tipo_servicio_display', label: 'Tipo de Servicio', visible: true },
    { field: 'hora_entrada', label: 'Hora Entrada', visible: true },
    { field: 'hora_salida', label: 'Hora Salida', visible: true },
    { field: 'duracion_minutos', label: 'Duración (min)', visible: true },
    { field: 'supervisor_nombre', label: 'Supervisor', visible: true },
    { field: 'descripcion_actividad', label: 'Actividades', visible: false }
]);

// Referencias para Toolbar
const dt = ref();
const toolbarRef = ref();
const filters = ref({
    global: { value: null, matchMode: 'contains' }
});

useResponsiveDataTable(dt);

// Opciones de Áreas de Acceso
const areasAcceso = [
    { label: 'Site de Servidores', value: 'site_servidores' },
    { label: 'Racks de Sala', value: 'racks_sala' },
    { label: 'Área de Máquinas (Piso)', value: 'area_maquinas' },
    { label: 'Oficinas Técnicas', value: 'oficinas_tecnicas' },
    { label: 'Bóveda / Área de Conteo', value: 'boveda_conteo' },
    { label: 'Sala de Juegos', value: 'sala' },
    { label: 'Cocina', value: 'cocina' },
    { label: 'Comedor', value: 'comedor' },
    { label: 'Cajas', value: 'cajas' },
    { label: 'JV / Monitoreo', value: 'jv' }
];

// Opciones de Tipos de Servicio
const tiposServicio = [
    { label: 'Internet y Enlaces', value: 'internet_enlaces' },
    { label: 'Aire Acondicionado / Clima', value: 'climatizacion' },
    { label: 'Energía / UPS / Plantas', value: 'energia_ups' },
    { label: 'Seguridad / CCTV', value: 'seguridad_cctv' },
    { label: 'Limpieza Especializada', value: 'limpieza_profunda' },
    { label: 'Mantenimiento de Equipo Técnico', value: 'mantenimiento_equipo' },
    { label: 'Fumigación / Sanitización', value: 'fumigacion' },
    { label: 'Reparaciones Locales', value: 'obra_civil' }
];

// Computed Properties
const casinoId = computed(() => usuario.value?.casino || null);

// Permisos de creación: pueden agregar nuevos registros
const canCreate = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO', 'GERENCIA', 'SUPERVISOR SALA']));

// Permisos de edición y eliminación: solo estos roles pueden modificar o eliminar
const canEditOrDelete = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'GERENCIA', 'SUPERVISOR SALA']));

onMounted(async () => {
    usuario.value = getUser();
    if (casinoId.value) {
        await cargarAuditorias();
    } else {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No tiene un casino asignado.', life: 3000 });
    }
});

const cargarAuditorias = async () => {
    if (!casinoId.value) return;
    
    loading.value = true;
    try {
        const response = await api.get('auditorias-externas/', {
            params: { casino: casinoId.value }
        });
        auditorias.value = response.data.results || response.data;
    } catch (error) {
        console.error('Error al cargar auditorías:', error);
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar las auditorías', life: 3000 });
    } finally {
        loading.value = false;
    }
};

const buscarProveedores = async (event) => {
    try {
        const query = event.query;
        const response = await api.get('proveedores/', {
            params: {
                search: query,
                page_size: 20
            }
        });
        
        const resultados = response.data.results || response.data;
        filteredProveedores.value = resultados.map(p => ({
            id: p.id,
            label: `${p.nombre} - ${p.rfc || 'Sin RFC'}`,
            nombre: p.nombre
        }));
    } catch (error) {
        console.error('Error buscando proveedores:', error);
    }
};

const openNew = () => {
    auditoria.value = {
        area_acceso: 'sala',
        tipo_servicio: 'mantenimiento_equipo',
        hora_entrada: new Date(),
        hora_salida: null
    };
    submitted.value = false;
    auditoriaDialog.value = true;
};

const hideDialog = () => {
    auditoriaDialog.value = false;
    submitted.value = false;
};

const saveAuditoria = async () => {
    submitted.value = true;

    // Validaciones
    if (!auditoria.value.empresa_proveedora || 
        !auditoria.value.nombre_tecnico_externo || 
        !auditoria.value.hora_entrada ||
        !auditoria.value.descripcion_actividad) {
        toast.add({ severity: 'warn', summary: 'Validación', detail: 'Complete todos los campos requeridos', life: 3000 });
        return;
    }

    // Validar que hora_salida sea mayor a hora_entrada
    if (auditoria.value.hora_salida && auditoria.value.hora_entrada) {
        const entrada = new Date(auditoria.value.hora_entrada);
        const salida = new Date(auditoria.value.hora_salida);
        
        if (salida <= entrada) {
            toast.add({ severity: 'error', summary: 'Error de Validación', detail: 'La hora de salida debe ser posterior a la hora de entrada', life: 3000 });
            return;
        }
    }

    loading.value = true;
    try {
        const payload = {
            casino: casinoId.value,
            empresa_proveedora: getProveedorId(auditoria.value.empresa_proveedora),
            nombre_tecnico_externo: auditoria.value.nombre_tecnico_externo,
            supervisor_interno: usuario.value.id,
            area_acceso: auditoria.value.area_acceso,
            tipo_servicio: auditoria.value.tipo_servicio,
            descripcion_actividad: auditoria.value.descripcion_actividad,
            hora_entrada: formatDateTimeForApi(auditoria.value.hora_entrada),
            hora_salida: auditoria.value.hora_salida ? formatDateTimeForApi(auditoria.value.hora_salida) : null
        };

        if (auditoria.value.id) {
            await api.put(`auditorias-externas/${auditoria.value.id}/`, payload);
            toast.add({ severity: 'success', summary: 'Éxito', detail: 'Auditoría actualizada', life: 3000 });
        } else {
            await api.post('auditorias-externas/', payload);
            toast.add({ severity: 'success', summary: 'Éxito', detail: 'Auditoría registrada correctamente', life: 3000 });
        }

        auditoriaDialog.value = false;
        auditoria.value = {};
        await cargarAuditorias();
    } catch (error) {
        console.error('Error al guardar:', error);
        toast.add({ severity: 'error', summary: 'Error', detail: 'Error al guardar la auditoría', life: 3000 });
    } finally {
        loading.value = false;
    }
};

const editAuditoria = (item) => {
    auditoria.value = { 
        ...item,
        hora_entrada: item.hora_entrada ? new Date(item.hora_entrada) : null,
        hora_salida: item.hora_salida ? new Date(item.hora_salida) : null
    };
    
    // Reconstruir objeto proveedor para el autocomplete
    if (item.empresa_proveedora) {
        auditoria.value.empresa_proveedora = {
            id: item.empresa_proveedora,
            label: item.proveedor_nombre,
            nombre: item.proveedor_nombre
        };
    }

    auditoriaDialog.value = true;
};

const confirmDeleteAuditoria = (item) => {
    auditoria.value = item;
    deleteDialog.value = true;
};

const deleteAuditoria = async () => {
    loading.value = true;
    try {
        await api.delete(`auditorias-externas/${auditoria.value.id}/`);
        toast.add({ severity: 'success', summary: 'Éxito', detail: 'Auditoría eliminada', life: 3000 });
        deleteDialog.value = false;
        auditoria.value = {};
        await cargarAuditorias();
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar el registro', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// Helpers
const getProveedorId = (proveedorObj) => {
    return proveedorObj?.id || proveedorObj;
};

const formatDateTimeForApi = (datetime) => {
    if (!datetime) return null;
    return datetime.toISOString();
};

const formatDuration = (minutos) => {
    if (!minutos) return 'En curso';
    
    const horas = Math.floor(minutos / 60);
    const mins = minutos % 60;
    
    if (horas > 0) {
        return `${horas}h ${mins}m`;
    }
    return `${mins}m`;
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
                    :datos="auditorias"
                    titulo-reporte="Auditorías de Servicios Externos"
                    nombre-archivo="auditorias_externas"
                    :columnas="columnas"
                    @refrescar="cargarAuditorias"
                    v-model:columnas-seleccionadas="columnas"
                >
                    <template #acciones-extra>
                        <Button 
                            v-if="canCreate"
                            label="Registrar Visita" 
                            icon="pi pi-plus" 
                            severity="primary" 
                            class="mr-2" 
                            @click="openNew" 
                        />
                    </template>
                </DataTableToolbar>

                <DataTable
                    ref="dt"
                    :value="auditorias"
                    :loading="loading"
                    v-model:filters="filters"
                    dataKey="id"
                    :paginator="true"
                    :rows="10"
                    :rowsPerPageOptions="[5, 10, 25]"
                    paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
                    currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} registros"
                    :globalFilterFields="['proveedor_nombre', 'nombre_tecnico_externo', 'area_acceso_display', 'tipo_servicio_display', 'supervisor_nombre']"
                    stripedRows
                    showGridlines
                    class="datatable-mobile"
                >
                    <template #empty>No se encontraron auditorías.</template>

                    <Column field="proveedor_nombre" header="Empresa Proveedora" sortable style="min-width: 12rem">
                        <template #body="slotProps">
                            <span class="font-bold">{{ slotProps.data.proveedor_nombre }}</span>
                        </template>
                    </Column>

                    <Column field="nombre_tecnico_externo" header="Técnico Externo" sortable style="min-width: 12rem"></Column>

                    <Column field="area_acceso_display" header="Área de Acceso" sortable style="min-width: 12rem">
                        <template #body="slotProps">
                            <Tag :value="slotProps.data.area_acceso_display" severity="info" />
                        </template>
                    </Column>

                    <Column field="tipo_servicio_display" header="Tipo de Servicio" sortable style="min-width: 14rem">
                        <template #body="slotProps">
                            <Tag :value="slotProps.data.tipo_servicio_display" severity="secondary" />
                        </template>
                    </Column>

                    <Column field="hora_entrada" header="Entrada" sortable style="min-width: 10rem">
                        <template #body="slotProps">
                            {{ new Date(slotProps.data.hora_entrada).toLocaleString('es-MX', { dateStyle: 'short', timeStyle: 'short' }) }}
                        </template>
                    </Column>

                    <Column field="hora_salida" header="Salida" sortable style="min-width: 10rem">
                        <template #body="slotProps">
                            <span v-if="slotProps.data.hora_salida">
                                {{ new Date(slotProps.data.hora_salida).toLocaleString('es-MX', { dateStyle: 'short', timeStyle: 'short' }) }}
                            </span>
                            <Tag v-else value="En curso" severity="warn" />
                        </template>
                    </Column>

                    <Column field="duracion_minutos" header="Duración" sortable style="min-width: 8rem">
                        <template #body="slotProps">
                            <span class="font-semibold">{{ formatDuration(slotProps.data.duracion_minutos) }}</span>
                        </template>
                    </Column>

                    <Column field="supervisor_nombre" header="Supervisor" sortable style="min-width: 10rem"></Column>

                    <Column header="Acciones" :exportable="false" style="min-width: 8rem" v-if="canEditOrDelete">
                        <template #body="slotProps">
                            <Button icon="pi pi-pencil" outlined rounded severity="success" class="mr-2" @click="editAuditoria(slotProps.data)" />
                            <Button icon="pi pi-trash" outlined rounded severity="danger" @click="confirmDeleteAuditoria(slotProps.data)" />
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>

        <!-- Dialog de Registro/Edición -->
        <Dialog v-model:visible="auditoriaDialog" :style="{ width: '700px' }" header="Registro de Visita Externa" :modal="true" class="p-fluid">
            <div class="flex flex-col gap-4">
                <!-- Empresa Proveedora -->
                <div class="flex flex-col gap-2">
                    <label for="proveedor" class="font-bold">Empresa Proveedora *</label>
                    <AutoComplete
                        id="proveedor"
                        v-model="auditoria.empresa_proveedora"
                        :suggestions="filteredProveedores"
                        @complete="buscarProveedores"
                        optionLabel="label"
                        placeholder="Buscar empresa..."
                        dropdown
                        :invalid="submitted && !auditoria.empresa_proveedora"
                    />
                    <small class="text-red-500" v-if="submitted && !auditoria.empresa_proveedora">La empresa es requerida.</small>
                </div>

                <!-- Técnico Externo -->
                <div class="flex flex-col gap-2">
                    <label for="tecnico" class="font-bold">Nombre del Técnico Externo *</label>
                    <InputText 
                        id="tecnico" 
                        v-model="auditoria.nombre_tecnico_externo" 
                        placeholder="Nombre completo del técnico"
                        :invalid="submitted && !auditoria.nombre_tecnico_externo"
                    />
                    <small class="text-red-500" v-if="submitted && !auditoria.nombre_tecnico_externo">El nombre del técnico es requerido.</small>
                </div>

                <!-- Área y Tipo de Servicio -->
                <div class="grid grid-cols-2 gap-4">
                    <div class="flex flex-col gap-2">
                        <label for="area" class="font-bold">Área de Acceso *</label>
                        <Select 
                            id="area" 
                            v-model="auditoria.area_acceso" 
                            :options="areasAcceso" 
                            optionLabel="label" 
                            optionValue="value" 
                            placeholder="Seleccione área"
                        />
                    </div>
                    <div class="flex flex-col gap-2">
                        <label for="tipo" class="font-bold">Tipo de Servicio *</label>
                        <Select 
                            id="tipo" 
                            v-model="auditoria.tipo_servicio" 
                            :options="tiposServicio" 
                            optionLabel="label" 
                            optionValue="value" 
                            placeholder="Seleccione tipo"
                        />
                    </div>
                </div>

                <!-- Cronometría: Entrada y Salida -->
                <div class="grid grid-cols-2 gap-4">
                    <div class="flex flex-col gap-2">
                        <label for="entrada" class="font-bold">Hora de Entrada *</label>
                        <DatePicker 
                            id="entrada" 
                            v-model="auditoria.hora_entrada" 
                            showTime 
                            hourFormat="24"
                            dateFormat="dd/mm/yy"
                            showIcon
                            :invalid="submitted && !auditoria.hora_entrada"
                        />
                        <small class="text-red-500" v-if="submitted && !auditoria.hora_entrada">Hora de entrada requerida.</small>
                    </div>
                    <div class="flex flex-col gap-2">
                        <label for="salida" class="font-bold">Hora de Salida</label>
                        <DatePicker 
                            id="salida" 
                            v-model="auditoria.hora_salida" 
                            showTime 
                            hourFormat="24"
                            dateFormat="dd/mm/yy"
                            showIcon
                            placeholder="Opcional - Completar al salir"
                        />
                        <small class="text-xs text-surface-500">Debe ser posterior a la hora de entrada</small>
                    </div>
                </div>

                <!-- Relato Técnico -->
                <div class="flex flex-col gap-2">
                    <label for="actividad" class="font-bold">Actividades Realizadas *</label>
                    <Textarea 
                        id="actividad" 
                        v-model="auditoria.descripcion_actividad" 
                        rows="5" 
                        placeholder="Detalle qué trabajos realizó el técnico externo (ej: cambio de cable UTP, instalación de AP, revisión de clima...)"
                        :invalid="submitted && !auditoria.descripcion_actividad"
                    />
                    <small class="text-red-500" v-if="submitted && !auditoria.descripcion_actividad">La descripción de actividades es requerida.</small>
                </div>

                <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                    <div class="flex items-start gap-2">
                        <i class="pi pi-info-circle text-blue-500 mt-1"></i>
                        <div class="text-sm text-blue-700 dark:text-blue-300">
                            <strong>Nota:</strong> Este registro quedará asociado automáticamente al casino <strong>{{ usuario?.casino_nombre }}</strong> 
                            y usted será registrado como el supervisor interno que autorizó el acceso.
                        </div>
                    </div>
                </div>
            </div>

            <template #footer>
                <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                <Button label="Registrar" icon="pi pi-check" @click="saveAuditoria" :loading="loading" />
            </template>
        </Dialog>

        <!-- Dialog de Confirmación de Eliminación -->
        <Dialog v-model:visible="deleteDialog" :style="{ width: '450px' }" header="Confirmar" :modal="true">
            <div class="flex items-center gap-4">
                <i class="pi pi-exclamation-triangle !text-3xl text-red-500" />
                <span v-if="auditoria">
                    ¿Está seguro de eliminar el registro de <b>{{ auditoria.proveedor_nombre }}</b> - <b>{{ auditoria.nombre_tecnico_externo }}</b>?
                </span>
            </div>
            <template #footer>
                <Button label="No" icon="pi pi-times" text @click="deleteDialog = false" />
                <Button label="Sí" icon="pi pi-check" severity="danger" @click="deleteAuditoria" :loading="loading" />
            </template>
        </Dialog>
    </div>
</template>
