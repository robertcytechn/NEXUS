<script setup>
import { ref, watch, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import api, { getUser } from '@/service/api';
import MaquinaForm from './MaquinaForm.vue';
import { parseServerError } from '@/utils/parseServerError';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    maquinaId: {
        type: [Number, String],
        default: null
    }
});

const emit = defineEmits(['update:visible', 'saved']);

const toast = useToast();
const maquinaLocal = ref({});
const submitted = ref(false);
const loading = ref(false);

const usuario = computed(() => getUser());

const cargarMaquina = async (id) => {
    loading.value = true;
    try {
        const response = await api.get(`maquinas/${id}/`);

        // Transformar flat ids de vuelta a Arrays para MultiSelect de Denominaciones si es que API envía id plano
        let dataTransformada = { ...response.data };
        if (dataTransformada.denominaciones && !Array.isArray(dataTransformada.denominaciones)) {
            dataTransformada.denominaciones = [dataTransformada.denominaciones];
        } else if (!dataTransformada.denominaciones) {
            dataTransformada.denominaciones = [];
        }

        // Si el modelo y casino son objetos con info completa de DB, extraer solo el ID para el Select
        if (typeof dataTransformada.modelo === 'object' && dataTransformada.modelo !== null) {
            dataTransformada.modelo = dataTransformada.modelo.id;
        }
        if (typeof dataTransformada.casino === 'object' && dataTransformada.casino !== null) {
            dataTransformada.casino = dataTransformada.casino.id;
        }

        maquinaLocal.value = dataTransformada;
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error al cargar máquina',
            detail: parseServerError(error, 'No se pudo cargar la información de la máquina'),
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

            if (props.maquinaId) {
                await cargarMaquina(props.maquinaId);
            } else {
                // Prellenados iniciales para nueva Máquina
                maquinaLocal.value = {
                    esta_activo: true,
                    ubicacion_piso: 'PISO_1',
                    ubicacion_sala: 'SALA_A',
                    coordenada_x: 0,
                    coordenada_y: 0,
                    estado_actual: 'OPERATIVA',
                    denominaciones: [], // MultiSelect debe iniciar como array vacío 
                    casino: usuario.value?.casino || null // Autoasignar casino del usuario
                };
            }
        }
    }
);

const hideDialog = () => {
    emit('update:visible', false);
    submitted.value = false;
    maquinaLocal.value = {};
};

const saveMaquina = async () => {
    submitted.value = true;
    loading.value = true;

    // Validación Básica
    if (
        !maquinaLocal.value.modelo ||
        !maquinaLocal.value.casino ||
        !maquinaLocal.value.uid_sala ||
        !maquinaLocal.value.juego ||
        !maquinaLocal.value.numero_serie ||
        !maquinaLocal.value.denominaciones ||
        maquinaLocal.value.denominaciones.length === 0
    ) {
        toast.add({
            severity: 'warn',
            summary: 'Campos requeridos',
            detail: 'Complete todos los campos obligatorios marcados con (*)',
            life: 3000
        });
        loading.value = false;
        return;
    }

    try {
        const payload = { ...maquinaLocal.value };

        if (payload.id) {
            await api.put(`maquinas/${payload.id}/`, payload);
        } else {
            await api.post('maquinas/', payload);
        }

        toast.add({
            severity: 'success',
            summary: 'Éxito',
            detail: payload.id ? 'Máquina actualizada correctamente' : 'Máquina registrada correctamente',
            life: 3000
        });

        emit('saved');
        hideDialog();
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error al guardar máquina',
            detail: parseServerError(error, 'Ocurrió un error al guardar la máquina.'),
            life: 6000
        });
    } finally {
        loading.value = false;
    }
};
</script>

<template>
    <Dialog :visible="visible" @update:visible="(val) => emit('update:visible', val)" :style="{ width: '800px' }"
        :header="maquinaLocal.id ? 'Editar Máquina' : 'Registrar Nueva Máquina'" :modal="true" :maximizable="true">
        <div v-if="loading && props.maquinaId" class="flex justify-center p-6">
            <i class="pi pi-spin pi-spinner text-4xl text-primary"></i>
        </div>

        <div v-else class="flex flex-col gap-6 w-full p-2">
            <!-- MOTOR DINÁMICO DE MÁQUINAS UI - v-if para no montar innecesariamente -->
            <MaquinaForm v-if="visible" v-model="maquinaLocal" :submitted="submitted" @validar="saveMaquina" />
        </div>

        <template #footer>
            <Button label="Cancelar" icon="pi pi-times" text severity="secondary" @click="hideDialog"
                :disabled="loading" />
            <Button label="Guardar Máquina" icon="pi pi-check" @click="saveMaquina" :loading="loading" />
        </template>
    </Dialog>
</template>
