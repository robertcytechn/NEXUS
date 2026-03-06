<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import api from '@/service/api';

// Cache a nivel de módulo para evitar re-fetchar el esquema en cada apertura del dialog.
const _schemaCache = {};

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

// Variables para selects dinámicos y dependencias
const allChoices = ref({});

const cargarEsquema = async () => {
    // Usar caché si ya fue cargado previamente
    if (_schemaCache['maquinas']) {
        formSchema.value = _schemaCache['maquinas'].campos;
        allChoices.value = _schemaCache['maquinas'].choices;
        return;
    }

    loadingSchema.value = true;
    errorSchema.value = null;
    try {
        const response = await api.options('maquinas/esquema/');
        formSchema.value = response.data.campos;
        allChoices.value = response.data.choices;
        // Guardar en caché
        _schemaCache['maquinas'] = { campos: response.data.campos, choices: response.data.choices };
    } catch (error) {
        errorSchema.value = "No se pudo cargar la definición del formulario. Verifica la conexión.";
        console.error("Error al cargar esquema de maquinas:", error);
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

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <template v-for="field in formSchema" :key="field.name">
            <div :class="{
                'md:col-span-2 lg:col-span-3': field.type === 'multiselect',
                'md:col-span-2': field.name === 'descripcion'
            }">
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
                    :placeholder="field.placeholder" :maxlength="field.maxLength" fluid
                    :invalid="props.submitted && field.required && !internalValue[field.name]" autocomplete="off" />

                <!-- Input Number -->
                <InputNumber v-else-if="field.type === 'number'" :inputId="field.name"
                    v-model="internalValue[field.name]" fluid
                    :invalid="props.submitted && field.required && internalValue[field.name] === null" />

                <!-- Textarea -->
                <Textarea v-else-if="field.type === 'textarea'" :id="field.name" v-model="internalValue[field.name]"
                    :placeholder="field.placeholder" rows="3" fluid
                    :invalid="props.submitted && field.required && !internalValue[field.name]" />

                <!-- Boolean / Checkbox -->
                <div v-else-if="field.type === 'boolean'" class="flex items-center gap-2 mt-2">
                    <Checkbox :inputId="field.name" v-model="internalValue[field.name]" :binary="true" />
                    <label :for="field.name">{{ field.label }}</label>
                </div>

                <!-- Select -->
                <div v-else-if="field.type === 'select'" class="relative">
                    <Select :inputId="field.name" v-model="internalValue[field.name]"
                        :options="allChoices[field.options] || []" optionLabel="label" optionValue="value"
                        :placeholder="`Seleccione ${field.label}`" fluid filter
                        :invalid="props.submitted && field.required && !internalValue[field.name]">
                        <template #option="slotProps">
                            <span v-if="field.name === 'modelo'">
                                {{ slotProps.option.label }}
                                <span class="text-xs text-surface-500 ml-2">({{ slotProps.option.proveedor_nombre
                                }})</span>
                            </span>
                            <span v-else>{{ slotProps.option.label }}</span>
                        </template>
                    </Select>
                </div>

                <!-- MultiSelect -->
                <div v-else-if="field.type === 'multiselect'" class="relative">
                    <MultiSelect :inputId="field.name" v-model="internalValue[field.name]"
                        :options="allChoices[field.options] || []" optionLabel="label" optionValue="value"
                        :placeholder="`Seleccione ${field.label}`" fluid filter :maxSelectedLabels="8"
                        :invalid="props.submitted && field.required && (!internalValue[field.name] || internalValue[field.name].length === 0)">
                        <template #option="slotProps">
                            <div class="flex items-center gap-2">
                                <span class="font-semibold">{{ slotProps.option.moneda }}</span>
                                <span>{{ slotProps.option.label }}</span>
                            </div>
                        </template>
                    </MultiSelect>
                </div>

                <!-- Mensaje de error genérico -->
                <small
                    v-if="props.submitted && field.required && (internalValue[field.name] === null || internalValue[field.name] === '' || (Array.isArray(internalValue[field.name]) && internalValue[field.name].length === 0))"
                    class="text-red-500 block mt-1">
                    {{ field.label }} es obligatorio.
                </small>
            </div>
        </template>
    </div>
</template>
