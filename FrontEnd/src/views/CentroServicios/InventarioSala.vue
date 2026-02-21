<script setup>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import api, { getUser, hasRoleAccess } from '@/service/api';
import inventarioService from '@/service/inventarioSalaService';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

const toast = useToast();
const confirm = useConfirm();

// Estado
const articulos = ref([]);
const loading = ref(false);
const articuloDialog = ref(false);
const articulo = ref({});
const submitted = ref(false);
const dt = ref();
const usuario = ref(getUser());

useResponsiveDataTable(dt);

// Filtros
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});

// Permisos
const canEdit = computed(() => hasRoleAccess(['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR']));

// Columnas para el Toolbar
const columnas = ref([
    { field: 'nombre', label: 'Nombre del Artículo', visible: true },
    { field: 'tipo', label: 'Tipo', visible: true },
    { field: 'cantidad', label: 'Existencia', visible: true },
    { field: 'modificado_en', label: 'Última Modificación', visible: true }
]);

const tiposArticulo = [
    { label: 'Herramienta', value: 'herramienta' },
    { label: 'Consumible', value: 'consumible' }
];

// Carga de datos
const cargarDatos = async () => {
    loading.value = true;
    try {
        // Filtra por el casino del usuario
        const casinoId = usuario.value?.casino;
        
        // Cargar inventario
        const response = await inventarioService.getInventario(casinoId);
        // Manejar paginación de DRF si es necesario, asumiendo array directo o results
        const todos = Array.isArray(response) ? response : response.results || [];
        articulos.value = todos.filter(item => item.esta_activo);
    } catch (error) {

        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudo cargar el inventario', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// Helpers de formato
const getTipoSeverity = (tipo) => {
    return tipo === 'herramienta' ? 'info' : 'warn';
};

const esColumnaVisible = (field) => {
    const col = columnas.value.find(c => c.field === field);
    return col ? col.visible : true;
};

// Acciones CRUD
const openNew = () => {
    articulo.value = {
        tipo: 'herramienta',
        cantidad: 1,
        esta_activo: true,
        casino: usuario.value?.casino // Preseleccionar casino del usuario
    };
    submitted.value = false;
    articuloDialog.value = true;
};

const editArticulo = (item) => {
    articulo.value = { ...item };
    submitted.value = false;
    articuloDialog.value = true;
};

const saveArticulo = async () => {
    submitted.value = true;

    if (articulo.value.nombre?.trim() && articulo.value.casino && articulo.value.tipo) {
        loading.value = true;
        try {
            await inventarioService.save(articulo.value);
            toast.add({ severity: 'success', summary: 'Éxito', detail: 'Artículo guardado correctamente', life: 3000 });
            articuloDialog.value = false;
            articulo.value = {};
            cargarDatos();
        } catch (error) {

            toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'Ocurrió un error al guardar', life: 3000 });
        } finally {
            loading.value = false;
        }
    }
};

const confirmToggleActivo = (item) => {
    const accion = item.esta_activo ? 'desactivar' : 'activar';
    
    confirm.require({
        message: `¿Está seguro de que desea ${accion} este artículo?`,
        header: 'Confirmación',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Sí',
        rejectLabel: 'No',
        accept: async () => {
            try {
                await inventarioService.toggleActivo(item.id, item.esta_activo);
                toast.add({ severity: 'success', summary: 'Éxito', detail: `Artículo ${accion === 'activar' ? 'activado' : 'desactivado'}`, life: 3000 });
                cargarDatos();
            } catch (error) {
                toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.error || error?.response?.data?.detail || `No se pudo ${accion} el artículo`, life: 3000 });
            }
        }
    });
};

onMounted(() => {
    cargarDatos();
});
</script>

<template>
    <div class="card">
        <Toast />
        <ConfirmDialog />

        <DataTableToolbar
            :dt="dt"
            :datos="articulos"
            titulo-reporte="Inventario de Activos y Herramientas"
            nombre-archivo="inventario_sala"
            :columnas="columnas"
            :mostrar-exportacion="true"
            :mostrar-imprimir="true"
            :mostrar-refrescar="true"
            :mostrar-selector-columnas="true"
            :mostrar-buscador="true"
            @refrescar="cargarDatos"
            v-model:columnas-seleccionadas="columnas"
            v-model:busqueda-global="filtros.global.value"
        >
            <template #acciones-extra>
                <Button 
                    v-if="canEdit"
                    label="Nuevo Artículo" 
                    icon="pi pi-plus" 
                    severity="primary" 
                    rounded
                    @click="openNew" 
                />
            </template>
        </DataTableToolbar>

        <DataTable
            ref="dt"
            :value="articulos"
            :loading="loading"
            v-model:filters="filtros"
            :globalFilterFields="['nombre', 'tipo']"
            paginator
            :rows="10"
            :rowsPerPageOptions="[5, 10, 20, 50]"
            dataKey="id"
            showGridlines
            stripedRows
            removableSort
            class="datatable-mobile"
        >
            <template #empty>
                <div class="text-center p-4">No se encontraron artículos en el inventario.</div>
            </template>

            <Column v-if="esColumnaVisible('nombre')" field="nombre" header="Nombre del Artículo" sortable style="min-width: 14rem">
                <template #body="{ data }">
                    <span class="font-semibold">{{ data.nombre }}</span>
                </template>
            </Column>

            <Column v-if="esColumnaVisible('tipo')" field="tipo" header="Tipo" sortable style="min-width: 10rem">
                <template #body="{ data }">
                    <Tag :value="data.tipo.toUpperCase()" :severity="getTipoSeverity(data.tipo)" />
                </template>
            </Column>

            <Column v-if="esColumnaVisible('cantidad')" field="cantidad" header="Existencia" sortable style="min-width: 8rem">
                <template #body="{ data }">
                    <div class="flex items-center gap-2">
                        <span class="text-lg font-bold" :class="{'text-red-500': data.cantidad === 0, 'text-green-600': data.cantidad > 0}">
                            {{ data.cantidad }}
                        </span>
                        <i v-if="data.cantidad === 0" class="pi pi-exclamation-circle text-red-500" v-tooltip="'Sin existencias'"></i>
                    </div>
                </template>
            </Column>

            <Column v-if="esColumnaVisible('modificado_en')" field="modificado_en" header="Última Modificación" sortable style="min-width: 12rem">
                <template #body="{ data }">
                    <div class="text-sm text-surface-600">
                        {{ new Date(data.modificado_en).toLocaleString('es-MX') }}
                    </div>
                    <div class="text-xs text-surface-400" v-if="data.modificado_por">
                        Por: {{ data.modificado_por }}
                    </div>
                </template>
            </Column>

            <Column header="Acciones" :exportable="false" style="min-width: 8rem" v-if="canEdit">
                <template #body="{ data }">
                    <div class="flex gap-2">
                        <Button icon="pi pi-pencil" outlined rounded severity="info" @click="editArticulo(data)" v-tooltip.top="'Editar'" />
                        <Button 
                            :icon="data.esta_activo ? 'pi pi-ban' : 'pi pi-check-circle'" 
                            outlined 
                            rounded 
                            :severity="data.esta_activo ? 'danger' : 'success'" 
                            @click="confirmToggleActivo(data)" 
                            v-tooltip.top="data.esta_activo ? 'Desactivar' : 'Activar'" 
                        />
                    </div>
                </template>
            </Column>
        </DataTable>

        <!-- Dialogo de Creación/Edición -->
        <Dialog v-model:visible="articuloDialog" :style="{ width: '500px' }" header="Detalles del Artículo" :modal="true" class="p-fluid">
            <div class="flex flex-col gap-4">
                <div>
                    <label for="nombre" class="block font-bold mb-2">Nombre del Artículo</label>
                    <InputText 
                        id="nombre" 
                        v-model.trim="articulo.nombre" 
                        required="true" 
                        autofocus 
                        :invalid="submitted && !articulo.nombre" 
                        placeholder="Ej: Taladro Percutor, Cinta Aislante"
                    />
                    <small class="text-red-500" v-if="submitted && !articulo.nombre">El nombre es obligatorio.</small>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label for="tipo" class="block font-bold mb-2">Tipo</label>
                        <Select 
                            id="tipo" 
                            v-model="articulo.tipo" 
                            :options="tiposArticulo" 
                            optionLabel="label" 
                            optionValue="value" 
                            placeholder="Seleccione Tipo"
                            :invalid="submitted && !articulo.tipo"
                        />
                        <small class="text-red-500" v-if="submitted && !articulo.tipo">El tipo es requerido.</small>
                    </div>

                    <div>
                        <label for="cantidad" class="block font-bold mb-2">Cantidad Física</label>
                        <InputNumber 
                            id="cantidad" 
                            v-model="articulo.cantidad" 
                            showButtons 
                            :min="0" 
                            integeronly
                        />
                    </div>
                </div>

                <div class="flex items-center gap-2 mt-2">
                    <Checkbox v-model="articulo.esta_activo" :binary="true" inputId="activo" />
                    <label for="activo">¿Está Activo?</label>
                </div>
            </div>

            <template #footer>
                <Button label="Cancelar" icon="pi pi-times" text @click="articuloDialog = false" />
                <Button label="Guardar" icon="pi pi-check" @click="saveArticulo" :loading="loading" />
            </template>
        </Dialog>
    </div>
</template>