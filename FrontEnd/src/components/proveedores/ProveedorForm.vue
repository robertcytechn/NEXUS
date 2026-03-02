<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import api from '@/service/api';
import { useToast } from 'primevue/usetoast';

// Configuración de Props
const props = defineProps({
    proveedorId: {
        type: [Number, String],
        default: null
    },
    casinoFijo: {
        type: [Number, String],
        default: null
    },
    permitirElegirCasino: {
        type: Boolean,
        default: false
    },
    readOnly: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['saved', 'cancel']);
const toast = useToast();

// Estados Reactivos
const loadingSchema = ref(true);
const loadingData = ref(false);
const saving = ref(false);
const esquema = ref([]);
const formData = ref({});
const errores = ref({});
const esEdicion = computed(() => !!props.proveedorId);

// RBAC y Sesión (Regla 4)
const getUserData = () => {
    try {
        return JSON.parse(localStorage.getItem('user')) || {};
    } catch { return {}; }
};

const userParseado = computed(() => getUserData());
const rolActual = computed(() => userParseado.value.rol_nombre ? userParseado.value.rol_nombre.toUpperCase() : '');
const casinoSesion = computed(() => userParseado.value.casino || null);

// Permisos Dinámicos
const puedeEditar = computed(() => ['SUP SISTEMAS', 'ADMINISTRADOR', 'SUPERVISOR SALA'].includes(rolActual.value));

// Inicializar el esquema desde el Backend (Regla 2)
const fetchEsquema = async () => {
    loadingSchema.value = true;
    try {
        const response = await api.get('proveedores/esquema/');
        esquema.value = response.data;

        // Limpiar Form Data con valores por defecto del esquema
        esquema.value.forEach(campo => {
            if (!esEdicion.value) {
                formData.value[campo.name] = campo.type === 'boolean' ? (campo.default !== undefined ? campo.default : false) : null;
            }
        });

        // Forzar Casino si no se permite elegir (Regla 1)
        if (!props.permitirElegirCasino) {
            formData.value.casino = props.casinoFijo ? Number(props.casinoFijo) : (casinoSesion.value ? Number(casinoSesion.value) : null);
        }

    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar la estructura del formulario.' });
    } finally {
        loadingSchema.value = false;
    }
};

// Cargar Datos del Proveedor (Si es edición)
const fetchProveedorData = async () => {
    if (!props.proveedorId) return;
    loadingData.value = true;
    try {
        const response = await api.get(`proveedores/${props.proveedorId}/`);
        formData.value = { ...response.data };
        // Eliminar contraseña del rellenado para evitar mutaciones accidentales
        delete formData.value.password;
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los datos del proveedor.' });
        emit('cancel');
    } finally {
        loadingData.value = false;
    }
};

// Validaciones Dinámicas (Regla 5)
const validarFormulario = () => {
    errores.value = {};
    let esValido = true;

    esquema.value.forEach(campo => {
        // En edición, password ya no es obligatoria a menos que la quieras cambiar
        if (campo.required && campo.name !== 'password' && (formData.value[campo.name] === null || formData.value[campo.name] === '')) {
            errores.value[campo.name] = 'Este campo es requerido';
            esValido = false;
        }

        if (campo.name === 'password' && !esEdicion.value && !formData.value[campo.name]) {
            errores.value[campo.name] = 'La contraseña es obligatoria en creación';
            esValido = false;
        }

        if (campo.type === 'email' && formData.value[campo.name]) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(formData.value[campo.name])) {
                errores.value[campo.name] = 'Correo electrónico inválido';
                esValido = false;
            }
        }
    });

    return esValido;
};

// Guardar Datos
const submitForm = async () => {
    if (!validarFormulario() || readOnly.value) return;

    saving.value = true;
    try {
        const payload = { ...formData.value };

        // Limpiar payload de paswords en blanco
        if (esEdicion.value && !payload.password) {
            delete payload.password;
        }

        let res;
        if (esEdicion.value) {
            res = await api.patch(`proveedores/${props.proveedorId}/`, payload);
            toast.add({ severity: 'success', summary: 'Éxito', detail: 'Proveedor actualizado correctamente.' });
        } else {
            res = await api.post('proveedores/', payload);
            toast.add({ severity: 'success', summary: 'Éxito', detail: 'Proveedor registrado correctamente.' });
        }

        emit('saved', res.data);
    } catch (error) {
        // Extraer mensajes de error de Django DRF
        const errData = error.response?.data;
        if (typeof errData === 'object' && errData !== null) {
            Object.keys(errData).forEach(key => {
                if (Array.isArray(errData[key])) {
                    errores.value[key] = errData[key][0];
                } else {
                    errores.value[key] = errData[key];
                }
            });
            toast.add({ severity: 'error', summary: 'Revise los campos', detail: 'Hay errores de validación.' });
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: 'Ocurrió un problema inesperado.' });
        }
    } finally {
        saving.value = false;
    }
};

onMounted(async () => {
    await fetchEsquema();
    if (esEdicion.value) {
        await fetchProveedorData();
    }
});

// Watcher si cambia el ID (reabrir modal sin desmontar)
watch(() => props.proveedorId, async (newVal) => {
    if (newVal) {
        await fetchProveedorData();
    } else {
        // Reset a creación
        Object.keys(formData.value).forEach(key => {
            const campoSq = esquema.value.find(c => c.name === key);
            formData.value[key] = campoSq && campoSq.type === 'boolean' ? (campoSq.default !== undefined ? campoSq.default : false) : null;
        });
        if (!props.permitirElegirCasino) {
            formData.value.casino = props.casinoFijo ? Number(props.casinoFijo) : (casinoSesion.value ? Number(casinoSesion.value) : null);
        }
        errores.value = {};
    }
});

</script>

<template>
    <div class="relative w-full">
        <!-- Loader del Esquema -->
        <div v-if="loadingSchema || loadingData" class="flex flex-col gap-4 p-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Skeleton width="100%" height="4rem" v-for="i in 4" :key="i" borderRadius="16px"></Skeleton>
            </div>
            <Skeleton width="100%" height="4rem" borderRadius="16px"></Skeleton>
        </div>

        <!-- Sin Permisos (Regla 4) -->
        <div v-else-if="!puedeEditar && !readOnly"
            class="flex flex-col items-center justify-center p-8 text-center bg-surface-50 dark:bg-surface-900 rounded-xl border border-dashed border-surface-200 dark:border-surface-700">
            <i class="pi pi-lock text-4xl text-surface-400 mb-4"></i>
            <h3 class="text-xl font-bold text-surface-900 dark:text-surface-0 mb-2">Acceso Restringido</h3>
            <p class="text-surface-500">No tienes los privilegios necesarios para gestionar proveedores.</p>
        </div>

        <!-- Formulario Renderizado Dinámicamente -->
        <form v-else @submit.prevent="submitForm" class="flex flex-col gap-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <template v-for="campo in esquema" :key="campo.name">

                    <!-- Text / Email / Username -->
                    <div v-if="['text', 'email', 'string'].includes(campo.type) && campo.name !== 'password'"
                        class="flex flex-col gap-2">
                        <label :for="campo.name" class="font-bold text-sm text-surface-900 dark:text-surface-0">
                            {{ campo.label }} <span v-if="campo.required" class="text-red-500">*</span>
                        </label>
                        <InputText :id="campo.name" v-model.trim="formData[campo.name]"
                            :type="campo.type === 'email' ? 'email' : 'text'"
                            :disabled="readOnly || campo.readOnly || (campo.name === 'casino' && !permitirElegirCasino)"
                            :invalid="!!errores[campo.name]" :placeholder="campo.placeholder || ''" class="w-full"
                            autocomplete="off" />
                        <small v-if="errores[campo.name]" class="text-red-500">{{ errores[campo.name] }}</small>
                        <small v-else-if="campo.help_text" class="text-surface-500">{{ campo.help_text }}</small>
                    </div>

                    <!-- Password -->
                    <div v-else-if="campo.name === 'password' && !readOnly" class="flex flex-col gap-2">
                        <label :for="campo.name" class="font-bold text-sm text-surface-900 dark:text-surface-0">
                            {{ campo.label }} <span v-if="campo.required && !esEdicion" class="text-red-500">*</span>
                        </label>
                        <Password :inputId="campo.name" v-model="formData[campo.name]" :feedback="true" toggleMask
                            :invalid="!!errores[campo.name]" :disabled="readOnly || campo.readOnly"
                            promptLabel="Introduce una contraseña" weakLabel="Débil" mediumLabel="Media"
                            strongLabel="Fuerte" class="w-full" inputClass="w-full" autocomplete="new-password" />
                        <small v-if="errores[campo.name]" class="text-red-500">{{ errores[campo.name] }}</small>
                        <small v-else-if="esEdicion" class="text-surface-500">Dejar en blanco para mantener la
                            actual.</small>
                    </div>

                    <!-- Selectores (Relaciones o Choices) -->
                    <div v-else-if="campo.type === 'choice' || campo.type === 'foreign_key'"
                        class="flex flex-col gap-2">
                        <label :for="campo.name" class="font-bold text-sm text-surface-900 dark:text-surface-0">
                            {{ campo.label }} <span v-if="campo.required" class="text-red-500">*</span>
                        </label>
                        <Select :inputId="campo.name" v-model="formData[campo.name]" :options="campo.choices"
                            optionLabel="label" optionValue="value"
                            :disabled="readOnly || campo.readOnly || (campo.name === 'casino' && !permitirElegirCasino)"
                            :invalid="!!errores[campo.name]" :placeholder="campo.placeholder || 'Seleccione una opción'"
                            class="w-full" />
                        <small v-if="errores[campo.name]" class="text-red-500">{{ errores[campo.name] }}</small>
                    </div>

                    <!-- Booleanos -->
                    <div v-else-if="campo.type === 'boolean'" class="flex items-center gap-2 mt-6">
                        <Checkbox :inputId="campo.name" v-model="formData[campo.name]" :binary="true"
                            :invalid="!!errores[campo.name]" :disabled="readOnly || campo.readOnly" />
                        <label :for="campo.name"
                            class="font-bold text-sm text-surface-900 dark:text-surface-0 cursor-pointer">
                            {{ campo.label }}
                        </label>
                    </div>

                </template>
            </div>

            <!-- Botones de Acción -->
            <div v-if="!readOnly"
                class="flex justify-end gap-3 pt-4 border-t border-surface-200 dark:border-surface-700 mt-4">
                <Button type="button" label="Cancelar" icon="pi pi-times" severity="secondary" outlined
                    @click="emit('cancel')" :disabled="saving" />
                <Button type="submit" :label="esEdicion ? 'Actualizar Proveedor' : 'Registrar Proveedor'"
                    icon="pi pi-check" :loading="saving" />
            </div>
        </form>
    </div>
</template>

<!-- =========================================================================================================
📝 TUTORIAL INTEGRADO Y TÉCNICA DE USO
==============================================================================================================
📌 ¿Qué es este componente?
`ProveedorForm.vue` es el motor inteligente del CRUD de Proveedores. 
Descarga su propia estructura (`esquema`) desde el backend de Django y construye los campos dinámicamente.

📌 Props Disponibles:
- `proveedorId` (Number|String, Default: null) : ID a modificar. Si es `null`, es modo "Nuevo Proveedor".
- `casinoFijo` (Number|String, Default: null): Fuerza un casino por ID ignorando cualquier otro. 
- `permitirElegirCasino` (Boolean, Default: false): Si es `true`, el select de casinos estará habilitado. Si es `false`, el sistema forzará `casinoFijo` o sacará el casino de la sesión actual (`casinoSesion`).
- `readOnly` (Boolean, Default: false): Convierte el formulario en modo solo lectura.

📌 Ejemplos de Implementación:

Ejemplo 1: Creación Libre (Super Admin)
--------------------------------------
<ProveedorForm 
    @saved="onGuardadoExitoso" 
    :permitirElegirCasino="true" 
/>

Ejemplo 2: Edición Forzada (Gerente de Sala que edita proveedor de su casino)
-------------------------------------------------------------------------------
<ProveedorForm 
    :proveedorId="15"
    :casinoFijo="6" 
    :permitirElegirCasino="false"
/>
========================================================================================================== -->
