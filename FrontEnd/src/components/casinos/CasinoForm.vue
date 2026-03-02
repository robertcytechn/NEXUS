<script setup>
import { ref, watch, onMounted } from 'vue';
import api from '@/service/api';
import { useToast } from 'primevue/usetoast';

const props = defineProps({
    modelValue: {
        type: Object,
        default: () => ({})
    },
    esquemaEndpoint: {
        type: String,
        default: 'casinos/esquema/'
    },
    modoEdicion: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['update:modelValue', 'validar']);

const toast = useToast();
const esquema = ref([]);
const formData = ref({ ...props.modelValue });
const loading = ref(true);
const errores = ref({});

const cargarEsquema = async () => {
    loading.value = true;
    try {
        const response = await api.options(props.esquemaEndpoint);
        esquema.value = response.data.campos || [];
        inicializarFormulario();
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'No se pudo cargar el esquema del formulario',
            life: 3000
        });
    } finally {
        loading.value = false;
    }
};

const inicializarFormulario = () => {
    esquema.value.forEach((campo) => {
        if (formData.value[campo.nombre] === undefined) {
            formData.value[campo.nombre] = campo.default !== undefined ? campo.default : (campo.tipo === 'booleano' ? false : null);
        }

        // Parsear hora en edición
        if (campo.tipo === 'hora' && formData.value[campo.nombre] && typeof formData.value[campo.nombre] === 'string') {
            const [hours, minutes] = formData.value[campo.nombre].split(':');
            const date = new Date();
            date.setHours(parseInt(hours), parseInt(minutes), 0);
            formData.value[campo.nombre] = date;
        }
    });
};

const validarPayload = () => {
    let esValido = true;
    errores.value = {};
    const clonedData = { ...formData.value };

    esquema.value.forEach((campo) => {
        const valor = formData.value[campo.nombre];

        // Validación Requeridos
        if (campo.requerido && (valor === null || valor === '' || valor === undefined)) {
            errores.value[campo.nombre] = 'Este campo es obligatorio.';
            esValido = false;
        }

        // Formato para envio HTTP
        if (campo.tipo === 'hora' && clonedData[campo.nombre] instanceof Date) {
            const date = clonedData[campo.nombre];
            clonedData[campo.nombre] = date.getHours().toString().padStart(2, '0') + ':' + date.getMinutes().toString().padStart(2, '0');
        }
    });

    emit('validar', { esValido, datos: clonedData });
    return esValido;
};

watch(
    () => props.modelValue,
    (newVal) => {
        formData.value = { ...newVal };
        inicializarFormulario();
    },
    { deep: true }
);

watch(
    formData,
    () => {
        emit('update:modelValue', formData.value);
        validarPayload();
    },
    { deep: true }
);

onMounted(() => {
    cargarEsquema();
});

defineExpose({ validarPayload });
</script>

<template>
    <div v-if="loading" class="flex justify-center p-4">
        <i class="pi pi-spin pi-spinner text-3xl text-primary"></i>
    </div>

    <div v-else class="flex flex-col gap-6">
        <!-- Renderizado Normal -->
        <div v-for="campo in esquema.filter(c => c.tipo !== 'booleano')" :key="campo.nombre">
            <label :for="campo.nombre" class="block font-bold mb-3">
                {{ campo.etiqueta }} <span v-if="campo.requerido" class="text-red-500">*</span>
            </label>

            <!-- Text Input -->
            <InputText v-if="campo.tipo === 'texto'" :id="campo.nombre" v-model="formData[campo.nombre]"
                :invalid="!!errores[campo.nombre]" fluid autocomplete="off" />

            <!-- Textarea -->
            <Textarea v-else-if="campo.tipo === 'textarea'" :id="campo.nombre" v-model="formData[campo.nombre]" rows="3"
                fluid />

            <!-- Time Input -->
            <DatePicker v-else-if="campo.tipo === 'hora'" :inputId="campo.nombre" v-model="formData[campo.nombre]"
                :invalid="!!errores[campo.nombre]" timeOnly fluid hourFormat="24" />

            <!-- Helper Text & Errores -->
            <small v-if="errores[campo.nombre]" class="text-red-500 block mt-1">
                {{ errores[campo.nombre] }}
            </small>
            <small v-else-if="campo.ayuda" class="text-surface-500 block mt-1">
                {{ campo.ayuda }}
            </small>
        </div>

        <!-- Renderizado de Checkboxes Agrupados al final -->
        <div class="grid grid-cols-1 gap-4 mt-2 p-4 bg-surface-50 dark:bg-surface-800 rounded-border">
            <div v-for="campo in esquema.filter(c => c.tipo === 'booleano')" :key="campo.nombre"
                class="flex items-center">
                <Checkbox v-model="formData[campo.nombre]" :inputId="campo.nombre" :binary="true" />
                <label :for="campo.nombre" class="ml-2 font-semibold">
                    {{ campo.etiqueta }}
                </label>
            </div>
        </div>
    </div>
</template>
