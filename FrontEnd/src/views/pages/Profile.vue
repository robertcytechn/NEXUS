<script setup>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { getUser, setUser } from '@/service/api';
import UsuarioService from '@/service/usuarioService';

const toast = useToast();
const user = ref({});
const loading = ref(false);
const loadingStats = ref(false);
const avatarUrl = ref(null);
const estadisticas = ref(null);

const passwordForm = ref({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
});

onMounted(() => {
    loadUserData();
});

const loadUserData = () => {
    const userData = getUser();
    if (userData) {
        user.value = { ...userData };

        // El serializer devuelve la URL absoluta. Fallback para sesiones antiguas con ruta relativa.
        if (user.value.avatar) {
            const av = user.value.avatar;
            avatarUrl.value = av.startsWith('http') ? av : `${window.location.protocol}//${window.location.hostname}:8000/media/${av}`;
        } else {
            avatarUrl.value = null;
        }

        if (user.value.id) {
            loadEstadisticas();
        }
    }
};

const loadEstadisticas = async () => {
    loadingStats.value = true;
    try {
        const result = await UsuarioService.obtenerEstadisticasPerfil(user.value.id);
        if (result.exito) {
            estadisticas.value = result.data;
        }
    } catch (e) {
        console.error('Error cargando estadísticas:', e);
    } finally {
        loadingStats.value = false;
    }
};

const formatFecha = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleString('es-MX', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
};

const onUploadAvatar = async (event) => {
    const file = event.files[0];
    if (!file) return;

    loading.value = true;
    try {
        const result = await UsuarioService.subirAvatar(user.value.id, file);

        if (result.exito) {
            toast.add({ severity: 'success', summary: 'Éxito', detail: 'Avatar actualizado correctamente', life: 3000 });
            const updatedUser = { ...user.value, avatar: result.data.avatar };
            setUser(updatedUser);
            loadUserData();
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.error, life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Ocurrió un error al subir la imagen', life: 3000 });
    } finally {
        loading.value = false;
    }
};

const onChangePassword = async () => {
    if (!passwordForm.value.newPassword) {
        toast.add({ severity: 'warn', summary: 'Atención', detail: 'Ingrese una nueva contraseña', life: 3000 });
        return;
    }
    if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
        toast.add({ severity: 'warn', summary: 'Atención', detail: 'Las contraseñas no coinciden', life: 3000 });
        return;
    }

    loading.value = true;
    try {
        const result = await UsuarioService.cambiarPassword(user.value.id, passwordForm.value.newPassword);

        if (result.exito) {
            toast.add({ severity: 'success', summary: 'Éxito', detail: 'Contraseña actualizada. Por favor inicie sesión nuevamente.', life: 3000 });
            passwordForm.value = { currentPassword: '', newPassword: '', confirmPassword: '' };
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.error, life: 3000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Error al cambiar la contraseña', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// KPIs para grid de estadísticas
const kpis = computed(() => {
    if (!estadisticas.value) return [];
    const t = estadisticas.value.tickets;
    const e = estadisticas.value.evoluciones;
    return [
        {
            label: 'Tickets Reportados',
            value: t?.reportados ?? 0,
            icon: 'pi pi-ticket',
            colorVar: '--p-blue-500',
            bgVar: '--p-blue-50',
        },
        {
            label: 'Tickets Asignados',
            value: t?.asignados ?? 0,
            icon: 'pi pi-user-edit',
            colorVar: '--p-orange-500',
            bgVar: '--p-orange-50',
        },
        {
            label: 'Tickets Abiertos',
            value: t?.abiertos ?? 0,
            icon: 'pi pi-exclamation-circle',
            colorVar: '--p-red-500',
            bgVar: '--p-red-50',
        },
        {
            label: 'Evoluciones NEXUS',
            value: e?.total ?? 0,
            icon: 'pi pi-bolt',
            colorVar: '--p-purple-500',
            bgVar: '--p-purple-50',
        },
    ];
});

const estadoTicketSeverity = (estado) => {
    const map = {
        'Abierto': 'danger',
        'En Proceso': 'warn',
        'En Espera': 'secondary',
        'Cerrado': 'success',
        'Reabierto': 'info',
    };
    return map[estado] || 'secondary';
};
</script>

<template>
    <div class="flex flex-col gap-4">

        <!-- Encabezado -->
        <div class="card mb-0">
            <div class="text-900 font-medium text-3xl mb-1">Mi Perfil</div>
            <div class="text-500">Gestione su información personal y seguridad.</div>
        </div>

        <!-- Contenido Principal (Perfil + Tabs) -->
        <div class="flex flex-col xl:flex-row gap-4">

            <!-- Columna Izquierda: Tarjeta de Perfil -->
            <div class="xl:w-80 shrink-0">
                <div class="card flex flex-col items-center h-full">

                    <!-- Avatar + botón cámara -->
                    <div class="relative mb-5">
                        <Avatar :image="avatarUrl" :label="!avatarUrl ? user.nombres?.[0] : ''" size="xlarge"
                            shape="circle" class="w-32 h-32 text-5xl shadow-md"
                            :style="!avatarUrl ? 'background-color: var(--p-primary-color); color: #fff' : ''" />
                        <div class="absolute bottom-0 right-0">
                            <FileUpload mode="basic" name="avatar" accept="image/*" :maxFileSize="3000000"
                                @select="onUploadAvatar" :auto="true" chooseLabel=" " icon="pi pi-camera"
                                class="p-button-rounded p-button-icon-only shadow-md" />
                        </div>
                    </div>

                    <!-- Nombre y username -->
                    <div class="text-900 font-bold text-2xl mb-1 text-center">{{ user.nombre_completo }}</div>
                    <div class="text-500 font-medium text-base mb-5 text-center">@{{ user.username }}</div>

                    <!-- Datos rápidos -->
                    <div class="w-full border-t border-surface pt-4">
                        <ul class="list-none p-0 m-0 flex flex-col gap-3">
                            <li class="flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-envelope text-500"></i>
                                    <span class="text-700 font-medium">Email</span>
                                </div>
                                <span class="text-900 text-sm text-right max-w-40 truncate" :title="user.email">{{
                                    user.email }}</span>
                            </li>
                            <li class="flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-id-card text-500"></i>
                                    <span class="text-700 font-medium">Rol</span>
                                </div>
                                <span class="text-900 text-sm">{{ user.rol_nombre }}</span>
                            </li>
                            <li class="flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-building text-500"></i>
                                    <span class="text-700 font-medium">Casino</span>
                                </div>
                                <span class="text-900 text-sm">{{ user.casino_nombre }}</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Columna Derecha: Tabs (Detalles + Seguridad) -->
            <div class="flex-1 min-w-0">
                <div class="card h-full">
                    <Tabs value="0">
                        <TabList>
                            <Tab value="0">
                                <i class="pi pi-user mr-2"></i>
                                <span class="font-medium">Detalles</span>
                            </Tab>
                            <Tab value="1">
                                <i class="pi pi-shield mr-2"></i>
                                <span class="font-medium">Seguridad</span>
                            </Tab>
                        </TabList>

                        <TabPanels>
                            <!-- Panel: Detalles -->
                            <TabPanel value="0">
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                                    <div class="flex flex-col gap-1">
                                        <label class="font-medium text-900 text-sm">Nombre(s)</label>
                                        <InputText v-model="user.nombres" disabled class="opacity-100 font-semibold" />
                                    </div>
                                    <div class="flex flex-col gap-1">
                                        <label class="font-medium text-900 text-sm">Apellido Paterno</label>
                                        <InputText v-model="user.apellido_paterno" disabled
                                            class="opacity-100 font-semibold" />
                                    </div>
                                    <div class="flex flex-col gap-1">
                                        <label class="font-medium text-900 text-sm">Apellido Materno</label>
                                        <InputText v-model="user.apellido_materno" disabled
                                            class="opacity-100 font-semibold" />
                                    </div>
                                    <div class="flex flex-col gap-1">
                                        <label class="font-medium text-900 text-sm">Fecha de Registro</label>
                                        <InputText
                                            :value="user.creado_en ? new Date(user.creado_en).toLocaleDateString() : '-'"
                                            disabled class="opacity-100 font-semibold" />
                                    </div>
                                    <div class="flex flex-col gap-1 md:col-span-2">
                                        <label class="font-medium text-900 text-sm">Última Dirección IP</label>
                                        <InputText v-model="user.ultima_ip" disabled
                                            class="opacity-100 font-semibold" />
                                    </div>
                                </div>
                            </TabPanel>

                            <!-- Panel: Seguridad -->
                            <TabPanel value="1">
                                <div class="flex flex-col gap-4 mt-3 max-w-md">

                                    <!-- Aviso de recomendaciones -->
                                    <div
                                        class="p-4 rounded-lg border border-blue-200 bg-blue-50 dark:bg-blue-950/30 dark:border-blue-800">
                                        <div class="flex items-center gap-2 mb-2">
                                            <i class="pi pi-info-circle text-blue-500 text-xl"></i>
                                            <span
                                                class="font-semibold text-blue-700 dark:text-blue-300">Recomendaciones</span>
                                        </div>
                                        <ul
                                            class="m-0 pl-4 text-blue-600 dark:text-blue-200 text-sm flex flex-col gap-1">
                                            <li>Use al menos 8 caracteres.</li>
                                            <li>Incluya letras mayúsculas y minúsculas.</li>
                                            <li>Combine números y símbolos especiales.</li>
                                        </ul>
                                    </div>

                                    <!-- Nueva Contraseña -->
                                    <div class="flex flex-col gap-1">
                                        <label class="font-medium text-900 text-sm">Nueva Contraseña</label>
                                        <Password v-model="passwordForm.newPassword" toggleMask :feedback="true"
                                            promptLabel="Ingrese contraseña" weakLabel="Débil" mediumLabel="Media"
                                            strongLabel="Fuerte" class="w-full" fluid />
                                    </div>

                                    <!-- Confirmar Contraseña -->
                                    <div class="flex flex-col gap-1">
                                        <label class="font-medium text-900 text-sm">Confirmar Contraseña</label>
                                        <Password v-model="passwordForm.confirmPassword" toggleMask :feedback="false"
                                            placeholder="Repita la contraseña" class="w-full" fluid />
                                    </div>

                                    <Button label="Actualizar Contraseña" icon="pi pi-check" severity="primary"
                                        @click="onChangePassword" :loading="loading" class="self-start" />
                                </div>
                            </TabPanel>

                        </TabPanels>
                    </Tabs>
                </div>
            </div>

        </div>

        <!-- =====================================================
             CARD DE ESTADÍSTICAS DE ACTIVIDAD
        ====================================================== -->
        <div class="card">
            <!-- Encabezado de la card -->
            <div class="flex items-center justify-between mb-5">
                <div class="flex items-center gap-3">
                    <div class="flex items-center justify-center w-10 h-10 rounded-xl"
                        style="background-color: var(--p-primary-100)">
                        <i class="pi pi-chart-bar text-xl" style="color: var(--p-primary-color)"></i>
                    </div>
                    <div>
                        <div class="text-900 font-semibold text-xl">Estadísticas de Actividad</div>
                        <div class="text-500 text-sm">Resumen de tu participación en el sistema</div>
                    </div>
                </div>
                <Button icon="pi pi-refresh" rounded text severity="secondary" @click="loadEstadisticas"
                    :loading="loadingStats" v-tooltip.left="'Actualizar estadísticas'" />
            </div>

            <!-- Skeleton mientras carga -->
            <template v-if="loadingStats">
                <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
                    <Skeleton v-for="i in 4" :key="i" height="6rem" border-radius="12px" />
                </div>
                <Skeleton height="12rem" border-radius="12px" />
            </template>

            <template v-else-if="estadisticas">
                <!-- KPIs Principales -->
                <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
                    <div v-for="kpi in kpis" :key="kpi.label"
                        class="rounded-xl p-4 border border-surface flex flex-col gap-2"
                        :style="{ backgroundColor: `var(${kpi.bgVar})` }">
                        <div class="flex items-center justify-between">
                            <span class="text-600 text-xs font-medium uppercase tracking-wide">{{ kpi.label }}</span>
                            <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-white/70">
                                <i :class="kpi.icon" :style="{ color: `var(${kpi.colorVar})` }"></i>
                            </div>
                        </div>
                        <div class="text-900 font-bold text-3xl" :style="{ color: `var(${kpi.colorVar})` }">
                            {{ kpi.value }}
                        </div>
                    </div>
                </div>

                <!-- Separador -->
                <Divider />

                <!-- Grid inferior: Info de Cuenta + Últimos Tickets -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">

                    <!-- Info de Cuenta -->
                    <div>
                        <div class="font-semibold text-900 mb-3 flex items-center gap-2">
                            <i class="pi pi-user-plus text-primary"></i>
                            Información de Cuenta
                        </div>
                        <ul class="list-none p-0 m-0 flex flex-col gap-3">
                            <li class="flex items-center justify-between py-2 border-b border-surface">
                                <div class="flex items-center gap-2 text-600">
                                    <i class="pi pi-calendar-plus text-sm"></i>
                                    <span class="text-sm">Fecha de Registro</span>
                                </div>
                                <span class="text-900 text-sm font-medium">
                                    {{ formatFecha(estadisticas.cuenta?.fecha_registro) }}
                                </span>
                            </li>
                            <li class="flex items-center justify-between py-2 border-b border-surface">
                                <div class="flex items-center gap-2 text-600">
                                    <i class="pi pi-sign-in text-sm"></i>
                                    <span class="text-sm">Último Acceso</span>
                                </div>
                                <span class="text-900 text-sm font-medium">
                                    {{ formatFecha(estadisticas.cuenta?.ultimo_acceso) }}
                                </span>
                            </li>
                            <li class="flex items-center justify-between py-2 border-b border-surface">
                                <div class="flex items-center gap-2 text-600">
                                    <i class="pi pi-clock text-sm"></i>
                                    <span class="text-sm">Días en el Sistema</span>
                                </div>
                                <Tag :value="`${estadisticas.cuenta?.dias_en_sistema ?? 0} días`" severity="info" />
                            </li>
                            <li class="flex items-center justify-between py-2 border-b border-surface">
                                <div class="flex items-center gap-2 text-600">
                                    <i class="pi pi-globe text-sm"></i>
                                    <span class="text-sm">Última IP</span>
                                </div>
                                <span class="text-900 text-sm font-mono">
                                    {{ estadisticas.cuenta?.ultima_ip ?? 'N/A' }}
                                </span>
                            </li>
                            <li class="flex items-center justify-between py-2">
                                <div class="flex items-center gap-2 text-600">
                                    <i class="pi pi-shield text-sm"></i>
                                    <span class="text-sm">Intentos Fallidos</span>
                                </div>
                                <Tag :value="estadisticas.cuenta?.intentos_fallidos > 0 ? estadisticas.cuenta.intentos_fallidos.toString() : 'Ninguno'"
                                    :severity="estadisticas.cuenta?.intentos_fallidos > 0 ? 'danger' : 'success'" />
                            </li>
                        </ul>
                    </div>

                    <!-- Últimos Tickets -->
                    <div>
                        <div class="font-semibold text-900 mb-3 flex items-center gap-2">
                            <i class="pi pi-ticket text-primary"></i>
                            Últimos Tickets Reportados
                        </div>

                        <div v-if="estadisticas.tickets?.recientes?.length === 0"
                            class="flex flex-col items-center justify-center py-8 text-center text-500">
                            <i class="pi pi-inbox text-4xl mb-3 opacity-40"></i>
                            <span class="text-sm">Sin tickets reportados aún</span>
                        </div>

                        <ul v-else class="list-none p-0 m-0 flex flex-col gap-2">
                            <li v-for="ticket in estadisticas.tickets?.recientes" :key="ticket.folio"
                                class="flex items-center gap-3 p-3 rounded-lg border border-surface hover:surface-hover transition-colors">
                                <div class="flex items-center justify-center w-9 h-9 rounded-lg bg-orange-50 shrink-0">
                                    <i class="pi pi-ticket text-orange-500"></i>
                                </div>
                                <div class="flex-1 min-w-0">
                                    <div class="font-semibold text-900 text-sm">{{ ticket.folio }}</div>
                                    <div class="text-500 text-xs truncate">{{ ticket.categoria }} ·
                                        {{ ticket.prioridad }}</div>
                                </div>
                                <Tag :value="ticket.estado" :severity="estadoTicketSeverity(ticket.estado)"
                                    class="shrink-0 text-xs" />
                            </li>
                        </ul>
                    </div>

                </div>
            </template>

            <!-- Estado de error / sin datos -->
            <template v-else>
                <div class="flex flex-col items-center justify-center py-12 text-center text-500">
                    <i class="pi pi-chart-bar text-5xl mb-3 opacity-30"></i>
                    <span class="text-base font-medium">Sin estadísticas disponibles</span>
                    <span class="text-sm mt-1">Intente recargar la información</span>
                </div>
            </template>

        </div>

    </div>
</template>
