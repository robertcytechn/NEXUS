<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api, { getUser } from '@/service/api';
import { guardarProveedor } from '@/service/proveedorService';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';
import { useContactLinks } from '@/composables/useContactLinks';

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
const proveedorDialog = ref(false);
const proveedor = ref({});
const submitted = ref(false);

// Modal de detalle
const detalleDialog = ref(false);
const proveedorDetalle = ref(null);

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

// CRUD
const openNew = () => {
    proveedor.value = {
        esta_activo: true,
        casino: casinoUsuario.value
    };
    submitted.value = false;
    proveedorDialog.value = true;
};

const editarProveedor = (data) => {
    proveedor.value = { ...data };
    proveedorDialog.value = true;
};

const hideDialog = () => {
    proveedorDialog.value = false;
    submitted.value = false;
};

const saveProveedor = async () => {
    submitted.value = true;

    if (proveedor.value.nombre?.trim() && proveedor.value.rfc?.trim() && proveedor.value.email_corporativo?.trim() && proveedor.value.username?.trim() && proveedor.value.password?.trim() && proveedor.value.casino) {
        loading.value = true;
        
        const esEdicion = !!proveedor.value.id;
        const resultado = await guardarProveedor(proveedor.value, esEdicion);
        
        if (!resultado.exito) {
            toast.add({ 
                severity: 'error', 
                summary: resultado.error, 
                detail: resultado.detalle, 
                life: 5000 
            });
            loading.value = false;
            return;
        }

        toast.add({ 
            severity: 'success', 
            summary: 'Éxito', 
            detail: resultado.mensaje, 
            life: 3000 
        });
        
        proveedorDialog.value = false;
        proveedor.value = {};
        cargarDatos();
        loading.value = false;
    }
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

// Modal detalle
const verDetalleProveedor = (data) => {
    proveedorDetalle.value = { ...data };
    detalleDialog.value = true;
};

// Toggle visibilidad password
const passwordVisible = ref({});
const togglePasswordVisibility = (id) => {
    passwordVisible.value[id] = !passwordVisible.value[id];
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
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Total Proveedores</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{ estadisticas.total }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-lg" style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-briefcase text-blue-500 dark:text-blue-400 text-2xl"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <Toast />
            <ConfirmDialog />

            <DataTableToolbar
                ref="toolbarRef"
                :dt="dt"
                :datos="proveedores"
                titulo-reporte="Lista de Proveedores"
                nombre-archivo="proveedores"
                :columnas="columnas"
                @refrescar="cargarDatos"
                v-model:columnas-seleccionadas="columnas"
                :mostrar-exportacion="permisos.puedeExportar"
                :mostrar-imprimir="permisos.puedeExportar"
            >
                <template #acciones-extra>
                    <Button v-if="permisos.puedeAgregar" icon="pi pi-plus" label="Nuevo Proveedor" rounded severity="primary" @click="openNew" />
                </template>
            </DataTableToolbar>

            <DataTable
                ref="dt" :value="proveedores" :loading="loading" v-model:filters="filtros"
                :globalFilterFields="['nombre', 'rfc', 'email_corporativo', 'telefono_soporte', 'nombre_contacto_tecnico', 'username']"
                paginator :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]"
                dataKey="id" showGridlines stripedRows
                class="datatable-mobile"
            >
                <template #empty><div class="text-center p-4">No se encontraron proveedores registrados.</div></template>

                <Column v-if="esColumnaVisible('nombre')" field="nombre" header="Proveedor" sortable style="min-width: 14rem">
                    <template #body="{ data }">
                        <span class="font-bold text-primary-500 cursor-pointer hover:text-primary-700 hover:underline" @click="verDetalleProveedor(data)">
                            {{ data.nombre }}
                        </span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('rfc')" field="rfc" header="RFC" sortable style="min-width: 10rem">
                    <template #body="{ data }"><span class="font-mono text-sm">{{ data.rfc }}</span></template>
                </Column>
                <Column v-if="esColumnaVisible('email_corporativo')" field="email_corporativo" header="Email" sortable style="min-width: 14rem">
                    <template #body="{ data }">
                        <span class="text-primary-500 hover:underline text-sm cursor-pointer" @click="abrirEmail(data.email_corporativo)">{{ data.email_corporativo }}</span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('telefono_soporte')" field="telefono_soporte" header="Tel. Soporte" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <span v-if="data.telefono_soporte" class="text-primary-500 hover:underline text-sm cursor-pointer" @click="abrirTelefono(data.telefono_soporte)">{{ data.telefono_soporte }}</span>
                        <span v-else class="text-surface-400 text-sm">N/A</span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('nombre_contacto_tecnico')" field="nombre_contacto_tecnico" header="Contacto Técnico" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <span class="text-sm">{{ data.nombre_contacto_tecnico || 'N/A' }}</span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('total_modelos')" field="total_modelos" header="Modelos" sortable style="min-width: 6rem">
                    <template #body="{ data }">
                        <Tag :value="String(data.total_modelos)" severity="info" rounded />
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('username')" field="username" header="Usuario" sortable style="min-width: 8rem">
                    <template #body="{ data }"><span class="font-mono text-sm">{{ data.username }}</span></template>
                </Column>
                <Column v-if="permisos.puedeEditar || permisos.puedeDesactivar" header="Acciones" :exportable="false" style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button v-if="permisos.puedeEditar" icon="pi pi-pencil" size="small" severity="info" rounded outlined @click="editarProveedor(data)" v-tooltip.top="'Editar'" />
                            <Button v-if="permisos.puedeDesactivar" icon="pi pi-ban" size="small" severity="warning" rounded outlined @click="toggleActivarProveedor(data)" v-tooltip.top="'Desactivar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <!-- Dialog de Crear/Editar -->
            <Dialog v-model:visible="proveedorDialog" :style="{ width: '700px' }" header="Datos del Proveedor" :modal="true">
                <div class="flex flex-col gap-6">
                    <div class="font-bold text-lg text-surface-500 border-b border-surface-200 dark:border-surface-700 pb-2">Información General</div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="casino" class="block font-bold mb-3">Casino</label>
                            <Select id="casino" v-model="proveedor.casino" :options="casinos" optionLabel="nombre" optionValue="id" placeholder="Seleccione Casino" fluid :invalid="submitted && !proveedor.casino" :disabled="true" />
                            <small class="text-surface-500">Casino asignado a tu usuario.</small>
                        </div>
                        <div>
                            <label for="nombre" class="block font-bold mb-3">Nombre / Razón Social</label>
                            <InputText id="nombre" v-model.trim="proveedor.nombre" fluid :invalid="submitted && !proveedor.nombre" />
                            <small class="text-red-500" v-if="submitted && !proveedor.nombre">Requerido.</small>
                        </div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="rfc" class="block font-bold mb-3">RFC</label>
                            <InputText id="rfc" v-model.trim="proveedor.rfc" fluid :invalid="submitted && !proveedor.rfc" maxlength="13" />
                            <small class="text-red-500" v-if="submitted && !proveedor.rfc">Requerido.</small>
                        </div>
                        <div>
                            <label for="email_corporativo" class="block font-bold mb-3">Email Corporativo</label>
                            <InputText id="email_corporativo" v-model.trim="proveedor.email_corporativo" fluid :invalid="submitted && !proveedor.email_corporativo" />
                            <small class="text-red-500" v-if="submitted && !proveedor.email_corporativo">Requerido.</small>
                        </div>
                    </div>

                    <div class="font-bold text-lg text-surface-500 border-b border-surface-200 dark:border-surface-700 pb-2">Contacto Soporte</div>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label for="telefono_soporte" class="block font-bold mb-3">Teléfono Soporte</label>
                            <InputText id="telefono_soporte" v-model.trim="proveedor.telefono_soporte" fluid />
                        </div>
                        <div>
                            <label for="email_soporte" class="block font-bold mb-3">Email Soporte</label>
                            <InputText id="email_soporte" v-model.trim="proveedor.email_soporte" fluid />
                        </div>
                        <div>
                            <label for="nombre_contacto_tecnico" class="block font-bold mb-3">Contacto Técnico</label>
                            <InputText id="nombre_contacto_tecnico" v-model.trim="proveedor.nombre_contacto_tecnico" fluid />
                        </div>
                    </div>

                    <div class="font-bold text-lg text-surface-500 border-b border-surface-200 dark:border-surface-700 pb-2">Credenciales de Acceso</div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="username" class="block font-bold mb-3">Usuario</label>
                            <InputText id="username" v-model.trim="proveedor.username" fluid :invalid="submitted && !proveedor.username" />
                            <small class="text-red-500" v-if="submitted && !proveedor.username">Requerido.</small>
                        </div>
                        <div>
                            <label for="password" class="block font-bold mb-3">Contraseña</label>
                            <Password id="password" v-model="proveedor.password" fluid :invalid="submitted && !proveedor.password" toggleMask :feedback="false" />
                            <small class="text-red-500" v-if="submitted && !proveedor.password">Requerido.</small>
                        </div>
                    </div>

                </div>
                <template #footer>
                    <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                    <Button label="Guardar" icon="pi pi-check" @click="saveProveedor" />
                </template>
            </Dialog>

            <!-- Modal de Detalle del Proveedor -->
            <Dialog v-model:visible="detalleDialog" :style="{ width: '850px' }" header="Ficha del Proveedor" :modal="true">
                <div v-if="proveedorDetalle" class="flex flex-col gap-5">
                    <div class="surface-card border-2 border-primary-200 dark:border-primary-900 rounded-xl p-5 bg-gradient-to-br from-primary-50 to-white dark:from-primary-950 dark:to-surface-900">
                        <!-- Cabecera -->
                        <div class="flex items-center gap-4 mb-5">
                            <div class="flex items-center justify-center bg-primary-500 rounded-xl shadow-lg" style="width:3.5rem;height:3.5rem">
                                <i class="pi pi-briefcase text-white text-2xl"></i>
                            </div>
                            <div class="flex-1">
                                <h3 class="text-2xl font-bold text-surface-900 dark:text-surface-0 mb-1">{{ proveedorDetalle.nombre }}</h3>
                                <p class="text-surface-600 dark:text-surface-400 font-medium">
                                    <Tag :value="proveedorDetalle.rfc" severity="secondary" class="text-xs font-mono" />
                                    <span class="text-primary-500 mx-2">•</span>
                                    {{ proveedorDetalle.casino_nombre }}
                                </p>
                            </div>
                        </div>

                        <div class="grid grid-cols-2 md:grid-cols-3 gap-6">
                            <!-- Email Corporativo -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-envelope text-blue-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Email Corporativo</span>
                                </div>
                                <span class="text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium cursor-pointer" @click="abrirEmail(proveedorDetalle.email_corporativo)">
                                    {{ proveedorDetalle.email_corporativo }}
                                </span>
                            </div>
                            <!-- Teléfono Soporte -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-phone text-green-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Tel. Soporte</span>
                                </div>
                                <span v-if="proveedorDetalle.telefono_soporte" class="text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium cursor-pointer" @click="abrirTelefono(proveedorDetalle.telefono_soporte)">
                                    {{ proveedorDetalle.telefono_soporte }}
                                </span>
                                <span v-else class="text-surface-400 text-xs">No registrado</span>
                            </div>
                            <!-- Email Soporte -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-at text-purple-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Email Soporte</span>
                                </div>
                                <span v-if="proveedorDetalle.email_soporte" class="text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium cursor-pointer" @click="abrirEmail(proveedorDetalle.email_soporte)">
                                    {{ proveedorDetalle.email_soporte }}
                                </span>
                                <span v-else class="text-surface-400 text-xs">No registrado</span>
                            </div>
                            <!-- Contacto Técnico -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-user text-teal-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Contacto Técnico</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{ proveedorDetalle.nombre_contacto_tecnico || 'No asignado' }}</span>
                            </div>
                            <!-- Total Modelos -->
                            <div class="bg-blue-50 dark:bg-blue-950 rounded-lg p-3 border border-blue-200 dark:border-blue-800">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-box text-blue-600 text-sm"></i>
                                    <span class="text-blue-700 dark:text-blue-400 text-xs font-semibold">Modelos de Máquina</span>
                                </div>
                                <span class="font-bold text-blue-800 dark:text-blue-300 text-2xl">{{ proveedorDetalle.total_modelos }}</span>
                            </div>
                            <!-- Casino -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-building text-red-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Casino</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{ proveedorDetalle.casino_nombre }}</span>
                            </div>
                        </div>

                        <!-- Credenciales (solo para roles autorizados) -->
                        <div v-if="permisos.puedeVerCredenciales" class="mt-5">
                            <div class="bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-orange-950 dark:to-yellow-950 rounded-lg p-4 border-2 border-orange-300 dark:border-orange-800">
                                <div class="flex items-center gap-2 mb-3">
                                    <i class="pi pi-lock text-orange-600 text-sm"></i>
                                    <span class="text-orange-700 dark:text-orange-400 text-sm font-bold uppercase tracking-wide">Credenciales de Acceso</span>
                                </div>
                                <div class="grid grid-cols-2 gap-4">
                                    <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                        <div class="flex items-center gap-2 mb-2">
                                            <i class="pi pi-user text-orange-500 text-sm"></i>
                                            <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Usuario</span>
                                        </div>
                                        <span class="font-bold text-surface-900 dark:text-surface-0 text-sm font-mono">{{ proveedorDetalle.username }}</span>
                                    </div>
                                    <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                        <div class="flex items-center gap-2 mb-2">
                                            <i class="pi pi-key text-orange-500 text-sm"></i>
                                            <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Contraseña</span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <span class="font-bold text-surface-900 dark:text-surface-0 text-sm font-mono">
                                                {{ passwordVisible[proveedorDetalle.id] ? proveedorDetalle.password : '••••••••' }}
                                            </span>
                                            <Button :icon="passwordVisible[proveedorDetalle.id] ? 'pi pi-eye-slash' : 'pi pi-eye'" text rounded size="small" severity="secondary" @click="togglePasswordVisibility(proveedorDetalle.id)" v-tooltip.top="'Mostrar / Ocultar'" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </Dialog>
        </div>
    </div>
</template>
