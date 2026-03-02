<script setup>
import { computed } from 'vue';
import { useToast } from 'primevue/usetoast';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    modelo: {
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
    const opciones = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(fechaStr).toLocaleDateString('es-MX', opciones);
};

const getSeverityEstado = (activo) => activo ? 'success' : 'danger';
const getLabelEstado = (activo) => activo ? 'Modelo Activo' : 'Modelo Descontinuado';

</script>

<template>
    <Dialog v-model:visible="isVisible" :style="{ width: '90vw', maxWidth: '650px' }" header="Ficha Técnica del Modelo"
        :modal="true" :dismissableMask="true" @hide="closeDialog">

        <div v-if="modelo" class="flex flex-col gap-6">

            <!-- Encabezado / Identidad -->
            <div
                class="flex items-center gap-4 bg-surface-50 dark:bg-surface-900 p-4 rounded-xl border border-surface-200 dark:border-surface-700">
                <div
                    class="w-16 h-16 rounded-lg bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-3xl font-bold shadow-sm">
                    <i class="pi pi-desktop text-3xl"></i>
                </div>
                <div class="flex-1">
                    <h2 class="text-2xl font-bold text-surface-900 dark:text-surface-0 m-0 leading-tight">
                        {{ modelo.nombre_modelo }}
                    </h2>
                    <div class="text-surface-500 font-medium text-sm mt-1 flex items-center gap-2">
                        <i class="pi pi-box text-surface-400"></i> {{ modelo.nombre_producto || 'Sin Nombre Comercial'
                        }}
                    </div>
                </div>
                <Tag :value="getLabelEstado(modelo.esta_activo)" :severity="getSeverityEstado(modelo.esta_activo)"
                    class="text-sm px-3 py-1 shadow-sm" rounded />
            </div>

            <!-- Información Corporativa & Detalles -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                    class="surface-card p-4 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm relative overflow-hidden group">
                    <div
                        class="absolute -right-4 -top-4 w-16 h-16 bg-blue-50 dark:bg-blue-900/20 rounded-full transition-transform group-hover:scale-150 duration-500">
                    </div>
                    <span
                        class="text-surface-500 text-sm font-semibold mb-2 block uppercase tracking-wider relative z-10"><i
                            class="pi pi-briefcase mr-2 text-blue-500"></i>Proveedor Fabricante</span>
                    <div
                        class="text-lg text-surface-900 dark:text-surface-0 font-medium flex items-center gap-2 relative z-10">
                        {{ modelo.proveedor_nombre || 'N/A' }}
                    </div>
                </div>

                <div
                    class="surface-card p-4 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm relative overflow-hidden group">
                    <div
                        class="absolute -right-4 -top-4 w-16 h-16 bg-purple-50 dark:bg-purple-900/20 rounded-full transition-transform group-hover:scale-150 duration-500">
                    </div>
                    <span
                        class="text-surface-500 text-sm font-semibold mb-2 block uppercase tracking-wider relative z-10"><i
                            class="pi pi-building mr-2 text-purple-500"></i>Casino Asignado</span>
                    <div
                        class="text-lg text-surface-900 dark:text-surface-0 font-medium flex items-center gap-2 relative z-10">
                        {{ modelo.casino_nombre || 'No definido' }}
                    </div>
                </div>
            </div>

            <Divider align="center" type="dashed">
                <span class="text-surface-500 text-sm font-semibold uppercase tracking-wider">
                    <i class="pi pi-list mr-2"></i>Especificaciones
                </span>
            </Divider>

            <!-- Descripcion del Modelo -->
            <div
                class="bg-surface-50 dark:bg-surface-800/50 p-5 rounded-xl border border-surface-200 dark:border-surface-700">
                <p class="text-surface-700 dark:text-surface-300 leading-relaxed whitespace-pre-wrap m-0">
                    {{ modelo.descripcion || 'Sin descripción técnica capturada.' }}
                </p>
            </div>

            <!-- Auditoría de Registro -->
            <div
                class="text-xs text-center border-t border-surface-200 dark:border-surface-700 pt-4 mt-2 text-surface-400">
                Registrado por {{ modelo.creado_por || 'Sistema' }} el {{ formatearFecha(modelo.creado_en) }}
                <span v-if="modelo.modificado_en && modelo.modificado_en !== modelo.creado_en">
                    <br />Última modificación por {{ modelo.modificado_por || 'Sistema' }} el {{
                        formatearFecha(modelo.modificado_en) }}
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
