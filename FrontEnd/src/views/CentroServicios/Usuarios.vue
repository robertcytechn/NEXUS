<script setup>
import { ref, onMounted, watch, computed, inject } from 'vue';
import api, { getUser } from '@/service/api';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

import UsuarioFormDialog from '@/components/usuarios/UsuarioFormDialog.vue';
import UsuarioDetalleDialog from '@/components/usuarios/UsuarioDetalleDialog.vue';
import { useContactLinks } from '@/composables/useContactLinks';
import { parseServerError } from '@/utils/parseServerError';

const usuarios = ref([]);
const roles = ref([]);
const estadisticas = ref({ total: 0, activos: 0, inactivos: 0 });
const loading = ref(false);
const dt = ref();
const toolbarRef = ref();

useResponsiveDataTable(dt);
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();
const isMobileView = inject('isMobileView', ref(false));

const confirm = useConfirm();
const { abrirEmail } = useContactLinks(toast);

const usuarioDialogVisible = ref(false);
const usuarioSeleccionadoId = ref(null);
const detalleDialogVisible = ref(false);
const usuarioSeleccionadoDetalle = ref(null);


// Obtener usuario actual y su rol
const usuarioActual = computed(() => getUser());
const rolUsuario = computed(() => usuarioActual.value?.rol_nombre || '');
const casinoUsuario = computed(() => usuarioActual.value?.casino || null);
const casinoIdSesion = computed(() => usuarioActual.value?.casino || null);


// Permisos basados en rol
const permisos = computed(() => ({
    puedeExportar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR', 'GERENCIA'].includes(rolUsuario.value),
    puedeAgregar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR', 'GERENCIA'].includes(rolUsuario.value),
    puedeEditar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR', 'GERENCIA'].includes(rolUsuario.value),
    puedeDesactivar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR', 'GERENCIA'].includes(rolUsuario.value)
}));

// Roles disponibles filtrados según el rol del usuario logueado (Tarea 6)
const rolesDisponibles = computed(() => {
    if (['ADMINISTRADOR', 'DB ADMIN'].includes(rolUsuario.value)) {
        // Admin y DB Admin ven todos los roles disponibles
        return roles.value;
    }
    if (rolUsuario.value === 'GERENCIA') {
        // Gerente puede crear: sup_sistemas, tecnico, supervisor_sala, encargado_area
        return roles.value.filter(r => ['SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA'].includes(r.nombre));
    }
    if (rolUsuario.value === 'SUP SISTEMAS') {
        // Sup Sistemas puede crear: tecnico, supervisor_sala, encargado_area
        return roles.value.filter(r => ['TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA'].includes(r.nombre));
    }
    // Si no coincide ningún rol con permisos de creación, no mostrar opciones
    return [];
});

// Sincronizar buscador
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Columnas
const columnas = ref([
    { field: 'nombre_completo', label: 'Nombre', visible: true },
    { field: 'username', label: 'Usuario', visible: true },
    { field: 'email', label: 'Email', visible: true },
    { field: 'rol_nombre', label: 'Rol', visible: true },
    { field: 'esta_activo', label: 'Estado', visible: true }
]);

// Cargar Datos
const cargarDatos = async () => {
    loading.value = true;
    try {
        if (!casinoUsuario.value) {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: 'Usuario sin casino asignado. Contacte al administrador.',
                life: 5000
            });
            return;
        }

        const res = await api.get(`usuarios/lista-por-casino/${casinoUsuario.value}/`);
        usuarios.value = res.data.usuarios;
        estadisticas.value = res.data.estadisticas;

        // Cargar roles si puede agregar/editar
        if (permisos.value.puedeAgregar || permisos.value.puedeEditar) {
            const resRoles = await api.get('roles/lista/');
            roles.value = resRoles.data.filter(r => r.esta_activo);  // rolesDisponibles computed filtra según rol del usuario
        }
    } catch (error) {

        toast.add({ severity: 'error', summary: 'Error', detail: parseServerError(error, 'No se pudieron cargar los usuarios'), life: 5000 });
    } finally {
        loading.value = false;
    }
};

// Helpers
const esColumnaVisible = (field) => {
    const col = columnas.value.find(c => c.field === field);
    return col ? col.visible : true;
};

const getSeverityEstado = (activo) => activo ? 'success' : 'danger';
const getLabelEstado = (activo) => activo ? 'Activo' : 'Inactivo';

const getSeverityRol = (rol) => {
    const mapa = {
        'ADMINISTRADOR': 'danger',
        'DB ADMIN': 'danger',
        'GERENCIA': 'warn',
        'SUP SISTEMAS': 'info',
        'SUPERVISOR SALA': 'info',
        'ENCARGADO AREA': 'secondary',
        'TECNICO': 'success'
    };
    return mapa[rol] || 'secondary';
};

// Acciones (Nueva Lógica con Componentes Inteligentes)
const editarUsuario = (data) => {
    usuarioSeleccionadoId.value = data.id;
    usuarioDialogVisible.value = true;
};

const openNew = () => {
    usuarioSeleccionadoId.value = null;
    usuarioDialogVisible.value = true;
};

const hideDialog = () => {
    usuarioDialogVisible.value = false;
};

const verDetalleUsuario = (data) => {
    usuarioSeleccionadoDetalle.value = data;
    detalleDialogVisible.value = true;
};

const toggleActivarUsuario = (data) => {
    const accion = data.esta_activo ? 'desactivar' : 'activar';
    confirm.require({
        message: `¿Estás seguro de que deseas ${accion} al usuario "${data.nombre_completo}"?`,
        header: 'Confirmar Acción',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: { label: 'Cancelar', severity: 'secondary', outlined: true },
        acceptProps: { label: 'Confirmar', severity: data.esta_activo ? 'danger' : 'success' },
        accept: async () => {
            loading.value = true;
            try {
                await api.patch(`usuarios/${data.id}/switch-estado/`, {});
                toast.add({ severity: 'success', summary: 'Éxito', detail: `Usuario ${accion === 'activar' ? 'activado' : 'desactivado'} correctamente`, life: 3000 });
                cargarDatos();
            } catch (error) {
                toast.add({ severity: 'error', summary: 'Error', detail: parseServerError(error, `No se pudo ${accion} el usuario`), life: 5000 });
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
                Usuarios - {{ usuarioActual?.casino_nombre }}
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Total
                                Usuarios</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{ estadisticas.total
                                }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-lg"
                            style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-users text-blue-500 dark:text-blue-400 text-2xl"></i>
                        </div>
                    </div>
                </div>
                <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Activos</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{
                                estadisticas.activos }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-green-100 dark:bg-green-400/10 rounded-lg"
                            style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-check-circle text-green-500 dark:text-green-400 text-2xl"></i>
                        </div>
                    </div>
                </div>
                <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Inactivos</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{
                                estadisticas.inactivos }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-red-100 dark:bg-red-400/10 rounded-lg"
                            style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-ban text-red-500 dark:text-red-400 text-2xl"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <Toast />
            <ConfirmDialog />

            <DataTableToolbar ref="toolbarRef" :dt="dt" :datos="usuarios" titulo-reporte="Lista de Usuarios"
                nombre-archivo="usuarios" :columnas="columnas" @refrescar="cargarDatos"
                v-model:columnas-seleccionadas="columnas" :mostrar-exportacion="permisos.puedeExportar"
                :mostrar-imprimir="permisos.puedeExportar">
                <template #acciones-extra>
                    <Button v-if="permisos.puedeAgregar" icon="pi pi-plus" label="Nuevo Usuario" rounded
                        severity="primary" @click="openNew" />
                </template>
            </DataTableToolbar>

            <DataTable ref="dt" :value="usuarios" :loading="loading" v-model:filters="filtros"
                :globalFilterFields="['nombre_completo', 'username', 'email', 'rol_nombre']" paginator :rows="10"
                :rowsPerPageOptions="[5, 10, 20, 50]" dataKey="id" showGridlines stripedRows class="datatable-mobile">
                <template #empty>
                    <div class="text-center p-4">No se encontraron usuarios registrados.</div>
                </template>

                <Column v-if="esColumnaVisible('nombre_completo')" field="nombre_completo" header="Nombre Completo"
                    sortable style="min-width: 14rem">
                    <template #body="{ data }">
                        <span class="font-bold text-primary-500 cursor-pointer hover:text-primary-700 hover:underline"
                            @click="verDetalleUsuario(data)">
                            {{ data.nombres }} {{ data.apellido_paterno }} {{ data.apellido_materno }}
                        </span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('username')" field="username" header="Usuario" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }"><span class="font-mono text-sm">{{ data.username }}</span></template>
                </Column>
                <Column v-if="esColumnaVisible('email')" field="email" header="Email" sortable style="min-width: 14rem">
                    <template #body="{ data }">
                        <span class="text-primary-500 hover:underline text-sm cursor-pointer"
                            @click="abrirEmail(data.email)">{{ data.email }}</span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('rol_nombre')" field="rol_nombre" header="Rol" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <Tag :value="data.rol_nombre" :severity="getSeverityRol(data.rol_nombre)" rounded />
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('esta_activo')" field="esta_activo" header="Estado" sortable
                    style="min-width: 8rem">
                    <template #body="{ data }">
                        <Tag :value="getLabelEstado(data.esta_activo)" :severity="getSeverityEstado(data.esta_activo)"
                            rounded />
                    </template>
                </Column>
                <Column v-if="permisos.puedeEditar || permisos.puedeDesactivar" header="Acciones" :exportable="false"
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button v-if="permisos.puedeEditar" icon="pi pi-pencil" size="small" severity="info" rounded
                                outlined @click="editarUsuario(data)" v-tooltip.top="'Editar'" />
                            <Button v-if="permisos.puedeDesactivar"
                                :icon="data.esta_activo ? 'pi pi-ban' : 'pi pi-check-circle'" size="small"
                                :severity="data.esta_activo ? 'warning' : 'success'" rounded outlined
                                @click="toggleActivarUsuario(data)"
                                v-tooltip.top="data.esta_activo ? 'Desactivar' : 'Activar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <!-- Componente Inteligente de Formulario Parametrizado -->
            <UsuarioFormDialog v-model:visible="usuarioDialogVisible" :usuarioId="usuarioSeleccionadoId"
                :casinoFijo="casinoIdSesion" @saved="cargarDatos" />

            <!-- Componente Inteligente de Detalle de Ficha -->
            <UsuarioDetalleDialog v-model:visible="detalleDialogVisible" :usuario="usuarioSeleccionadoDetalle"
                @closed="usuarioSeleccionadoDetalle = null" />
        </div>
    </div>
</template>
