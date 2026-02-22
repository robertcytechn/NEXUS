<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { getUser, hasRoleAccess } from '@/service/api';

import {
    getTareasEspeciales,
    createTareaEspecial,
    updateTareaEspecial
} from '@/service/tareasEspecialesService';

import api from '@/service/api';

const toast = useToast();
const confirm = useConfirm();
const user = getUser();

const tareas = ref([]);
const casinos = ref([]);
const loading = ref(false);

const dt = ref();
const toolbarRef = ref();
useResponsiveDataTable(dt);

const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});

watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Roles y Permisos
const canEditCreate = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA']));
const isTech = computed(() => hasRoleAccess(['TECNICO', 'SUP SISTEMAS']));

const columnas = ref([
    { field: 'folio', label: 'Folio', visible: true },
    { field: 'titulo', label: 'Título', visible: true },
    { field: 'casino_nombre', label: 'Casino', visible: true },
    { field: 'prioridad', label: 'Prioridad', visible: true },
    { field: 'estatus', label: 'Estado', visible: true },
    { field: 'asignado_a_nombre', label: 'Técnico', visible: true },
    { field: 'fecha_apertura', label: 'Fecha Apertura', visible: true }
]);

const esColumnaVisible = (field) => {
    const columna = columnas.value.find(c => c.field === field);
    return columna ? columna.visible : true;
};

// Formateadores
const formatearFecha = (fecha) => {
    if (!fecha) return '---';
    return new Date(fecha).toLocaleString('es-MX', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit'
    });
};

const prioridadColor = (prioridad) => {
    const mapa = {
        'baja': 'success',
        'media': 'info',
        'alta': 'warning',
        'critica': 'danger'
    };
    return mapa[prioridad] || 'secondary';
};

const estadoColor = (estado) => {
    const mapa = {
        'pendiente': 'secondary',
        'en_curso': 'info',
        'completada': 'success',
        'cancelada': 'danger'
    };
    return mapa[estado] || 'secondary';
};

// Carga Inicial
const cargarDatos = async () => {
    loading.value = true;
    try {
        const [resTareas, resCasinos] = await Promise.all([
            getTareasEspeciales(),
            api.get('casinos/lista/')
        ]);

        if (resTareas.success) {
            // Filtrar tareas por el casino del usuario si no es un rol global
            if (user?.casino) {
                tareas.value = resTareas.data.filter(t => t.casino === user.id_casino || t.casino === user.casino);
            } else {
                tareas.value = resTareas.data;
            }
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Fallo al cargar la información', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// Modal de Creación/Edición
const tareaDialog = ref(false);
const tarea = ref({});
const submitted = ref(false);

const prioridadOpciones = [
    { label: 'Baja', value: 'baja' },
    { label: 'Media', value: 'media' },
    { label: 'Alta', value: 'alta' },
    { label: 'Crítica / Inmediata', value: 'critica' }
];

const estadoOpciones = [
    { label: 'Pendiente', value: 'pendiente' },
    { label: 'En Curso', value: 'en_curso' },
    { label: 'Terminada', value: 'completada' },
    { label: 'Cancelada', value: 'cancelada' }
];

const openNew = () => {
    tarea.value = {
        prioridad: 'media',
        estatus: 'pendiente',
        casino: user?.casino // Asignar casino del usuario
    };
    submitted.value = false;
    tareaDialog.value = true;
};

const editarTarea = (t) => {
    tarea.value = { ...t };
    submitted.value = false;
    tareaDialog.value = true;
};

const closeDialog = () => {
    tareaDialog.value = false;
    submitted.value = false;
};

const saveTarea = async () => {
    submitted.value = true;
    if (tarea.value.titulo?.trim() && tarea.value.descripcion?.trim() && tarea.value.casino) {
        loading.value = true;
        const payload = {
            titulo: tarea.value.titulo,
            descripcion: tarea.value.descripcion,
            casino: tarea.value.casino,
            prioridad: tarea.value.prioridad,
            estatus: tarea.value.estatus,
            resultado_final: tarea.value.resultado_final
        };

        let result;
        if (tarea.value.id) {
            result = await updateTareaEspecial(tarea.value.id, payload);
        } else {
            result = await createTareaEspecial(payload);
        }

        if (result.success) {
            toast.add({ severity: 'success', summary: 'Éxito', detail: 'Tarea guardada correctamente', life: 3000 });
            closeDialog();
            cargarDatos();
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: result.error?.mensaje || 'No se pudo guardar la tarea', life: 3000 });
        }
        loading.value = false;
    }
};

// Lógica Especial Técnicos
const btnTecnicoDialog = ref(false);
const tareaTecnica = ref({});
const atencionSubmitted = ref(false);

const openTecnicoDialog = (t) => {
    tareaTecnica.value = { ...t };
    atencionSubmitted.value = false;
    btnTecnicoDialog.value = true;
};

const procesarTareaTecnica = async () => {
    atencionSubmitted.value = true;

    // Si la está finalizando, debe haber reporte
    if (tareaTecnica.value.estatus === 'completada' && !tareaTecnica.value.resultado_final?.trim()) {
        return;
    }

    loading.value = true;
    const payload = {
        estatus: tareaTecnica.value.estatus,
        resultado_final: tareaTecnica.value.resultado_final
    };

    const res = await updateTareaEspecial(tareaTecnica.value.id, payload);

    if (res.success) {
        toast.add({ severity: 'success', summary: 'Tarea Actualizada', detail: 'Progreso guardado correctamente', life: 3000 });
        btnTecnicoDialog.value = false;
        cargarDatos();
    } else {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo procesar la tarea', life: 3000 });
    }
    loading.value = false;
};


onMounted(() => {
    cargarDatos();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <div class="card">
            <Toast />
            <ConfirmDialog />

            <DataTableToolbar ref="toolbarRef" :dt="dt" :datos="tareas" titulo-reporte="Tareas Especiales"
                nombre-archivo="tareas_especiales" :columnas="columnas" :mostrar-exportacion="true"
                :mostrar-imprimir="true" :mostrar-refrescar="true" :mostrar-selector-columnas="true"
                :mostrar-buscador="true" @refrescar="cargarDatos" v-model:columnas-seleccionadas="columnas">
                <template #acciones-extra>
                    <Button v-if="canEditCreate" icon="pi pi-plus" label="Nueva Tarea" rounded severity="primary"
                        @click="openNew" />
                </template>
            </DataTableToolbar>

            <DataTable ref="dt" :value="tareas" :loading="loading" v-model:filters="filtros"
                :globalFilterFields="['folio', 'titulo', 'casino_nombre', 'asignado_a_nombre']" paginator :rows="10"
                :rowsPerPageOptions="[5, 10, 20]" dataKey="id" filterDisplay="menu" showGridlines stripedRows
                class="datatable-mobile">
                <template #empty>
                    <div class="text-center p-4">No se encontraron tareas especiales.</div>
                </template>
                <template #loading>
                    Cargando información de tareas...
                </template>

                <Column v-if="esColumnaVisible('folio')" field="folio" header="Folio" sortable
                    style="min-width: 8rem" />

                <Column v-if="esColumnaVisible('titulo')" field="titulo" header="Título" sortable
                    style="min-width: 14rem">
                    <template #body="{ data }">
                        <span class="font-bold">{{ data.titulo }}</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('casino_nombre')" field="casino_nombre" header="Casino" sortable
                    style="min-width: 10rem" />

                <Column v-if="esColumnaVisible('prioridad')" field="prioridad" header="Prioridad" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <Tag :value="data.prioridad" :severity="prioridadColor(data.prioridad)" class="uppercase" />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('estatus')" field="estatus" header="Estado" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <Tag :value="data.estatus" :severity="estadoColor(data.estatus)" class="uppercase" />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('asignado_a_nombre')" field="asignado_a_nombre" header="Técnico" sortable
                    style="min-width: 12rem">
                    <template #body="{ data }">
                        <span v-if="data.asignado_a_nombre">{{ data.asignado_a_nombre }}</span>
                        <span v-else class="text-surface-400 italic">No asignado</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('fecha_apertura')" field="fecha_apertura" header="Apertura" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="text-sm">{{ formatearFecha(data.fecha_apertura) }}</div>
                    </template>
                </Column>

                <Column header="Acciones" :exportable="false" style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button v-if="canEditCreate" icon="pi pi-pencil" size="small" severity="info" rounded
                                outlined @click="editarTarea(data)" v-tooltip.top="'Editar (Manager)'" />

                            <!-- Botón Técnico -->
                            <Button v-if="isTech && data.estatus !== 'completada' && data.estatus !== 'cancelada'"
                                icon="pi pi-bolt" size="small" severity="warning" rounded outlined
                                @click="openTecnicoDialog(data)" v-tooltip.top="'Atender Tarea'" />

                            <Button v-if="data.estatus === 'completada'" icon="pi pi-eye" size="small"
                                severity="success" rounded text @click="editarTarea(data)"
                                v-tooltip.top="'Ver Detalles'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <!-- Dialog Administrador / Creador -->
            <Dialog v-model:visible="tareaDialog" :style="{ width: '600px' }"
                :header="tarea.id ? (canEditCreate ? 'Editar Tarea' : 'Detalles de Tarea') : 'Nueva Tarea'"
                :modal="true">
                <div class="flex flex-col gap-4">
                    <div>
                        <label class="block font-bold mb-1">Título</label>
                        <InputText v-model.trim="tarea.titulo" required="true" autofocus
                            :invalid="submitted && !tarea.titulo" fluid :disabled="!canEditCreate" />
                        <small class="text-red-500" v-if="submitted && !tarea.titulo">Requerido.</small>
                    </div>

                    <div>
                        <label class="block font-bold mb-1">Descripción</label>
                        <Textarea v-model="tarea.descripcion" rows="4" fluid :invalid="submitted && !tarea.descripcion"
                            :disabled="!canEditCreate" />
                        <small class="text-red-500" v-if="submitted && !tarea.descripcion">Requerido.</small>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block font-bold mb-1">Casino / Sucursal</label>
                            <InputText :value="user?.casino_nombre" disabled fluid
                                class="bg-surface-100 dark:bg-surface-800" />
                            <small class="text-surface-500">Asignado automáticamente.</small>
                        </div>
                        <div>
                            <label class="block font-bold mb-1">Prioridad</label>
                            <Select v-model="tarea.prioridad" :options="prioridadOpciones" optionLabel="label"
                                optionValue="value" fluid :disabled="!canEditCreate" />
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4" v-if="tarea.id">
                        <div>
                            <label class="block font-bold mb-1">Estado</label>
                            <Select v-model="tarea.estatus" :options="estadoOpciones" optionLabel="label"
                                optionValue="value" fluid :disabled="!canEditCreate" />
                        </div>
                        <div>
                            <label class="block font-bold mb-1">Responsable Actual</label>
                            <InputText :value="tarea.asignado_a_nombre || 'No asignado'" disabled fluid />
                        </div>
                    </div>

                    <div v-if="tarea.id">
                        <label class="block font-bold mb-1">Resultado Final (Opcional)</label>
                        <Textarea v-model="tarea.resultado_final" rows="3" fluid :disabled="!canEditCreate"
                            placeholder="Reporte de finalización..." />
                    </div>
                </div>

                <template #footer>
                    <Button label="Cerrar" icon="pi pi-times" text @click="closeDialog" />
                    <Button v-if="canEditCreate" label="Guardar Tarea" icon="pi pi-check" @click="saveTarea"
                        severity="primary" />
                </template>
            </Dialog>

            <!-- Dialog Modal Exclusivo para Técnicos -->
            <Dialog v-model:visible="btnTecnicoDialog" :style="{ width: '500px' }" header="Atención a Tarea Especial"
                :modal="true">
                <div class="flex flex-col gap-4 p-2 bg-surface-50 dark:bg-surface-800 rounded mb-4">
                    <span class="font-bold text-lg">{{ tareaTecnica.titulo }}</span>
                    <span class="text-surface-600 dark:text-surface-300">{{ tareaTecnica.descripcion }}</span>
                </div>

                <div class="flex flex-col gap-4">
                    <div>
                        <label class="block font-bold mb-1">Nuevo Estado</label>
                        <Select v-model="tareaTecnica.estatus"
                            :options="estadoOpciones.filter(e => e.value !== 'pendiente' && e.value !== 'cancelada')"
                            optionLabel="label" optionValue="value" fluid />
                        <small class="text-surface-500 mt-1">Al cambiar a "En Curso", tu usuario se auto-asignará a esta
                            labor.</small>
                    </div>

                    <div v-if="tareaTecnica.estatus === 'completada'">
                        <label class="block font-bold mb-1">Reporte de Cierre</label>
                        <Textarea v-model="tareaTecnica.resultado_final" rows="4" fluid
                            :invalid="atencionSubmitted && !tareaTecnica.resultado_final"
                            placeholder="Describe lo que se hizo para culminar este trabajo..." />
                        <small class="text-red-500"
                            v-if="atencionSubmitted && !tareaTecnica.resultado_final">Obligatorio al marcar
                            como completada.</small>
                    </div>
                </div>

                <template #footer>
                    <Button label="Cancelar" icon="pi pi-times" text @click="btnTecnicoDialog = false" />
                    <Button label="Guardar Progreso" icon="pi pi-save" @click="procesarTareaTecnica"
                        severity="warning" />
                </template>
            </Dialog>

        </div>
    </div>
</template>
