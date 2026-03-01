<script setup>
import { computed } from 'vue';
import ProveedorForm from './ProveedorForm.vue';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
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
    }
});

const emit = defineEmits(['update:visible', 'saved', 'closed']);

const isVisible = computed({
    get: () => props.visible,
    set: (value) => emit('update:visible', value)
});

const esEdicion = computed(() => !!props.proveedorId);

const closeDialog = () => {
    isVisible.value = false;
    emit('closed');
};

const onFormSaved = (data) => {
    emit('saved', data);
    closeDialog();
};
</script>

<template>
    <Dialog v-model:visible="isVisible" :style="{ width: '95vw', maxWidth: '700px' }"
        :header="esEdicion ? 'Editar Proveedor' : 'Nuevo Proveedor'" :modal="true" :dismissableMask="true">
        <!-- Componente Inteligente Inyectado -->
        <ProveedorForm v-if="isVisible" :proveedorId="proveedorId" :casinoFijo="casinoFijo"
            :permitirElegirCasino="permitirElegirCasino" @saved="onFormSaved" @cancel="closeDialog" />
    </Dialog>
</template>

<!-- =====================================================================================
📝 TUTORIAL DE IMPLEMENTACIÓN (Wrapper de Proveedores)
==========================================================================================
📌 ¿Qué es este componente?
`ProveedorFormDialog.vue` es el puente oficial y Contenedor (Wrapper) del componente `ProveedorForm.vue`. 
Abstrae la lógica de visibilidad del Dialog modal de PrimeVue.

📌 Props:
- `v-model:visible`: Controla reactivamente si el Modal se abre o se cierra.
- `proveedorId`: ID asigando para editar. Si es nulo entra en modo Creación.
- `casinoFijo` y `permitirElegirCasino`: Controlan permisos y autoselección de los Selects (Casinos).

📌 Eventos: `@saved` y `@closed`.
====================================================================================== -->
