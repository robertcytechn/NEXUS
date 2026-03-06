<script setup>
import { ref, watch, onMounted } from 'vue';
import api from '@/service/api';
import { useToast } from 'primevue/usetoast';

// Cache a nivel de módulo: persiste entre aperturas del dialog sin recargar la página.
// Se resetea solo si el endpoint cambia.
const _schemaCache = {};      // { [endpoint]: campos[] }
const _fkCache = {};          // { [endpoint+fkEndpoint]: data[] }

const props = defineProps({
    modelValue: {
        type: Object,
        default: () => ({})
    },
    esquemaEndpoint: {
        type: String,
        default: 'tickets/esquema/'
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
const dataRelacional = ref({}); // Para guardar opciones de ForeignKeys dinamicas

const cargarEsquema = async () => {
    // Si ya tenemos el esquema cacheado, usarlo directamente sin petición de red
    if (_schemaCache[props.esquemaEndpoint]) {
        esquema.value = _schemaCache[props.esquemaEndpoint];
        dataRelacional.value = _fkCache[props.esquemaEndpoint] || {};
        loading.value = false;
        inicializarFormulario();
        return;
    }

    loading.value = true;
    try {
        const response = await api.options(props.esquemaEndpoint);
        esquema.value = response.data.campos || [];

        // Cargar datos relacionales en paralelo si existen
        const promesasFK = esquema.value
            .filter(c => c.tipo === 'fk' && c.endpoint)
            .map(async (campo) => {
                const res = await api.get(campo.endpoint);
                dataRelacional.value[campo.nombre] = res.data;
            });

        await Promise.all(promesasFK);

        // Guardar en caché para las próximas aperturas
        _schemaCache[props.esquemaEndpoint] = esquema.value;
        _fkCache[props.esquemaEndpoint] = { ...dataRelacional.value };

        inicializarFormulario();
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar el esquema del Ticket', life: 3000 });
    } finally {
        loading.value = false;
    }
};

const inicializarFormulario = () => {
    esquema.value.forEach((campo) => {
        if (formData.value[campo.nombre] === undefined) {
            formData.value[campo.nombre] = campo.default !== undefined ? campo.default : null;
        }
    });

    validarPayload();
};

const validarPayload = () => {
    let esValido = true;
    errores.value = {};
    const clonedData = { ...formData.value };

    esquema.value.forEach((campo) => {
        const valor = formData.value[campo.nombre];

        // Validacion Requeridos
        // NOTA: Para FK de Maquina y Estado_Ciclo durante edicion
        if (campo.requerido && (valor === null || valor === '' || valor === undefined)) {
            // Excepción legal para 'subcategoria' y campos de seguimiento
            errores.value[campo.nombre] = 'Este campo es obligatorio.';
            esValido = false;
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

    <div v-else class="flex flex-col gap-5">
        <div v-for="campo in esquema" :key="campo.nombre">
            <label :for="campo.nombre" class="block font-bold mb-2">
                {{ campo.etiqueta }} <span v-if="campo.requerido" class="text-red-500">*</span>
            </label>

            <!-- Input Tipo Texto Normal -->
            <InputText v-if="campo.tipo === 'texto'" :id="campo.nombre" v-model.trim="formData[campo.nombre]"
                :invalid="!!errores[campo.nombre]" fluid autocomplete="off" />

            <!-- TextArea Extenso -->
            <Textarea v-else-if="campo.tipo === 'textarea'" :id="campo.nombre" v-model="formData[campo.nombre]" rows="3"
                :invalid="!!errores[campo.nombre]" fluid />

            <!-- Selects (Choices quemados Django) -->
            <Select v-else-if="campo.tipo === 'select'" :inputId="campo.nombre" v-model="formData[campo.nombre]"
                :options="campo.opciones" optionLabel="label" optionValue="value" :invalid="!!errores[campo.nombre]"
                fluid />

            <!-- ForeignKey (Relacionales API) -->
            <Select v-else-if="campo.tipo === 'fk'" :inputId="campo.nombre" v-model="formData[campo.nombre]"
                :options="dataRelacional[campo.nombre]" optionLabel="uid_sala" optionValue="id" filter
                :placeholder="`Seleccionar ${campo.etiqueta}...`" :invalid="!!errores[campo.nombre]" fluid>
                <template #option="slotProps">
                    <div class="flex flex-col">
                        <span class="font-bold">{{ slotProps.option.uid_sala || slotProps.option.nombre }}</span>
                        <span v-if="slotProps.option.casino_nombre" class="text-xs text-surface-500">
                            {{ slotProps.option.casino_nombre }} - {{ slotProps.option.modelo_nombre }}
                        </span>
                    </div>
                </template>
            </Select>

            <!-- Render Errores o HelpText -->
            <small v-if="errores[campo.nombre]" class="text-red-500 block mt-1">
                {{ errores[campo.nombre] }}
            </small>
            <small v-else-if="campo.ayuda" class="text-surface-500 block mt-1 text-xs">
                <i class="pi pi-info-circle mr-1"></i>{{ campo.ayuda }}
            </small>
        </div>
    </div>
</template>
