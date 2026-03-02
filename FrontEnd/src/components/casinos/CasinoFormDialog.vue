<script setup>
import { ref, watch } from 'vue';
import api from '@/service/api';
import { useToast } from 'primevue/usetoast';
import CasinoForm from './CasinoForm.vue';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    casinoProp: {
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
    () => props.casinoProp,
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

const saveCasino = async () => {
    submitted.value = true;

    // Fuerza validación final (el motor la emite reactivamente)
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
            await api.put(`casinos/${id}/`, payload);
        } else {
            await api.post('casinos/', payload);
        }

        toast.add({
            severity: 'success',
            summary: 'Éxito',
            detail: id ? 'Casino actualizado correctamente' : 'Casino creado correctamente',
            life: 3000
        });

        emit('saved');
        hideDialog();
    } catch (error) {
        const detalle = error?.response?.data?.mensaje || error?.response?.data?.detail || 'Error al guardar casino';
        toast.add({ severity: 'error', summary: 'Error', detail: detalle, life: 3000 });
    } finally {
        loading.value = false;
    }
};
</script>

<template>
    <Dialog :visible="visible" @update:visible="(val) => emit('update:visible', val)" :style="{ width: '550px' }"
        :header="casinoProp.id ? 'Editar Casino' : 'Nuevo Casino'" :modal="true" class="p-fluid">
        <CasinoForm v-if="visible" v-model="localData" :modoEdicion="!!casinoProp.id" @validar="handleValidar" />

        <div v-if="casinoProp.id" class="border-t border-surface-200 dark:border-surface-700 pt-4 mt-4">
            <div class="font-bold mb-3 text-surface-500 dark:text-surface-400">Auditoría</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Creado
                        por</label>
                    <InputText :value="casinoProp.creado_por || 'Sistema'" disabled fluid class="opacity-100" />
                </div>
                <div>
                    <label class="block font-bold mb-1 text-sm text-surface-600 dark:text-surface-300">Última
                        Modificación</label>
                    <InputText :value="casinoProp.modificado_por || 'N/A'" disabled fluid class="opacity-100" />
                </div>
            </div>
        </div>

        <template #footer>
            <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" :disabled="loading" />
            <Button label="Guardar" icon="pi pi-check" @click="saveCasino" :loading="loading" />
        </template>
    </Dialog>
</template>
