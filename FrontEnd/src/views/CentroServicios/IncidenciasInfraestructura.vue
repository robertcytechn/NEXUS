
<script setup>
import { ref, onMounted, computed } from 'vue';
import infraestructuraService from '@/service/infraestructuraService';
import { useToast } from 'primevue/usetoast';
import { hasRoleAccess, getUser } from '@/service/api';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import Card from 'primevue/card';
import Divider from 'primevue/divider';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

const incidencias = ref([]);
const casinos = ref([]);
const loading = ref(false);
const dt = ref();
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});

useResponsiveDataTable(dt);
const toast = useToast();
const incidenciaDialog = ref(false);
const incidencia = ref({});
const submitted = ref(false);
const detalleDialog = ref(false);
const incidenciaDetalle = ref(null);
const usuario = ref(getUser());

const canExport = computed(() => hasRoleAccess(['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR']));
const canCreate = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA']));


const columnas = ref([
    { field: 'titulo', label: 'Título', visible: true },
    { field: 'categoria', label: 'Categoría', visible: true },
    { field: 'severidad', label: 'Severidad', visible: true },
    { field: 'afecta_operacion', label: 'Afecta Operación', visible: true },
    { field: 'hora_inicio', label: 'Hora Inicio', visible: true },
    { field: 'hora_fin', label: 'Hora Fin', visible: true },
    { field: 'creado_en', label: 'Fecha Registro', visible: true }
]);

const categorias = [
    { label: 'Falla Eléctrica / Luz', value: 'electrica' },
    { label: 'Filtración / Agua / Gotera', value: 'agua' },
    { label: 'Climatización / Aire Acondicionado', value: 'clima' },
    { label: 'Proveedor de Internet / Enlace', value: 'red_externa' },
    { label: 'Estructura / Paredes / Techos', value: 'obra_civil' },
    { label: 'Otros Eventos Externos', value: 'otros' }
];

const severidades = [
    { label: 'Baja (Sin afectación)', value: 'baja' },
    { label: 'Media (Afectación parcial)', value: 'media' },
    { label: 'Alta (Riesgo operativo)', value: 'alta' },
    { label: 'Crítica (Cierre de sala/área)', value: 'critica' }
];

const cargarIncidencias = async () => {
    loading.value = true;
    try {
        let data = await infraestructuraService.getIncidencias();

        // Filtro para ENCARGADO AREA: Solo ver sus propios reportes
        if (usuario.value && usuario.value.rol_nombre === 'ENCARGADO AREA') {
            const username = usuario.value.username;
            if (username) {
                data = data.filter(item => item.creado_por === username);
            }
        }

        incidencias.value = data;
    } catch (error) {
        console.error('Error al cargar incidencias:', error);
        toast.add({ 
            severity: 'error', 
            summary: 'Error', 
            detail: 'No se pudo cargar la lista de incidencias', 
            life: 3000 
        });
    } finally {
        loading.value = false;
    }
};

const cargarCasinos = async () => {
    try {
        casinos.value = await infraestructuraService.getCasinos();
    } catch (error) {
        console.error('Error al cargar casinos:', error);
    }
};

const formatearFechaHora = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleString('es-MX', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
};

const esColumnaVisible = (field) => {
    const columna = columnas.value.find(c => c.field === field);
    return columna ? columna.visible : true;
};

const getSeveridadSeverity = (severidad) => {
    const severities = {
        'baja': 'info',
        'media': 'warn',
        'alta': 'danger',
        'critica': 'danger'
    };
    return severities[severidad] || 'secondary';
};

const getCategoriaNombre = (categoria) => {
    const cat = categorias.find(c => c.value === categoria);
    return cat ? cat.label : categoria;
};

const getSeveridadNombre = (severidad) => {
    const sev = severidades.find(s => s.value === severidad);
    return sev ? sev.label.split(' ')[0] : severidad;
};

const tituloReporte = computed(() => {
    if (usuario.value && usuario.value.casino_nombre) {
        return `Registro de Incidencias de Infraestructura - ${usuario.value.casino_nombre}`;
    }
    return 'Registro de Incidencias de Infraestructura';
});

const openNew = () => {
    incidencia.value = {
        esta_activo: true,
        afecta_operacion: false,
        severidad: 'media',
        casino: usuario.value?.casino || null
    };
    submitted.value = false;
    incidenciaDialog.value = true;
};

const hideDialog = () => {
    incidenciaDialog.value = false;
    submitted.value = false;
};

const saveIncidencia = async () => {
    submitted.value = true;
    if (incidencia.value.titulo?.trim() && incidencia.value.casino && incidencia.value.hora_inicio) {
        loading.value = true;
        try {
            await infraestructuraService.saveIncidencia(incidencia.value);
            toast.add({ 
                severity: 'success', 
                summary: 'Éxito', 
                detail: `Incidencia ${incidencia.value.id ? 'actualizada' : 'registrada'} correctamente`, 
                life: 3000 
            });
            incidenciaDialog.value = false;
            incidencia.value = {};
            cargarIncidencias();
        } catch (error) {
            console.error(error);
            toast.add({ 
                severity: 'error', 
                summary: 'Error', 
                detail: 'No se pudo guardar la incidencia', 
                life: 3000 
            });
        } finally {
            loading.value = false;
        }
    }
};

const verDetalleIncidencia = (data) => {
    incidenciaDetalle.value = data;
    detalleDialog.value = true;
};


onMounted(() => {
    cargarIncidencias();
    cargarCasinos();
});
</script>

<template>
    <div class="card">
        <Toast />
        
        <DataTableToolbar
            :dt="dt"
            :datos="incidencias"
            :titulo-reporte="tituloReporte"
            nombre-archivo="incidencias-infraestructura"
            :columnas="columnas"
            :mostrar-exportacion="canExport"
            :mostrar-imprimir="canExport"
            :mostrar-refrescar="true"
            :mostrar-selector-columnas="true"
            :mostrar-buscador="true"
            @refrescar="cargarIncidencias"
            v-model:columnas-seleccionadas="columnas"
            v-model:busqueda-global="filtros.global.value"
        >
            <template #acciones-extra>
                <Button 
                    v-if="canCreate"
                    icon="pi pi-plus" 
                    label="Nueva Incidencia"
                    rounded
                    severity="danger"
                    @click="openNew"
                />
            </template>
        </DataTableToolbar>
        
        <DataTable 
            ref="dt"
            :value="incidencias" 
            :loading="loading"
            v-model:filters="filtros"
            :globalFilterFields="['titulo', 'categoria', 'severidad', 'descripcion']"
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
                <div class="text-center p-4">No se encontraron incidencias registradas.</div>
            </template>
            
            <template #loading>Cargando incidencias...</template>
            
            <Column v-if="esColumnaVisible('titulo')" field="titulo" header="Título" sortable style="min-width: 15rem">
                <template #body="{ data }">
                    <span 
                        class="font-semibold text-primary-600 dark:text-primary-400 cursor-pointer hover:underline"
                        @click="verDetalleIncidencia(data)"
                        v-tooltip.top="'Ver detalle completo'"
                    >
                        {{ data.titulo }}
                    </span>
                </template>
            </Column>

            <Column v-if="esColumnaVisible('categoria')" field="categoria" header="Categoría" sortable style="min-width: 12rem">
                <template #body="{ data }">
                    <Tag :value="getCategoriaNombre(data.categoria)" severity="secondary" />
                </template>
            </Column>

            <Column v-if="esColumnaVisible('severidad')" field="severidad" header="Severidad" sortable style="min-width: 10rem">
                <template #body="{ data }">
                    <Tag 
                        :value="getSeveridadNombre(data.severidad)" 
                        :severity="getSeveridadSeverity(data.severidad)" 
                    />
                </template>
            </Column>

            <Column v-if="esColumnaVisible('afecta_operacion')" field="afecta_operacion" header="Afecta Operación" sortable style="min-width: 10rem">
                <template #body="{ data }">
                    <Tag 
                        :value="data.afecta_operacion ? 'SÍ' : 'NO'" 
                        :severity="data.afecta_operacion ? 'danger' : 'success'" 
                    />
                </template>
            </Column>

            <Column v-if="esColumnaVisible('hora_inicio')" field="hora_inicio" header="Hora Inicio" sortable style="min-width: 12rem">
                <template #body="{ data }">
                    <div class="flex items-center gap-2">
                        <i class="pi pi-calendar text-blue-500"></i>
                        <span>{{ formatearFechaHora(data.hora_inicio) }}</span>
                    </div>
                </template>
            </Column>

            <Column v-if="esColumnaVisible('hora_fin')" field="hora_fin" header="Hora Fin" sortable style="min-width: 12rem">
                <template #body="{ data }">
                    <div v-if="data.hora_fin" class="flex items-center gap-2">
                        <i class="pi pi-calendar-minus text-green-500"></i>
                        <span>{{ formatearFechaHora(data.hora_fin) }}</span>
                    </div>
                    <span v-else class="text-surface-400 italic text-sm">En curso</span>
                </template>
            </Column>
            
            <Column v-if="esColumnaVisible('creado_en')" field="creado_en" header="Fecha Registro" sortable style="min-width: 12rem">
                <template #body="{ data }">
                    <div class="text-sm text-surface-600">
                        {{ formatearFechaHora(data.creado_en) }}
                    </div>
                </template>
            </Column>
        </DataTable>

        <Dialog 
            v-model:visible="incidenciaDialog" 
            :style="{ width: '650px' }" 
            header="Detalles de la Incidencia" 
            :modal="true"
            class="p-fluid"
        >
            <div class="flex flex-col gap-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label for="casino" class="block font-bold mb-3">Casino Afectado *</label>
                        <Select 
                            id="casino" 
                            v-model="incidencia.casino" 
                            :options="casinos" 
                            optionLabel="label" 
                            optionValue="value"
                            placeholder="Selecciona un casino"
                            :invalid="submitted && !incidencia.casino"
                            fluid
                            :disabled="!!usuario?.casino"
                        />
                        <small class="text-red-500" v-if="submitted && !incidencia.casino">El casino es obligatorio.</small>
                    </div>

                    <div>
                        <label for="severidad" class="block font-bold mb-3">Severidad *</label>
                        <Select 
                            id="severidad" 
                            v-model="incidencia.severidad" 
                            :options="severidades" 
                            optionLabel="label" 
                            optionValue="value"
                            placeholder="Selecciona severidad"
                            fluid
                        />
                    </div>
                </div>

                <div>
                    <label for="titulo" class="block font-bold mb-3">Título del Evento *</label>
                    <InputText 
                        id="titulo" 
                        v-model.trim="incidencia.titulo" 
                        required="true" 
                        autofocus 
                        :invalid="submitted && !incidencia.titulo" 
                        fluid 
                        placeholder="Ej: Apagón zona sur, Gotera fila 5"
                    />
                    <small class="text-red-500" v-if="submitted && !incidencia.titulo">El título es obligatorio.</small>
                </div>

                <div>
                    <label for="categoria" class="block font-bold mb-3">Categoría *</label>
                    <Select 
                        id="categoria" 
                        v-model="incidencia.categoria" 
                        :options="categorias" 
                        optionLabel="label" 
                        optionValue="value"
                        placeholder="Selecciona la categoría"
                        fluid
                    />
                </div>
                
                <div>
                    <label for="descripcion" class="block font-bold mb-3">Descripción Detallada</label>
                    <Textarea 
                        id="descripcion" 
                        v-model="incidencia.descripcion" 
                        rows="4" 
                        fluid 
                        placeholder="Relato completo de lo ocurrido y afectaciones visibles..."
                    />
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label for="hora_inicio" class="block font-bold mb-3">Hora de Inicio *</label>
                        <DatePicker 
                            id="hora_inicio" 
                            v-model="incidencia.hora_inicio" 
                            showTime 
                            hourFormat="24"
                            fluid
                            :invalid="submitted && !incidencia.hora_inicio"
                            dateFormat="dd/mm/yy"
                        />
                        <small class="text-red-500" v-if="submitted && !incidencia.hora_inicio">La hora de inicio es obligatoria.</small>
                    </div>
                    <div>
                        <label for="hora_fin" class="block font-bold mb-3">Hora de Finalización</label>
                        <DatePicker 
                            id="hora_fin" 
                            v-model="incidencia.hora_fin" 
                            showTime 
                            hourFormat="24"
                            fluid
                            dateFormat="dd/mm/yy"
                        />
                    </div>
                </div>

                <div class="flex items-center gap-4 mt-2">
                    <div class="flex items-center">
                        <Checkbox v-model="incidencia.afecta_operacion" :binary="true" inputId="afecta_operacion" />
                        <label for="afecta_operacion" class="ml-2">¿Afecta Operación?</label>
                    </div>

                    <div class="flex items-center">
                        <Checkbox v-model="incidencia.esta_activo" :binary="true" inputId="esta_activo" />
                        <label for="esta_activo" class="ml-2">¿Está Activo?</label>
                    </div>
                </div>

                <div v-if="incidencia.id" class="border-t border-surface-200 dark:border-surface-700 pt-4">
                    <div class="font-bold mb-3 text-surface-500 dark:text-surface-400">Auditoría</div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Creado por</label>
                            <InputText id="creado_por" name="creado_por" :value="incidencia.creado_por || 'Sistema'" disabled fluid class="opacity-100" />
                        </div>
                        <div>
                            <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Fecha Registro</label>
                            <InputText id="fecha_registro" name="fecha_registro" :value="formatearFechaHora(incidencia.creado_en)" disabled fluid class="opacity-100" />
                        </div>
                    </div>
                </div>
            </div>

            <template #footer>
                <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                <Button label="Guardar" icon="pi pi-check" @click="saveIncidencia" />
            </template>
        </Dialog>

        <Dialog v-model:visible="detalleDialog" :style="{ width: '850px' }" header="Detalle de la Incidencia" :modal="true" :maximizable="true">
            <div v-if="incidenciaDetalle" class="flex flex-col gap-5 p-4 bg-surface-50 dark:bg-surface-800 rounded-lg">

                <Card class="shadow-md">
                    <template #content>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
                            <!-- Casino -->
                            <div class="flex items-start gap-3">
                                <i class="pi pi-building text-lg text-primary mt-1"></i>
                                <div>
                                    <label class="block font-bold text-surface-600 dark:text-surface-300">Casino</label>
                                    <p class="font-semibold text-lg">{{ incidenciaDetalle.casino_nombre }}</p>
                                </div>
                            </div>
                            <!-- Categoría -->
                            <div class="flex items-start gap-3">
                                <i class="pi pi-tag text-lg text-primary mt-1"></i>
                                <div>
                                    <label class="block font-bold text-surface-600 dark:text-surface-300">Categoría</label>
                                    <Tag :value="getCategoriaNombre(incidenciaDetalle.categoria)" rounded />
                                </div>
                            </div>
                            <!-- Severidad -->
                            <div class="flex items-start gap-3">
                                <i class="pi pi-shield text-lg text-primary mt-1"></i>
                                <div>
                                    <label class="block font-bold text-surface-600 dark:text-surface-300">Severidad</label>
                                    <Tag :value="getSeveridadNombre(incidenciaDetalle.severidad)" :severity="getSeveridadSeverity(incidenciaDetalle.severidad)" rounded />
                                </div>
                            </div>
                            <!-- Afecta Operación -->
                            <div class="flex items-start gap-3">
                                <i :class="['pi', incidenciaDetalle.afecta_operacion ? 'pi-exclamation-triangle' : 'pi-check-circle', 'text-lg', incidenciaDetalle.afecta_operacion ? 'text-red-500' : 'text-green-500', 'mt-1']"></i>
                                <div>
                                    <label class="block font-bold text-surface-600 dark:text-surface-300">Afecta Operación</label>
                                    <Tag :value="incidenciaDetalle.afecta_operacion ? 'SÍ' : 'NO'" :severity="incidenciaDetalle.afecta_operacion ? 'danger' : 'success'" />
                                </div>
                            </div>
                            <!-- Estado -->
                             <div class="flex items-start gap-3">
                                <i :class="['pi', incidenciaDetalle.esta_activo ? 'pi-play-circle' : 'pi-stop-circle', 'text-lg', incidenciaDetalle.esta_activo ? 'text-green-500' : 'text-gray-500', 'mt-1']"></i>
                                <div>
                                    <label class="block font-bold text-surface-600 dark:text-surface-300">Estado</label>
                                    <Tag :value="incidenciaDetalle.esta_activo ? 'Activo' : 'Cerrado'" :severity="incidenciaDetalle.esta_activo ? 'success' : 'secondary'" />
                                </div>
                            </div>
                        </div>
                    </template>
                </Card>

                <Card class="shadow-md">
                    <template #title><div class="text-lg font-bold">Título: {{ incidenciaDetalle.titulo }}</div></template>
                    <template #content>
                        <p v-if="incidenciaDetalle.descripcion" class="text-surface-700 dark:text-surface-200">{{ incidenciaDetalle.descripcion }}</p>
                        <p v-else class="text-surface-400 italic">No hay descripción detallada.</p>
                    </template>
                </Card>

                <Divider />

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card>
                         <template #title><div class="text-base font-semibold">Registro de Tiempos</div></template>
                        <template #content>
                            <div class="flex flex-col gap-4">
                                <div class="flex items-center gap-3">
                                    <i class="pi pi-calendar-plus text-blue-500 text-xl"></i>
                                    <div>
                                        <label class="font-bold text-sm text-surface-500">Inicio del Evento</label>
                                        <p>{{ formatearFechaHora(incidenciaDetalle.hora_inicio) }}</p>
                                    </div>
                                </div>
                                <div class="flex items-center gap-3">
                                    <i class="pi pi-calendar-times text-green-500 text-xl"></i>
                                    <div>
                                        <label class="font-bold text-sm text-surface-500">Fin del Evento</label>
                                        <p v-if="incidenciaDetalle.hora_fin">{{ formatearFechaHora(incidenciaDetalle.hora_fin) }}</p>
                                        <p v-else class="italic text-surface-400">En curso</p>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </Card>

                    <Card>
                         <template #title><div class="text-base font-semibold">Auditoría</div></template>
                        <template #content>
                             <div class="flex flex-col gap-4">
                                <div class="flex items-center gap-3">
                                    <i class="pi pi-user-plus text-surface-500 text-xl"></i>
                                    <div>
                                        <label class="font-bold text-sm text-surface-500">Registrado por</label>
                                        <p>{{ incidenciaDetalle.creado_por || 'Sistema' }} el {{ formatearFechaHora(incidenciaDetalle.creado_en) }}</p>
                                    </div>
                                </div>
                                <div class="flex items-center gap-3">
                                    <i class="pi pi-user-edit text-surface-500 text-xl"></i>
                                    <div>
                                        <label class="font-bold text-sm text-surface-500">Última Modificación</label>
                                        <p v-if="incidenciaDetalle.modificado_por">{{ incidenciaDetalle.modificado_por }} el {{ formatearFechaHora(incidenciaDetalle.modificado_en) }}</p>
                                        <p v-else class="italic text-surface-400">Sin modificaciones</p>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </Card>
                </div>

                <div v-if="incidenciaDetalle.notas_internas">
                    <Divider />
                    <Card>
                        <template #title><div class="text-base font-semibold">Notas Internas</div></template>
                        <template #content>
                            <p class="text-sm bg-surface-100 dark:bg-surface-700 p-3 rounded-md">{{ incidenciaDetalle.notas_internas }}</p>
                        </template>
                    </Card>
                </div>
            </div>
            <template #footer>
                <Button label="Cerrar" icon="pi pi-times" @click="detalleDialog = false" text />
            </template>
        </Dialog>
    </div>
</template>
