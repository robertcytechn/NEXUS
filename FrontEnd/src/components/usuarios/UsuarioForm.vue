<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import api from '@/service/api';
import { useToast } from 'primevue/usetoast';

// Configuración de Props
const props = defineProps({
    usuarioId: {
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
const esEdicion = computed(() => !!props.usuarioId);

// RBAC y Sesión (Regla 4)
const getUserData = () => {
    try {
        const u = localStorage.getItem('user');
        return u ? JSON.parse(u) : {};
    } catch { return {}; }
};

const userParseado = computed(() => getUserData());
const rolActual = computed(() => userParseado.value.rol_nombre ? userParseado.value.rol_nombre.toUpperCase() : '');
const nivelJerarquiaActual = computed(() => userParseado.value.nivel_jerarquia || 0);
const casinoSesion = computed(() => userParseado.value.casino || null);

// Permisos Dinámicos
const puedeEditar = computed(() => ['SUP SISTEMAS', 'ADMINISTRADOR', 'GERENCIA', 'SUPERVISOR SALA'].includes(rolActual.value));

// Interceptor del Esquema para Segregación de Funciones (Anti-Escalación)
const esquemaFiltrado = computed(() => {
    return esquema.value.map(campo => {
        if (campo.name === 'rol' && campo.choices) {
            return {
                ...campo,
                choices: campo.choices.filter(opcion => (opcion.nivel_jerarquia || 0) <= nivelJerarquiaActual.value)
            };
        }
        return campo;
    });
});


// Inicializar el esquema desde el Backend (Regla 2)
const fetchEsquema = async () => {
    loadingSchema.value = true;
    try {
        // Asumiendo que el backend responderá en este endpoint:
        const { data } = await api.get('/usuarios/esquema/');
        esquema.value = data;

        // Inicializar formData basado en el esquema
        data.forEach(campo => {
            if (campo.type === 'boolean') {
                formData.value[campo.name] = campo.default !== undefined ? campo.default : false;
            } else {
                formData.value[campo.name] = campo.default !== undefined ? campo.default : null;
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

// Cargar Datos del Usuario (Si es edición)
const fetchUsuarioData = async () => {
    if (!esEdicion.value) return;

    loadingData.value = true;
    try {
        const { data } = await api.get(`/usuarios/${props.usuarioId}/`);
        // Mezclar datos con el formData
        formData.value = { ...formData.value, ...data };

        // Limpiar password por seguridad
        formData.value.password = '';

    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los datos del usuario.' });
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
        if (campo.required) {
            // Regla especial para password en edición
            if (campo.name === 'password' && esEdicion.value) return;

            if (formData.value[campo.name] === null || formData.value[campo.name] === '' || formData.value[campo.name] === undefined) {
                errores.value[campo.name] = `El campo ${campo.label} es obligatorio.`;
                esValido = false;
            }
        }
        if (campo.maxLength && formData.value[campo.name]?.length > campo.maxLength) {
            errores.value[campo.name] = `Máximo ${campo.maxLength} caracteres.`;
            esValido = false;
        }
    });

    return esValido;
};

// Guardar Datos
const submitForm = async () => {
    if (!validarFormulario()) {
        toast.add({ severity: 'warn', summary: 'Validación', detail: 'Por favor, corrige los errores del formulario.' });
        return;
    }

    saving.value = true;
    const payload = { ...formData.value };

    // Si es edición y el password está vacío, no enviarlo
    if (esEdicion.value && !payload.password) {
        delete payload.password;
    }

    try {
        if (esEdicion.value) {
            await api.put(`/usuarios/${props.usuarioId}/`, payload);
        } else {
            await api.post('/usuarios/', payload);
        }
        toast.add({ severity: 'success', summary: 'Éxito', detail: `Usuario ${esEdicion.value ? 'actualizado' : 'creado'} correctamente.` });
        emit('saved', payload);
    } catch (error) {
        const errMsg = error.response?.data?.message || error.response?.data?.detail || 'Error al guardar el usuario.';
        toast.add({ severity: 'error', summary: 'Error', detail: errMsg });
        // Mapear errores del backend a los campos si existen
        if (error.response?.data && typeof error.response.data === 'object' && !error.response.data.message) {
            Object.keys(error.response.data).forEach(key => {
                if (Array.isArray(error.response.data[key])) {
                    errores.value[key] = error.response.data[key][0];
                }
            });
        }
    } finally {
        saving.value = false;
    }
};

onMounted(async () => {
    await fetchEsquema();
    if (esEdicion.value) {
        await fetchUsuarioData();
    }
});

// Watcher si cambia el ID (reabrir modal sin desmontar)
watch(() => props.usuarioId, async (newVal) => {
    if (newVal) {
        await fetchUsuarioData();
    } else {
        // Reset a modo creación
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
            <p class="text-surface-500">No tienes los privilegios necesarios para gestionar usuarios.</p>
        </div>

        <!-- Formulario Renderizado Dinámicamente -->
        <form v-else @submit.prevent="submitForm" class="flex flex-col gap-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <template v-for="campo in esquemaFiltrado" :key="campo.name">

                    <!-- Text / Email / Username -->
                    <div v-if="['text', 'email', 'string'].includes(campo.type) && campo.name !== 'password' && campo.name !== 'avatar'"
                        class="flex flex-col gap-2">
                        <label :for="campo.name" class="font-bold text-sm text-surface-900 dark:text-surface-0">
                            {{ campo.label }} <span v-if="campo.required" class="text-red-500">*</span>
                        </label>
                        <InputText :id="campo.name" v-model.trim="formData[campo.name]"
                            :type="campo.type === 'email' ? 'email' : 'text'"
                            :disabled="readOnly || campo.readOnly || (campo.name === 'casino' && !permitirElegirCasino)"
                            :invalid="!!errores[campo.name]" :placeholder="campo.placeholder || ''" class="w-full" />
                        <small v-if="errores[campo.name]" class="text-red-500">{{ errores[campo.name] }}</small>
                        <small v-else-if="campo.help_text" class="text-surface-500">{{ campo.help_text }}</small>
                    </div>

                    <!-- Password -->
                    <div v-else-if="campo.name === 'password' && !readOnly" class="flex flex-col gap-2">
                        <label :for="campo.name" class="font-bold text-sm text-surface-900 dark:text-surface-0">
                            {{ campo.label }} <span v-if="campo.required && !esEdicion" class="text-red-500">*</span>
                        </label>
                        <Password :id="campo.name" v-model="formData[campo.name]" :feedback="true" toggleMask
                            :invalid="!!errores[campo.name]" :disabled="readOnly || campo.readOnly"
                            promptLabel="Introduce una contraseña" weakLabel="Débil" mediumLabel="Media"
                            strongLabel="Fuerte" class="w-full" inputClass="w-full" />
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
                        <Select :id="campo.name" v-model="formData[campo.name]" :options="campo.choices"
                            optionLabel="label" optionValue="value"
                            :disabled="readOnly || campo.readOnly || (campo.name === 'casino' && !permitirElegirCasino)"
                            :invalid="!!errores[campo.name]" :placeholder="campo.placeholder || 'Seleccione una opción'"
                            class="w-full" />
                        <small v-if="errores[campo.name]" class="text-red-500">{{ errores[campo.name] }}</small>
                    </div>

                    <!-- Booleanos -->
                    <div v-else-if="campo.type === 'boolean'" class="flex items-center gap-2 mt-6">
                        <Checkbox :inputId="campo.name" v-model="formData[campo.name]" :binary="true"
                            :disabled="readOnly || campo.readOnly" :invalid="!!errores[campo.name]" />
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
                <Button type="button" label="Cancelar" icon="pi pi-times" severity="secondary" text
                    @click="emit('cancel')" :disabled="saving" />
                <Button type="submit" :label="esEdicion ? 'Actualizar Usuario' : 'Crear Usuario'" icon="pi pi-check"
                    :loading="saving" />
            </div>
        </form>
    </div>
</template>

<style scoped>
/* Estilos adicionales si son necesarios, delegando max-width a PrimeVue classes */
</style>

<!-- =========================================================================================================
📝 TUTORIAL INTEGRADO Y TÉCNICA DE USO (Regla 6)
==============================================================================================================
📌 ¿Qué es este componente?
`UsuarioForm.vue` es el motor inteligente del CRUD de Usuarios.
Descarga su propia estructura (`esquema`) desde el backend de Django, construyendo dinámicamente cada campo,
su validación, y evaluando proactivamente los permisos del usuario usando el `localStorage`.

📌 Props Disponibles (Parametrización Absoluta):
- `usuarioId` (Number|String, Default: null) : ID del usuario a modificar. Si es `null`, el form entra en modo "Nuevo Usuario".
- `casinoFijo` (Number|String, Default: null): Fuerza un casino por ID ignorando cualquier otro. Ideal cuando sabes a qué casino enviar al usuario.
- `permitirElegirCasino` (Boolean, Default: false): Si es `true`, el select de casinos estará habilitado. Si es `false`, el sistema forzará `casinoFijo` o sacará el casino de la sesión actual (`casinoSesion`) para auto-asignarlo y bloquear el select.
- `readOnly` (Boolean, Default: false): Convierte el formulario en modo de solo lectura. Útil para vistas de detalles.

📌 Ejemplos de Implementación:

Ejemplo 1: Creación Libre (Super Admin)
--------------------------------------
<UsuarioForm 
    @saved="onGuardadoExitoso" 
    :permitirElegirCasino="true" 
/>
* Explicación: Permitirá al admin crear un usuario nuevo y elegir libremente en qué casino registrarlo.

Ejemplo 2: Edición Forzada a un Casino (Gerente de Sala)
--------------------------------------------------------
<UsuarioForm 
    :usuarioId="15"
    :casinoFijo="6" 
    :permitirElegirCasino="false"
    @saved="onUsuarioActualizado"
/>
* Explicación: Editará al usuario #15 bloqueando el <Select> de Casino y forzando el registro al Casino con ID 6.

Ejemplo 3: Modo Ficha Técnica (Solo Vista)
------------------------------------------
<UsuarioForm 
    :usuarioId="15"
    :readOnly="true"
/>
* Explicación: Cargará los datos del usuario #15 en los campos correspondientes, pero deshabilitará todo tipo de edición y removerá los botones de guardado.

📌 Reglas Internas de Negocio Activas:
1. Anti-Escalación de Privilegios: El select de Roles solo mostrará roles que tengan un `nivel_jerarquia` MENOR o IGUAL al `nivel_jerarquia` del empleado que tiene la sesión activa (leyendo de `localStorage`).
2. RBAC (Bloqueo Total): Si el rol actual no está en la lista blanca de edición (`['SUP SISTEMAS', 'ADMINISTRADOR', 'GERENCIA', 'SUPERVISOR SALA']`), mostrará un candado en vez del formulario.
========================================================================================================== -->
