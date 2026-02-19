<script setup>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import EvolucionService from '@/service/EvolucionService';
import { getUser } from '@/service/api';
import DnaBackground from '@/components/DnaBackground.vue';


const toast = useToast();
const evolucionService = new EvolucionService();

const evoluciones = ref([]);
const evolucionDialog = ref(false);
const deleteEvolucionDialog = ref(false);
const evolucion = ref({});
const selectedEvoluciones = ref(null);
const submitted = ref(false);
const loading = ref(true);

// Opciones de Categoría
const categorias = [
    { label: 'Error (Bug)', value: 'ERROR' },
    { label: 'Visual (Estilo)', value: 'VISUAL' },
    { label: 'Comportamiento (Lógica)', value: 'COMPORTAMIENTO' },
    { label: 'Funcionalidad (Nuevo Módulo)', value: 'FUNCIONALIDAD' },
    { label: 'Crear Nuevo ...', value: 'CREAR' }
];

// Opciones de Estado
const estados = [
    { label: 'No Revisado', value: 'NO_REVISADO' },
    { label: 'Abierto por Revisar', value: 'POR_REVISAR' },
    { label: 'Analizando Requerimientos', value: 'ANALIZANDO' },
    { label: 'Estudio de Mercado / Adquisición', value: 'ADQUISICION' },
    { label: 'Iniciando Maquetación', value: 'MAQUETACION' },
    { label: 'En Desarrollo', value: 'DESARROLLO' },
    { label: 'Pruebas / QA', value: 'PRUEBAS' },
    { label: 'Completado', value: 'COMPLETADO' }
];

const currentUser = getUser();
const isAdminOrDBA = computed(() => {
    const rol = currentUser?.rol_nombre?.toLowerCase();
    return ['administrador', 'dba', 'sistemas'].includes(rol);
});

onMounted(() => {
    evolucionService.getEvoluciones().then((data) => {
        evoluciones.value = data;
        loading.value = false;
    });
});

const openNew = () => {
    evolucion.value = {
        categoria: 'ERROR',
        datos_extra: {}
    };
    submitted.value = false;
    evolucionDialog.value = true;
};

const hideDialog = () => {
    evolucionDialog.value = false;
    submitted.value = false;
};

const saveEvolucion = () => {
    submitted.value = true;

    if (evolucion.value.titulo && evolucion.value.titulo.trim()) {
        if (evolucion.value.id) {
            evolucionService.updateEvolucion(evolucion.value).then((data) => {
                const index = evoluciones.value.findIndex(e => e.id === data.id);
                evoluciones.value[index] = data;
                toast.add({ severity: 'success', summary: 'Exitoso', detail: 'Registro Actualizado', life: 3000 });
                evolucionDialog.value = false;
                evolucion.value = {};
            });
        } else {
            evolucionService.createEvolucion(evolucion.value).then((data) => {
                evoluciones.value.unshift(data);
                toast.add({ severity: 'success', summary: 'Exitoso', detail: 'Registro Creado', life: 3000 });
                evolucionDialog.value = false;
                evolucion.value = {};
            });
        }
    }
};

const editEvolucion = (prod) => {
    evolucion.value = { ...prod };
    // Asegurar que datos_extra existe
    if (!evolucion.value.datos_extra) {
        evolucion.value.datos_extra = {};
    }
    evolucionDialog.value = true;
};

const getBadgeSeverity = (estado) => {
    switch (estado) {
        case 'NO_REVISADO': return 'danger';
        case 'POR_REVISAR': return 'warning';
        case 'ANALIZANDO': return 'info';
        case 'COMPLETADO': return 'success';
        default: return 'primary'; // null severity is not valid in some versions, use primary or undefined
    }
};

const getCategoriaSeverity = (categoria) => {
    switch (categoria) {
        case 'ERROR': return 'danger';
        case 'VISUAL': return 'info';
        case 'FUNCIONALIDAD': return 'success';
        default: return 'warning';
    }
};

</script>

<template>
    <div class="flex flex-col gap-6 relative min-h-screen">
        <DnaBackground :trigger="evolucion" opacity="opacity-5 dark:opacity-10"
            class="fixed inset-0 pointer-events-none" />

        <div
            class="card relative z-10 bg-surface-0/80 dark:bg-surface-900/80 backdrop-blur-md shadow-xl border border-surface-200 dark:border-surface-700">
            <Toast />
            <Toolbar class="mb-4 border-none bg-surface-50/50 dark:bg-surface-900/50 p-4 rounded-xl">
                <template v-slot:start>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-sparkles text-primary text-2xl"></i>
                        <span class="text-xl font-bold">Evolución NEXUS</span>
                    </div>
                </template>
                <template v-slot:end>
                    <Button label="Nueva Propuesta" icon="pi pi-plus" severity="primary" raised rounded
                        @click="openNew" />
                </template>
            </Toolbar>

            <DataTable :value="evoluciones" :paginator="true" :rows="10" :loading="loading" responsiveLayout="scroll"
                :rowHover="true" stripedRows showGridlines tableStyle="min-width: 50rem" :class="'p-datatable-sm'">

                <Column field="id" header="ID" :sortable="true" style="width: 80px">
                    <template #body="{ data }">
                        <span class="font-mono text-sm text-surface-500">#{{ data.id }}</span>
                    </template>
                </Column>

                <Column field="categoria" header="Categoría" :sortable="true">
                    <template #body="slotProps">
                        <Tag :value="slotProps.data.categoria"
                            :severity="getCategoriaSeverity(slotProps.data.categoria)" rounded />
                    </template>
                </Column>

                <Column field="titulo" header="Título" :sortable="true" style="min-width: 200px">
                    <template #body="{ data }">
                        <div class="font-semibold">{{ data.titulo }}</div>
                        <div class="text-xs text-surface-500 truncate max-w-xs">{{ data.descripcion }}</div>
                    </template>
                </Column>

                <Column field="estado" header="Estado" :sortable="true">
                    <template #body="slotProps">
                        <Tag :value="slotProps.data.estado" :severity="getBadgeSeverity(slotProps.data.estado)" />
                    </template>
                </Column>

                <Column header="Acciones" style="width: 100px; text-align: center">
                    <template #body="slotProps">
                        <Button icon="pi pi-pencil" text rounded severity="secondary"
                            @click="editEvolucion(slotProps.data)" v-tooltip.top="'Ver/Editar Detalles'" />
                    </template>
                </Column>
            </DataTable>

            <Dialog v-model:visible="evolucionDialog" :style="{ width: '650px' }" :modal="true"
                class="p-fluid relative overflow-hidden">
                <DnaBackground :trigger="evolucion" opacity="opacity-10 dark:opacity-20"
                    class="absolute inset-0 z-0 pointer-events-none" />

                <template #header>
                    <div class="flex items-center gap-2 relative z-10">
                        <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                            <i class="pi pi-star text-primary text-xl"></i>
                        </div>
                        <div>
                            <div class="font-bold text-lg">{{ evolucion.id ? 'Editar Propuesta' : 'Nueva Propuesta' }}
                            </div>
                            <div class="text-sm text-surface-500">Completa los detalles para evolusionar el sistema
                            </div>
                        </div>
                    </div>
                </template>

                <div class="flex flex-col gap-5 mt-2 relative z-10">
                    <!-- Título y Categoría -->
                    <div class="flex flex-col gap-4">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label for="categoria"
                                    class="block font-medium mb-1 text-surface-600 dark:text-surface-300">Categoría</label>
                                <Select id="categoria" v-model="evolucion.categoria" :options="categorias"
                                    optionLabel="label" optionValue="value" placeholder="Seleccione Categoría" fluid
                                    class="w-full">
                                    <template #value="slotProps">
                                        <div v-if="slotProps.value" class="flex items-center gap-2">
                                            <Tag :severity="getCategoriaSeverity(slotProps.value)"
                                                class="w-2 h-2 p-0 rounded-full"></Tag>
                                            <div>{{categorias.find(c => c.value === slotProps.value)?.label}}</div>
                                        </div>
                                        <span v-else>{{ slotProps.placeholder }}</span>
                                    </template>
                                    <template #option="slotProps">
                                        <div class="flex items-center gap-2">
                                            <Tag :severity="getCategoriaSeverity(slotProps.option.value)"
                                                class="w-2 h-2 p-0 rounded-full"></Tag>
                                            <div>{{ slotProps.option.label }}</div>
                                        </div>
                                    </template>
                                </Select>
                            </div>
                            <div>
                                <label for="titulo"
                                    class="block font-medium mb-1 text-surface-600 dark:text-surface-300">Título
                                    Corto</label>
                                <IconField>
                                    <InputIcon class="pi pi-tag" />
                                    <InputText id="titulo" v-model.trim="evolucion.titulo" required="true" autofocus
                                        :invalid="submitted && !evolucion.titulo" fluid
                                        placeholder="Ej: Error en login..." />
                                </IconField>
                                <small class="text-red-500" v-if="submitted && !evolucion.titulo">El título es
                                    requerido.</small>
                            </div>
                        </div>

                        <div>
                            <label for="descripcion"
                                class="block font-medium mb-1 text-surface-600 dark:text-surface-300">Descripción
                                General</label>
                            <Textarea id="descripcion" v-model="evolucion.descripcion" required="true" rows="3" fluid
                                placeholder="Describe brevemente la situación..." class="resize-none" />
                        </div>
                    </div>

                    <!-- Sección Dinámica con Transición -->
                    <div
                        class="bg-surface-50 dark:bg-surface-900 p-4 rounded-lg border border-surface-200 dark:border-surface-700">
                        <Transition name="fade" mode="out-in">
                            <div v-if="evolucion.categoria === 'ERROR'" key="error" class="flex flex-col gap-4">
                                <div class="flex items-center gap-2 text-primary font-medium">
                                    <i class="pi pi-exclamation-circle"></i>
                                    <span>Detalles del Error (Bug)</span>
                                </div>
                                <div>
                                    <label for="modulo" class="block text-sm font-medium mb-1">Módulo / Pantalla
                                        Afectada</label>
                                    <IconField>
                                        <InputIcon class="pi pi-desktop" />
                                        <InputText id="modulo" v-model="evolucion.datos_extra.modulo_afectado" fluid
                                            placeholder="Ej: Mando Central > Usuarios" />
                                    </IconField>
                                </div>
                                <div>
                                    <label for="pasos" class="block text-sm font-medium mb-1">Pasos para
                                        reproducir</label>
                                    <Textarea id="pasos" v-model="evolucion.datos_extra.pasos_reproducir" rows="3" fluid
                                        placeholder="1. Entrar a... 2. Hacer click en..." />
                                </div>
                            </div>

                            <div v-else-if="['VISUAL', 'COMPORTAMIENTO'].includes(evolucion.categoria)" key="visual"
                                class="flex flex-col gap-4">
                                <div class="flex items-center gap-2 text-info font-medium text-blue-500">
                                    <i class="pi pi-palette"></i>
                                    <span>Propuesta de Mejora</span>
                                </div>
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label for="actual" class="block text-sm font-medium mb-1">Situación
                                            Actual</label>
                                        <Textarea id="actual" v-model="evolucion.datos_extra.situacion_actual" rows="4"
                                            fluid placeholder="Cómo se ve/comporta ahora..."
                                            class="bg-red-50 dark:bg-red-900/10" />
                                    </div>
                                    <div>
                                        <label for="propuesto" class="block text-sm font-medium mb-1">Cambio
                                            Propuesto</label>
                                        <Textarea id="propuesto" v-model="evolucion.datos_extra.cambio_propuesto"
                                            rows="4" fluid placeholder="Cómo debería verse/comportarse..."
                                            class="bg-green-50 dark:bg-green-900/10" />
                                    </div>
                                </div>
                            </div>

                            <div v-else-if="['FUNCIONALIDAD', 'CREAR'].includes(evolucion.categoria)"
                                key="funcionalidad" class="flex flex-col gap-4">
                                <div class="flex items-center gap-2 text-success font-medium text-green-500">
                                    <i class="pi pi-bolt"></i>
                                    <span>Nueva Característica</span>
                                </div>
                                <div>
                                    <label for="beneficio" class="block text-sm font-medium mb-1">Descripción detallada
                                        y
                                        Beneficio</label>
                                    <Textarea id="beneficio" v-model="evolucion.datos_extra.beneficio" rows="5" fluid
                                        placeholder="Explica qué se necesita y qué valor aporta al negocio..." />
                                </div>
                            </div>
                        </Transition>
                    </div>

                    <!-- Estado (Solo admin/dba en edición) -->
                    <div v-if="evolucion.id && isAdminOrDBA"
                        class="border-t border-surface-200 dark:border-surface-700 pt-4 mt-2">
                        <label for="estado" class="block font-bold mb-2 text-primary">Estado del Ticket
                            (Administrativo)</label>
                        <Select id="estado" v-model="evolucion.estado" :options="estados" optionLabel="label"
                            optionValue="value" placeholder="Seleccione Estado" fluid class="w-full">
                            <template #option="slotProps">
                                <Tag :value="slotProps.option.label"
                                    :severity="getBadgeSeverity(slotProps.option.value)" />
                            </template>
                            <template #value="slotProps">
                                <Tag v-if="slotProps.value"
                                    :value="estados.find(e => e.value === slotProps.value)?.label"
                                    :severity="getBadgeSeverity(slotProps.value)" />
                                <span v-else>{{ slotProps.placeholder }}</span>
                            </template>
                        </Select>
                    </div>
                </div>

                <template #footer>
                    <div class="relative z-10 flex justify-end gap-2">
                        <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" severity="secondary" />
                        <Button label="Guardar Propuesta" icon="pi pi-check" @click="saveEvolucion"
                            severity="primary" />
                    </div>
                </template>
            </Dialog>
        </div>
    </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>
