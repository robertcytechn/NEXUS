<script setup>
import { ref, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import api from '@/service/api';
import ModeloForm from './ModeloForm.vue';
import { parseServerError } from '@/utils/parseServerError';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    modeloId: {
        type: [Number, String],
        default: null
    }
});

const emit = defineEmits(['update:visible', 'saved']);

const toast = useToast();
const modeloLocal = ref({});
const submitted = ref(false);
const loading = ref(false);

const cargarModelo = async (id) => {
    loading.value = true;
    try {
        const response = await api.get(`modelos/${id}/`);
        modeloLocal.value = response.data;
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error al cargar modelo',
            detail: parseServerError(error, 'No se pudo cargar la información del modelo'),
            life: 5000
        });
        hideDialog();
    } finally {
        loading.value = false;
    }
};

watch(
    () => props.visible,
    async (newVal) => {
        if (newVal) {
            submitted.value = false;
            loading.value = false;
            if (props.modeloId) {
                await cargarModelo(props.modeloId);
            } else {
                modeloLocal.value = { esta_activo: true };
            }
        }
    }
);

const hideDialog = () => {
    emit('update:visible', false);
    submitted.value = false;
    modeloLocal.value = {};
};

const saveModelo = async () => {
    submitted.value = true;
    loading.value = true;

    // Validación básica: Checamos que estén los obligatorios (del esquema original en backend)
    if (!modeloLocal.value.proveedor || !modeloLocal.value.nombre_modelo || !modeloLocal.value.nombre_producto) {
        toast.add({
            severity: 'warn',
            summary: 'Campos requeridos',
            detail: 'Complete todos los campos obligatorios (*)',
            life: 3000
        });
        loading.value = false;
        return;
    }

    try {
        const payload = { ...modeloLocal.value };

        // Determinar si es un ID simple o un objeto el que se obtuvo del v-model de Proveedor
        if (typeof payload.proveedor === 'object' && payload.proveedor !== null) {
            payload.proveedor = payload.proveedor.id;
        }

        if (payload.id) {
            await api.put(`modelos/${payload.id}/`, payload);
        } else {
            await api.post('modelos/', payload);
        }

        toast.add({
            severity: 'success',
            summary: 'Éxito',
            detail: payload.id ? 'Modelo actualizado correctamente' : 'Modelo creado correctamente',
            life: 3000
        });

        emit('saved');
        hideDialog();
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error al guardar modelo',
            detail: parseServerError(error, 'Ocurrió un error al guardar el modelo.'),
            life: 6000
        });
    } finally {
        loading.value = false;
    }
};
</script>

<template>
    <Dialog :visible="visible" @update:visible="(val) => emit('update:visible', val)" :style="{ width: '550px' }"
        :header="modeloLocal.id ? 'Editar Modelo de Máquina' : 'Nuevo Modelo de Máquina'" :modal="true">
        <div v-if="loading && props.modeloId" class="flex justify-center p-6">
            <i class="pi pi-spin pi-spinner text-4xl text-primary"></i>
        </div>
        <div v-else class="flex flex-col gap-6 w-full p-2">
            <!-- MOTOR DINÁMICO UI -->
            <ModeloForm v-model="modeloLocal" :submitted="submitted" @validar="saveModelo" />
        </div>

        <template #footer>
            <Button label="Cancelar" icon="pi pi-times" text severity="secondary" @click="hideDialog"
                :disabled="loading" />
            <Button label="Guardar Modelo" icon="pi pi-check" @click="saveModelo" :loading="loading" />
        </template>
    </Dialog>
</template>
