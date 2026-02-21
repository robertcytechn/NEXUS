<template>
    <div class="card">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
            <div>
                <h2 class="text-3xl font-bold mb-2">Ojo de Dios <i class="pi pi-eye text-primary-500"></i></h2>
                <span class="text-surface-600 dark:text-surface-400">Auditoría global e histórico de modificaciones del sistema</span>
            </div>
            
            <Button 
                icon="pi pi-refresh" 
                label="Actualizar" 
                @click="cargarHistorial" 
                :loading="loading"
                severity="secondary" 
                outlined
            />
        </div>

        <!-- Filtros -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6 p-4 bg-surface-50 dark:bg-surface-800 rounded-xl border border-surface-200 dark:border-surface-700">
            <div class="flex flex-col gap-2">
                <label class="font-semibold text-sm">Tabla Afectada</label>
                <Dropdown 
                    v-model="filtros.tabla" 
                    :options="listaTablas" 
                    placeholder="Todas las tablas"
                    showClear 
                    class="w-full" 
                    @change="onFiltroChange"
                />
            </div>
            <div class="flex flex-col gap-2">
                <label class="font-semibold text-sm">Tipo de Acción</label>
                <Dropdown 
                    v-model="filtros.accion" 
                    :options="listaAcciones" 
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Todas las acciones"
                    showClear 
                    class="w-full" 
                    @change="onFiltroChange"
                />
            </div>
            <div class="flex flex-col gap-2">
                <label class="font-semibold text-sm">ID de Usuario</label>
                <InputText 
                    v-model="filtros.usuario" 
                    placeholder="Filtrar por ID" 
                    class="w-full" 
                    @keyup.enter="onFiltroChange"
                />
            </div>
            <div class="flex flex-col justify-end">
                <Button 
                    label="Limpiar Filtros" 
                    icon="pi pi-filter-slash" 
                    @click="limpiarFiltros"
                    severity="danger" 
                    outlined
                />
            </div>
        </div>

        <!-- Tabla Expandible -->
        <DataTable 
            ref="dt"
            v-model:expandedRows="expandedRows" 
            :value="historial" 
            :loading="loading"
            dataKey="id"
            paginator 
            :rows="50"
            :totalRecords="totalRecords"
            :lazy="true"
            @page="onPage"
            class="p-datatable-sm"
            stripedRows
        >
            <template #empty>No se encontraron registros de auditoría</template>
            <template #loading>Cargando registros históricos del sistema...</template>

            <!-- Expander Column -->
            <Column expander style="width: 3rem" />

            <Column field="fecha" header="Fecha / Hora" style="min-width: 12rem">
                <template #body="{ data }">
                    <span class="font-mono">{{ formatearFechaCompleta(data.fecha) }}</span>
                </template>
            </Column>

            <Column field="usuario_nombre" header="Usuario" style="min-width: 10rem">
                <template #body="{ data }">
                    <div class="flex items-center gap-2">
                        <i class="pi pi-user text-surface-500"></i>
                        <span class="font-semibold">{{ data.usuario_nombre || 'Sistema / Anónimo' }}</span>
                    </div>
                </template>
            </Column>

            <Column field="casino_nombre" header="Casino" style="min-width: 10rem">
                <template #body="{ data }">
                    {{ data.casino_nombre || 'Global' }}
                </template>
            </Column>

            <Column field="accion" header="Acción" style="min-width: 8rem">
                <template #body="{ data }">
                    <Tag 
                        :value="data.accion" 
                        :severity="getAccionSeverity(data.accion)" 
                        :icon="getAccionIcon(data.accion)"
                        class="w-full text-center"
                    />
                </template>
            </Column>
            
            <Column field="tabla" header="Modelo Local" style="min-width: 10rem">
                <template #body="{ data }">
                    <span class="bg-surface-200 dark:bg-surface-700 px-2 py-1 rounded font-mono text-xs">
                        {{ data.tabla }} (ID: {{ data.registro_id }})
                    </span>
                </template>
            </Column>

            <!-- Expansión: Visor JSON interactivo -->
            <template #expansion="slotProps">
                <div class="p-4 bg-surface-50 dark:bg-surface-800 rounded-lg mx-3 my-2 border border-surface-200 dark:border-surface-700 shadow-inner">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        
                        <!-- Panel Izquierdo: Datos Anteriores -->
                        <div v-if="slotProps.data.accion === 'UPDATE' || slotProps.data.accion === 'DELETE'">
                            <div class="flex items-center gap-2 mb-3 text-red-600 dark:text-red-400 font-bold border-b border-surface-200 dark:border-surface-700 pb-2">
                                <i class="pi pi-history"></i>
                                <span>Datos Anteriores</span>
                            </div>
                            <pre class="bg-surface-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm font-mono shadow">
{{ formatJSON(slotProps.data.datos_anteriores) }}
                            </pre>
                        </div>
                        
                         <!-- Centrar panel si es solo Creación y no hay datos anteriores -->
                        <div v-if="slotProps.data.accion === 'CREATE'" class="hidden md:block flex justify-center items-center opacity-50">
                            <i class="pi pi-arrow-right text-6xl text-surface-400"></i>
                        </div>

                        <!-- Panel Derecho: Datos Nuevos -->
                        <div v-if="slotProps.data.accion === 'CREATE' || slotProps.data.accion === 'UPDATE'">
                            <div class="flex items-center gap-2 mb-3 text-green-600 dark:text-green-400 font-bold border-b border-surface-200 dark:border-surface-700 pb-2">
                                <i class="pi pi-check-square"></i>
                                <span>Datos Nuevos</span>
                            </div>
                            <pre class="bg-surface-900 text-blue-300 p-4 rounded-lg overflow-x-auto text-sm font-mono shadow">
{{ formatJSON(slotProps.data.datos_nuevos) }}
                            </pre>
                        </div>

                        <div v-if="slotProps.data.accion === 'DELETE'" class="hidden md:block flex justify-center items-center opacity-50">
                            <div class="text-center text-red-500">
                                <i class="pi pi-trash text-6xl mb-2"></i>
                                <p class="font-bold">Registro Destruido</p>
                            </div>
                        </div>

                    </div>
                </div>
            </template>
        </DataTable>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import auditoriaService from '@/service/auditoriaService';
import { getUser, hasRoleAccess } from '@/service/api';

const toast = useToast();

const loading = ref(false);
const historial = ref([]);
const totalRecords = ref(0);
const expandedRows = ref({});

const listaTablas = ref([]);
const listaAcciones = ref([
    { label: 'Creaciones (CREATE)', value: 'CREATE' },
    { label: 'Modificaciones (UPDATE)', value: 'UPDATE' },
    { label: 'Eliminaciones (DELETE)', value: 'DELETE' }
]);

const filtros = ref({
    tabla: null,
    accion: null,
    usuario: null,
    entornoAdmin: true
});

const pageConfig = ref({
    page: 1,
});

onMounted(async () => {
    // Seguridad adicional: Sólo ADMIN
    const user = getUser();
    if (!user || user.rol_nombre !== 'ADMINISTRADOR') {
        window.location.href = '/';
        return;
    }

    await fetchTablas();
    await cargarHistorial();
});

const fetchTablas = async () => {
    try {
        listaTablas.value = await auditoriaService.getTablasAfectadas();
    } catch (error) {
        console.error("Tablas fallaron al cargar", error);
    }
};

const cargarHistorial = async () => {
    loading.value = true;
    try {
        const queryParams = { ...filtros.value, page: pageConfig.value.page };
        const response = await auditoriaService.getAuditoriaHistorial(queryParams);
        historial.value = response.results;
        totalRecords.value = response.count;
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'No se pudo cargar el historial de auditoría'
        });
    } finally {
        loading.value = false;
    }
};

const onFiltroChange = () => {
    pageConfig.value.page = 1;
    cargarHistorial();
};

const limpiarFiltros = () => {
    filtros.value = { tabla: null, accion: null, usuario: null, entornoAdmin: true };
    pageConfig.value.page = 1;
    cargarHistorial();
};

const onPage = (event) => {
    pageConfig.value.page = event.page + 1; // event.page es index-0
    cargarHistorial();
};

// Utilidades Visuales
const formatJSON = (obj) => {
    if (!obj) return 'Ninguno / Vacío';
    try {
        // En caso que el field haya quedado como double string, re-parsing test
        const parsed = typeof obj === 'string' ? JSON.parse(obj) : obj;
        return JSON.stringify(parsed, null, 2);
    } catch (e) {
        return obj;
    }
};

const formatearFechaCompleta = (fechaStr) => {
    if (!fechaStr) return '';
    return new Date(fechaStr).toLocaleString('es-MX', {
        year: 'numeric', month: 'short', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
};

const getAccionSeverity = (accion) => {
    switch(accion) {
        case 'CREATE': return 'success';
        case 'UPDATE': return 'info';
        case 'DELETE': return 'danger';
        default: return 'secondary';
    }
};

const getAccionIcon = (accion) => {
    switch(accion) {
        case 'CREATE': return 'pi pi-plus';
        case 'UPDATE': return 'pi pi-sync';
        case 'DELETE': return 'pi pi-trash';
        default: return 'pi pi-circle';
    }
};
</script>

<style scoped>
pre {
    white-space: pre-wrap;
    word-wrap: break-word;
}
</style>
