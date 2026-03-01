<script setup>
import { computed } from 'vue';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    usuario: {
        type: Object,
        default: null
    }
});

const emit = defineEmits(['update:visible', 'closed', 'mailOpened']);

const isVisible = computed({
    get: () => props.visible,
    set: (value) => emit('update:visible', value)
});

// Roles permitidos para gamificación (simulando helper visual)
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

const getSeverityEstado = (activo) => activo ? 'success' : 'danger';
const getLabelEstado = (activo) => activo ? 'Activo' : 'Inactivo';

const abrirEmail = (email) => {
    window.location.href = `mailto:${email}`;
    emit('mailOpened', email);
};

const closeDialog = () => {
    isVisible.value = false;
    emit('closed');
};
</script>

<template>
    <Dialog v-model:visible="isVisible" :style="{ width: '95vw', maxWidth: '850px' }" header="Ficha del Usuario"
        :modal="true" :dismissableMask="true">
        <div v-if="usuario" class="flex flex-col gap-5">
            <div
                class="surface-card border-2 border-primary-200 dark:border-primary-900 rounded-xl p-5 bg-gradient-to-br from-primary-50 to-white dark:from-primary-950 dark:to-surface-900">

                <!-- Cabecera Perfil -->
                <div class="flex items-center gap-4 mb-5">
                    <div class="flex items-center justify-center bg-primary-500 rounded-xl shadow-lg"
                        style="width:3.5rem;height:3.5rem">
                        <i class="pi pi-user text-white text-2xl"></i>
                    </div>
                    <div class="flex-1">
                        <h3 class="text-2xl font-bold text-surface-900 dark:text-surface-0 mb-1">{{
                            usuario.nombre_completo || `${usuario.nombres} ${usuario.apellido_paterno}` }}</h3>
                        <p class="text-surface-600 dark:text-surface-400 font-medium flex items-center gap-2 flex-wrap">
                            <Tag :value="usuario.rol_nombre" :severity="getSeverityRol(usuario.rol_nombre)"
                                class="text-xs" />
                            <span class="text-primary-500 hidden sm:inline">•</span>
                            <span>{{ usuario.casino_nombre || 'N/A' }}</span>
                            <span class="text-primary-500 hidden sm:inline">•</span>
                            <Tag :value="getLabelEstado(usuario.esta_activo)"
                                :severity="getSeverityEstado(usuario.esta_activo)" class="text-xs" rounded />
                        </p>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <!-- Username -->
                    <div
                        class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                        <div class="flex items-center gap-2 mb-2">
                            <i class="pi pi-at text-blue-500 text-sm"></i>
                            <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Usuario</span>
                        </div>
                        <span class="font-bold text-surface-900 dark:text-surface-0 text-sm font-mono">{{
                            usuario.username }}</span>
                    </div>

                    <!-- Email -->
                    <div
                        class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                        <div class="flex items-center gap-2 mb-2">
                            <i class="pi pi-envelope text-blue-500 text-sm"></i>
                            <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Email</span>
                        </div>
                        <span
                            class="text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium cursor-pointer"
                            @click="abrirEmail(usuario.email)">
                            {{ usuario.email }}
                        </span>
                    </div>

                    <!-- Datos Personales Puros -->
                    <div
                        class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                        <div class="flex items-center gap-2 mb-2">
                            <i class="pi pi-id-card text-teal-500 text-sm"></i>
                            <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Nombres
                                Completos</span>
                        </div>
                        <span class="font-bold text-surface-900 dark:text-surface-0 text-[13px] leading-tight block">
                            {{ usuario.nombres }} {{ usuario.apellido_paterno }} {{ usuario.apellido_materno || '' }}
                        </span>
                    </div>
                </div>

                <!-- Info Sistema -->
                <div class="mt-5">
                    <div
                        class="bg-gradient-to-br from-slate-50 to-gray-50 dark:from-slate-950 dark:to-gray-950 rounded-lg p-4 border border-surface-200 dark:border-surface-700">
                        <div class="flex items-center gap-2 mb-3">
                            <i class="pi pi-shield text-slate-600 text-sm"></i>
                            <span
                                class="text-slate-700 dark:text-slate-400 text-sm font-bold uppercase tracking-wide">Información
                                del Sistema</span>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-globe text-slate-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Última IP
                                        / Intents de Acceso</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm font-mono block">
                                    {{ usuario.ultima_ip || 'Sin registro' }}
                                    <Badge v-if="usuario.intentos_fallidos > 0" :value="usuario.intentos_fallidos"
                                        severity="danger" class="ml-2"></Badge>
                                </span>
                            </div>
                            <div
                                class="bg-white dark:bg-surface-800 rounded-lg p-3 border border-surface-200 dark:border-surface-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <i class="pi pi-calendar text-slate-500 text-sm"></i>
                                    <span class="text-surface-500 dark:text-surface-400 text-xs font-semibold">Creado en
                                        Sistema</span>
                                </div>
                                <span class="font-bold text-surface-900 dark:text-surface-0 text-sm">
                                    {{ usuario.creado_en ? new Date(usuario.creado_en).toLocaleString('es-MX') : 'N/A'
                                    }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <template #footer>
            <Button label="Cerrar Ficha" icon="pi pi-times" @click="closeDialog" />
        </template>
    </Dialog>
</template>

<!-- ==========================================
📝 TUTORIAL INTEGRADO Y DOCUMENTACIÓN (Regla 6)
==============================================
📌 ¿Qué es este componente?
`UsuarioDetalleDialog.vue` es el Modal estéticamente rico encargado de visualizar (read-only) la ficha de un usuario.
Elimina la carga de tener cientos de líneas de HTML hardcodeadas en las vistas (Regla 3).

📌 ¿Cómo usarlo en la vista padre?
1. Importación:
   `import UsuarioDetalleDialog from '@/components/usuarios/UsuarioDetalleDialog.vue';`

2. Variables y Estado:
   `const detalleVisible = ref(false);`
   `const usrDataCompleto = ref(null);`

3. Uso y Pasaje del Objecto Completo:
   <UsuarioDetalleDialog 
       v-model:visible="detalleVisible"
       :usuario="usrDataCompleto" 
       @closed="limpiarDatos"
   />
============================================== -->
