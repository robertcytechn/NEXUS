<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import api, { getUser } from '@/service/api';
import { useToast } from 'primevue/usetoast';
import { parseServerError } from '@/utils/parseServerError';

const toast  = useToast();
const usuario = computed(() => getUser());
const loading  = ref(false);
const enviando = ref(false);

// ── Datos de apoyo ─────────────────────────────────────────
const casinos = ref([]);
const roles   = ref([]);
const usuarios = ref([]);
const loadingUsuarios = ref(false);

// ── Tipos de alcance ───────────────────────────────────────
const tiposAlcance = [
    {
        valor: 'global',
        label: 'Global',
        desc: 'Todos los usuarios del sistema, todos los casinos.',
        icon: 'pi pi-globe',
        severity: 'warn'
    },
    {
        valor: 'director',
        label: 'Dirección',
        desc: 'Global · Permanece 7 días · Visible en todos los casinos.',
        icon: 'pi pi-megaphone',
        severity: 'danger'
    },
    {
        valor: 'casino',
        label: 'Por Casino',
        desc: 'Todos los roles de un casino específico.',
        icon: 'pi pi-building',
        severity: 'info'
    },
    {
        valor: 'rol_casino',
        label: 'Rol + Casino',
        desc: 'Solo un rol en un casino específico.',
        icon: 'pi pi-users',
        severity: 'success'
    },
    {
        valor: 'personal',
        label: 'Personal',
        desc: 'Un usuario específico, sin importar su casino.',
        icon: 'pi pi-user',
        severity: 'secondary'
    },
];

// ── Opciones catálogo ──────────────────────────────────────
const nivelesOpts = [
    { label: '🚨 Urgente (Acción Inmediata)', value: 'urgente' },
    { label: '⚠️  Alerta (Atención Requerida)', value: 'alerta' },
    { label: 'ℹ️  Informativa (Solo lectura)',   value: 'informativa' },
];

const tiposOpts = [
    { label: 'Aviso del Sistema',        value: 'sistema' },
    { label: 'Gestión de Tickets',       value: 'ticket' },
    { label: 'Incidencia Infraestructura', value: 'infraestructura' },
    { label: 'Nueva Guía en Wiki',       value: 'wiki' },
    { label: 'Mensaje de Dirección',     value: 'DIRECTOR' },
];

// ── Formulario ─────────────────────────────────────────────
const alcance  = ref(null); // 'global' | 'director' | 'casino' | 'rol_casino' | 'personal'
const form     = ref({
    titulo:          '',
    contenido:       '',
    nivel:           'informativa',
    tipo:            'sistema',
    casino_destino:  null,
    rol_destino:     null,
    usuario_destino: null,
    es_global:       false,
    es_del_director: false,
});
const submitted = ref(false);

// ── Computed helpers ───────────────────────────────────────
const mostrarCasino   = computed(() => ['casino', 'rol_casino'].includes(alcance.value));
const mostrarRol      = computed(() => alcance.value === 'rol_casino');
const mostrarUsuario  = computed(() => alcance.value === 'personal');

const resumenAlcance = computed(() => {
    switch (alcance.value) {
        case 'global':    return 'Esta notificación será visible para TODOS los usuarios de TODOS los casinos.';
        case 'director':  return 'Mensaje de Dirección: visible para TODOS y permanece 7 días en el sistema.';
        case 'casino':    return `Todos los usuarios del casino seleccionado la podrán ver.`;
        case 'rol_casino':return `Solo los usuarios con el rol seleccionado dentro del casino elegido la verán.`;
        case 'personal':  return `Solo el usuario seleccionado recibirá esta notificación.`;
        default:          return '';
    }
});

// ── Estilo del alcance seleccionado ───────────────────────
const severidadAlcance = computed(() => {
    const t = tiposAlcance.find(t => t.valor === alcance.value);
    return t ? t.severity : 'secondary';
});

// ── Carga de datos ─────────────────────────────────────────
const cargarCatalogos = async () => {
    loading.value = true;
    try {
        const [resCasinos, resRoles] = await Promise.all([
            api.get('casinos/lista/'),
            api.get('roles/lista/'),
        ]);
        casinos.value = resCasinos.data.filter(c => c.esta_activo);
        roles.value   = resRoles.data.filter(r => r.esta_activo);
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: parseServerError(e, 'No se pudieron cargar los catálogos.'), life: 5000 });
    } finally {
        loading.value = false;
    }
};

// Carga usuarios cuando se selecciona un casino (para modo personal o como referencia)
const cargarUsuariosDeCasino = async (casinoId) => {
    if (!casinoId) { usuarios.value = []; return; }
    loadingUsuarios.value = true;
    try {
        const res = await api.get(`usuarios/lista-por-casino/${casinoId}/`);
        usuarios.value = (res.data.usuarios || []).filter(u => u.esta_activo);
    } catch {
        usuarios.value = [];
    } finally {
        loadingUsuarios.value = false;
    }
};

// Cuando cambia el alcance, resetea los campos de segmentación
watch(alcance, () => {
    form.value.casino_destino  = null;
    form.value.rol_destino     = null;
    form.value.usuario_destino = null;
    form.value.es_global       = false;
    form.value.es_del_director = false;
    usuarios.value             = [];

    if (alcance.value === 'global') {
        form.value.es_global = true;
    }
    if (alcance.value === 'director') {
        form.value.es_global       = true;
        form.value.es_del_director = true;
        form.value.tipo            = 'DIRECTOR';
    } else if (form.value.tipo === 'DIRECTOR') {
        form.value.tipo = 'sistema';
    }
});

// Carga usuarios SOLO en modo personal (el casino se usa únicamente como filtro de UI)
watch(() => form.value.casino_destino, (nuevoId) => {
    if (mostrarUsuario.value) {
        cargarUsuariosDeCasino(nuevoId);
    }
});

// ── Validación ─────────────────────────────────────────────
const esValido = computed(() => {
    if (!alcance.value)               return false;
    if (!form.value.titulo?.trim())   return false;
    if (!form.value.contenido?.trim())return false;
    if (mostrarCasino.value   && !form.value.casino_destino)  return false;
    if (mostrarRol.value      && !form.value.rol_destino)     return false;
    if (mostrarUsuario.value  && !form.value.usuario_destino) return false;
    return true;
});

// ── Enviar ─────────────────────────────────────────────────
const enviarNotificacion = async () => {
    submitted.value = true;
    if (!esValido.value) return;

    enviando.value = true;
    try {
        // Para notificaciones personales el casino se usa solo como filtro UI
        // y NO debe enviarse al backend; si lo incluimos, la condición
        // Q(casino_destino, rol_destino__isnull=True) haría visible la
        // notificación a TODOS los usuarios del casino.
        const esPersonal = alcance.value === 'personal';

        const payload = {
            titulo:    form.value.titulo.trim(),
            contenido: form.value.contenido.trim(),
            nivel:     form.value.nivel,
            tipo:      form.value.tipo,
            es_global:       form.value.es_global,
            es_del_director: form.value.es_del_director,
            casino_destino:  esPersonal ? null : (form.value.casino_destino  || null),
            rol_destino:     form.value.rol_destino     || null,
            usuario_destino: form.value.usuario_destino || null,
        };

        await api.post('notificaciones/', payload);

        toast.add({
            severity: 'success',
            summary:  '✅ Notificación Enviada',
            detail:   'La notificación ha sido creada y distribuida correctamente.',
            life:     4000,
        });

        resetForm();
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error al Enviar', detail: parseServerError(e, 'No se pudo enviar la notificación.'), life: 5000 });
    } finally {
        enviando.value  = false;
        submitted.value = false;
    }
};

const resetForm = () => {
    alcance.value  = null;
    submitted.value = false;
    form.value = {
        titulo:          '',
        contenido:       '',
        nivel:           'informativa',
        tipo:            'sistema',
        casino_destino:  null,
        rol_destino:     null,
        usuario_destino: null,
        es_global:       false,
        es_del_director: false,
    };
    usuarios.value = [];
};

onMounted(cargarCatalogos);
</script>

<template>
    <div class="grid grid-cols-1 gap-6 p-4">

        <!-- ═══ Encabezado ═══════════════════════════════════════════ -->
        <div class="flex flex-col gap-1">
            <h1 class="text-2xl font-bold text-color">📣 Notificaciones Especiales</h1>
            <p class="text-muted-color text-sm">
                Crea notificaciones manuales de alcance global, por casino, por rol o personales.
                Solo disponible para Administradores y Dirección.
            </p>
        </div>

        <!-- ═══ Paso 1: Alcance ══════════════════════════════════════ -->
        <div class="card p-4">
            <h2 class="text-lg font-semibold mb-3 text-color">
                <i class="pi pi-bullseye mr-2 text-primary"></i>Paso 1 — Selecciona el Alcance
            </h2>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                <div
                    v-for="tipo in tiposAlcance"
                    :key="tipo.valor"
                    class="border rounded-lg p-4 cursor-pointer transition-all"
                    :class="{
                        'border-primary bg-primary/10': alcance === tipo.valor,
                        'border-surface-200 dark:border-surface-700 hover:border-primary/50': alcance !== tipo.valor,
                    }"
                    @click="alcance = tipo.valor"
                >
                    <div class="flex flex-col items-center gap-2 text-center">
                        <i :class="[tipo.icon, 'text-2xl', alcance === tipo.valor ? 'text-primary' : 'text-muted-color']"></i>
                        <span class="font-semibold text-sm" :class="alcance === tipo.valor ? 'text-primary' : 'text-color'">
                            {{ tipo.label }}
                        </span>
                        <span class="text-xs text-muted-color leading-tight">{{ tipo.desc }}</span>
                    </div>
                </div>
            </div>

            <!-- Resumen del alcance seleccionado -->
            <div v-if="alcance" class="mt-4">
                <Message :severity="severidadAlcance" :closable="false">
                    <i class="pi pi-info-circle mr-2"></i>{{ resumenAlcance }}
                </Message>
            </div>
        </div>

        <!-- ═══ Paso 2: Formulario ════════════════════════════════════ -->
        <Transition name="fade-slide">
        <div v-if="alcance" class="card p-4">
            <h2 class="text-lg font-semibold mb-4 text-color">
                <i class="pi pi-file-edit mr-2 text-primary"></i>Paso 2 — Redacta la Notificación
            </h2>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">

                <!-- Título -->
                <div class="flex flex-col gap-1 lg:col-span-2">
                    <label class="text-sm font-medium text-color">Título <span class="text-red-500">*</span></label>
                    <InputText
                        v-model="form.titulo"
                        placeholder="Ej: Mantenimiento programado esta noche"
                        :invalid="submitted && !form.titulo?.trim()"
                        maxlength="150"
                    />
                    <small v-if="submitted && !form.titulo?.trim()" class="text-red-500">El título es requerido.</small>
                    <small class="text-muted-color text-right">{{ form.titulo?.length || 0 }} / 150</small>
                </div>

                <!-- Contenido -->
                <div class="flex flex-col gap-1 lg:col-span-2">
                    <label class="text-sm font-medium text-color">Contenido <span class="text-red-500">*</span></label>
                    <Textarea
                        v-model="form.contenido"
                        rows="4"
                        placeholder="Describe el motivo, contexto y cualquier acción requerida..."
                        :invalid="submitted && !form.contenido?.trim()"
                        autoResize
                    />
                    <small v-if="submitted && !form.contenido?.trim()" class="text-red-500">El contenido es requerido.</small>
                </div>

                <!-- Nivel -->
                <div class="flex flex-col gap-1">
                    <label class="text-sm font-medium text-color">Nivel de Prioridad</label>
                    <Select
                        v-model="form.nivel"
                        :options="nivelesOpts"
                        optionLabel="label"
                        optionValue="value"
                        placeholder="Selecciona un nivel"
                    />
                </div>

                <!-- Tipo -->
                <div class="flex flex-col gap-1">
                    <label class="text-sm font-medium text-color">Tipo de Notificación</label>
                    <Select
                        v-model="form.tipo"
                        :options="tiposOpts"
                        optionLabel="label"
                        optionValue="value"
                        :disabled="alcance === 'director'"
                        placeholder="Selecciona un tipo"
                    />
                    <small v-if="alcance === 'director'" class="text-muted-color">
                        Fijado en "Mensaje de Dirección" automáticamente.
                    </small>
                </div>

                <!-- Casino destino (solo si aplica) -->
                <div v-if="mostrarCasino" class="flex flex-col gap-1">
                    <label class="text-sm font-medium text-color">Casino Destino <span class="text-red-500">*</span></label>
                    <Select
                        v-model="form.casino_destino"
                        :options="casinos"
                        optionLabel="nombre"
                        optionValue="id"
                        :loading="loading"
                        :invalid="submitted && mostrarCasino && !form.casino_destino"
                        placeholder="Selecciona un casino"
                        showClear
                    />
                    <small v-if="submitted && mostrarCasino && !form.casino_destino" class="text-red-500">
                        Debes seleccionar un casino.
                    </small>
                </div>

                <!-- Rol destino (solo si aplica) -->
                <div v-if="mostrarRol" class="flex flex-col gap-1">
                    <label class="text-sm font-medium text-color">Rol Destino <span class="text-red-500">*</span></label>
                    <Select
                        v-model="form.rol_destino"
                        :options="roles"
                        optionLabel="nombre"
                        optionValue="id"
                        :invalid="submitted && mostrarRol && !form.rol_destino"
                        placeholder="Selecciona un rol"
                        showClear
                    />
                    <small v-if="submitted && mostrarRol && !form.rol_destino" class="text-red-500">
                        Debes seleccionar un rol.
                    </small>
                </div>

                <!-- Usuario personal (solo si aplica) -->
                <div v-if="mostrarUsuario" class="flex flex-col gap-1 lg:col-span-2">
                    <label class="text-sm font-medium text-color">Casino del Usuario</label>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div class="flex flex-col gap-1">
                            <Select
                                v-model="form.casino_destino"
                                :options="casinos"
                                optionLabel="nombre"
                                optionValue="id"
                                :loading="loading"
                                placeholder="1. Selecciona el casino del usuario"
                                showClear
                            />
                            <small class="text-muted-color">Filtra los usuarios por casino.</small>
                        </div>
                        <div class="flex flex-col gap-1">
                            <Select
                                v-model="form.usuario_destino"
                                :options="usuarios"
                                :optionLabel="u => `${u.nombre_completo} (${u.username}) — ${u.rol_nombre}`"
                                optionValue="id"
                                :loading="loadingUsuarios"
                                :disabled="!form.casino_destino"
                                :invalid="submitted && mostrarUsuario && !form.usuario_destino"
                                placeholder="2. Selecciona el usuario"
                                filter
                                showClear
                            />
                            <small v-if="submitted && mostrarUsuario && !form.usuario_destino" class="text-red-500">
                                Debes seleccionar un usuario destino.
                            </small>
                        </div>
                    </div>
                </div>

            </div><!-- /grid formulario -->

            <!-- ── Vista previa ───────────────────────────────────── -->
            <div v-if="form.titulo || form.contenido" class="mt-6 border border-surface-200 dark:border-surface-700 rounded-lg overflow-hidden">
                <div class="bg-surface-100 dark:bg-surface-800 px-4 py-2 text-xs font-semibold text-muted-color uppercase tracking-wider">
                    Vista Previa
                </div>
                <div class="p-4 flex flex-col gap-2">
                    <div class="flex items-center gap-2">
                        <Tag
                            :value="form.nivel"
                            :severity="form.nivel === 'urgente' ? 'danger' : form.nivel === 'alerta' ? 'warn' : 'info'"
                        />
                        <Tag :value="form.tipo" severity="secondary" />
                        <Tag v-if="form.es_del_director" value="DIRECTOR · 7 días" severity="contrast" />
                        <Tag v-if="form.es_global" value="GLOBAL" severity="warn" />
                    </div>
                    <p class="font-semibold text-color text-base">{{ form.titulo || '(Sin título)' }}</p>
                    <p class="text-muted-color text-sm whitespace-pre-wrap">{{ form.contenido || '(Sin contenido)' }}</p>
                </div>
            </div>

            <!-- ── Acciones ────────────────────────────────────────── -->
            <div class="flex flex-col sm:flex-row items-center justify-end gap-3 mt-6 pt-4 border-t border-surface-200 dark:border-surface-700">
                <Button
                    label="Limpiar Formulario"
                    icon="pi pi-refresh"
                    severity="secondary"
                    outlined
                    @click="resetForm"
                    :disabled="enviando"
                />
                <Button
                    label="Enviar Notificación"
                    icon="pi pi-send"
                    :loading="enviando"
                    :disabled="!esValido || enviando"
                    @click="enviarNotificacion"
                    class="min-w-48"
                />
            </div>
        </div>
        </Transition>

        <!-- ═══ Estado vacío cuando no se ha elegido alcance ════════ -->
        <div v-if="!alcance" class="card p-8 flex flex-col items-center gap-3 text-center text-muted-color">
            <i class="pi pi-megaphone text-5xl opacity-30"></i>
            <p class="text-lg font-medium">Selecciona el tipo de alcance para comenzar</p>
            <p class="text-sm max-w-md">
                Puedes enviar notificaciones globales, a todo un casino, a un rol específico
                dentro de un casino, o directamente a un usuario en particular.
            </p>
        </div>

    </div>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
    transition: all 0.25s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
    opacity: 0;
    transform: translateY(12px);
}
</style>
