<script setup>
import { computed } from 'vue';
import { useToast } from 'primevue/usetoast';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    proveedor: {
        type: Object,
        default: null
    }
});

const emit = defineEmits(['update:visible', 'closed']);
const toast = useToast();

const isVisible = computed({
    get: () => props.visible,
    set: (value) => emit('update:visible', value)
});

const closeDialog = () => {
    isVisible.value = false;
    emit('closed');
};

const formatearFecha = (fechaStr) => {
    if (!fechaStr) return 'N/A';
    const opciones = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(fechaStr).toLocaleDateString('es-MX', opciones);
};

const getSeverityEstado = (activo) => activo ? 'success' : 'danger';
const getLabelEstado = (activo) => activo ? 'Activo' : 'Inactivo';

// Composables para interacciones
const copiarAlPortapapeles = async (texto, mensaje) => {
    if (!texto) return;
    try {
        await navigator.clipboard.writeText(texto);
        toast.add({ severity: 'success', summary: 'Copiado', detail: mensaje, life: 2000 });
    } catch (err) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo copiar al portapapeles', life: 2000 });
    }
};

const llamarTelefono = (telefono) => window.open(`tel:${telefono}`);
const enviarEmail = (email) => window.open(`mailto:${email}`);

</script>

<template>
    <Dialog v-model:visible="isVisible" :style="{ width: '90vw', maxWidth: '600px' }"
        header="Ficha Técnica del Proveedor" :modal="true" :dismissableMask="true" @hide="closeDialog">

        <div v-if="proveedor" class="flex flex-col gap-6">

            <!-- Encabezado / Identidad -->
            <div
                class="flex items-center gap-4 bg-surface-50 dark:bg-surface-900 p-4 rounded-xl border border-surface-200 dark:border-surface-700">
                <div
                    class="w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900/40 text-primary-600 dark:text-primary-400 flex items-center justify-center text-3xl font-bold uppercase shadow-sm">
                    {{ proveedor.nombre?.charAt(0) || 'P' }}
                </div>
                <div class="flex-1">
                    <h2 class="text-2xl font-bold text-surface-900 dark:text-surface-0 m-0 leading-tight">
                        {{ proveedor.nombre }}
                    </h2>
                    <div class="text-surface-500 font-medium text-sm mt-1 flex items-center gap-2">
                        <i class="pi pi-building text-surface-400"></i> {{ proveedor.casino_nombre || 'Casino no asignado' }}
                    </div>
                </div>
                <Tag :value="getLabelEstado(proveedor.esta_activo)" :severity="getSeverityEstado(proveedor.esta_activo)"
                    class="text-sm px-3 py-1 shadow-sm" rounded />
            </div>

            <!-- Información Corporativa -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                    class="surface-card p-4 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm relative overflow-hidden group">
                    <div
                        class="absolute -right-4 -top-4 w-16 h-16 bg-blue-50 dark:bg-blue-900/20 rounded-full transition-transform group-hover:scale-150 duration-500">
                    </div>
                    <span
                        class="text-surface-500 text-sm font-semibold mb-2 block uppercase tracking-wider relative z-10"><i
                            class="pi pi-id-card mr-2 text-blue-500"></i>RFC</span>
                    <div
                        class="text-lg text-surface-900 dark:text-surface-0 font-mono font-medium flex items-center gap-2 relative z-10">
                        {{ proveedor.rfc || 'N/A' }}
                        <Button v-if="proveedor.rfc" icon="pi pi-copy" text rounded severity="secondary" size="small"
                            @click="copiarAlPortapapeles(proveedor.rfc, 'RFC Copiado')" v-tooltip.top="'Copiar RFC'" />
                    </div>
                </div>

                <div
                    class="surface-card p-4 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm relative overflow-hidden group">
                    <div
                        class="absolute -right-4 -top-4 w-16 h-16 bg-purple-50 dark:bg-purple-900/20 rounded-full transition-transform group-hover:scale-150 duration-500">
                    </div>
                    <span
                        class="text-surface-500 text-sm font-semibold mb-2 block uppercase tracking-wider relative z-10"><i
                            class="pi pi-briefcase mr-2 text-purple-500"></i>Email Corporativo</span>
                    <div
                        class="text-lg text-surface-900 dark:text-surface-0 font-medium break-all flex items-center gap-2 relative z-10">
                        <span class="cursor-pointer hover:underline hover:text-primary-500 transition-colors"
                            @click="enviarEmail(proveedor.email_corporativo)">{{ proveedor.email_corporativo || 'N/A'
                            }}</span>
                    </div>
                </div>
            </div>

            <Divider align="center" type="dashed">
                <span class="text-surface-400 text-sm uppercase font-semibold"><i
                        class="pi pi-headphones mr-2"></i>Contacto de Soporte</span>
            </Divider>

            <!-- Soporte Técnico -->
            <div
                class="bg-surface-50 dark:bg-surface-800/50 p-5 rounded-xl border border-surface-200 dark:border-surface-700">
                <div class="flex flex-col md:flex-row gap-6">
                    <div class="flex-1">
                        <div class="flex items-center gap-3 mb-2">
                            <i class="pi pi-user text-xl text-primary-500"></i>
                            <div>
                                <span
                                    class="block text-sm text-surface-500 font-semibold uppercase tracking-wider">Contacto
                                    Técnico</span>
                                <span class="text-lg text-surface-900 dark:text-surface-0 font-medium">{{
                                    proveedor.nombre_contacto_tecnico || 'No Asignado' }}</span>
                            </div>
                        </div>
                    </div>
                    <div
                        class="flex flex-col gap-3 md:border-l border-surface-200 dark:border-surface-700 md:pl-6 justify-center">
                        <Button v-if="proveedor.telefono_soporte" :label="proveedor.telefono_soporte" icon="pi pi-phone"
                            severity="success" outlined class="w-full text-left"
                            @click="llamarTelefono(proveedor.telefono_soporte)" />
                        <Button v-if="proveedor.email_soporte" :label="proveedor.email_soporte" icon="pi pi-envelope"
                            severity="info" text
                            class="w-full text-left bg-surface-100 dark:bg-surface-700 hover:bg-surface-200 dark:hover:bg-surface-600"
                            @click="enviarEmail(proveedor.email_soporte)" />
                    </div>
                </div>
            </div>

            <!-- Accesos y Auditoría -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                <div class="flex flex-col gap-1">
                    <span class="text-xs text-surface-500 font-semibold uppercase">Credenciales Portal Web</span>
                    <div
                        class="bg-surface-100 dark:bg-surface-800 p-2 rounded flex items-center justify-between border border-surface-200 dark:border-surface-700">
                        <span class="font-mono text-sm text-surface-900 dark:text-surface-0">{{ proveedor.username ||
                            'N/A' }}</span>
                        <Button v-if="proveedor.username" icon="pi pi-copy" text rounded severity="secondary"
                            size="small" @click="copiarAlPortapapeles(proveedor.username, 'Usuario Copiado')"
                            v-tooltip.top="'Copiar Usuario'" />
                    </div>
                </div>

                <div class="flex flex-col gap-1 items-end justify-center text-right">
                    <span class="text-xs text-surface-500 font-semibold uppercase">Estadísticas</span>
                    <div class="flex items-center gap-2">
                        <Badge :value="proveedor.total_modelos || 0" size="large" severity="info" />
                        <span class="text-sm font-medium text-surface-700 dark:text-surface-300">Modelos de
                            Máquinas</span>
                    </div>
                </div>
            </div>

            <div
                class="text-xs text-center border-t border-surface-200 dark:border-surface-700 pt-4 mt-2 text-surface-400">
                Registrado por {{ proveedor.creado_por }} el {{ formatearFecha(proveedor.creado_en) }}
                <span v-if="proveedor.modificado_en !== proveedor.creado_en">
                    <br />Última modificación por {{ proveedor.modificado_por }} el {{
                        formatearFecha(proveedor.modificado_en) }}
                </span>
            </div>

        </div>

        <template #footer>
            <div class="flex justify-end pt-2">
                <Button label="Cerrar Ficha" icon="pi pi-times" rounded severity="secondary" @click="closeDialog"
                    autofocus />
            </div>
        </template>
    </Dialog>
</template>

<style scoped>
.surface-card {
    transition: transform 0.2s, box-shadow 0.2s;
}

.surface-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}
</style>
