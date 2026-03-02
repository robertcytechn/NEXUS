<script setup>
import { ref, watch, onMounted } from 'vue';
import api from '@/service/api';

const props = defineProps({
    modelValue: {
        type: Object,
        default: () => ({})
    },
    submitted: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['update:modelValue', 'validar']);

const formSchema = ref([]);
const loadingSchema = ref(false);
const errorSchema = ref(null);

// Variables para selects dinámicos (e.g. proveedor)
const dynamicOptions = ref({});
const loadingOptions = ref({});

const cargarEsquema = async () => {
    loadingSchema.value = true;
    errorSchema.value = null;
    try {
        const response = await api.options('modelos/esquema/');
        formSchema.value = response.data;

        // Extraer opciones embebidas del esquema OPTIONS si existen
        formSchema.value.forEach(field => {
            if (field.type === 'select' && field.choices) {
                dynamicOptions.value[field.name] = field.choices;
            }
        });
    } catch (error) {
        errorSchema.value = "No se pudo cargar la definición del formulario. Verifica la conexión.";
        console.error("Error al cargar esquema de modelos:", error);
    } finally {
        loadingSchema.value = false;
    }
};

const internalValue = ref({ ...props.modelValue });

watch(internalValue, (newVal) => {
    emit('update:modelValue', newVal);
}, { deep: true });

watch(() => props.modelValue, (newVal) => {
    internalValue.value = { ...newVal };
}, { deep: true });

onMounted(() => {
    cargarEsquema();
});
</script>

<template>
    <div v-if="loadingSchema" class="flex justify-center p-6">
        <i class="pi pi-spin pi-spinner text-4xl text-primary"></i>
    </div>

    <div v-else-if="errorSchema"
        class="text-center p-6 text-red-500 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200">
        <i class="pi pi-exclamation-triangle text-3xl mb-3"></i>
        <p>{{ errorSchema }}</p>
        <Button label="Reintentar" icon="pi pi-refresh" size="small" class="mt-3" @click="cargarEsquema" />
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <template v-for="field in formSchema" :key="field.name">
            <div :class="{ 'md:col-span-2': field.type === 'textarea' }">
                <label :for="field.name" class="block font-bold mb-3 flex items-center justify-between">
                    <span>
                        {{ field.label }}
                        <span v-if="field.required" class="text-red-500 ml-1">*</span>
                    </span>
                    <i v-if="field.help_text" class="pi pi-info-circle text-surface-400"
                        v-tooltip.top="field.help_text"></i>
                </label>

                <!-- Input Text -->
                <InputText v-if="field.type === 'text'" :id="field.name" v-model="internalValue[field.name]"
                    :placeholder="field.placeholder" fluid
                    :invalid="props.submitted && field.required && !internalValue[field.name]" autocomplete="off" />

                <!-- Textarea -->
                <Textarea v-else-if="field.type === 'textarea'" :id="field.name" v-model="internalValue[field.name]"
                    :placeholder="field.placeholder" rows="4" fluid
                    :invalid="props.submitted && field.required && !internalValue[field.name]" />

                <!-- Boolean / Checkbox -->
                <div v-else-if="field.type === 'boolean'" class="flex items-center gap-2 mt-2">
                    <Checkbox :inputId="field.name" v-model="internalValue[field.name]" :binary="true" />
                    <label :for="field.name">{{ field.label }}</label>
                </div>

                <!-- Select -->
                <div v-else-if="field.type === 'select'" class="relative">
                    <Select :inputId="field.name" v-model="internalValue[field.name]"
                        :options="dynamicOptions[field.name]" optionLabel="label" optionValue="value"
                        :placeholder="field.placeholder || `Seleccione ${field.label}`" fluid filter
                        :invalid="props.submitted && field.required && !internalValue[field.name]"
                        :loading="loadingOptions[field.name]">
                        <template #option="slotProps">
                            {{ slotProps.option.label }}
                        </template>
                    </Select>
                </div>

                <!-- Mensaje de error genérico -->
                <small v-if="props.submitted && field.required && !internalValue[field.name]"
                    class="text-red-500 block mt-1">
                    {{ field.label }} es obligatorio.
                </small>
            </div>
        </template>
    </div>
</template>
