<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '@/service/api';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

const roles = ref([]);
const loading = ref(false);
const dt = ref(); // Referencia al DataTable
const toolbarRef = ref(); // Referencia al Toolbar

// Hacer el DataTable responsive en móvil
useResponsiveDataTable(dt);
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();
const confirm = useConfirm();
const rolDialog = ref(false);
const rol = ref({});
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
    { field: 'descripcion', label: 'Descripción', visible: true },
    { field: 'nivel', label: 'Nivel', visible: true },
    { field: 'esta_activo', label: 'Estado', visible: true },
    { field: 'creado_en', label: 'Fecha Creación', visible: true }
]);

// Datos de referencia para la guía de niveles (Diccionario)
const guiaNiveles = [
    { nivel: '0 - 10', rol: 'Observador', area: 'Auditoría Externa', accion: 'Solo lectura. Consulta de estados.', severity: 'secondary', icon: 'pi pi-eye' },
    { nivel: '11 - 30', rol: 'Solicitante', area: 'Operación Sala', accion: 'Reporte Rápido de fallas.', severity: 'secondary', icon: 'pi pi-id-card' },
    { nivel: '31 - 50', rol: 'Proveedor', area: 'Servicios Externos', accion: 'Bitácora de entrada/salida.', severity: 'secondary', icon: 'pi pi-truck' },
    { nivel: '51 - 70', rol: 'Encargado de Área', area: 'Jefes Operativos', accion: 'Gestión de inventario local.', severity: 'success', icon: 'pi pi-box' },
    { nivel: '71 - 100', rol: 'Supervisor Sala', area: 'Jefes de Turno', accion: 'Validación de relevos.', severity: 'success', icon: 'pi pi-users' },
    { nivel: '101 - 140', rol: 'Técnico Sistemas', area: 'Campo', accion: 'Gestión total de tickets y máquinas.', severity: 'warn', icon: 'pi pi-wrench' },
    { nivel: '141 - 165', rol: 'Sup. de Sistemas', area: 'Coordinación', accion: 'Autorización de guías y proveedores.', severity: 'info', icon: 'pi pi-sitemap' },
    { nivel: '166 - 185', rol: 'Gerencia / Socios', area: 'Directivos', accion: 'KPIs y reportes ejecutivos.', severity: 'help', icon: 'pi pi-chart-bar' },
    { nivel: '186 - 199', rol: 'DB Admin', area: 'Soporte Senior', accion: 'Gestión de usuarios y roles.', severity: 'danger', icon: 'pi pi-database' },
    { nivel: '200', rol: 'Director Sistemas', area: 'Arquitecto Raíz', accion: 'Control absoluto y auditoría.', severity: 'contrast', icon: 'pi pi-shield' }
];

// Cargar roles desde la API
const cargarRoles = async () => {
    loading.value = true;
    try {
        const response = await api.get('roles/lista/');
        roles.value = response.data;
    } catch (error) {

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

// Función helper para determinar el severity del nivel
const getNivelSeverity = (nivel) => {
    if (nivel >= 200) return 'danger';
    if (nivel >= 150) return 'info';
    if (nivel >= 100) return 'warning';
    if (nivel >= 50) return 'success';
    return 'secondary';
};

// Función para verificar si una columna está visible
const esColumnaVisible = (field) => {
    const columna = columnas.value.find(c => c.field === field);
    return columna ? columna.visible : true;
};

// Acciones
const editarRol = (data) => {
    if (data.nivel === 200) {
        toast.add({ severity: 'warn', summary: 'Acción Restringida', detail: 'El Rol Maestro (Nivel 200) no puede ser modificado.', life: 3000 });
        return;
    }
    rol.value = { ...data };
    rolDialog.value = true;
};

const openNew = () => {
    rol.value = {
        esta_activo: true,
        nivel: 0
    };
    submitted.value = false;
    rolDialog.value = true;
};

const hideDialog = () => {
    rolDialog.value = false;
    submitted.value = false;
};

const saveRol = async () => {
    submitted.value = true;

    if (rol.value.nombre?.trim()) {
        loading.value = true;
        try {
            if (rol.value.id) {
                await api.put(`roles/${rol.value.id}/`, rol.value);
                toast.add({ severity: 'success', summary: 'Éxito', detail: 'Rol actualizado', life: 3000 });
            } else {
                await api.post('roles/', rol.value);
                toast.add({ severity: 'success', summary: 'Éxito', detail: 'Rol creado', life: 3000 });
            }
            rolDialog.value = false;
            rol.value = {};
            cargarRoles();
        } catch (error) {

            toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudo guardar el rol', life: 3000 });
        } finally {
            loading.value = false;
        }
    }
};

const toggleActivarRol = (data) => {
    if (data.nivel === 200) {
        toast.add({ severity: 'warn', summary: 'Acción Restringida', detail: 'El Rol Maestro (Nivel 200) no puede ser desactivado.', life: 3000 });
        return;
    }

    const accion = data.esta_activo ? 'desactivar' : 'activar';
    
    confirm.require({
        message: `¿Estás seguro de que deseas ${accion} el rol "${data.nombre}"?`,
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
                await api.patch(`roles/${data.id}/switch-estado/`, {});
                toast.add({ severity: 'success', summary: 'Éxito', detail: `Rol ${accion === 'activar' ? 'activado' : 'desactivado'} correctamente`, life: 3000 });
                cargarRoles();
            } catch (error) {

                toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.error || error?.response?.data?.detail || `No se pudo ${accion} el rol`, life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

onMounted(() => {
    cargarRoles();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <!-- Guía de Referencia (Diccionario de Niveles) -->
        <div class="card">
            <div class="flex items-center gap-2 mb-4">
                <i class="pi pi-book text-primary text-xl"></i>
                <span class="font-semibold text-xl">Guía de Niveles y Jerarquías (CNM)</span>
            </div>
            
            <DataTable :value="guiaNiveles" size="small" showGridlines stripedRows class="text-sm mb-4">
                <Column field="nivel" header="Nivel" class="w-32">
                    <template #body="slotProps">
                        <Tag :value="slotProps.data.nivel" :severity="slotProps.data.severity" class="w-full font-bold" />
                    </template>
                </Column>
                <Column field="rol" header="Rol Oficial" class="w-48">
                    <template #body="slotProps">
                        <div class="flex items-center gap-2">
                            <i :class="slotProps.data.icon" class="text-surface-500 dark:text-surface-400 text-lg"></i>
                            <span class="font-semibold text-surface-700 dark:text-surface-100">{{ slotProps.data.rol }}</span>
                        </div>
                    </template>
                </Column>
                <Column field="area" header="Áreas" class="w-48">
                    <template #body="slotProps">
                        <span class="text-surface-600 dark:text-surface-300">{{ slotProps.data.area }}</span>
                    </template>
                </Column>
                <Column field="accion" header="Alcance de Acción">
                    <template #body="slotProps">
                        <span class="text-surface-600 dark:text-surface-300">{{ slotProps.data.accion }}</span>
                    </template>
                </Column>
            </DataTable>

            <div class="flex flex-col gap-2 text-sm bg-surface-50 dark:bg-surface-900 p-4 rounded border border-surface-200 dark:border-surface-700">
                <div class="font-bold text-surface-700 dark:text-surface-200 flex items-center gap-2">
                    <i class="pi pi-shield"></i> Directivas de Seguridad
                </div>
                <ul class="list-disc list-inside text-surface-600 dark:text-surface-400 ml-1">
                    <li><strong>Nivel 200 (Director):</strong> Único con acceso a logs de auditoría maestra. Indestructible.</li>
                    <li><strong>Validación:</strong> El sistema usa <code>minLevel</code>. Si un módulo requiere 186, niveles inferiores no tienen acceso.</li>
                </ul>
            </div>
        </div>

        <div class="card">
        <Toast />
        <ConfirmDialog />
        <!-- Toolbar personalizable -->
        <DataTableToolbar
            ref="toolbarRef"
            :dt="dt"
            :datos="roles"
            titulo-reporte="Roles del Sistema"
            nombre-archivo="roles"
            :columnas="columnas"
            :mostrar-exportacion="true"
            :mostrar-imprimir="true"
            :mostrar-refrescar="true"
            :mostrar-selector-columnas="true"
            :mostrar-buscador="true"
            @refrescar="cargarRoles"
            v-model:columnas-seleccionadas="columnas"
        >
            <template #acciones-extra>
                <Button 
                    icon="pi pi-plus" 
                    label="Nuevo Rol"
                    rounded
                    severity="primary"
                    @click="openNew"
                />
            </template>
        </DataTableToolbar>
        
        <DataTable 
            ref="dt"
            :value="roles" 
            :loading="loading"
            v-model:filters="filtros"
            :globalFilterFields="['nombre', 'descripcion', 'nivel']"
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
                    No se encontraron roles.
                </div>
            </template>
            
            <template #loading>
                Cargando roles...
            </template>
            
            <Column 
                v-if="esColumnaVisible('nombre')"
                field="nombre" 
                header="Nombre" 
                sortable 
                style="min-width: 12rem"
            >
                <template #body="{ data }">
                    <Tag :value="data.nombre" :severity="getNivelSeverity(data.nivel)" class="text-sm font-bold px-3" />
                </template>
            </Column>
            
            <Column 
                v-if="esColumnaVisible('descripcion')"
                field="descripcion" 
                header="Descripción" 
                sortable 
                style="min-width: 20rem"
            >
                <template #body="{ data }">
                    <div class="text-sm">{{ data.descripcion || 'Sin descripción' }}</div>
                </template>
            </Column>
            
            <Column 
                v-if="esColumnaVisible('nivel')"
                field="nivel" 
                header="Nivel" 
                sortable 
                style="min-width: 8rem"
            >
                <template #body="{ data }">
                    <Tag :value="data.nivel" :severity="getNivelSeverity(data.nivel)" />
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
                header="Fecha Creación" 
                sortable 
                style="min-width: 12rem"
            >
                <template #body="{ data }">
                    <div class="text-sm">{{ formatearFecha(data.creado_en) }}</div>
                </template>
            </Column>
            
            <Column header="Acciones" :exportable="false" style="min-width: 12rem">
                <template #body="{ data }">
                    <div class="flex gap-2">
                        <Button 
                            icon="pi pi-pencil" 
                            size="small"
                            severity="info"
                            rounded 
                            outlined
                            @click="editarRol(data)"
                            :disabled="data.nivel === 200"
                            v-tooltip.top="'Editar'"
                        />
                        <Button 
                            :icon="data.esta_activo ? 'pi pi-ban' : 'pi pi-check-circle'" 
                            size="small"
                            :severity="data.esta_activo ? 'warning' : 'success'"
                            rounded 
                            outlined
                            @click="toggleActivarRol(data)"
                            :disabled="data.nivel === 200"
                            v-tooltip.top="data.esta_activo ? 'Desactivar' : 'Activar'"
                        />
                    </div>
                </template>
            </Column>
        </DataTable>

        <Dialog v-model:visible="rolDialog" :style="{ width: '450px' }" header="Detalles del Rol" :modal="true">
            <div class="flex flex-col gap-6">
                <div>
                    <label for="nombre" class="block font-bold mb-3">Nombre</label>
                    <InputText id="nombre" v-model.trim="rol.nombre" required="true" autofocus :invalid="submitted && !rol.nombre" fluid />
                    <small class="text-red-500" v-if="submitted && !rol.nombre">El nombre es obligatorio.</small>
                </div>
                
                <div>
                    <label for="descripcion" class="block font-bold mb-3">Descripción</label>
                    <Textarea id="descripcion" v-model="rol.descripcion" rows="3" cols="20" fluid />
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label for="nivel" class="block font-bold mb-3">Nivel de Acceso</label>
                        <InputNumber id="nivel" v-model="rol.nivel" showButtons :min="0" :max="200" fluid />
                    </div>
                    
                    <div class="flex items-center mt-8">
                        <Checkbox v-model="rol.esta_activo" :binary="true" inputId="esta_activo" />
                        <label for="esta_activo" class="ml-2">¿Está Activo?</label>
                    </div>
                </div>

                <div v-if="rol.id" class="border-t border-surface-200 dark:border-surface-700 pt-4">
                    <div class="font-bold mb-3 text-surface-500 dark:text-surface-400">Auditoría</div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Creado por</label>
                            <InputText id="creado_por" name="creado_por" :value="rol.creado_por || 'Sistema'" disabled fluid class="opacity-100" />
                        </div>
                        <div>
                            <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Fecha Creación</label>
                            <InputText id="creado_en" name="creado_en" :value="formatearFecha(rol.creado_en)" disabled fluid class="opacity-100" />
                        </div>
                        <div>
                            <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Modificado por</label>
                            <InputText id="modificado_por" name="modificado_por" :value="rol.modificado_por || 'N/A'" disabled fluid class="opacity-100" />
                        </div>
                        <div>
                            <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Última Modificación</label>
                            <InputText id="modificado_en" name="modificado_en" :value="formatearFecha(rol.modificado_en)" disabled fluid class="opacity-100" />
                        </div>
                    </div>
                </div>
            </div>

            <template #footer>
                <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                <Button label="Guardar" icon="pi pi-check" @click="saveRol" />
            </template>
        </Dialog>
        </div>
    </div>
</template>
