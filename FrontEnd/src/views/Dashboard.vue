<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { getUser, hasRoleAccess, fetchRoles } from '@/service/api';
import { getDashboardStats, guardarUsuario } from '@/service/usuarioService';
import { crearTicket } from '@/service/ticketService';
import { getMaquinasPorCasino } from '@/service/maquinaService';
import EvolucionService from '@/service/EvolucionService';
import { useToast } from 'primevue/usetoast';

// Components
// Auto-imported in this project structure (matching Usuarios.vue)

const router = useRouter();
const user = getUser();
const toast = useToast();
const evolucionService = new EvolucionService();

// Permissions
const canViewGlobalStats = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA']));
const canViewTechStats = computed(() => hasRoleAccess(['ADMINISTRADOR', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA']));

// Data State
const stats = ref({
    usuariosActivos: 0,
    ticketsPendientes: 0,
    ticketsCriticos: 0,
    reportesEvolucion: 0
});

const recentActivity = ref([]);
const loading = ref(true);

// --- QUICK ACTIONS STATE ---

// 1. Evolucion Nexus (Reportar Error)
const evolucionDialog = ref(false);
const evolucion = ref({ categoria: 'ERROR', datos_extra: {}, titulo: '', descripcion: '' });
const submittedEvolucion = ref(false);

const openEvolucionDialog = () => {
    evolucion.value = { categoria: 'ERROR', datos_extra: {}, titulo: '', descripcion: '' };
    submittedEvolucion.value = false;
    evolucionDialog.value = true;
};

const saveEvolucion = () => {
    submittedEvolucion.value = true;
    if (evolucion.value.titulo && evolucion.value.titulo.trim() && evolucion.value.descripcion) {
        evolucionService.createEvolucion(evolucion.value).then(() => {
            toast.add({ severity: 'success', summary: 'Reporte Enviado', detail: 'Gracias por tu feedback', life: 3000 });
            evolucionDialog.value = false; // Cerrar el modal
            loadDashboardData(); // Refresh activity
        });
    }
};

// 2. Nuevo Usuario (Refinado)
const usuarioDialog = ref(false);
const usuario = ref({});
const submittedUsuario = ref(false);
const roles = ref([]);

// Roles disponibles filtrados según el rol del usuario logueado
const rolesDisponibles = computed(() => {
    if (!roles.value) return [];

    const rolActual = user?.rol_nombre;
    const esAdminODBA = ['ADMINISTRADOR', 'DB ADMIN'].includes(rolActual);
    if (esAdminODBA) {
        // Admin y DB Admin ven todos los roles (excepto ADMINISTRADOR)
        return roles.value.filter(r => r.nombre !== 'ADMINISTRADOR');
    }
    // Los demás solo ven TECNICO y SUPERVISOR SALA
    return roles.value.filter(r => ['TECNICO', 'SUPERVISOR SALA'].includes(r.nombre));
});

const openUsuarioDialog = async () => {
    usuario.value = {
        esta_activo: true,
        casino: user?.casino // Auto-asignar casino del usuario logueado
    };
    submittedUsuario.value = false;
    usuarioDialog.value = true;

    // Cargar roles si no existen
    if (roles.value.length === 0) {
        const resRoles = await fetchRoles();
        if (resRoles.success && Array.isArray(resRoles.data)) {
            roles.value = resRoles.data.filter(r => r.esta_activo);
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los roles', life: 3000 });
        }
    }
};

const saveUsuario = async () => {
    submittedUsuario.value = true;
    // Validar campos requeridos
    if (usuario.value.username && usuario.value.nombres && usuario.value.apellido_paterno && usuario.value.email && usuario.value.rol && usuario.value.casino && usuario.value.password) {
        const res = await guardarUsuario(usuario.value);
        if (res.exito) {
            toast.add({ severity: 'success', summary: 'Usuario Creado', detail: res.mensaje, life: 3000 });
            usuarioDialog.value = false; // Cerrar el modal
            loadDashboardData();
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: res.detalle || res.error, life: 3000 });
        }
    }
};

// 3. Nuevo Ticket
const ticketDialog = ref(false);
const ticket = ref({});
const submittedTicket = ref(false);
const maquinas = ref([]);
const categoriasTicket = ref([
    { label: 'Hardware', value: 'hardware' },
    { label: 'Periféricos', value: 'perifericos' },
    { label: 'Software', value: 'software' },
    { label: 'Red / Comunicación', value: 'red' },
    { label: 'Otros', value: 'otros' }
]);
const prioridadesTicket = ref([
    { label: 'Baja', value: 'baja' },
    { label: 'Media', value: 'media' },
    { label: 'Alta', value: 'alta' },
    { label: 'Crítica', value: 'critica' },
    { label: 'Emergencia', value: 'emergencia' }
]);

const openTicketDialog = async () => {
    ticket.value = { prioridad: 'media', categoria: 'hardware' }; // Default values
    submittedTicket.value = false;
    ticketDialog.value = true;

    // Cargar máquinas del casino del usuario
    if ((maquinas.value.length === 0) && user?.casino) {
        const res = await getMaquinasPorCasino(user.casino);
        if (res.exito) {
            maquinas.value = res.data.maquinas || res.data;
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar las máquinas', life: 3000 });
        }
    }
};

const saveTicket = async () => {
    submittedTicket.value = true;

    // Validar campos mínimos
    if (ticket.value.maquina && ticket.value.categoria && ticket.value.descripcion) {
        // Encontrar UID de la máquina seleccionada para mostrar en el mensaje
        const maquinaSeleccionada = maquinas.value.find(m => m.id === ticket.value.maquina);
        const maquinaUid = maquinaSeleccionada ? maquinaSeleccionada.uid_sala : 'Desconocida';

        const result = await crearTicket({
            maquinaId: ticket.value.maquina,
            maquinaUid: maquinaUid,
            categoria: ticket.value.categoria,
            subcategoria: ticket.value.subcategoria,
            prioridad: ticket.value.prioridad,
            descripcionBase: ticket.value.descripcion,
            estadoMaquina: 'DAÑADA', // Asumimos dañada por defecto en quick action
            reportanteId: user.id,
            notasSeguimiento: '',
            incrementarContador: true,
            actualizarEstado: true
        });

        if (result.exito) {
            toast.add({ severity: 'success', summary: 'Ticket Creado', detail: `Folio: ${result.ticket.folio}`, life: 3000 });
            ticketDialog.value = false; // Cerrar el modal
            loadDashboardData();
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.detalle || result.error, life: 3000 });
        }
    }
};

// 4. Botón de Pánico
const panicDialog = ref(false);
const panicTicket = ref({ uid_sala: '' });
const submittedPanic = ref(false);

const openPanicDialog = async () => {
    panicTicket.value = { uid_sala: '' };
    submittedPanic.value = false;
    panicDialog.value = true;

    // Cargar máquinas si no están cargadas
    if ((maquinas.value.length === 0) && user?.casino) {
        const res = await getMaquinasPorCasino(user.casino);
        if (res.exito) {
            maquinas.value = res.data.maquinas || res.data;
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar las máquinas', life: 3000 });
        }
    }
};

const savePanicTicket = async () => {
    submittedPanic.value = true;

    if (panicTicket.value.uid_sala) {
        const searchUid = panicTicket.value.uid_sala.trim().toUpperCase();
        const maquinaSeleccionada = maquinas.value.find(m => m.uid_sala.toUpperCase() === searchUid);

        if (!maquinaSeleccionada) {
            toast.add({ severity: 'error', summary: 'Error', detail: `No se encontró una máquina con el UID: ${searchUid}`, life: 3000 });
            return;
        }

        const result = await crearTicket({
            maquinaId: maquinaSeleccionada.id,
            maquinaUid: maquinaSeleccionada.uid_sala,
            categoria: 'otros',
            subcategoria: 'Ticket Rápido',
            prioridad: 'emergencia',
            descripcionBase: 'Ticket generado automáticamente desde el botón de acceso rápido del dashboard. Revisar de inmediato.',
            estadoMaquina: 'DAÑADA',
            reportanteId: user.id,
            notasSeguimiento: '',
            incrementarContador: true,
            actualizarEstado: true
        });

        if (result.exito) {
            toast.add({ severity: 'success', summary: 'Ticket Rápido Creado', detail: `Folio: ${result.ticket.folio}`, life: 4000 });
            panicDialog.value = false;
            loadDashboardData();
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.detalle || result.error, life: 3000 });
        }
    }
};

const quickActions = computed(() => {
    const actions = [
        {
            label: 'Ticket Rápido',
            icon: 'pi pi-bolt',
            action: openPanicDialog,
            color: 'bg-red-500',
            allowed: true
        },
        {
            label: 'Nuevo Ticket',
            icon: 'pi pi-ticket',
            action: openTicketDialog,
            color: 'bg-blue-500',
            allowed: true
        },
        {
            label: 'Crear Usuario',
            icon: 'pi pi-user-plus',
            action: openUsuarioDialog,
            color: 'bg-green-500',
            allowed: hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS']) // Ampliado para coincidir con Usuarios.vue
        },
        {
            label: 'Reportar Error',
            icon: 'pi pi-exclamation-circle',
            action: openEvolucionDialog,
            color: 'bg-orange-500',
            allowed: true
        },
        {
            label: 'Inventario',
            icon: 'pi pi-box',
            action: () => router.push('/centro-servicios/inventario'),
            color: 'bg-purple-500',
            allowed: hasRoleAccess(['ADMINISTRADOR', 'SUP SISTEMAS', 'TECNICO'])
        }
    ];
    return actions.filter(a => a.allowed);
});

// Mock/Fetch Data
const loadDashboardData = async () => {
    loading.value = true;
    try {
        const data = await getDashboardStats();

        if (canViewGlobalStats.value) {
            stats.value.usuariosActivos = data.kpis.usuarios_activos;
            stats.value.ticketsPendientes = data.kpis.tickets_pendientes;
            stats.value.ticketsCriticos = data.kpis.tickets_criticos;
            stats.value.reportesEvolucion = data.kpis.reportes_evolucion;
        }

        // Mapear actividad reciente del backend
        recentActivity.value = data.actividad_reciente.map(item => ({
            ...item,
            date: new Date(item.fecha).toLocaleString()
        }));

    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar el estado del dashboard', life: 3000 });
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    loadDashboardData();
});

const handleAction = (actionFn) => {
    if (actionFn) actionFn();
};
</script>

<template>
    <div class="grid grid-cols-12 gap-6">
        <Toast />
        <!-- Welcome Section -->
        <div class="col-span-12">
            <div class="card bg-surface-0 dark:bg-surface-900 border-l-4 border-primary">
                <div class="flex items-center justify-between">
                    <div>
                        <div class="text-2xl font-bold mb-1">¡Hola, {{ user?.nombres }}!</div>
                        <div class="text-surface-500">Bienvenido al Centro de Comando NEXUS.</div>
                    </div>
                    <i class="pi pi-compass text-4xl text-primary opacity-50"></i>
                </div>
            </div>
        </div>

        <!-- Quick Actions (Moved to Top) -->
        <div class="col-span-12">
            <div class="card">
                <div class="font-semibold text-xl mb-4">Accesos Rápidos</div>
                <div class="grid grid-cols-2 md:grid-cols-5 gap-4 transition-all">
                    <div v-for="action in quickActions" :key="action.label"
                        class="flex flex-col items-center p-4 border rounded-xl cursor-pointer hover:bg-surface-100 dark:hover:bg-surface-800 transition-transform hover:scale-105"
                        @click="handleAction(action.action)">
                        <div
                            :class="['flex items-center justify-center w-14 h-14 rounded-full text-white mb-3 shadow-lg', action.color]">
                            <i :class="[action.icon, 'text-2xl']"></i>
                        </div>
                        <span class="font-medium text-center">{{ action.label }}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- KPI Widgets (Grouped in Single Card) -->
        <div v-if="canViewGlobalStats" class="col-span-12">
            <div class="card">
                <div class="font-semibold text-xl mb-4">Estado del Sistema</div>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <!-- KPI 1 -->
                    <div
                        class="flex justify-between items-center p-4 border rounded-lg bg-surface-50 dark:bg-surface-800">
                        <div>
                            <span class="block text-surface-500 font-medium mb-1">Usuarios Activos</span>
                            <div class="text-surface-900 dark:text-surface-0 font-bold text-2xl">{{
                                stats.usuariosActivos }}</div>
                        </div>
                        <div
                            class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-full w-12 h-12">
                            <i class="pi pi-users text-blue-500 text-xl"></i>
                        </div>
                    </div>
                    <!-- KPI 2 -->
                    <div
                        class="flex justify-between items-center p-4 border rounded-lg bg-surface-50 dark:bg-surface-800">
                        <div>
                            <span class="block text-surface-500 font-medium mb-1">Tickets Pendientes</span>
                            <div class="text-surface-900 dark:text-surface-0 font-bold text-2xl">{{
                                stats.ticketsPendientes }}</div>
                        </div>
                        <div
                            class="flex items-center justify-center bg-orange-100 dark:bg-orange-400/10 rounded-full w-12 h-12">
                            <i class="pi pi-ticket text-orange-500 text-xl"></i>
                        </div>
                    </div>
                    <!-- KPI 3 -->
                    <div
                        class="flex justify-between items-center p-4 border rounded-lg bg-surface-50 dark:bg-surface-800">
                        <div>
                            <span class="block text-surface-500 font-medium mb-1">Tickets Críticos</span>
                            <div class="text-surface-900 dark:text-surface-0 font-bold text-2xl">{{
                                stats.ticketsCriticos }}</div>
                        </div>
                        <div
                            class="flex items-center justify-center bg-red-100 dark:bg-red-400/10 rounded-full w-12 h-12">
                            <i class="pi pi-exclamation-circle text-red-500 text-xl"></i>
                        </div>
                    </div>
                    <!-- KPI 4 -->
                    <div
                        class="flex justify-between items-center p-4 border rounded-lg bg-surface-50 dark:bg-surface-800">
                        <div>
                            <span class="block text-surface-500 font-medium mb-1">Reportes Evolución</span>
                            <div class="text-surface-900 dark:text-surface-0 font-bold text-2xl">{{
                                stats.reportesEvolucion }}</div>
                        </div>
                        <div
                            class="flex items-center justify-center bg-purple-100 dark:bg-purple-400/10 rounded-full w-12 h-12">
                            <i class="pi pi-bolt text-purple-500 text-xl"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Activity Feed -->
        <div class="col-span-12">
            <div class="card h-full">
                <div class="flex items-center justify-between mb-4">
                    <div class="font-semibold text-xl">Actividad Reciente</div>
                    <Button icon="pi pi-refresh" text rounded @click="loadDashboardData" :loading="loading" />
                </div>
                <div v-if="loading" class="flex justify-center p-4">
                    <i class="pi pi-spin pi-spinner text-2xl"></i>
                </div>
                <ul v-else class="p-0 m-0 list-none max-h-[400px] overflow-y-auto">
                    <li v-for="(activity, index) in recentActivity" :key="index"
                        class="flex items-start py-3 border-b border-surface-200 dark:border-surface-700 last:border-0 hover:bg-surface-50 dark:hover:bg-surface-800/50 px-2 rounded-md transition-colors">
                        <div
                            class="w-10 h-10 flex items-center justify-center rounded-full bg-surface-100 dark:bg-surface-800 mr-3 shrink-0 mt-1">
                            <i :class="[activity.icono, activity.color, 'text-lg']"></i>
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="font-medium text-sm truncate" :title="activity.titulo">{{ activity.titulo }}
                            </div>
                            <div class="text-sm text-surface-600 dark:text-surface-400 line-clamp-2"
                                :title="activity.descripcion">{{ activity.descripcion }}</div>
                            <div class="text-xs text-surface-500 mt-1">{{ activity.date }}</div>
                        </div>
                    </li>
                    <li v-if="recentActivity.length === 0" class="text-center py-4 text-surface-500">
                        No hay actividad reciente.
                    </li>
                </ul>
            </div>
        </div>

        <!-- Dialog: Nuevo Ticket -->
        <Dialog v-model:visible="ticketDialog" :style="{ width: '600px' }" :modal="true" header="Nuevo Ticket Rápido">
            <div class="flex flex-col gap-4">
                <div>
                    <label class="block font-medium mb-1">Máquina</label>
                    <Select v-model="ticket.maquina" :options="maquinas" optionLabel="uid_sala" optionValue="id"
                        placeholder="Seleccione Máquina" filter fluid :invalid="submittedTicket && !ticket.maquina">
                        <template #option="slotProps">
                            <div class="flex flex-col">
                                <span class="font-bold">{{ slotProps.option.uid_sala }}</span>
                                <span class="text-xs text-surface-500">{{ slotProps.option.modelo_nombre }}</span>
                            </div>
                        </template>
                    </Select>
                    <small class="text-red-500" v-if="submittedTicket && !ticket.maquina">Requerido.</small>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block font-medium mb-1">Categoría</label>
                        <Select v-model="ticket.categoria" :options="categoriasTicket" optionLabel="label"
                            optionValue="value" fluid :invalid="submittedTicket && !ticket.categoria" />
                        <small class="text-red-500" v-if="submittedTicket && !ticket.categoria">Requerido.</small>
                    </div>
                    <div>
                        <label class="block font-medium mb-1">Prioridad</label>
                        <Select v-model="ticket.prioridad" :options="prioridadesTicket" optionLabel="label"
                            optionValue="value" fluid />
                    </div>
                </div>
                <div>
                    <label class="block font-medium mb-1">Descripción del Problema</label>
                    <Textarea v-model="ticket.descripcion" rows="4" fluid placeholder="Describe la falla..."
                        :invalid="submittedTicket && !ticket.descripcion" />
                    <small class="text-red-500" v-if="submittedTicket && !ticket.descripcion">Requerido.</small>
                </div>
                <div>
                    <label class="block font-medium mb-1">Subcategoría (Opcional)</label>
                    <InputText v-model="ticket.subcategoria" fluid placeholder="Ej: Billetero Atascado" />
                </div>
            </div>
            <template #footer>
                <Button label="Cancelar" text severity="secondary" @click="ticketDialog = false" />
                <Button label="Crear Ticket" icon="pi pi-check" severity="primary" @click="saveTicket" />
            </template>
        </Dialog>

        <!-- Dialog: Reportar Error (Evolución) -->
        <Dialog v-model:visible="evolucionDialog" :style="{ width: '500px' }" :modal="true"
            header="Reportar Incidencia Rápida">
            <div class="flex flex-col gap-4">
                <div>
                    <label class="block font-medium mb-1">Título</label>
                    <InputText v-model="evolucion.titulo" fluid placeholder="Ej: Error al guardar..."
                        :invalid="submittedEvolucion && !evolucion.titulo" />
                    <small class="text-red-500" v-if="submittedEvolucion && !evolucion.titulo">Requerido.</small>
                </div>
                <div>
                    <label class="block font-medium mb-1">Descripción</label>
                    <Textarea v-model="evolucion.descripcion" rows="4" fluid placeholder="Describe qué sucedió..."
                        :invalid="submittedEvolucion && !evolucion.descripcion" />
                    <small class="text-red-500" v-if="submittedEvolucion && !evolucion.descripcion">Requerido.</small>
                </div>
            </div>
            <template #footer>
                <Button label="Cancelar" text severity="secondary" @click="evolucionDialog = false" />
                <Button label="Enviar Reporte" icon="pi pi-send" severity="primary" @click="saveEvolucion" />
            </template>
        </Dialog>

        <!-- Dialog: Ticket Rápido -->
        <Dialog v-model:visible="panicDialog" :style="{ width: '400px' }" :modal="true" header="Ticket Rápido">
            <div class="flex flex-col gap-4 items-center text-center p-4">
                <i class="pi pi-bolt text-red-500 text-6xl mb-2"></i>
                <p class="text-surface-600 dark:text-surface-300">
                    Ingrese el UID de la máquina para generar un ticket de alta prioridad de forma inmediata. La máquina
                    debe
                    pertenecer a su casino asignado.
                </p>
                <div class="w-full">
                    <label class="block font-medium mb-1 text-left">UID de la Máquina</label>
                    <InputText v-model="panicTicket.uid_sala" fluid placeholder="Ej: MQ-001" autofocus
                        :invalid="submittedPanic && !panicTicket.uid_sala" @keyup.enter="savePanicTicket" />
                    <small class="text-red-500 text-left block"
                        v-if="submittedPanic && !panicTicket.uid_sala">Requerido.</small>
                </div>
            </div>
            <template #footer>
                <Button label="Cancelar" text severity="secondary" @click="panicDialog = false" />
                <Button label="Generar Ticket" icon="pi pi-bolt" severity="danger" @click="savePanicTicket" />
            </template>
        </Dialog>

        <!-- Dialog: Nuevo Usuario (Simplificado) -->
        <Dialog v-model:visible="usuarioDialog" :style="{ width: '700px' }" :modal="true"
            header="Registro Rápido de Usuario">
            <div class="flex flex-col gap-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block font-medium mb-1">Casino</label>
                        <InputText :value="user?.casino_nombre" fluid disabled
                            class="bg-surface-100 dark:bg-surface-800" />
                        <small class="text-surface-500">Auto-asignado.</small>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block font-medium mb-1">Usuario</label>
                        <InputText v-model="usuario.username" fluid :invalid="submittedUsuario && !usuario.username" />
                        <small class="text-red-500" v-if="submittedUsuario && !usuario.username">Requerido.</small>
                    </div>
                    <div>
                        <label class="block font-medium mb-1">Email</label>
                        <InputText v-model="usuario.email" fluid :invalid="submittedUsuario && !usuario.email" />
                        <small class="text-red-500" v-if="submittedUsuario && !usuario.email">Requerido.</small>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label class="block font-medium mb-1">Nombres</label>
                        <InputText v-model="usuario.nombres" fluid :invalid="submittedUsuario && !usuario.nombres" />
                        <small class="text-red-500" v-if="submittedUsuario && !usuario.nombres">Requerido.</small>
                    </div>
                    <div>
                        <label class="block font-medium mb-1">Apellido Paterno</label>
                        <InputText v-model="usuario.apellido_paterno" fluid
                            :invalid="submittedUsuario && !usuario.apellido_paterno" />
                        <small class="text-red-500"
                            v-if="submittedUsuario && !usuario.apellido_paterno">Requerido.</small>
                    </div>
                    <div>
                        <label class="block font-medium mb-1">Apellido Materno</label>
                        <InputText v-model="usuario.apellido_materno" fluid />
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block font-medium mb-1">Rol</label>
                        <Select v-model="usuario.rol" :options="rolesDisponibles" optionLabel="nombre" optionValue="id"
                            placeholder="Seleccione Rol" fluid :invalid="submittedUsuario && !usuario.rol" />
                        <small class="text-red-500" v-if="submittedUsuario && !usuario.rol">Requerido.</small>
                    </div>
                    <div>
                        <label class="block font-medium mb-1">Contraseña</label>
                        <Password v-model="usuario.password" toggleMask fluid :feedback="false"
                            :invalid="submittedUsuario && !usuario.password" />
                        <small class="text-red-500" v-if="submittedUsuario && !usuario.password">Requerido.</small>
                    </div>
                </div>
            </div>
            <template #footer>
                <Button label="Cancelar" text severity="secondary" @click="usuarioDialog = false" />
                <Button label="Crear Usuario" icon="pi pi-check" severity="success" @click="saveUsuario" />
            </template>
        </Dialog>

    </div>
</template>
