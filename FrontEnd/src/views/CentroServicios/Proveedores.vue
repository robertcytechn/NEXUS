<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api, { getUser } from '@/service/api';
import { guardarProveedor } from '@/service/proveedorService';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';
import { useContactLinks } from '@/composables/useContactLinks';
import ProveedorFormDialog from '@/components/proveedores/ProveedorFormDialog.vue';
import ProveedorDetalleDialog from '@/components/proveedores/ProveedorDetalleDialog.vue';

const proveedores = ref([]);
const casinos = ref([]);
const estadisticas = ref({ total: 0 });
const loading = ref(false);
const dt = ref();
const toolbarRef = ref();

useResponsiveDataTable(dt);
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();
const confirm = useConfirm();
const { abrirTelefono, abrirEmail } = useContactLinks(toast);

// Estado de los Componentes Inteligentes
const dialogFormVisible = ref(false);
const dialogDetalleVisible = ref(false);
const idProveedorForm = ref(null);
const objProveedorDetalle = ref(null);

// Obtener usuario actual y su rol
const usuario = computed(() => getUser());
const rolUsuario = computed(() => usuario.value?.rol_nombre || '');
const casinoUsuario = computed(() => usuario.value?.casino || null);

// Permisos basados en rol
const permisos = computed(() => ({
    puedeExportar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeAgregar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeEditar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeDesactivar: ['SUP SISTEMAS', 'ADMINISTRADOR'].includes(rolUsuario.value),
    puedeVerCredenciales: ['SUP SISTEMAS', 'ADMINISTRADOR'].includes(rolUsuario.value)
}));

// Sincronizar buscador
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Columnas
const columnas = ref([
    { field: 'nombre', label: 'Proveedor', visible: true },
    { field: 'rfc', label: 'RFC', visible: true },
    { field: 'email_corporativo', label: 'Email', visible: true },
    { field: 'telefono_soporte', label: 'Tel. Soporte', visible: true },
    { field: 'nombre_contacto_tecnico', label: 'Contacto Técnico', visible: true },
    { field: 'total_modelos', label: 'Modelos', visible: true },
    { field: 'username', label: 'Usuario', visible: false }
]);

// Cargar Datos
const cargarDatos = async () => {
    loading.value = true;
    try {
        if (!casinoUsuario.value) {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'Usuario sin casino asignado. Contacte al administrador.',
                life: 5000
            });
            return;
        }

        const res = await api.get(`proveedores/lista-por-casino/${casinoUsuario.value}/`);
        proveedores.value = res.data.proveedores;
        estadisticas.value = res.data.estadisticas;

        // Cargar casinos si puede agregar/editar
        if (permisos.value.puedeAgregar || permisos.value.puedeEditar) {
            const resCasinos = await api.get('casinos/lista/');
            casinos.value = resCasinos.data;
        }
    } catch (error) {

        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudieron cargar los proveedores', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// Helpers
const esColumnaVisible = (field) => {
    const col = columnas.value.find(c => c.field === field);
    return col ? col.visible : true;
};

// Acciones de Componentes Inteligentes
const openNew = () => {
    idProveedorForm.value = null;
    dialogFormVisible.value = true;
};

const editarProveedor = (data) => {
    idProveedorForm.value = data.id;
    dialogFormVisible.value = true;
};

const verDetalleProveedor = (data) => {
    objProveedorDetalle.value = { ...data };
    dialogDetalleVisible.value = true;
};

const onProveedorSaved = async () => {
    await cargarDatos();
};

const toggleActivarProveedor = (data) => {
    const accion = data.esta_activo ? 'desactivar' : 'activar';
    confirm.require({
        message: `¿Estás seguro de que deseas ${accion} al proveedor "${data.nombre}"?`,
        header: 'Confirmar Acción',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: { label: 'Cancelar', severity: 'secondary', outlined: true },
        acceptProps: { label: 'Confirmar', severity: data.esta_activo ? 'danger' : 'success' },
        accept: async () => {
            loading.value = true;
            try {
                await api.patch(`proveedores/${data.id}/switch-estado/`, {});
                toast.add({ severity: 'success', summary: 'Éxito', detail: `Proveedor ${accion === 'activar' ? 'activado' : 'desactivado'} correctamente`, life: 3000 });
                cargarDatos();
            } catch (error) {
                toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.error || error?.response?.data?.detail || `No se pudo ${accion} el proveedor`, life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

onMounted(() => {
    cargarDatos();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <!-- Estadísticas -->
        <div v-if="permisos.puedeExportar" class="card">
            <div class="font-bold text-xl mb-6 text-surface-900 dark:text-surface-0">
                Proveedores - {{ usuario?.casino_nombre }}
            </div>
            <div class="grid grid-cols-1 gap-4">
                <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Total
                                Proveedores</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{ estadisticas.total
                                }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-lg"
                            style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-briefcase text-blue-500 dark:text-blue-400 text-2xl"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <Toast />
            <ConfirmDialog />

            <DataTableToolbar ref="toolbarRef" :dt="dt" :datos="proveedores" titulo-reporte="Lista de Proveedores"
                nombre-archivo="proveedores" :columnas="columnas" @refrescar="cargarDatos"
                v-model:columnas-seleccionadas="columnas" :mostrar-exportacion="permisos.puedeExportar"
                :mostrar-imprimir="permisos.puedeExportar">
                <template #acciones-extra>
                    <Button v-if="permisos.puedeAgregar" icon="pi pi-plus" label="Nuevo Proveedor" rounded
                        severity="primary" @click="openNew" />
                </template>
            </DataTableToolbar>

            <DataTable ref="dt" :value="proveedores" :loading="loading" v-model:filters="filtros"
                :globalFilterFields="['nombre', 'rfc', 'email_corporativo', 'telefono_soporte', 'nombre_contacto_tecnico', 'username']"
                paginator :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]" dataKey="id" showGridlines stripedRows
                class="datatable-mobile">
                <template #empty>
                    <div class="text-center p-4">No se encontraron proveedores registrados.</div>
                </template>

                <Column v-if="esColumnaVisible('nombre')" field="nombre" header="Proveedor" sortable
                    style="min-width: 14rem">
                    <template #body="{ data }">
                        <span class="font-bold text-primary-500 cursor-pointer hover:text-primary-700 hover:underline"
                            @click="verDetalleProveedor(data)">
                            {{ data.nombre }}
                        </span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('rfc')" field="rfc" header="RFC" sortable style="min-width: 10rem">
                    <template #body="{ data }"><span class="font-mono text-sm">{{ data.rfc }}</span></template>
                </Column>
                <Column v-if="esColumnaVisible('email_corporativo')" field="email_corporativo" header="Email" sortable
                    style="min-width: 14rem">
                    <template #body="{ data }">
                        <span class="text-primary-500 hover:underline text-sm cursor-pointer"
                            @click="abrirEmail(data.email_corporativo)">{{ data.email_corporativo }}</span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('telefono_soporte')" field="telefono_soporte" header="Tel. Soporte"
                    sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <span v-if="data.telefono_soporte"
                            class="text-primary-500 hover:underline text-sm cursor-pointer"
                            @click="abrirTelefono(data.telefono_soporte)">{{ data.telefono_soporte }}</span>
                        <span v-else class="text-surface-400 text-sm">N/A</span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('nombre_contacto_tecnico')" field="nombre_contacto_tecnico"
                    header="Contacto Técnico" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <span class="text-sm">{{ data.nombre_contacto_tecnico || 'N/A' }}</span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('total_modelos')" field="total_modelos" header="Modelos" sortable
                    style="min-width: 6rem">
                    <template #body="{ data }">
                        <Tag :value="String(data.total_modelos)" severity="info" rounded />
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('username')" field="username" header="Usuario" sortable
                    style="min-width: 8rem">
                    <template #body="{ data }"><span class="font-mono text-sm">{{ data.username }}</span></template>
                </Column>
                <Column v-if="permisos.puedeEditar || permisos.puedeDesactivar" header="Acciones" :exportable="false"
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button v-if="permisos.puedeEditar" icon="pi pi-pencil" size="small" severity="info" rounded
                                outlined @click="editarProveedor(data)" v-tooltip.top="'Editar'" />
                            <Button v-if="permisos.puedeDesactivar" icon="pi pi-ban" size="small" severity="warning"
                                rounded outlined @click="toggleActivarProveedor(data)" v-tooltip.top="'Desactivar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <!-- COMPONENTES INTELIGENTES -->
            <ProveedorFormDialog v-model:visible="dialogFormVisible" :proveedorId="idProveedorForm"
                :casinoFijo="casinoUsuario" :permitirElegirCasino="false" @saved="onProveedorSaved" />

            <ProveedorDetalleDialog v-model:visible="dialogDetalleVisible" :proveedor="objProveedorDetalle" />
        </div>
    </div>
</template>
