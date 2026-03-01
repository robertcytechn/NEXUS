<script setup>
import { computed } from 'vue';
import UsuarioForm from './UsuarioForm.vue';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
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
    }
});

const emit = defineEmits(['update:visible', 'saved', 'closed']);

const isVisible = computed({
    get: () => props.visible,
    set: (value) => emit('update:visible', value)
});

const esEdicion = computed(() => !!props.usuarioId);

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
        :header="esEdicion ? 'Editar Usuario' : 'Nuevo Usuario'" :modal="true" :dismissableMask="true">
        <!-- Componente Inteligente Inyectado -->
        <UsuarioForm v-if="isVisible" :usuarioId="usuarioId" :casinoFijo="casinoFijo"
            :permitirElegirCasino="permitirElegirCasino" @saved="onFormSaved" @cancel="closeDialog" />
    </Dialog>
</template>

<!-- =====================================================================================
📝 TUTORIAL DE IMPLEMENTACIÓN (Wrapper)
==========================================================================================
📌 ¿Qué es este componente?
`UsuarioFormDialog.vue` es el puente oficial y Contenedor (Wrapper) del componente `UsuarioForm.vue`. 
Abstrae la lógica de visibilidad del Dialog modal de PrimeVue (<Dialog>) para que tu vista principal
(`Usuarios.vue`) quede totalmente limpia (Regla 3 de Negocio).

📌 Props que le puedes enviar:
- `v-model:visible` (Boolean): Controla reactivamente si el Modal se abre o se cierra.
- `usuarioId` (Number|String): Se lo pasa al Formulario. Si mandas un ID, cargará los datos para editarlos.
- `casinoFijo` (Number|String): Fuerza al Formulario a seleccionar este casino automáticamente.
- `permitirElegirCasino` (Boolean, Default: false): Desbloquea el selector de casinos del formulario.

📌 Eventos que emite (`@`):
- `@saved` : Se dispara cuando el usuario final presionó "Guardar" y la petición a Django fue 200 OK.
           Recibe el `payload` rellenado como argumento `$event`.
- `@closed` : Se dispara cuando el modal se oculta (ya sea por cancelar, por hacer clic fuera o después de guardar).

📌 ¿Cómo instanciarlo en una vista (ej. MandoCentral/Usuarios.vue)?
------------------------------------------------------------------
<script setup>
import { ref } from 'vue';
import UsuarioFormDialog from '@/components/usuarios/UsuarioFormDialog.vue';

const mostrarDialog = ref(false);
const idAEditar = ref(null); // Usar `null` para crear; o `15` para editar

const cuandoTermine = () => {
    // Aquí puedes refrescar tu DataGrid
    mostrarDialog.value = false;
};
</script>

<template>
   <button @click="mostrarDialog = true">Abrir Formulario</button>

   <UsuarioFormDialog 
       v-model:visible="mostrarDialog"
       :usuarioId="idAEditar" 
       :permitirElegirCasino="true"
       @saved="cuandoTermine"
   />
</template>
====================================================================================== -->
