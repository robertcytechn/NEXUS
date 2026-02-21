<script setup>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import EvolucionService from '@/service/EvolucionService';
import { getUser } from '@/service/api';


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
    <div class="flex flex-col gap-6 min-h-screen">

        <!-- WELCOME CARD Y ANIMACIÓN DE ADN (Requerimiento 1) -->
        <Card
            class="overflow-hidden bg-gradient-to-r from-surface-0 to-surface-50 dark:from-surface-900 dark:to-surface-800 shadow-xl border-0 border-l-4 border-l-primary p-0">
            <template #content>
                <div class="grid grid-cols-1 md:grid-cols-12 gap-0 items-center min-h-[140px]">
                    <div class="col-span-1 md:col-span-8 p-6 z-10">
                        <h1
                            class="text-3xl font-extrabold text-surface-900 dark:text-surface-0 mb-3 flex items-center gap-3">
                            <i class="pi pi-sparkles text-primary-500 text-3xl"></i> Laboratorio de Evolución NEXUS
                        </h1>
                        <p class="text-surface-600 dark:text-surface-300 text-lg leading-relaxed max-w-2xl">
                            Bienvenido al sistema de mejora continua. Tus reportes y sugerencias alteran positivamente
                            el <strong>código genético</strong> de la plataforma, adaptándola a las nuevas necesidades
                            operativas.
                        </p>
                    </div>
                    <!-- Animación ADN pequeña y elegante CSS-only (Ligera para Móvil) -->
                    <div
                        class="col-span-1 md:col-span-4 h-40 md:h-full w-full relative -mt-6 md:mt-0 flex items-center justify-center opacity-80 pointer-events-none overflow-hidden">
                        <div class="light-dna-container scale-75 md:scale-100">
                            <div class="dna-strand"></div>
                            <div class="dna-strand delay-1"></div>
                            <div class="dna-strand delay-2"></div>
                            <div class="dna-strand delay-3"></div>
                            <div class="dna-strand delay-4"></div>
                        </div>
                    </div>
                </div>
            </template>
        </Card>

        <!-- DATA TABLE CONTENEDOR -->
        <div class="card bg-surface-0 dark:bg-surface-900 shadow-lg border border-surface-200 dark:border-surface-700">
            <Toast />
            <Toolbar class="mb-4 border-none bg-surface-50/50 dark:bg-surface-900/50 p-4 rounded-xl">
                <template v-slot:start>
                    <div class="flex flex-col">
                        <span class="text-xl font-bold">Bitácora de Mutaciones</span>
                        <span class="text-sm text-surface-500">Historial de tickets evolutivos</span>
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

            <!-- DIALOGO CON LAYOUT 2 COLUMNAS (Requerimiento 2) -->
            <Dialog v-model:visible="evolucionDialog" :style="{ width: '900px' }" :breakpoints="{ '960px': '95vw' }"
                :modal="true" class="p-fluid overflow-hidden custom-dialog-no-padding">

                <template #header>
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                            <i class="pi pi-bolt text-primary text-xl"></i>
                        </div>
                        <div>
                            <div class="font-bold text-xl">{{ evolucion.id ? 'Editar Propuesta' : `Nueva Propuesta
                                Evolutiva` }}</div>
                            <div class="text-sm text-surface-500">Cada tecla altera el código.</div>
                        </div>
                    </div>
                </template>

                <!-- LAYOUT 2 COLUMNAS (FormularioIzq | AdnDer) -->
                <div class="grid grid-cols-1 md:grid-cols-12 gap-0">

                    <!-- Animación CSS-only (Arriba en Mobile, Derecha en Desktop) -->
                    <div
                        class="col-span-1 md:col-span-4 order-first md:order-last bg-surface-900 flex items-center justify-center min-h-[160px] md:min-h-full rounded-t-xl md:rounded-t-none md:rounded-r-xl overflow-hidden relative border-l-0 md:border-l-4 border-primary">
                        <div class="absolute inset-0 opacity-80 flex items-center justify-center">
                            <!-- Animación CSS mejorada: Sistema Complejo -->
                            <div class="orbit-container">
                                <div class="orbit ring-1"></div>
                                <div class="orbit ring-2"></div>
                                <div class="orbit ring-3"></div>
                                <div class="core-node">
                                    <i class="pi pi-code text-surface-900 text-2xl"></i>
                                </div>
                            </div>
                        </div>
                        <div class="absolute bottom-4 text-center w-full z-10 pointer-events-none">
                            <div
                                class="text-primary-400 text-xs font-mono tracking-widest backdrop-blur-sm bg-surface-900/50 inline-block px-3 py-1 rounded-full border border-primary-500/30">
                                SISTEMA_RECEPTIVO
                            </div>
                        </div>
                    </div>

                    <!-- Formulario (Izquierda) -->
                    <div class="col-span-1 md:col-span-8 p-5 md:p-6 flex flex-col gap-5">
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
                                <Textarea id="descripcion" v-model="evolucion.descripcion" required="true" rows="3"
                                    fluid placeholder="Describe brevemente la situación..." class="resize-none" />
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
                                        <Textarea id="pasos" v-model="evolucion.datos_extra.pasos_reproducir" rows="3"
                                            fluid placeholder="1. Entrar a... 2. Hacer click en..." />
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
                                            <Textarea id="actual" v-model="evolucion.datos_extra.situacion_actual"
                                                rows="4" fluid placeholder="Cómo se ve/comporta ahora..."
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
                                        <label for="beneficio" class="block text-sm font-medium mb-1">Descripción
                                            detallada
                                            y
                                            Beneficio</label>
                                        <Textarea id="beneficio" v-model="evolucion.datos_extra.beneficio" rows="5"
                                            fluid
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
                </div> <!-- Fin de Grid 2 Columnas -->

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

/* Evitar padding del Dialog default para que el panel negro del ADN llegue al borde derecho */
::v-deep(.custom-dialog-no-padding .p-dialog-content) {
    padding: 0 !important;
}

/* --- Animaciones Ligeras CSS-Only --- */
.light-dna-container {
    display: flex;
    gap: 8px;
    align-items: center;
    height: 100px;
}

.dna-strand {
    width: 6px;
    height: 100%;
    background: linear-gradient(to bottom, var(--p-primary-400), var(--p-primary-600));
    border-radius: 9999px;
    animation: wave 1.5s ease-in-out infinite;
    opacity: 0.7;
}

.delay-1 {
    animation-delay: 0.1s;
}

.delay-2 {
    animation-delay: 0.2s;
}

.delay-3 {
    animation-delay: 0.3s;
}

.delay-4 {
    animation-delay: 0.4s;
}

@keyframes wave {

    0%,
    100% {
        transform: scaleY(0.3);
        opacity: 0.3;
    }

    50% {
        transform: scaleY(1);
        opacity: 1;
    }
}

/* --- Animación Modal Compleja CSS-only --- */
.orbit-container {
    position: relative;
    width: 140px;
    height: 140px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.core-node {
    position: absolute;
    width: 40px;
    height: 40px;
    background: radial-gradient(circle, var(--p-primary-300), var(--p-primary-500));
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 0 15px var(--p-primary-600);
    z-index: 10;
    animation: corePulse 2s infinite ease-in-out alternate;
}

.orbit {
    position: absolute;
    border-radius: 50%;
    border: 2px dashed var(--p-primary-600);
    opacity: 0.6;
}

.ring-1 {
    width: 70px;
    height: 70px;
    border-style: solid;
    border-color: var(--p-primary-400) transparent var(--p-primary-400) transparent;
    animation: spinRight 4s linear infinite;
}

.ring-2 {
    width: 100px;
    height: 100px;
    border-color: transparent var(--p-primary-300) transparent var(--p-primary-500);
    animation: spinLeft 6s linear infinite;
}

.ring-3 {
    width: 130px;
    height: 130px;
    border: 1px solid var(--p-primary-700);
    border-top: 3px solid var(--p-primary-300);
    animation: spinRight 8s linear infinite;
}

@keyframes spinRight {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

@keyframes spinLeft {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(-360deg);
    }
}

@keyframes corePulse {
    0% {
        transform: scale(0.9);
        box-shadow: 0 0 10px var(--p-primary-600);
    }

    100% {
        transform: scale(1.1);
        box-shadow: 0 0 25px var(--p-primary-400);
    }
}
</style>
