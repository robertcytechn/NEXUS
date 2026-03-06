<script setup>
import { ref, watch } from 'vue';
import api from '@/service/api';
import { useToast } from 'primevue/usetoast';
import RolForm from './RolForm.vue';
import { parseServerError } from '@/utils/parseServerError';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    rolProp: {
        type: Object,
        default: () => ({})
    }
});

const emit = defineEmits(['update:visible', 'saved']);

const toast = useToast();
const loading = ref(false);
const submitted = ref(false);

const localData = ref({});
const esValidoForm = ref(false);

watch(
    () => props.rolProp,
    (newVal) => {
        localData.value = { ...newVal };
    },
    { immediate: true, deep: true }
);

const hideDialog = () => {
    emit('update:visible', false);
    submitted.value = false;
};

const handleValidar = ({ esValido, datos }) => {
    esValidoForm.value = esValido;
    localData.value = datos;
};

const saveRol = async () => {
    submitted.value = true;

    if (!esValidoForm.value) {
        toast.add({
            severity: 'warn',
            summary: 'Atención',
            detail: 'Por favor complete todos los datos requeridos.',
            life: 3000
        });
        return;
    }

    loading.value = true;
    try {
        const payload = { ...localData.value };
        const id = payload.id;

        if (id) {
            await api.put(`roles/${id}/`, payload);
        } else {
            await api.post('roles/', payload);
        }

        toast.add({
            severity: 'success',
            summary: 'Éxito',
            detail: id ? 'Rol actualizado correctamente' : 'Rol creado correctamente',
            life: 3000
        });

        emit('saved');
        hideDialog();
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error al guardar rol', detail: parseServerError(error, 'Error al guardar rol'), life: 6000 });
    } finally {
        loading.value = false;
    }
};

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
</script>

<template>
    <Dialog :visible="visible" @update:visible="(val) => emit('update:visible', val)" :style="{ width: '450px' }"
        :header="rolProp.id ? 'Editar Rol' : 'Nuevo Rol'" :modal="true" class="p-fluid">
        <template v-if="rolProp.nivel === 200">
            <Message severity="warn" class="mb-4">
                Estás visualizando el Rol Maestro (Dios). Este registro está protegido y no puede ser alterado o
                degradado estructuralmente.
            </Message>
        </template>

        <RolForm v-if="visible" v-model="localData" :modoEdicion="!!rolProp.id" @validar="handleValidar" />

        <div v-if="rolProp.id" class="border-t border-surface-200 dark:border-surface-700 pt-4 mt-4">
            <div class="font-bold mb-3 text-surface-500 dark:text-surface-400">Auditoría Temporal</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Creado
                        por</label>
                    <InputText :value="rolProp.creado_por || 'Sistema'" disabled fluid class="opacity-100 text-sm" />
                </div>
                <div>
                    <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Fecha
                        Creación</label>
                    <InputText :value="formatearFecha(rolProp.creado_en)" disabled fluid class="opacity-100 text-sm" />
                </div>
                <div>
                    <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Modificado
                        por</label>
                    <InputText :value="rolProp.modificado_por || 'N/A'" disabled fluid class="opacity-100 text-sm" />
                </div>
                <div>
                    <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Última
                        Modificación</label>
                    <InputText :value="formatearFecha(rolProp.modificado_en)" disabled fluid
                        class="opacity-100 text-sm" />
                </div>
            </div>
        </div>

        <template #footer>
            <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" :disabled="loading" />
            <Button label="Guardar" icon="pi pi-check" @click="saveRol" :loading="loading"
                :disabled="rolProp.nivel === 200 && !!rolProp.id" />
        </template>
    </Dialog>
</template>
