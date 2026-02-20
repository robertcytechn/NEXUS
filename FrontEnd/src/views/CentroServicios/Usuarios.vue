<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api, { getUser } from '@/service/api';
import { guardarUsuario } from '@/service/usuarioService';
import { crearNotificacion } from '@/service/notificationService';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

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
const confirm = useConfirm();
const usuarioDialog = ref(false);
const usuarioForm = ref({});
const submitted = ref(false);

// Modal de detalle
const detalleDialog = ref(false);
const usuarioDetalle = ref(null);

// Obtener usuario actual y su rol
const usuarioActual = computed(() => getUser());
const rolUsuario = computed(() => usuarioActual.value?.rol_nombre || '');
const casinoUsuario = computed(() => usuarioActual.value?.casino || null);

// Permisos basados en rol
const permisos = computed(() => ({
    puedeExportar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR', 'GERENCIA'].includes(rolUsuario.value),
    puedeAgregar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR', 'GERENCIA'].includes(rolUsuario.value),
    puedeEditar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR', 'GERENCIA'].includes(rolUsuario.value),
    puedeDesactivar: ['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR', 'GERENCIA'].includes(rolUsuario.value)
}));

// Roles disponibles filtrados según el rol del usuario logueado
const rolesDisponibles = computed(() => {
    const esAdminODBA = ['ADMINISTRADOR', 'DB ADMIN'].includes(rolUsuario.value);
    if (esAdminODBA) {
        // Admin y DB Admin ven todos los roles (excepto ADMINISTRADOR)
        return roles.value.filter(r => r.nombre !== 'ADMINISTRADOR');
    }
    // Los demás solo ven TECNICO y SUPERVISOR SALA
    return roles.value.filter(r => ['TECNICO', 'SUPERVISOR SALA'].includes(r.nombre));
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

        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los usuarios', life: 3000 });
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

// CRUD
const openNew = () => {
    usuarioForm.value = {
        esta_activo: true,
        casino: casinoUsuario.value
    };
    submitted.value = false;
    usuarioDialog.value = true;
};

const editarUsuario = (data) => {
    usuarioForm.value = { ...data, password: '' };
    usuarioDialog.value = true;
};

const hideDialog = () => {
    usuarioDialog.value = false;
    submitted.value = false;
};

const saveUsuario = async () => {
    submitted.value = true;

    const u = usuarioForm.value;
    const esEdicion = !!u.id;
    const camposRequeridos = u.nombres?.trim() && u.apellido_paterno?.trim() && u.username?.trim() && u.email?.trim() && u.rol && u.casino;
    const passwordValido = esEdicion || u.password?.trim();

    if (camposRequeridos && passwordValido) {
        loading.value = true;

        const resultado = await guardarUsuario(u, esEdicion);

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

        // Enviar notificaciones al crear un usuario nuevo
        if (!esEdicion) {
            const nombreNuevo = `${u.nombres} ${u.apellido_paterno}`.trim();
            const rolesDestino = ['GERENCIA', 'SUP SISTEMAS', 'SUPERVISOR SALA', 'DB ADMIN', 'ADMINISTRADOR'];

            // Obtener IDs de los roles destinatarios desde la lista cargada
            const rolesNotificar = roles.value.filter(r => rolesDestino.includes(r.nombre));

            // Crear una notificación por cada rol (no bloqueante)
            rolesNotificar.forEach(rol => {
                crearNotificacion({
                    titulo: 'Nuevo Usuario Registrado',
                    contenido: `Se ha registrado al usuario "${nombreNuevo}" (${u.username}) en el casino ${usuarioActual.value?.casino_nombre || ''}.`,
                    nivel: 'informativa',
                    tipo: 'sistema',
                    casino_destino: casinoUsuario.value,
                    rol_destino: rol.id,
                    es_global: false
                }).catch(err => console.error('Error al notificar:', err));
            });
        }

        usuarioDialog.value = false;
        usuarioForm.value = {};
        cargarDatos();
        loading.value = false;
    }
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
                toast.add({ severity: 'error', summary: 'Error', detail: `No se pudo ${accion} el usuario`, life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

// Modal detalle
const verDetalleUsuario = (data) => {
    usuarioDetalle.value = { ...data };
    detalleDialog.value = true;
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
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Total Usuarios</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{ estadisticas.total }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-lg" style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-users text-blue-500 dark:text-blue-400 text-2xl"></i>
                        </div>
                    </div>
                </div>
                <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Activos</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{ estadisticas.activos }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-green-100 dark:bg-green-400/10 rounded-lg" style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-check-circle text-green-500 dark:text-green-400 text-2xl"></i>
                        </div>
                    </div>
                </div>
                <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <span class="block text-surface-500 dark:text-surface-400 font-medium mb-3">Inactivos</span>
                            <div class="text-surface-900 dark:text-surface-0 font-medium text-4xl">{{ estadisticas.inactivos }}</div>
                        </div>
                        <div class="flex items-center justify-center bg-red-100 dark:bg-red-400/10 rounded-lg" style="width:3.5rem;height:3.5rem">
                            <i class="pi pi-ban text-red-500 dark:text-red-400 text-2xl"></i>
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
                :datos="usuarios"
                titulo-reporte="Lista de Usuarios"
                nombre-archivo="usuarios"
                :columnas="columnas"
                @refrescar="cargarDatos"
                v-model:columnas-seleccionadas="columnas"
                :mostrar-exportacion="permisos.puedeExportar"
                :mostrar-imprimir="permisos.puedeExportar"
            >
                <template #acciones-extra>
                    <Button v-if="permisos.puedeAgregar" icon="pi pi-plus" label="Nuevo Usuario" rounded severity="primary" @click="openNew" />
                </template>
            </DataTableToolbar>

            <DataTable
                ref="dt" :value="usuarios" :loading="loading" v-model:filters="filtros"
                :globalFilterFields="['nombre_completo', 'username', 'email', 'rol_nombre']"
                paginator :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]"
                dataKey="id" showGridlines stripedRows
                class="datatable-mobile"
            >
                <template #empty><div class="text-center p-4">No se encontraron usuarios registrados.</div></template>

                <Column v-if="esColumnaVisible('nombre_completo')" field="nombre_completo" header="Nombre" sortable style="min-width: 14rem">
                    <template #body="{ data }">
                        <span class="font-bold text-primary-500 cursor-pointer hover:text-primary-700 hover:underline" @click="verDetalleUsuario(data)">
                            {{ data.nombre_completo }}
                        </span>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('username')" field="username" header="Usuario" sortable style="min-width: 10rem">
                    <template #body="{ data }"><span class="font-mono text-sm">{{ data.username }}</span></template>
                </Column>
                <Column v-if="esColumnaVisible('email')" field="email" header="Email" sortable style="min-width: 14rem">
                    <template #body="{ data }">
                        <a :href="'mailto:' + data.email" class="text-primary-500 hover:underline text-sm">{{ data.email }}</a>
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('rol_nombre')" field="rol_nombre" header="Rol" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <Tag :value="data.rol_nombre" :severity="getSeverityRol(data.rol_nombre)" rounded />
                    </template>
                </Column>
                <Column v-if="esColumnaVisible('esta_activo')" field="esta_activo" header="Estado" sortable style="min-width: 8rem">
                    <template #body="{ data }">
                        <Tag :value="getLabelEstado(data.esta_activo)" :severity="getSeverityEstado(data.esta_activo)" rounded />
                    </template>
                </Column>
                <Column v-if="permisos.puedeEditar || permisos.puedeDesactivar" header="Acciones" :exportable="false" style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button v-if="permisos.puedeEditar" icon="pi pi-pencil" size="small" severity="info" rounded outlined @click="editarUsuario(data)" v-tooltip.top="'Editar'" />
                            <Button v-if="permisos.puedeDesactivar" :icon="data.esta_activo ? 'pi pi-ban' : 'pi pi-check-circle'" size="small" :severity="data.esta_activo ? 'warning' : 'success'" rounded outlined @click="toggleActivarUsuario(data)" v-tooltip.top="data.esta_activo ? 'Desactivar' : 'Activar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <!-- Dialog de Crear/Editar -->
            <Dialog v-model:visible="usuarioDialog" :style="{ width: '95vw', maxWidth: '700px' }" :header="usuarioForm.id ? 'Editar Usuario' : 'Nuevo Usuario'" :modal="true">
                <div class="flex flex-col gap-6">
                    <div class="font-bold text-lg text-surface-500 border-b border-surface-200 dark:border-surface-700 pb-2">Información Personal</div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="md:col-span-2">
                            <label for="casino_usr" class="block font-bold mb-3">Casino</label>
                            <InputText id="casino_usr" :modelValue="usuarioActual?.casino_nombre" fluid disabled />
                            <small class="text-surface-500">Casino asignado a tu usuario.</small>
                        </div>
                        <div>
                            <label for="nombres" class="block font-bold mb-3">Nombres</label>
                            <InputText id="nombres" v-model.trim="usuarioForm.nombres" fluid :invalid="submitted && !usuarioForm.nombres" />
                            <small class="text-red-500" v-if="submitted && !usuarioForm.nombres">Requerido.</small>
                        </div>
                        <div>
                            <label for="apellido_paterno" class="block font-bold mb-3">Apellido Paterno</label>
                            <InputText id="apellido_paterno" v-model.trim="usuarioForm.apellido_paterno" fluid :invalid="submitted && !usuarioForm.apellido_paterno" />
                            <small class="text-red-500" v-if="submitted && !usuarioForm.apellido_paterno">Requerido.</small>
                        </div>
                        <div>
                            <label for="apellido_materno" class="block font-bold mb-3">Apellido Materno</label>
                            <InputText id="apellido_materno" v-model.trim="usuarioForm.apellido_materno" fluid />
                            <small class="text-surface-500">Opcional.</small>
                        </div>
                        <div>
                            <label for="email_usr" class="block font-bold mb-3">Email</label>
                            <InputText id="email_usr" v-model.trim="usuarioForm.email" fluid :invalid="submitted && !usuarioForm.email" type="email" />
                            <small class="text-red-500" v-if="submitted && !usuarioForm.email">Requerido.</small>
                        </div>
                    </div>

                    <div class="font-bold text-lg text-surface-500 border-b border-surface-200 dark:border-surface-700 pb-2">Credenciales de Acceso</div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="username_usr" class="block font-bold mb-3">Usuario</label>
                            <InputText id="username_usr" v-model.trim="usuarioForm.username" fluid :invalid="submitted && !usuarioForm.username" />
                            <small class="text-red-500" v-if="submitted && !usuarioForm.username">Requerido.</small>
                        </div>
                        <div>
                            <label for="password_usr" class="block font-bold mb-3">Contraseña</label>
                            <Password id="password_usr" v-model="usuarioForm.password" fluid :invalid="submitted && !usuarioForm.id && !usuarioForm.password" toggleMask :feedback="false" />
                            <small class="text-red-500" v-if="submitted && !usuarioForm.id && !usuarioForm.password">Requerido.</small>
                            <small class="text-surface-500" v-else-if="usuarioForm.id">Dejar vacío para mantener la actual.</small>
                        </div>
                    </div>

                    <div class="font-bold text-lg text-surface-500 border-b border-surface-200 dark:border-surface-700 pb-2">Rol y Permisos</div>
                    <div class="grid grid-cols-1 gap-4">
                        <div>
                            <label for="rol_usr" class="block font-bold mb-3">Rol</label>
                            <Select id="rol_usr" v-model="usuarioForm.rol" :options="rolesDisponibles" optionLabel="nombre" optionValue="id" placeholder="Seleccione un Rol" fluid :invalid="submitted && !usuarioForm.rol" />
                            <small class="text-red-500" v-if="submitted && !usuarioForm.rol">Requerido.</small>
                        </div>
                    </div>
                </div>
                <template #footer>
                    <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                    <Button label="Guardar" icon="pi pi-check" @click="saveUsuario" />
                </template>
            </Dialog>

            <!-- Modal de Detalle del Usuario -->
            <Dialog v-model:visible="detalleDialog" :style="{ width: '95vw', maxWidth: '850px' }" header="Ficha del Usuario" :modal="true">
                <div v-if="usuarioDetalle" class="flex flex-col gap-5">
                    <div class="surface-card border-2 border-primary-200 dark:border-primary-900 rounded-xl p-5 bg-gradient-to-br from-primary-50 to-white dark:from-primary-950 dark:to-surface-900">
                        <!-- Cabecera -->
                        <div class="flex items-center gap-4 mb-5">
                            <div class="flex items-center justify-center bg-primary-500 rounded-xl shadow-lg" style="width:3.5rem;height:3.5rem">
                                <i class="pi pi-user text-white text-2xl"></i>
                            </div>
                            <div class="flex-1">
                                <h3 class="text-2xl font-bold text-surface-900 dark:text-surface-0 mb-1">{{ usuarioDetalle.nombre_completo }}</h3>
                                <p class="text-surface-600 dark:text-surface-400 font-medium">
                                    <Tag :value="usuarioDetalle.rol_nombre" :severity="getSeverityRol(usuarioDetalle.rol_nombre)" class="text-xs" />
                                    <span class="text-primary-500 mx-2">•</span>
                                    {{ usuarioDetalle.casino_nombre }}
                                    <span class="text-primary-500 mx-2">•</span>
                                    <Tag :value="getLabelEstado(usuarioDetalle.esta_activo)" :severity="getSeverityEstado(usuarioDetalle.esta_activo)" class="text-xs" rounded />
                                </p>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <!-- Username -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-at text-blue-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Usuario</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm font-mono">{{ usuarioDetalle.username }}</span>
                            </div>
                            <!-- Email -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-envelope text-blue-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Email</span>
                                </div>
                                <a :href="'mailto:' + usuarioDetalle.email" class="text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium">
                                    {{ usuarioDetalle.email }}
                                </a>
                            </div>
                            <!-- Casino -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-building text-red-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Casino</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{ usuarioDetalle.casino_nombre }}</span>
                            </div>
                            <!-- Nombres -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-id-card text-teal-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Nombres</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{ usuarioDetalle.nombres }}</span>
                            </div>
                            <!-- Apellido Paterno -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-id-card text-teal-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Apellido Paterno</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{ usuarioDetalle.apellido_paterno }}</span>
                            </div>
                            <!-- Apellido Materno -->
                            <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-id-card text-teal-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Apellido Materno</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{ usuarioDetalle.apellido_materno || 'No registrado' }}</span>
                            </div>
                        </div>

                        <!-- Info de sesión -->
                        <div class="mt-5">
                            <div class="bg-gradient-to-br from-slate-50 to-gray-50 dark:from-slate-950 dark:to-gray-950 rounded-lg p-4 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-3">
                                    <i class="pi pi-shield text-slate-600 text-sm"></i>
                                    <span class="text-slate-700 dark:text-slate-400 text-sm font-bold uppercase tracking-wide">Información del Sistema</span>
                                </div>
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                        <div class="flex items-center gap-2 mb-2">
                                            <i class="pi pi-globe text-slate-500 text-sm"></i>
                                            <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Última IP</span>
                                        </div>
                                        <span class="font-bold text-surface-900 dark:text-surface-0 text-sm font-mono">{{ usuarioDetalle.ultima_ip || 'Sin registro' }}</span>
                                    </div>
                                    <div class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                        <div class="flex items-center gap-2 mb-2">
                                            <i class="pi pi-calendar text-slate-500 text-sm"></i>
                                            <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Creado</span>
                                        </div>
                                        <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">{{ usuarioDetalle.creado_en ? new Date(usuarioDetalle.creado_en).toLocaleDateString('es-MX') : 'N/A' }}</span>
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
