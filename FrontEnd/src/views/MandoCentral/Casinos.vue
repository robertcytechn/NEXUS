<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '@/service/api';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

const casinos = ref([]);
const loading = ref(false);
const dt = ref(); // Referencia al DataTable
const toolbarRef = ref(); // Referencia al Toolbar

useResponsiveDataTable(dt);
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();
const confirm = useConfirm();
const casinoDialog = ref(false);
const casino = ref({});
const submitted = ref(false);

// Sincronizar buscador del toolbar con filtros del DataTable
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Columnas configurables
const columnas = ref([
    { field: 'nombre', label: 'Nombre', visible: true },
    { field: 'identificador', label: 'Identificador', visible: true },
    { field: 'ciudad', label: 'Ciudad', visible: true },
    { field: 'telefono', label: 'Teléfono', visible: true },
    { field: 'horario_apertura', label: 'Apertura', visible: true },
    { field: 'horario_cierre', label: 'Cierre', visible: true },
    { field: 'encargado', label: 'Encargado', visible: true },
    { field: 'direccion', label: 'Dirección', visible: true },
    { field: 'esta_activo', label: 'Estado', visible: true },
    { field: 'creado_en', label: 'Fecha Registro', visible: true }
]);

// Cargar casinos desde la API
const cargarCasinos = async () => {
    loading.value = true;
    try {
        const response = await api.get('casinos/lista/');
        casinos.value = response.data;
    } catch (error) {
        console.error('Error al cargar casinos:', error);
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar la lista de casinos', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// Formatear fecha
const formatearFecha = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleString('es-MX', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// Función para verificar si una columna está visible
const esColumnaVisible = (field) => {
    const columna = columnas.value.find(c => c.field === field);
    return columna ? columna.visible : true;
};

// Acciones
const editarCasino = (data) => {
    casino.value = { ...data };
    
    // Convertir strings de hora a objetos Date para el TimePicker
    const convertirHora = (horaStr) => {
        if (!horaStr) return null;
        const [hours, minutes] = horaStr.split(':');
        const date = new Date();
        date.setHours(parseInt(hours), parseInt(minutes), 0);
        return date;
    };

    if (casino.value.horario_apertura) casino.value.horario_apertura = convertirHora(casino.value.horario_apertura);
    if (casino.value.horario_cierre) casino.value.horario_cierre = convertirHora(casino.value.horario_cierre);
    
    casinoDialog.value = true;
};

const openNew = () => {
    casino.value = {
        esta_activo: true
    };
    submitted.value = false;
    casinoDialog.value = true;
};

const hideDialog = () => {
    casinoDialog.value = false;
    submitted.value = false;
};

const saveCasino = async () => {
    submitted.value = true;

    if (casino.value.nombre?.trim()) {
        loading.value = true;
        
        // Preparar payload y formatear horas
        const payload = { ...casino.value };
        const formatTime = (date) => {
            if (!date) return null;
            return date.getHours().toString().padStart(2, '0') + ':' + date.getMinutes().toString().padStart(2, '0');
        };

        if (payload.horario_apertura instanceof Date) payload.horario_apertura = formatTime(payload.horario_apertura);
        if (payload.horario_cierre instanceof Date) payload.horario_cierre = formatTime(payload.horario_cierre);

        try {
            if (casino.value.id) {
                await api.put(`casinos/${casino.value.id}/`, payload);
                toast.add({ severity: 'success', summary: 'Éxito', detail: 'Casino actualizado correctamente', life: 3000 });
            } else {
                await api.post('casinos/', payload);
                toast.add({ severity: 'success', summary: 'Éxito', detail: 'Casino creado correctamente', life: 3000 });
            }
            casinoDialog.value = false;
            casino.value = {};
            cargarCasinos();
        } catch (error) {
            console.error(error);
            toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo guardar el casino', life: 3000 });
        } finally {
            loading.value = false;
        }
    }
};

const toggleActivarCasino = (data) => {
    const accion = data.esta_activo ? 'desactivar' : 'activar';
    
    confirm.require({
        message: `¿Estás seguro de que deseas ${accion} el casino "${data.nombre}"?`,
        header: 'Confirmar Acción',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: {
            label: 'Cancelar',
            severity: 'secondary',
            outlined: true
        },
        acceptProps: {
            label: 'Confirmar',
            severity: data.esta_activo ? 'danger' : 'success'
        },
        accept: async () => {
            loading.value = true;
            try {
                await api.patch(`casinos/${data.id}/switch-estado/`, {});
                toast.add({ severity: 'success', summary: 'Éxito', detail: `Casino ${accion === 'activar' ? 'activado' : 'desactivado'} correctamente`, life: 3000 });
                cargarCasinos();
            } catch (error) {
                console.error(error);
                toast.add({ severity: 'error', summary: 'Error', detail: `No se pudo ${accion} el casino`, life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

onMounted(() => {
    cargarCasinos();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <div class="card">
            <Toast />
            <ConfirmDialog />
            
            <!-- Toolbar personalizable -->
            <DataTableToolbar
                ref="toolbarRef"
                :dt="dt"
                :datos="casinos"
                titulo-reporte="Gestión de Casinos y Salas"
                nombre-archivo="casinos"
                :columnas="columnas"
                :mostrar-exportacion="true"
                :mostrar-imprimir="true"
                :mostrar-refrescar="true"
                :mostrar-selector-columnas="true"
                :mostrar-buscador="true"
                @refrescar="cargarCasinos"
                v-model:columnas-seleccionadas="columnas"
            >
                <template #acciones-extra>
                    <Button 
                        icon="pi pi-plus" 
                        label="Nuevo Casino"
                        rounded
                        severity="primary"
                        @click="openNew"
                    />
                </template>
            </DataTableToolbar>
            
            <DataTable 
                ref="dt"
                :value="casinos" 
                :loading="loading"
                v-model:filters="filtros"
                :globalFilterFields="['nombre', 'identificador', 'ciudad', 'encargado', 'direccion']"
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
                    <div class="text-center p-4">
                        No se encontraron casinos registrados.
                    </div>
                </template>
                
                <template #loading>
                    Cargando información de casinos...
                </template>
                
                <Column 
                    v-if="esColumnaVisible('nombre')"
                    field="nombre" 
                    header="Nombre" 
                    sortable 
                    style="min-width: 14rem"
                >
                    <template #body="{ data }">
                        <span class="font-bold">{{ data.nombre }}</span>
                    </template>
                </Column>
                
                <Column 
                    v-if="esColumnaVisible('identificador')"
                    field="identificador" 
                    header="ID" 
                    sortable 
                    style="min-width: 8rem"
                />

                <Column 
                    v-if="esColumnaVisible('ciudad')"
                    field="ciudad" 
                    header="Ciudad" 
                    sortable 
                    style="min-width: 10rem"
                />
                
                <Column 
                    v-if="esColumnaVisible('telefono')"
                    field="telefono" 
                    header="Teléfono" 
                    sortable 
                    style="min-width: 10rem"
                />

                <Column 
                    v-if="esColumnaVisible('horario_apertura')"
                    field="horario_apertura" 
                    header="Apertura" 
                    sortable 
                    style="min-width: 8rem"
                />

                <Column 
                    v-if="esColumnaVisible('horario_cierre')"
                    field="horario_cierre" 
                    header="Cierre" 
                    sortable 
                    style="min-width: 8rem"
                />

                <Column 
                    v-if="esColumnaVisible('encargado')"
                    field="encargado" 
                    header="Encargado" 
                    sortable 
                    style="min-width: 12rem"
                />

                <Column 
                    v-if="esColumnaVisible('direccion')"
                    field="direccion" 
                    header="Dirección" 
                    sortable 
                    style="min-width: 20rem"
                >
                    <template #body="{ data }">
                        <div class="text-sm">{{ data.direccion || 'Sin dirección registrada' }}</div>
                    </template>
                </Column>
                
                <Column 
                    v-if="esColumnaVisible('esta_activo')"
                    field="esta_activo" 
                    header="Estado" 
                    sortable 
                    style="min-width: 8rem"
                >
                    <template #body="{ data }">
                        <Tag 
                            :value="data.esta_activo ? 'Activo' : 'Inactivo'" 
                            :severity="data.esta_activo ? 'success' : 'danger'" 
                        />
                    </template>
                </Column>
                
                <Column 
                    v-if="esColumnaVisible('creado_en')"
                    field="creado_en" 
                    header="Fecha Registro" 
                    sortable 
                    style="min-width: 12rem"
                >
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
                                @click="editarCasino(data)"
                                v-tooltip.top="'Editar'"
                            />
                            <Button 
                                :icon="data.esta_activo ? 'pi pi-ban' : 'pi pi-check-circle'" 
                                size="small"
                                :severity="data.esta_activo ? 'warning' : 'success'"
                                rounded 
                                outlined
                                @click="toggleActivarCasino(data)"
                                v-tooltip.top="data.esta_activo ? 'Desactivar' : 'Activar'"
                            />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <Dialog v-model:visible="casinoDialog" :style="{ width: '500px' }" header="Detalles del Casino" :modal="true">
                <div class="flex flex-col gap-6">
                    <div>
                        <label for="nombre" class="block font-bold mb-3">Nombre del Casino</label>
                        <InputText id="nombre" v-model.trim="casino.nombre" required="true" autofocus :invalid="submitted && !casino.nombre" fluid />
                        <small class="text-red-500" v-if="submitted && !casino.nombre">El nombre es obligatorio.</small>
                    </div>
                    
                    <div>
                        <label for="identificador" class="block font-bold mb-3">Identificador</label>
                        <InputText id="identificador" v-model.trim="casino.identificador" fluid />
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="ciudad" class="block font-bold mb-3">Ciudad</label>
                            <InputText id="ciudad" v-model="casino.ciudad" fluid />
                        </div>
                        <div>
                            <label for="telefono" class="block font-bold mb-3">Teléfono</label>
                            <InputText id="telefono" v-model="casino.telefono" fluid />
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="horario_apertura" class="block font-bold mb-3">Horario Apertura</label>
                            <DatePicker id="horario_apertura" v-model="casino.horario_apertura" timeOnly fluid hourFormat="24" />
                        </div>
                        <div>
                            <label for="horario_cierre" class="block font-bold mb-3">Horario Cierre</label>
                            <DatePicker id="horario_cierre" v-model="casino.horario_cierre" timeOnly fluid hourFormat="24" />
                        </div>
                    </div>

                    <div>
                        <label for="encargado" class="block font-bold mb-3">Nombre del Encargado</label>
                        <InputText id="encargado" v-model="casino.encargado" fluid />
                    </div>
                    
                    <div>
                        <label for="direccion" class="block font-bold mb-3">Dirección Física</label>
                        <Textarea id="direccion" v-model="casino.direccion" rows="3" cols="20" fluid placeholder="Calle, Número, Colonia, Ciudad..." />
                    </div>

                    <div class="flex items-center mt-2">
                        <Checkbox v-model="casino.esta_activo" :binary="true" inputId="esta_activo" />
                        <label for="esta_activo" class="ml-2">¿Está Operativo?</label>
                    </div>

                    <div v-if="casino.id" class="border-t border-surface-200 dark:border-surface-700 pt-4">
                        <div class="font-bold mb-3 text-surface-500 dark:text-surface-400">Auditoría</div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Creado por</label>
                                <InputText id="creado_por" name="creado_por" :value="casino.creado_por || 'Sistema'" disabled fluid class="opacity-100" />
                            </div>
                            <div>
                                <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Fecha Registro</label>
                                <InputText id="creado_en" name="creado_en" :value="formatearFecha(casino.creado_en)" disabled fluid class="opacity-100" />
                            </div>
                        </div>
                    </div>
                </div>

                <template #footer>
                    <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                    <Button label="Guardar" icon="pi pi-check" @click="saveCasino" />
                </template>
            </Dialog>
        </div>
    </div>
</template>