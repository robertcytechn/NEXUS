<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { getUser, hasRoleAccess, fetchRoles } from '@/service/api';
import { getDashboardStats, guardarUsuario, getReporteDiario } from '@/service/usuarioService';
import { crearTicket, crearTicketConBitacora } from '@/service/ticketService';
import { getMaquinasPorCasino } from '@/service/maquinaService';
import EvolucionService from '@/service/EvolucionService';
import { useToast } from 'primevue/usetoast';
import InsigniaRangoAnimada from '@/components/InsigniaRangoAnimada.vue';

// Components
// Auto-imported in this project structure (matching Usuarios.vue)
import DashboardCharts from '@/components/DashboardCharts.vue';

const router = useRouter();
const user = getUser();
const toast = useToast();
const evolucionService = new EvolucionService();

// Permissions
const canViewGlobalStats = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA']));
const canViewTechStats = computed(() => hasRoleAccess(['ADMINISTRADOR', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA']));
// Solo roles analíticos ven las gráficas completas (Tarea 3)
const canViewCharts = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'GERENCIA']));
// Solo roles de gestión pueden ver el reporte diario (Tarea 4)
const canViewReporteDiario = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS']));
// Insignia de rango: solo técnicos y sup sistemas participan en gamificación
const canViewInsignia = computed(() => hasRoleAccess(['SUP SISTEMAS', 'TECNICO']));

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

// Roles disponibles filtrados según el rol del usuario logueado (Tarea 6)
const rolesDisponibles = computed(() => {
    if (!roles.value) return [];

    const rolActual = user?.rol_nombre;

    if (['ADMINISTRADOR', 'DB ADMIN'].includes(rolActual)) {
        // Admin y DB Admin ven todos los roles disponibles
        return roles.value;
    }
    if (rolActual === 'GERENCIA') {
        // Gerente puede crear: sup_sistemas, tecnico, supervisor_sala, encargado_area
        return roles.value.filter(r => ['SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA'].includes(r.nombre));
    }
    if (rolActual === 'SUP SISTEMAS') {
        // Sup Sistemas puede crear: tecnico, supervisor_sala, encargado_area
        return roles.value.filter(r => ['TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA'].includes(r.nombre));
    }
    // Por defecto sin permisos para crear
    return [];
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
            toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudieron cargar los roles', life: 3000 });
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
            toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudieron cargar las máquinas', life: 3000 });
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
            toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudieron cargar las máquinas', life: 3000 });
        }
    }
};

const savePanicTicket = async () => {
    submittedPanic.value = true;

    if (panicTicket.value.uid_sala) {
        const searchUid = panicTicket.value.uid_sala.trim().toUpperCase();
        const maquinaSeleccionada = maquinas.value.find(m => m.uid_sala.toUpperCase() === searchUid);

        if (!maquinaSeleccionada) {
            toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.error || error?.response?.data?.detail || `No se encontró una máquina con el UID: ${searchUid}`, life: 3000 });
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

// 5. Cierre / Ticket Express (Técnico)
const expressDialog = ref(false);
const expressData = ref({ uid_sala: '', descripcion: '', estado_final: 'operativa' });
const submittedExpress = ref(false);
const estadosFinales = ref([
    { label: 'Solucionado - Máquina Operativa', value: 'operativa' },
    { label: 'Pendiente - Sigue Dañada', value: 'dañada' },
    { label: 'Parcial - Dañada pero Operando', value: 'dañada_operativa' }
]);

const openExpressDialog = async () => {
    expressData.value = { uid_sala: '', descripcion: '', estado_final: 'operativa' };
    submittedExpress.value = false;
    expressDialog.value = true;

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

const saveExpressTicket = async () => {
    submittedExpress.value = true;

    if (expressData.value.uid_sala && expressData.value.descripcion) {
        const searchUid = expressData.value.uid_sala.trim().toUpperCase();
        const maquinaSeleccionada = maquinas.value.find(m => m.uid_sala.toUpperCase() === searchUid);

        if (!maquinaSeleccionada) {
            toast.add({ severity: 'error', summary: 'Error', detail: `No se encontró máquina con el UID: ${searchUid}`, life: 3000 });
            return;
        }

        const isClosed = expressData.value.estado_final === 'operativa';

        const result = await crearTicketConBitacora({
            maquinaId: maquinaSeleccionada.id,
            maquinaUid: maquinaSeleccionada.uid_sala,
            categoria: 'otros', // Por defecto para algo exprés
            descripcionProblema: `Ticket Express por Técnico: ${expressData.value.descripcion}`,
            usuarioTecnicoId: user.id,
            tipoIntervencion: 'Mantenimiento Correctivo', // Estándar para este flujo
            descripcionTrabajo: expressData.value.descripcion,
            resultadoIntervencion: expressData.value.estado_final === 'operativa' ? 'exitosa' : 'pendiente',
            estadoMaquinaResultante: expressData.value.estado_final,
            finalizaTicket: isClosed,
            explicacionCierre: isClosed ? 'Cerrado mediante flujo express en Dashboard.' : ''
        });

        if (result.exito) {
            toast.add({ severity: 'success', summary: 'Cierre Express Exitoso', detail: `Folio: ${result.ticket.folio} procesado.`, life: 4000 });
            expressDialog.value = false;
            loadDashboardData();
        } else {
            toast.add({ severity: 'error', summary: 'Error en Proceso Compuesto', detail: result.detalle || result.error, life: 5000 });
        }
    }
};

const quickActions = computed(() => {
    const actions = [
        {
            // Tarea 2: Solo gerente, sup_sistemas, supervisor_sala, jefe_area
            label: 'Ticket Rápido',
            icon: 'pi pi-bolt',
            action: openPanicDialog,
            color: 'bg-red-500',
            allowed: hasRoleAccess(['GERENCIA', 'SUP SISTEMAS', 'SUPERVISOR SALA', 'JEFE AREA'])
        },
        {
            // Tarea 2: Solo sup_sistemas y tecnico
            label: 'Reporte Técnico',
            icon: 'pi pi-wrench',
            action: openExpressDialog,
            color: 'bg-indigo-500',
            allowed: hasRoleAccess(['SUP SISTEMAS', 'TECNICO'])
        },
        {
            // Tarea 2: Solo sup_sistemas y tecnico
            label: 'Nuevo Ticket',
            icon: 'pi pi-ticket',
            action: openTicketDialog,
            color: 'bg-blue-500',
            allowed: hasRoleAccess(['SUP SISTEMAS', 'TECNICO'])
        },
        {
            // Tarea 2: Solo sup_sistemas, bd_admin, gerente, administrador
            label: 'Crear Usuario',
            icon: 'pi pi-user-plus',
            action: openUsuarioDialog,
            color: 'bg-green-500',
            allowed: hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS'])
        },
        {
            // Tarea 4: Solo roles de gestión
            label: 'Reporte del Día',
            icon: 'pi pi-chart-bar',
            action: openReporteDiario,
            color: 'bg-teal-500',
            allowed: hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS'])
        },
        {
            // Tarea 2: Visible para TODOS
            label: 'Reportar Error en el sistema',
            icon: 'pi pi-exclamation-circle',
            action: openEvolucionDialog,
            color: 'bg-orange-500',
            allowed: true
        },
        {
            // Tarea 2: Visible para TODOS
            label: 'Inventario',
            icon: 'pi pi-box',
            action: () => router.push('/centro-servicios/inventario'),
            color: 'bg-purple-500',
            allowed: true
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
        toast.add({ severity: 'error', summary: 'Error', detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudo cargar el estado del dashboard', life: 3000 });
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

// ── Reporte Diario (Tarea 4) ─────────────────────────────────────────────────
const reporteDiarioDialog = ref(false);
const reporteDiarioData = ref(null);
const loadingReporte = ref(false);

const openReporteDiario = async () => {
    reporteDiarioDialog.value = true;
    if (!reporteDiarioData.value) {
        await refreshReporteDiario();
    }
};

const refreshReporteDiario = async () => {
    if (!user?.casino) return;
    loadingReporte.value = true;
    const res = await getReporteDiario(user.casino);
    if (res.exito) {
        reporteDiarioData.value = res.data;
    } else {
        toast.add({ severity: 'error', summary: 'Error', detail: res.detalle, life: 3000 });
    }
    loadingReporte.value = false;
};

// Genera el texto plano del reporte para copiar / compartir
const getReporteTexto = () => {
    if (!reporteDiarioData.value) return '';
    const d = reporteDiarioData.value;
    let txt = `=== REPORTE DIARIO NEXUS === ${d.fecha}\n\n`;
    txt += `⚠️ MÁQUINAS CON FALLAS ACTIVAS (${d.maquinas_danadas.length})\n`;
    txt += '─'.repeat(40) + '\n';
    if (d.maquinas_danadas.length === 0) {
        txt += 'Sin máquinas con fallas activas.\n';
    } else {
        d.maquinas_danadas.forEach(m => {
            txt += `• ${m.uid} - ${m.modelo}\n`;
            txt += `  Estado: ${m.estado_display}\n`;
            txt += `  Ubicación: ${m.piso} / ${m.sala}\n`;
        });
    }
    txt += `\n⚠️ INCIDENCIAS DE INFRAESTRUCTURA (${d.incidencias_infra.length})\n`;
    txt += '─'.repeat(40) + '\n';
    if (d.incidencias_infra.length === 0) {
        txt += 'Sin incidencias de infraestructura.\n';
    } else {
        d.incidencias_infra.forEach(inc => {
            txt += `[${inc.dia}] ${inc.titulo} (${inc.categoria}) - ${inc.severidad}\n`;
            txt += `  Hora: ${inc.hora_inicio}${inc.hora_fin ? ' - ' + inc.hora_fin : ''}\n`;
            txt += `  ${inc.descripcion}\n`;
        });
    }
    return txt;
};

// Copiar al portapapeles — compatible con WebView Android/iOS
const copiarReporte = async () => {
    const texto = getReporteTexto();
    try {
        await navigator.clipboard.writeText(texto);
        toast.add({ severity: 'success', summary: 'Copiado', detail: 'Reporte copiado al portapapeles', life: 2000 });
    } catch {
        // Fallback para WebViews sin acceso a clipboard API
        const el = document.createElement('textarea');
        el.value = texto;
        el.style.cssText = 'position:fixed;top:-9999px;left:-9999px;opacity:0;';
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        toast.add({ severity: 'success', summary: 'Copiado', detail: 'Reporte copiado al portapapeles', life: 2000 });
    }
};

// Exportar a PDF (solo escritorio — oculto en móvil vía CSS)
const exportarReportePDF = () => {
    const texto = getReporteTexto();
    const ventana = window.open('', '_blank');
    if (!ventana) return;
    ventana.document.write(`<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Reporte Diario NEXUS</title>
    <style>body{font-family:monospace;padding:24px;white-space:pre-wrap;}</style></head>
    <body>${texto.replace(/</g, '&lt;')}</body></html>`);
    ventana.document.close();
    setTimeout(() => { ventana.print(); ventana.close(); }, 250);
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
                        <div class="text-surface-500 mb-3">Bienvenido al Centro de Comando NEXUS.</div>
                        <InsigniaRangoAnimada
                            v-if="user?.rango_gamificacion && canViewInsignia"
                            :nivel="user.rango_gamificacion.nivel"
                            :nombreRango="user.rango_gamificacion.titulo"
                        />
                    </div>
                    <div class="flex flex-col items-end gap-2">
                        <i class="pi pi-compass text-4xl text-primary opacity-50"></i>
                    </div>
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

        <!-- Dashboard Charts – Solo roles analíticos (Tarea 3) -->
        <div v-if="user?.casino && canViewCharts" class="col-span-12">
            <DashboardCharts :casinoId="user.casino" />
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
            header="Reportar Incidencia Rápida (error en el sistema)">
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

        <!-- Dialog: Cierre Express / Reporte Técnico -->
        <Dialog v-model:visible="expressDialog" :style="{ width: '450px' }" :modal="true"
            header="Reporte Técnico Express">
            <div class="flex flex-col gap-4 p-2">
                <p class="text-surface-600 dark:text-surface-300 mb-2">
                    Abre un ticket y anexa tu resolución en un solo paso.
                </p>
                <div>
                    <label class="block font-medium mb-1">UID de la Máquina</label>
                    <InputText v-model="expressData.uid_sala" fluid placeholder="Ej: MQ-001" autofocus
                        :invalid="submittedExpress && !expressData.uid_sala" />
                    <small class="text-red-500 block" v-if="submittedExpress && !expressData.uid_sala">El UID es
                        obligatorio.</small>
                </div>
                <div>
                    <label class="block font-medium mb-1">Problema y Solución</label>
                    <Textarea v-model="expressData.descripcion" rows="4" fluid
                        placeholder="Describe qué estaba fallando y cómo lo solucionaste..."
                        :invalid="submittedExpress && !expressData.descripcion" />
                    <small class="text-red-500 block" v-if="submittedExpress && !expressData.descripcion">Debes
                        justificar la
                        bitácora.</small>
                </div>
                <div>
                    <label class="block font-medium mb-1">Estado de la Máquina</label>
                    <Select v-model="expressData.estado_final" :options="estadosFinales" optionLabel="label"
                        optionValue="value" fluid />
                </div>
            </div>
            <template #footer>
                <Button label="Cancelar" text severity="secondary" @click="expressDialog = false" />
                <Button label="Cerrar Incidencia" icon="pi pi-check-circle" severity="success"
                    @click="saveExpressTicket" />
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

        <!-- Dialog: Reporte Diario (Tarea 4) -->
        <Dialog v-model:visible="reporteDiarioDialog" :style="{ width: '700px' }" :modal="true" header="📊 Reporte Diario de Operaciones">
            <!-- Toolbar del reporte -->
            <div class="flex items-center gap-2 mb-4">
                <Button icon="pi pi-refresh" label="Actualizar" text size="small" @click="refreshReporteDiario" :loading="loadingReporte" />
                <Button icon="pi pi-copy" label="Copiar" size="small" severity="secondary" outlined @click="copiarReporte" />
                <!-- Exportar PDF — oculto en móvil mediante media query -->
                <Button icon="pi pi-file-pdf" label="Exportar PDF" size="small" severity="danger" outlined @click="exportarReportePDF" class="reporte-pdf-btn" />
            </div>

            <div v-if="loadingReporte" class="flex justify-center p-8">
                <i class="pi pi-spin pi-spinner text-3xl text-primary"></i>
            </div>

            <div v-else-if="reporteDiarioData" class="flex flex-col gap-5">
                <p class="text-surface-500 text-sm">Fecha: <strong>{{ reporteDiarioData.fecha }}</strong></p>

                <!-- Máquinas con Fallas Activas -->
                <div>
                    <div class="font-semibold text-base mb-2 flex items-center gap-2">
                        <i class="pi pi-exclamation-triangle text-red-500"></i>
                        Máquinas con Fallas Activas
                        <span class="text-xs text-surface-400">({{ reporteDiarioData.maquinas_danadas.length }})</span>
                    </div>
                    <div v-if="reporteDiarioData.maquinas_danadas.length === 0" class="text-surface-400 text-sm italic">
                        Sin máquinas con fallas activas en este casino. ✅
                    </div>
                    <div v-for="m in reporteDiarioData.maquinas_danadas" :key="m.uid"
                        class="mb-2 p-3 rounded-lg border border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800">
                        <div class="flex items-center justify-between mb-1">
                            <span class="font-bold text-primary-600 dark:text-primary-400">{{ m.uid }}</span>
                            <Tag :value="m.estado_display" size="small"
                                :severity="m.estado === 'DAÑADA' ? 'danger' : 'warn'" />
                        </div>
                        <div class="text-xs text-surface-500 mb-1">{{ m.modelo }}</div>
                        <div class="text-xs text-surface-400 mt-1 flex items-center gap-1">
                            <i class="pi pi-map-marker text-xs"></i>
                            {{ m.piso }} — {{ m.sala }}
                        </div>
                    </div>
                </div>

                <!-- Incidencias de Infraestructura -->
                <div>
                    <div class="font-semibold text-base mb-2 flex items-center gap-2">
                        <i class="pi pi-exclamation-triangle text-orange-500"></i>
                        Incidencias de Infraestructura (Hoy y Ayer)
                        <span class="text-xs text-surface-400">({{ reporteDiarioData.incidencias_infra.length }})</span>
                    </div>
                    <div v-if="reporteDiarioData.incidencias_infra.length === 0" class="text-surface-400 text-sm italic">
                        Sin incidencias de infraestructura en las últimas 48h.
                    </div>
                    <div v-for="(inc, idx) in reporteDiarioData.incidencias_infra" :key="idx"
                        class="mb-2 p-3 rounded-lg border border-orange-200 dark:border-orange-900 bg-orange-50 dark:bg-orange-950/30">
                        <div class="flex items-center justify-between mb-1">
                            <span class="font-semibold text-sm">{{ inc.titulo }}</span>
                            <div class="flex items-center gap-1">
                                <Tag :value="inc.dia" size="small"
                                    :severity="inc.dia === 'Hoy' ? 'danger' : 'warn'" />
                            </div>
                        </div>
                        <div class="text-xs text-surface-500 mb-1">
                            {{ inc.categoria }} — {{ inc.severidad }}
                            <span class="ml-2">{{ inc.hora_inicio }}{{ inc.hora_fin ? ' – ' + inc.hora_fin : '' }}</span>
                        </div>
                        <div class="text-sm text-surface-700 dark:text-surface-300">{{ inc.descripcion }}</div>
                    </div>
                </div>
            </div>

            <template #footer>
                <Button label="Cerrar" text severity="secondary" @click="reporteDiarioDialog = false" />
            </template>
        </Dialog>

    </div>
</template>

<style>
/* Ocultar botón PDF en dispositivos móviles (Tarea 4) */
@media (max-width: 768px) {
    .reporte-pdf-btn {
        display: none !important;
    }
}
</style>
