<script setup>
import { ref, watch } from 'vue';
import api, { getUser } from '@/service/api';
import { useToast } from 'primevue/usetoast';
import TicketForm from './TicketForm.vue';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    ticketProp: {
        type: Object,
        default: () => ({})
    }
});

const emit = defineEmits(['update:visible', 'saved']);

const toast = useToast();
const loading = ref(false);
const submitted = ref(false);

const formEngineInstance = ref(null);
const localData = ref({});
const esValidoForm = ref(false);

watch(
    () => props.ticketProp,
    (newVal) => {
        localData.value = { ...newVal };
    },
    { immediate: true, deep: true }
);

const hideDialog = () => {
    emit('update:visible', false);
    submitted.value = false;
};

const handleValidar = ({ esValido, datos }) => {
    esValidoForm.value = esValido;
    localData.value = datos;
};

const saveTicket = async () => {
    submitted.value = true;

    if (formEngineInstance.value) {
        formEngineInstance.value.validarPayload();
    }

    if (!esValidoForm.value) {
        toast.add({
            severity: 'warn',
            summary: 'Formulario Incompleto',
            detail: 'Debe rellenar los datos obligatorios del Ticket',
            life: 3000
        });
        return;
    }

    loading.value = true;
    try {
        const payload = { ...localData.value };
        const id = payload.id;

        // Auto-Asignar Reportante en la Creación si no se pasa uno manual
        if (!id && !payload.reportante) {
            const user = getUser();
            if (user && user.id) {
                payload.reportante = user.id;
            }
        }

        if (id) {
            await api.put(`tickets/${id}/`, payload);
        } else {
            await api.post('tickets/', payload);

            // Re-Sync de fallas en máquina (Lógica extraida del anterior Tickets.vue)
            if (payload.maquina) {
                try { await api.post(`maquinas/${payload.maquina}/incrementar-fallas/`); }
                catch (err) { console.warn('Silenced error en sincronización contador fallas'); }
            }
        }

        toast.add({
            severity: 'success',
            summary: 'Éxito',
            detail: id ? 'Ticket actualizado correctamente' : 'El Ticket de Soporte fue generado',
            life: 3000
        });

        emit('saved');
        hideDialog();
    } catch (error) {
        const detalle = error?.response?.data?.mensaje || error?.response?.data?.detail || error?.response?.data?.error || 'Falló el guardado del ticket';
        toast.add({ severity: 'error', summary: 'Error', detail: detalle, life: 5000 });
    } finally {
        loading.value = false;
    }
};
</script>

<template>
    <Dialog :visible="visible" @update:visible="(val) => emit('update:visible', val)" :style="{ width: '550px' }"
        :header="ticketProp.id ? `Editar Ticket: ${ticketProp.folio || ''}` : 'Alta de Nuevo Ticket'" :modal="true"
        class="p-fluid">
        <TicketForm v-if="visible" ref="formEngineInstance" v-model="localData" :modoEdicion="!!ticketProp.id"
            @validar="handleValidar" />

        <div v-if="ticketProp.id" class="border-t border-surface-200 dark:border-surface-700 pt-4 mt-4">
            <div class="font-bold mb-3 text-surface-500 dark:text-surface-400">Contexto del Ciclo de Vida</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                    <span class="font-bold text-surface-600">Reaperturas:</span> {{ ticketProp.contador_reaperturas }}
                </div>
                <div>
                    <span class="font-bold text-surface-600">Creador Base:</span> {{ ticketProp.creado_por || 'Sistema'
                    }}
                </div>
            </div>
        </div>

        <template #footer>
            <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" :disabled="loading" />
            <Button label="Guardar Incidencia" icon="pi pi-check" @click="saveTicket" :loading="loading" />
        </template>
    </Dialog>
</template>
