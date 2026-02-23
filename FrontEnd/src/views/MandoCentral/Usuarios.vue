<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '@/service/api';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import InsigniaRangoAnimada from '@/components/InsigniaRangoAnimada.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import Chart from 'primevue/chart';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

const usuarios = ref([]);
const casinos = ref([]);
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
const usuarioDialog = ref(false);
const usuario = ref({});
const submitted = ref(false);

// Variables para Gráficas
const chartDataCasinos = ref();
const chartOptionsCasinos = ref();
const chartDataRoles = ref();
const chartOptionsRoles = ref();
const chartDataEstado = ref();
const chartOptionsEstado = ref();
const chartDataRolesCasino = ref();
const chartOptionsRolesCasino = ref();
const chartDataEstadoCasino = ref();
const chartOptionsEstadoCasino = ref();
const casinoGraficaSeleccionado = ref(null);

// Sincronizar buscador del toolbar con filtros del DataTable
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Columnas configurables
const columnas = ref([
    { field: 'username', label: 'Usuario', visible: true },
    { field: 'nombre_completo', label: 'Nombre Completo', visible: true },
    { field: 'rango_gamificacion', label: 'Rango', visible: true },
    { field: 'email', label: 'Email', visible: true },
    { field: 'rol_nombre', label: 'Rol', visible: true },
    { field: 'casino_nombre', label: 'Casino', visible: true },
    { field: 'esta_activo', label: 'Estado', visible: true },
    { field: 'creado_en', label: 'Fecha Registro', visible: true },
    { field: 'ultima_ip', label: 'Última IP', visible: false },
    { field: 'user_agent', label: 'Dispositivo', visible: false },
    { field: 'intentos_fallidos', label: 'Intentos Fallidos', visible: false },
    { field: 'requiere_cambio_password', label: 'Cambio Pass', visible: false }
]);

// Cargar usuarios desde la API
const cargarUsuarios = async () => {
    loading.value = true;
    try {
        const response = await api.get('usuarios/lista/');
        usuarios.value = response.data;
        actualizarGraficas();
    } catch (error) {

        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudo cargar la lista de usuarios', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// Cargar catálogos para los dropdowns
const cargarCatalogos = async () => {
    try {
        const [resCasinos, resRoles] = await Promise.all([
            api.get('casinos/lista/'),
            api.get('roles/lista/')
        ]);
        casinos.value = resCasinos.data;
        roles.value = resRoles.data;
    } catch (error) {

        toast.add({ severity: 'warn', summary: 'Advertencia', detail: 'No se pudieron cargar algunos catálogos', life: 3000 });
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
const editarUsuario = (data) => {
    usuario.value = { ...data };
    // Limpiamos el password para que no se envíe si no se modifica
    usuario.value.password = '';
    usuarioDialog.value = true;
};

const openNew = () => {
    usuario.value = {
        esta_activo: true
    };
    submitted.value = false;
    usuarioDialog.value = true;
};

const hideDialog = () => {
    usuarioDialog.value = false;
    submitted.value = false;
};

const saveUsuario = async () => {
    submitted.value = true;

    // Validaciones básicas
    if (usuario.value.username?.trim() && usuario.value.nombres?.trim() && usuario.value.email?.trim() && usuario.value.rol && usuario.value.casino) {
        
        // Validación de contraseña para nuevos usuarios
        if (!usuario.value.id && !usuario.value.password) {
            toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'La contraseña es obligatoria para nuevos usuarios', life: 3000 });
            return;
        }

        loading.value = true;
        const payload = { ...usuario.value };

        // Si es edición y no se escribió password, lo eliminamos del payload para no enviarlo vacío
        if (usuario.value.id && !usuario.value.password) {
            delete payload.password;
        }

        try {
            if (usuario.value.id) {
                await api.put(`usuarios/${usuario.value.id}/`, payload);
                toast.add({ severity: 'success', summary: 'Éxito', detail: 'Usuario actualizado correctamente', life: 3000 });
            } else {
                await api.post('usuarios/', payload);
                toast.add({ severity: 'success', summary: 'Éxito', detail: 'Usuario creado correctamente', life: 3000 });
            }
            usuarioDialog.value = false;
            usuario.value = {};
            cargarUsuarios();
        } catch (error) {

            const msg = error.response?.data?.message || 'No se pudo guardar el usuario';
            toast.add({ severity: 'error', summary: 'Error', detail: msg, life: 3000 });
        } finally {
            loading.value = false;
        }
    }
};

const toggleActivarUsuario = (data) => {
    // Restricción de seguridad: No permitir desactivar usuarios ADMINISTRADOR
    if (data.rol_nombre === 'ADMINISTRADOR') {
        toast.add({ severity: 'warn', summary: 'Acción Restringida', detail: 'El usuario Administrador no puede ser desactivado.', life: 3000 });
        return;
    }

    const accion = data.esta_activo ? 'desactivar' : 'activar';
    
    confirm.require({
        message: `¿Estás seguro de que deseas ${accion} al usuario "${data.username}"?`,
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
                await api.patch(`usuarios/${data.id}/switch-estado/`, {});
                toast.add({ severity: 'success', summary: 'Éxito', detail: `Usuario ${accion === 'activar' ? 'activado' : 'desactivado'} correctamente`, life: 3000 });
                cargarUsuarios();
            } catch (error) {

                toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.error || error?.response?.data?.detail || `No se pudo ${accion} el usuario`, life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

// Lógica para Gráficas
const actualizarGraficas = () => {
    if (!usuarios.value.length) return;

    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--p-text-color') || '#334155';
    const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color') || '#64748b';
    const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color') || '#e2e8f0';

    // Opciones Base
    const baseOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: textColor } }
        },
        scales: {
            x: {
                ticks: { color: textColorSecondary },
                grid: { color: surfaceBorder }
            },
            y: {
                ticks: { color: textColorSecondary },
                grid: { color: surfaceBorder }
            }
        }
    };

    // 1. Gráfica: Usuarios por Casino
    const conteoCasinos = {};
    usuarios.value.forEach(u => {
        const nombre = u.casino_nombre || 'Sin Asignar';
        conteoCasinos[nombre] = (conteoCasinos[nombre] || 0) + 1;
    });

    chartDataCasinos.value = {
        labels: Object.keys(conteoCasinos),
        datasets: [{
            label: 'Cantidad de Usuarios',
            data: Object.values(conteoCasinos),
            backgroundColor: 'rgba(6, 182, 212, 0.6)', // Cyan
            borderColor: 'rgba(6, 182, 212, 1)',
            borderWidth: 1
        }]
    };
    chartOptionsCasinos.value = baseOptions;

    // 2. Gráfica: Tipos de Usuario (Roles Globales)
    const conteoRoles = {};
    usuarios.value.forEach(u => {
        const nombre = u.rol_nombre || 'Sin Rol';
        conteoRoles[nombre] = (conteoRoles[nombre] || 0) + 1;
    });

    chartDataRoles.value = {
        labels: Object.keys(conteoRoles),
        datasets: [{
            data: Object.values(conteoRoles),
            backgroundColor: [
                '#3b82f6', '#ef4444', '#22c55e', '#eab308', '#a855f7', 
                '#06b6d4', '#f97316', '#14b8a6', '#6366f1', '#ec4899'
            ]
        }]
    };
    chartOptionsRoles.value = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: { usePointStyle: true, color: textColor }
            }
        }
    };

    // 3. Gráfica: Estado de Usuarios (Activos vs Inactivos)
    const activos = usuarios.value.filter(u => u.esta_activo).length;
    const inactivos = usuarios.value.length - activos;

    chartDataEstado.value = {
        labels: ['Activos', 'Inactivos'],
        datasets: [{
            data: [activos, inactivos],
            backgroundColor: ['#22c55e', '#ef4444'],
            hoverBackgroundColor: ['#16a34a', '#dc2626']
        }]
    };
    chartOptionsEstado.value = {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
            legend: { position: 'bottom', labels: { color: textColor } }
        }
    };

    // Actualizar gráfica interactiva si hay selección
    actualizarGraficaRolesCasino();
};

const actualizarGraficaRolesCasino = () => {
    if (!casinoGraficaSeleccionado.value) {
        chartDataRolesCasino.value = null;
        chartDataEstadoCasino.value = null;
        return;
    }

    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--p-text-color') || '#334155';
    const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color') || '#64748b';
    const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color') || '#e2e8f0';

    const casinoId = casinoGraficaSeleccionado.value;
    const usuariosFiltrados = usuarios.value.filter(u => u.casino === casinoId);
    
    // 1. Roles en Casino (Pie)
    const conteoRoles = {};
    usuariosFiltrados.forEach(u => {
        const nombre = u.rol_nombre || 'Sin Rol';
        conteoRoles[nombre] = (conteoRoles[nombre] || 0) + 1;
    });

    chartDataRolesCasino.value = {
        labels: Object.keys(conteoRoles),
        datasets: [{
            data: Object.values(conteoRoles),
            backgroundColor: [
                '#3b82f6', '#ef4444', '#22c55e', '#eab308', '#a855f7', 
                '#06b6d4', '#f97316', '#14b8a6', '#6366f1', '#ec4899'
            ]
        }]
    };
    chartOptionsRolesCasino.value = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: { usePointStyle: true, color: textColor }
            }
        }
    };

    // 2. Estado en Casino (Doughnut)
    const activos = usuariosFiltrados.filter(u => u.esta_activo).length;
    const inactivos = usuariosFiltrados.length - activos;

    chartDataEstadoCasino.value = {
        labels: ['Activos', 'Inactivos'],
        datasets: [{
            data: [activos, inactivos],
            backgroundColor: ['#22c55e', '#ef4444'],
            hoverBackgroundColor: ['#16a34a', '#dc2626']
        }]
    };
    chartOptionsEstadoCasino.value = {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
            legend: { position: 'bottom', labels: { color: textColor } }
        }
    };
};

// Watcher para la gráfica interactiva
watch(casinoGraficaSeleccionado, actualizarGraficaRolesCasino);

onMounted(() => {
    cargarUsuarios();
    cargarCatalogos();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <!-- Sección de Estadísticas -->
        <div class="card">
            <div class="font-semibold text-xl mb-4">Métricas de Usuarios</div>
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <!-- Gráfica 1: Usuarios por Casino -->
                <div class="flex flex-col items-center justify-center">
                    <div class="font-semibold mb-2 text-center">Usuarios por Casino</div>
                    <div class="relative w-full h-[200px]">
                        <Chart v-if="chartDataCasinos" type="bar" :data="chartDataCasinos" :options="chartOptionsCasinos" class="h-full w-full" />
                    </div>
                </div>

                <!-- Gráfica 2: Distribución de Roles Global -->
                <div class="flex flex-col items-center justify-center">
                    <div class="font-semibold mb-2 text-center">Distribución de Roles</div>
                    <div class="relative w-full h-[200px] flex justify-center">
                        <Chart v-if="chartDataRoles" type="pie" :data="chartDataRoles" :options="chartOptionsRoles" class="h-full w-full" />
                    </div>
                </div>

                <!-- Gráfica 3: Estado de Usuarios -->
                <div class="flex flex-col items-center justify-center">
                    <div class="font-semibold mb-2 text-center">Estado de Usuarios</div>
                    <div class="relative w-full h-[200px] flex justify-center">
                        <Chart v-if="chartDataEstado" type="doughnut" :data="chartDataEstado" :options="chartOptionsEstado" class="h-full w-full" />
                    </div>
                </div>
            </div>

            <div class="border-t border-surface-200 dark:border-surface-700 my-8"></div>

            <!-- Gráfica 4: Roles por Casino (Interactivo) -->
            <div class="flex flex-col">
                <div class="flex flex-col sm:flex-row items-center justify-between mb-4 gap-4">
                    <div class="font-semibold text-lg">Estadísticas por Casino</div>
                    <Select 
                        v-model="casinoGraficaSeleccionado" 
                        :options="casinos" 
                        optionLabel="nombre" 
                        optionValue="id" 
                        placeholder="Seleccione Casino" 
                        class="w-full sm:w-72" 
                    />
                </div>
                <div v-if="chartDataRolesCasino" class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div class="flex flex-col items-center justify-center">
                        <div class="font-semibold mb-2 text-center">Distribución de Roles</div>
                        <div class="relative w-full h-[250px] flex justify-center">
                            <Chart type="pie" :data="chartDataRolesCasino" :options="chartOptionsRolesCasino" class="h-full w-full" />
                        </div>
                    </div>
                    <div class="flex flex-col items-center justify-center">
                        <div class="font-semibold mb-2 text-center">Estado de Usuarios</div>
                        <div class="relative w-full h-[250px] flex justify-center">
                            <Chart type="doughnut" :data="chartDataEstadoCasino" :options="chartOptionsEstadoCasino" class="h-full w-full" />
                        </div>
                    </div>
                </div>
                <div v-else class="flex items-center justify-center h-[250px] text-surface-500 bg-surface-50 dark:bg-surface-900 rounded border border-dashed border-surface-300 dark:border-surface-700">
                    <div class="text-center text-sm">
                        <i class="pi pi-chart-bar text-2xl mb-2"></i>
                        <p>Seleccione un casino para ver detalles.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <Toast />
            <ConfirmDialog />
            
            <!-- Toolbar personalizable -->
            <DataTableToolbar
                ref="toolbarRef"
                :dt="dt"
                :datos="usuarios"
                titulo-reporte="Gestión de Usuarios del Sistema"
                nombre-archivo="usuarios"
                :columnas="columnas"
                :mostrar-exportacion="true"
                :mostrar-imprimir="true"
                :mostrar-refrescar="true"
                :mostrar-selector-columnas="true"
                :mostrar-buscador="true"
                @refrescar="cargarUsuarios"
                v-model:columnas-seleccionadas="columnas"
            >
                <template #acciones-extra>
                    <Button 
                        icon="pi pi-plus" 
                        label="Nuevo Usuario"
                        rounded
                        severity="primary"
                        @click="openNew"
                    />
                </template>
            </DataTableToolbar>
            
            <DataTable 
                ref="dt"
                :value="usuarios" 
                :loading="loading"
                v-model:filters="filtros"
                :globalFilterFields="['username', 'nombres', 'apellido_paterno', 'email', 'rol_nombre', 'casino_nombre']"
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
                        No se encontraron usuarios registrados.
                    </div>
                </template>
                
                <template #loading>
                    Cargando información de usuarios...
                </template>
                
                <Column v-if="esColumnaVisible('username')" field="username" header="Usuario" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <span class="font-bold">{{ data.username }}</span>
                    </template>
                </Column>
                
                <Column v-if="esColumnaVisible('nombre_completo')" field="nombre_completo" header="Nombre Completo" sortable style="min-width: 14rem">
                    <template #body="{ data }">
                        {{ data.nombres }} {{ data.apellido_paterno }} {{ data.apellido_materno }}
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('rango_gamificacion')" field="rango_gamificacion" header="Rango" sortable style="min-width: 11rem">
                    <template #body="{ data }">
                        <InsigniaRangoAnimada
                            v-if="data.rango_gamificacion"
                            :nivel="data.rango_gamificacion.nivel"
                            :nombreRango="data.rango_gamificacion.titulo"
                            :compact="true"
                        />
                        <span v-else class="text-surface-400 text-sm">—</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('email')" field="email" header="Email" sortable style="min-width: 14rem" />
                
                <Column v-if="esColumnaVisible('rol_nombre')" field="rol_nombre" header="Rol" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <Tag :value="data.rol_nombre" severity="info" />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('casino_nombre')" field="casino_nombre" header="Casino" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <span class="text-sm">{{ data.casino_nombre || 'N/A' }}</span>
                    </template>
                </Column>
                
                <Column v-if="esColumnaVisible('esta_activo')" field="esta_activo" header="Estado" sortable style="min-width: 8rem">
                    <template #body="{ data }">
                        <Tag :value="data.esta_activo ? 'Activo' : 'Inactivo'" :severity="data.esta_activo ? 'success' : 'danger'" />
                    </template>
                </Column>
                
                <Column v-if="esColumnaVisible('creado_en')" field="creado_en" header="Fecha Registro" sortable style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="text-sm">{{ formatearFecha(data.creado_en) }}</div>
                    </template>
                </Column>
                
                <Column v-if="esColumnaVisible('ultima_ip')" field="ultima_ip" header="Última IP" sortable style="min-width: 10rem">
                    <template #body="{ data }">
                        <span class="font-mono text-sm">{{ data.ultima_ip || 'N/A' }}</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('user_agent')" field="user_agent" header="Dispositivo" sortable style="min-width: 15rem">
                    <template #body="{ data }">
                        <span class="text-xs truncate block max-w-[15rem]" :title="data.user_agent">{{ data.user_agent || 'N/A' }}</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('intentos_fallidos')" field="intentos_fallidos" header="Intentos Fallidos" sortable style="min-width: 8rem">
                    <template #body="{ data }">
                        <Badge :value="data.intentos_fallidos" :severity="data.intentos_fallidos > 0 ? 'warn' : 'success'" />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('requiere_cambio_password')" field="requiere_cambio_password" header="Cambio Pass" sortable style="min-width: 8rem">
                    <template #body="{ data }">
                        <i :class="[data.requiere_cambio_password ? 'pi pi-check-circle text-orange-500' : 'pi pi-minus-circle text-surface-400']"></i>
                    </template>
                </Column>

                <Column header="Acciones" :exportable="false" style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button icon="pi pi-pencil" size="small" severity="info" rounded outlined @click="editarUsuario(data)" v-tooltip.top="'Editar'" />
                            <Button :icon="data.esta_activo ? 'pi pi-ban' : 'pi pi-check-circle'" size="small" :severity="data.esta_activo ? 'warning' : 'success'" rounded outlined @click="toggleActivarUsuario(data)" v-tooltip.top="data.esta_activo ? 'Desactivar' : 'Activar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <Dialog v-model:visible="usuarioDialog" :style="{ width: '600px' }" header="Detalles del Usuario" :modal="true">
                <div class="flex flex-col gap-6">
                    <!-- Formulario -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="username" class="block font-bold mb-3">Usuario</label>
                            <InputText id="username" v-model.trim="usuario.username" required="true" autofocus :invalid="submitted && !usuario.username" fluid />
                            <small class="text-red-500" v-if="submitted && !usuario.username">El usuario es obligatorio.</small>
                        </div>
                        <div>
                            <label for="email" class="block font-bold mb-3">Email</label>
                            <InputText id="email" v-model.trim="usuario.email" required="true" :invalid="submitted && !usuario.email" fluid />
                            <small class="text-red-500" v-if="submitted && !usuario.email">El email es obligatorio.</small>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label for="nombres" class="block font-bold mb-3">Nombres</label>
                            <InputText id="nombres" v-model.trim="usuario.nombres" required="true" :invalid="submitted && !usuario.nombres" fluid />
                            <small class="text-red-500" v-if="submitted && !usuario.nombres">Requerido.</small>
                        </div>
                        <div>
                            <label for="apellido_paterno" class="block font-bold mb-3">Apellido Paterno</label>
                            <InputText id="apellido_paterno" v-model.trim="usuario.apellido_paterno" fluid />
                        </div>
                        <div>
                            <label for="apellido_materno" class="block font-bold mb-3">Apellido Materno</label>
                            <InputText id="apellido_materno" v-model.trim="usuario.apellido_materno" fluid />
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="rol" class="block font-bold mb-3">Rol</label>
                            <Select id="rol" v-model="usuario.rol" :options="roles" optionLabel="nombre" optionValue="id" placeholder="Seleccione un Rol" fluid :invalid="submitted && !usuario.rol" />
                            <small class="text-red-500" v-if="submitted && !usuario.rol">El rol es obligatorio.</small>
                        </div>
                        <div>
                            <label for="casino" class="block font-bold mb-3">Casino</label>
                            <Select id="casino" v-model="usuario.casino" :options="casinos" optionLabel="nombre" optionValue="id" placeholder="Seleccione un Casino" fluid :invalid="submitted && !usuario.casino" />
                            <small class="text-red-500" v-if="submitted && !usuario.casino">El casino es obligatorio.</small>
                        </div>
                    </div>

                    <div>
                        <label for="password" class="block font-bold mb-3">Contraseña</label>
                        <Password id="password" v-model="usuario.password" :feedback="true" toggleMask fluid placeholder="Dejar en blanco para mantener actual" />
                        <small class="text-surface-500" v-if="usuario.id">Solo llenar si desea cambiar la contraseña.</small>
                        <small class="text-red-500" v-if="submitted && !usuario.id && !usuario.password">La contraseña es obligatoria para nuevos usuarios.</small>
                    </div>

                    <div class="flex flex-col gap-3 mt-2">
                        <div class="flex items-center">
                            <Checkbox v-model="usuario.esta_activo" :binary="true" inputId="esta_activo" />
                            <label for="esta_activo" class="ml-2 cursor-pointer">¿Usuario Activo?</label>
                        </div>
                        <div class="flex items-center">
                            <Checkbox v-model="usuario.requiere_cambio_password" :binary="true" inputId="requiere_cambio_password" />
                            <label for="requiere_cambio_password" class="ml-2 cursor-pointer">¿Forzar cambio de contraseña?</label>
                        </div>
                    </div>

                    <!-- Sección de Auditoría (Solo visible en edición) -->
                    <div v-if="usuario.id" class="border-t border-surface-200 dark:border-surface-700 pt-4 mt-2">
                        <div class="font-bold mb-3 text-surface-500 dark:text-surface-400">Información de Auditoría</div>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                            <div>
                                <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Última IP</label>
                                <InputText id="ultima_ip" name="ultima_ip" :value="usuario.ultima_ip || 'N/A'" disabled fluid class="opacity-100 font-mono text-sm" />
                            </div>
                            <div>
                                <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Intentos Fallidos</label>
                                <InputText id="intentos_fallidos" name="intentos_fallidos" :value="usuario.intentos_fallidos" disabled fluid class="opacity-100" />
                            </div>
                            <div>
                                <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Fecha Registro</label>
                                <InputText id="creado_en" name="creado_en" :value="formatearFecha(usuario.creado_en)" disabled fluid class="opacity-100" />
                            </div>
                        </div>
                        <div>
                            <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">User Agent (Última Conexión)</label>
                            <Textarea id="user_agent" name="user_agent" :value="usuario.user_agent || 'Sin registro de conexión'" rows="2" disabled fluid class="opacity-100 text-xs" />
                        </div>
                    </div>
                </div>

                <template #footer>
                    <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                    <Button label="Guardar" icon="pi pi-check" @click="saveUsuario" />
                </template>
            </Dialog>
        </div>
    </div>
</template>