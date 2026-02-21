<script setup>
import { ref, onMounted, computed } from 'vue';
import api, { getUser, hasRoleAccess } from '@/service/api';
import { crearTicket, TIPOS_TICKET } from '@/service/ticketService';
import { useToast } from 'primevue/usetoast';

const toast = useToast();

// Estado
const panicoDialog = ref(false);
const uidMaquina = ref('');
const loading = ref(false);
const submitted = ref(false);
const usuario = ref(null);

// Computed
const casinoId = computed(() => usuario.value?.casino || null);
const puedeReportarMaquina = computed(() => {
    return hasRoleAccess([
        'SUPERVISOR SALA',
        'ENCARGADO AREA',
        'TECNICO',
        'SUP SISTEMAS',
        'GERENCIA',
        'DB ADMIN',
        'ADMINISTRADOR'
    ]);
});

// Verificar usuario al montar
onMounted(() => {
    cargarUsuario();
});

const cargarUsuario = () => {
    usuario.value = getUser();

    if (!usuario.value) {
        toast.add({
            severity: 'error',
            summary: 'Usuario no encontrado',
            detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se encontró información de usuario. Por favor inicie sesión.',
            life: 5000
        });
        return;
    }

    if (!usuario.value.casino) {
        toast.add({
            severity: 'error',
            summary: 'Casino no asignado',
            detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'Su usuario no tiene un casino asignado. Contacte al administrador para resolver este problema.',
            life: 6000
        });
    }
};

const abrirPanico = () => {
    if (!casinoId.value) {
        toast.add({
            severity: 'error',
            summary: 'Casino no identificado',
            detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No puede crear tickets sin un casino asignado. Cierre sesión y vuelva a iniciar sesión, o contacte al administrador.',
            life: 6000
        });
        return;
    }

    if (!puedeReportarMaquina.value) {
        toast.add({
            severity: 'warn',
            summary: 'Permisos insuficientes',
            detail: 'No tiene permisos para crear tickets de pánico. Esta función está reservada para supervisores y personal autorizado.',
            life: 5000
        });
        return;
    }

    uidMaquina.value = '';
    submitted.value = false;
    panicoDialog.value = true;
};

const cerrarPanico = () => {
    panicoDialog.value = false;
    uidMaquina.value = '';
    submitted.value = false;
};

const crearTicketPanico = async () => {
    submitted.value = true;

    if (!uidMaquina.value || !uidMaquina.value.trim()) {
        toast.add({
            severity: 'warn',
            summary: 'UID requerido',
            detail: 'Debe ingresar el UID de la máquina para crear un ticket de pánico.',
            life: 4000
        });
        return;
    }

    if (!casinoId.value) {
        toast.add({
            severity: 'error',
            summary: 'Casino no identificado',
            detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se encontró información del casino. Por favor cierre sesión y vuelva a iniciar sesión.',
            life: 5000
        });
        return;
    }

    if (!usuario.value || !usuario.value.id) {
        toast.add({
            severity: 'error',
            summary: 'Usuario no autenticado',
            detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.detail || error?.response?.data?.error || 'No se pudo obtener su información de usuario. Por favor inicie sesión nuevamente.',
            life: 5000
        });
        return;
    }

    loading.value = true;

    try {
        // 1. Buscar la máquina por UID en el casino actual
        const responseMaquinas = await api.get('maquinas/', {
            params: {
                uid: uidMaquina.value.trim(),
                casino: casinoId.value
            }
        });

        let maquinas = [];
        if (responseMaquinas.data) {
            if (responseMaquinas.data.results && Array.isArray(responseMaquinas.data.results)) {
                maquinas = responseMaquinas.data.results;
            } else if (Array.isArray(responseMaquinas.data)) {
                maquinas = responseMaquinas.data;
            }
        }

        if (maquinas.length === 0) {
            toast.add({
                severity: 'error',
                summary: 'Máquina no encontrada',
                detail: error?.response?.data?.mensaje || error?.response?.data?.message || error?.response?.data?.error || error?.response?.data?.detail || `El UID "${uidMaquina.value.trim()}" no existe en este casino.`,
                life: 6000
            });
            loading.value = false;
            return;
        }

        const maquina = maquinas[0];

        // 2. Usar el servicio global para crear el ticket
        const resultado = await crearTicket({
            maquinaId: maquina.id,
            maquinaUid: maquina.uid,
            ...TIPOS_TICKET.PANICO,
            reportanteId: usuario.value.id,
            estadoMaquina: 'DAÑADA',
            incrementarContador: true,
            actualizarEstado: true
        });

        // 3. Manejar el resultado
        if (!resultado.exito) {
            toast.add({
                severity: 'error',
                summary: resultado.error,
                detail: resultado.detalle,
                life: 6000
            });
            loading.value = false;
            return;
        }

        // 4. Mostrar éxito
        const mensajeContador = resultado.contadorFallas
            ? ` | Contador de fallas: ${resultado.contadorFallas}`
            : '';

        toast.add({
            severity: 'success',
            summary: '✓ Ticket de Pánico Creado',
            detail: `Ticket #${resultado.ticket.folio || resultado.ticket.id} creado para la máquina "${maquina.uid}". La máquina ha sido marcada como DAÑADA${mensajeContador}.`,
            life: 6000
        });

        if (resultado.advertencia) {
            toast.add({
                severity: 'warn',
                summary: 'Advertencia',
                detail: resultado.advertencia,
                life: 5000
            });
        }

        cerrarPanico();

    } catch (error) {


        const mensajesError = {
            'ECONNABORTED': 'No se pudo conectar con el servidor.',
            'ERR_NETWORK': 'Error de conexión. Verifique su conexión a internet.',
            400: error.response?.data?.detail || 'Los datos enviados no son válidos',
            401: 'Su sesión ha expirado. Por favor inicie sesión nuevamente.',
            403: 'No tiene permisos suficientes para crear tickets de pánico.',
            404: 'No se encontró el recurso solicitado.',
            500: 'Error del servidor. Intente nuevamente más tarde.'
        };

        const status = error.response?.status;
        const detalle = mensajesError[error.code] || mensajesError[status]
            || error.response?.data?.error
            || 'Ocurrió un error inesperado al crear el ticket de pánico.';

        toast.add({
            severity: 'error',
            summary: 'Error al crear ticket',
            detail: detalle,
            life: 6000
        });
    } finally {
        loading.value = false;
    }
};
</script>

<template>
    <div class="col-span-12">
        <div class="card p-3 md:p-4">
            <!-- Barra de herramientas responsiva -->
            <div class="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
                <!-- Acciones principales: columna en móvil, fila en desktop -->
                <div class="flex flex-col md:flex-row gap-2">
                    <Button
                        label="Auditoría Externa"
                        icon="pi pi-file-check"
                        severity="secondary"
                        outlined
                        class="w-full md:w-auto"
                    />
                    <Button
                        label="Incidencia Infraestructura"
                        icon="pi pi-building"
                        severity="secondary"
                        outlined
                        class="w-full md:w-auto"
                    />
                    <Button
                        label="Gestión de Personal"
                        icon="pi pi-users"
                        severity="secondary"
                        outlined
                        class="w-full md:w-auto"
                    />
                </div>

                <!-- Acción crítica: Reportar Máquina -->
                <Button
                    v-if="puedeReportarMaquina"
                    label="Reportar Máquina"
                    icon="pi pi-exclamation-triangle"
                    severity="danger"
                    class="w-full md:w-auto"
                    @click="abrirPanico"
                    :disabled="!casinoId"
                />
            </div>
        </div>
    </div>

    <!-- Dialog de Pánico -->
    <Dialog
        v-model:visible="panicoDialog"
        :style="{ width: '95vw', maxWidth: '550px' }"
        :modal="true"
        :closable="!loading"
        :draggable="false"
    >
        <template #header>
            <div class="flex items-center gap-3">
                <div class="bg-red-100 dark:bg-red-900/30 p-3 rounded-full">
                    <i class="pi pi-exclamation-triangle text-red-600 text-2xl"></i>
                </div>
                <div>
                    <h2 class="text-xl font-bold text-surface-900 dark:text-surface-0">
                        Crear Ticket de Pánico
                    </h2>
                    <p class="text-sm text-surface-600 dark:text-surface-400">
                        Reporte de emergencia
                    </p>
                </div>
            </div>
        </template>

        <div class="flex flex-col gap-5 py-2">
            <!-- Información del Casino -->
            <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-300 dark:border-blue-700 rounded-lg p-3" v-if="usuario?.casino_nombre">
                <div class="flex items-center gap-2">
                    <i class="pi pi-info-circle text-blue-600"></i>
                    <span class="text-sm text-blue-900 dark:text-blue-100">
                        <strong>Casino:</strong> {{ usuario.casino_nombre }}
                    </span>
                </div>
            </div>

            <!-- Información -->
            <div class="bg-orange-50 dark:bg-orange-900/20 border border-orange-300 dark:border-orange-700 rounded-lg p-4">
                <div class="text-sm">
                    <p class="font-semibold mb-2 text-orange-900 dark:text-orange-100">Este es un ticket de emergencia</p>
                    <ul class="list-disc list-inside space-y-1 text-xs text-orange-800 dark:text-orange-200">
                        <li>Ingrese el <strong>UID de la máquina de su casino</strong></li>
                        <li>El ticket se creará con <strong>prioridad CRÍTICA</strong></li>
                        <li>La máquina será marcada como <strong>DAÑADA</strong></li>
                        <li>Se notificará al técnico de inmediato</li>
                        <li>No puede crear otro ticket si ya existe uno abierto</li>
                    </ul>
                </div>
            </div>

            <!-- Campo UID -->
            <div class="flex flex-col gap-2">
                <label for="uid" class="font-semibold text-surface-900 dark:text-surface-0">
                    UID de la Máquina <span class="text-red-500">*</span>
                </label>
                <InputText
                    id="uid"
                    v-model="uidMaquina"
                    placeholder="Ingrese el UID (Ej: MAQ-001)"
                    :invalid="submitted && !uidMaquina?.trim()"
                    :disabled="loading"
                    autofocus
                    size="large"
                    class="w-full"
                    @keyup.enter="crearTicketPanico"
                />
                <small class="text-red-500" v-if="submitted && !uidMaquina?.trim()">
                    Debe ingresar el UID de la máquina para continuar
                </small>
                <small class="text-surface-500 dark:text-surface-400" v-else>
                    Ingrese el identificador único de la máquina que desea reportar
                </small>
            </div>

            <!-- Advertencia Final -->
            <div class="bg-red-50 dark:bg-red-900/20 border border-red-300 dark:border-red-700 rounded-lg p-4">
                <div class="text-center">
                    <p class="text-sm font-semibold text-red-900 dark:text-red-100">
                        ⚠️ Use este botón solo para emergencias reales
                    </p>
                </div>
            </div>
        </div>

        <template #footer>
            <div class="flex justify-end gap-2">
                <Button
                    label="Cancelar"
                    icon="pi pi-times"
                    severity="secondary"
                    outlined
                    @click="cerrarPanico"
                    :disabled="loading"
                />
                <Button
                    label="Crear Ticket de Pánico"
                    icon="pi pi-check"
                    severity="danger"
                    @click="crearTicketPanico"
                    :loading="loading"
                />
            </div>
        </template>
    </Dialog>
</template>
