<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api from '@/service/api'; import { guardarMaquina } from '@/service/maquinaService'; import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

const maquinas = ref([]);
const casinos = ref([]);
const modelos = ref([]);
const denominaciones = ref([]);
const loading = ref(false);
const dt = ref();
const toolbarRef = ref();

useResponsiveDataTable(dt);
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();
const confirm = useConfirm();
const maquinaDialog = ref(false);
const maquina = ref({});
const submitted = ref(false);

// Opciones de Estado (Hardcoded según modelo Django)
const estados = ref([
    { label: 'Operativa', value: 'OPERATIVA' },
    { label: 'Dañada (Operativa)', value: 'DAÑADA_OPERATIVA' },
    { label: 'Dañada (No Operativa)', value: 'DAÑADA' },
    { label: 'Mantenimiento', value: 'MANTENIMIENTO' },
    { label: 'Observación', value: 'OBSERVACION' },
    { label: 'Pruebas', value: 'PRUEBAS' }
]);

// Choices de ubicación (deben coincidir con el modelo Django)
const pisosChoices = [
    { label: 'Piso 1', value: 'PISO_1' },
    { label: 'Piso 2', value: 'PISO_2' },
    { label: 'Piso 3', value: 'PISO_3' },
    { label: 'Área VIP', value: 'VIP' },
    { label: 'Terraza', value: 'TERRAZA' },
    { label: 'Sótano', value: 'SÓTANO' },
];
const salasChoices = [
    { label: 'Sala A', value: 'SALA_A' },
    { label: 'Sala B', value: 'SALA_B' },
    { label: 'Sala C', value: 'SALA_C' },
    { label: 'Sala D', value: 'SALA_D' },
    { label: 'Sala Principal', value: 'SALA_PRINCIPAL' },
    { label: 'Zona Fumadores', value: 'ZONA_FUMADORES' },
    { label: 'Zona No Fumadores', value: 'ZONA_NO_FUMADORES' },
];

// Sincronizar buscador
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Columnas
const columnas = ref([
    { field: 'uid_sala', label: 'UID Sala', visible: true },
    { field: 'numero_serie', label: 'No. Serie', visible: true },
    { field: 'casino_nombre', label: 'Casino', visible: true },
    { field: 'modelo_nombre', label: 'Modelo', visible: true },
    { field: 'juego', label: 'Juego', visible: true },
    { field: 'ip_maquina', label: 'IP', visible: true },
    { field: 'ubicacion_piso', label: 'Piso', visible: false },
    { field: 'ubicacion_sala', label: 'Sala', visible: false },
    { field: 'estado_actual', label: 'Estado', visible: true },
    { field: 'esta_activo', label: 'Activo', visible: true }
]);

// Cargar Datos Iniciales
const cargarDatos = async () => {
    loading.value = true;
    try {
        const [resMaquinas, resCasinos, resModelos, resProveedores, resDenominaciones] = await Promise.all([
            api.get('maquinas/lista/'),
            api.get('casinos/lista/'),
            api.get('modelos/lista/'),
            api.get('proveedores/lista/'),
            api.get('denominaciones/') // Asumiendo endpoint existente
        ]);

        maquinas.value = resMaquinas.data;
        casinos.value = resCasinos.data;
        denominaciones.value = resDenominaciones.data;

        // Enriquecer modelos con el ID del casino de su proveedor para filtrar
        modelos.value = resModelos.data.map(m => {
            const prov = resProveedores.data.find(p => p.id === m.proveedor);
            return {
                ...m,
                casino_id: prov ? prov.casino : null,
                proveedor_nombre: prov ? prov.nombre : 'N/A'
            };
        });

    } catch (error) {

        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los datos necesarios', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// Filtrar modelos según el casino seleccionado
const modelosFiltrados = computed(() => {
    if (!maquina.value.casino) return [];
    return modelos.value.filter(m => m.casino_id === maquina.value.casino && m.esta_activo);
});

// Helpers
const getEstadoSeverity = (estado) => {
    switch (estado) {
        case 'OPERATIVA': return 'success';
        case 'DAÑADA_OPERATIVA': return 'warn';
        case 'DAÑADA': return 'danger';
        case 'MANTENIMIENTO': return 'info';
        case 'OBSERVACION': return 'secondary';
        case 'PRUEBAS': return 'contrast';
        default: return 'secondary';
    }
};

const esColumnaVisible = (field) => {
    const columna = columnas.value.find(c => c.field === field);
    return columna ? columna.visible : true;
};

// CRUD
const openNew = () => {
    maquina.value = {
        esta_activo: true,
        estado_actual: 'OPERATIVA',
        coordenada_x: 0,
        coordenada_y: 0,
        contador_fallas: 0,
        denominaciones: []
    };
    submitted.value = false;
    maquinaDialog.value = true;
};

const editarMaquina = (data) => {
    maquina.value = { ...data };
    // Asegurar que denominaciones sea un array de IDs para el MultiSelect
    if (maquina.value.denominaciones && maquina.value.denominaciones.length > 0 && typeof maquina.value.denominaciones[0] === 'object') {
        maquina.value.denominaciones = maquina.value.denominaciones.map(d => d.id);
    }

    // Convertir fechas string a Date objects para DatePicker
    if (maquina.value.ultimo_mantenimiento) maquina.value.ultimo_mantenimiento = new Date(maquina.value.ultimo_mantenimiento);
    if (maquina.value.fecha_vencimiento_licencia) maquina.value.fecha_vencimiento_licencia = new Date(maquina.value.fecha_vencimiento_licencia);

    maquinaDialog.value = true;
};

const hideDialog = () => {
    maquinaDialog.value = false;
    submitted.value = false;
};

const saveMaquina = async () => {
    submitted.value = true;

    if (maquina.value.uid_sala?.trim() &&
        maquina.value.numero_serie?.trim() &&
        maquina.value.casino &&
        maquina.value.modelo &&
        maquina.value.ubicacion_piso &&
        maquina.value.ubicacion_sala &&
        maquina.value.coordenada_x != null &&
        maquina.value.coordenada_y != null) {

        loading.value = true;

        const esEdicion = !!maquina.value.id;
        const resultado = await guardarMaquina(maquina.value, esEdicion);

        if (!resultado.exito) {
            toast.add({
                severity: 'error',
                summary: resultado.error,
                detail: resultado.detalle,
                life: 5000
            });
            loading.value = false;
            return;
        }

        toast.add({
            severity: 'success',
            summary: 'Éxito',
            detail: resultado.mensaje,
            life: 3000
        });

        maquinaDialog.value = false;
        maquina.value = {};
        cargarDatos();
        loading.value = false;
    }
};

const toggleActivarMaquina = (data) => {
    const accion = data.esta_activo ? 'desactivar' : 'activar';
    confirm.require({
        message: `¿Estás seguro de que deseas ${accion} la máquina "${data.uid_sala}"?`,
        header: 'Confirmar Acción',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: { label: 'Cancelar', severity: 'secondary', outlined: true },
        acceptProps: { label: 'Confirmar', severity: data.esta_activo ? 'danger' : 'success' },
        accept: async () => {
            loading.value = true;
            try {
                await api.patch(`maquinas/${data.id}/switch-estado/`, {});
                toast.add({ severity: 'success', summary: 'Éxito', detail: `Máquina ${accion === 'activar' ? 'activada' : 'desactivada'} correctamente`, life: 3000 });
                cargarDatos();
            } catch (error) {
                toast.add({ severity: 'error', summary: 'Error', detail: `No se pudo ${accion} la máquina`, life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
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

            <DataTableToolbar ref="toolbarRef" :dt="dt" :datos="maquinas" titulo-reporte="Inventario de Máquinas"
                nombre-archivo="maquinas" :columnas="columnas" @refrescar="cargarDatos"
                v-model:columnas-seleccionadas="columnas">
                <template #acciones-extra>
                    <Button icon="pi pi-plus" label="Nueva Máquina" rounded severity="primary" @click="openNew" />
                </template>
            </DataTableToolbar>

            <DataTable ref="dt" :value="maquinas" :loading="loading" v-model:filters="filtros"
                :globalFilterFields="['uid_sala', 'numero_serie', 'casino_nombre', 'modelo_nombre', 'juego', 'ip_maquina']"
                paginator :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]" dataKey="id" showGridlines stripedRows
                class="datatable-mobile">
                <template #empty>
                    <div class="text-center p-4">No se encontraron máquinas registradas.</div>
                </template>

                <Column v-if="esColumnaVisible('uid_sala')" field="uid_sala" header="UID Sala" sortable
                    style="min-width: 8rem">
                    <template #body="{ data }"><span class="font-bold">{{ data.uid_sala }}</span></template>
                </Column>
                <Column v-if="esColumnaVisible('numero_serie')" field="numero_serie" header="No. Serie" sortable
                    style="min-width: 10rem" />
                <Column v-if="esColumnaVisible('casino_nombre')" field="casino_nombre" header="Casino" sortable
                    style="min-width: 12rem" />
                <Column v-if="esColumnaVisible('modelo_nombre')" field="modelo_nombre" header="Modelo" sortable
                    style="min-width: 12rem" />
                <Column v-if="esColumnaVisible('juego')" field="juego" header="Juego" sortable
                    style="min-width: 12rem" />
                <Column v-if="esColumnaVisible('ip_maquina')" field="ip_maquina" header="IP" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }"><span class="font-mono text-sm">{{ data.ip_maquina || 'N/A'
                            }}</span></template>
                </Column>
                <Column v-if="esColumnaVisible('ubicacion_piso')" field="ubicacion_piso" header="Piso" sortable
                    style="min-width: 8rem" />
                <Column v-if="esColumnaVisible('ubicacion_sala')" field="ubicacion_sala" header="Sala" sortable
                    style="min-width: 10rem" />

                <Column v-if="esColumnaVisible('estado_actual')" field="estado_actual" header="Estado Técnico" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <Tag :value="data.estado_actual" :severity="getEstadoSeverity(data.estado_actual)" />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('esta_activo')" field="esta_activo" header="Activo" sortable
                    style="min-width: 6rem">
                    <template #body="{ data }">
                        <i
                            :class="[data.esta_activo ? 'pi pi-check-circle text-green-500' : 'pi pi-times-circle text-red-500']"></i>
                    </template>
                </Column>

                <Column header="Acciones" :exportable="false" style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button icon="pi pi-pencil" size="small" severity="info" rounded outlined
                                @click="editarMaquina(data)" v-tooltip.top="'Editar'" />
                            <Button :icon="data.esta_activo ? 'pi pi-ban' : 'pi pi-check-circle'" size="small"
                                :severity="data.esta_activo ? 'warning' : 'success'" rounded outlined
                                @click="toggleActivarMaquina(data)"
                                v-tooltip.top="data.esta_activo ? 'Desactivar' : 'Activar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <Dialog v-model:visible="maquinaDialog" :style="{ width: '800px' }" header="Detalles de la Máquina"
                :modal="true">
                <div class="flex flex-col gap-6">
                    <!-- Sección 1: Identificación y Ubicación -->
                    <div
                        class="font-bold text-lg text-surface-500 border-b border-surface-200 dark:border-surface-700 pb-2">
                        Identificación y Ubicación</div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="casino" class="block font-bold mb-3">Casino</label>
                            <Select id="casino" v-model="maquina.casino" :options="casinos" optionLabel="nombre"
                                optionValue="id" placeholder="Seleccione Casino" fluid
                                :invalid="submitted && !maquina.casino" @change="maquina.modelo = null" />
                            <small class="text-red-500" v-if="submitted && !maquina.casino">Requerido.</small>
                        </div>
                        <div>
                            <label for="modelo" class="block font-bold mb-3">Modelo</label>
                            <Select id="modelo" v-model="maquina.modelo" :options="modelosFiltrados"
                                optionLabel="nombre_modelo" optionValue="id" placeholder="Seleccione Modelo" fluid
                                :invalid="submitted && !maquina.modelo" :disabled="!maquina.casino" />
                            <small class="text-red-500" v-if="submitted && !maquina.modelo">Requerido.</small>
                            <small v-if="!maquina.casino" class="text-surface-500">Seleccione un casino primero.</small>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label for="uid_sala" class="block font-bold mb-3">UID Sala (Ej. A01)</label>
                            <InputText id="uid_sala" v-model.trim="maquina.uid_sala" required="true"
                                :invalid="submitted && !maquina.uid_sala" fluid />
                            <small class="text-red-500" v-if="submitted && !maquina.uid_sala">Requerido.</small>
                        </div>
                        <div>
                            <label for="numero_serie" class="block font-bold mb-3">No. Serie</label>
                            <InputText id="numero_serie" v-model.trim="maquina.numero_serie" required="true"
                                :invalid="submitted && !maquina.numero_serie" fluid />
                            <small class="text-red-500" v-if="submitted && !maquina.numero_serie">Requerido.</small>
                        </div>
                        <div>
                            <label for="ip_maquina" class="block font-bold mb-3">Dirección IP</label>
                            <InputText id="ip_maquina" v-model.trim="maquina.ip_maquina" fluid
                                placeholder="172.16.xx.xx" />
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="ubicacion_piso" class="block font-bold mb-3">Piso / Área</label>
                            <Select id="ubicacion_piso" v-model="maquina.ubicacion_piso" :options="pisosChoices"
                                optionLabel="label" optionValue="value" placeholder="Seleccione piso" showClear fluid
                                :invalid="submitted && !maquina.ubicacion_piso" />
                            <small class="text-red-500" v-if="submitted && !maquina.ubicacion_piso">Requerido.</small>
                        </div>
                        <div>
                            <label for="ubicacion_sala" class="block font-bold mb-3">Sala / Sección</label>
                            <Select id="ubicacion_sala" v-model="maquina.ubicacion_sala" :options="salasChoices"
                                optionLabel="label" optionValue="value" placeholder="Seleccione sala" showClear fluid
                                :invalid="submitted && !maquina.ubicacion_sala" />
                            <small class="text-red-500" v-if="submitted && !maquina.ubicacion_sala">Requerido.</small>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block font-bold mb-3">Coordenadas (X, Y)</label>
                            <div class="flex gap-2">
                                <InputNumber id="coordenada_x" name="coordenada_x" v-model="maquina.coordenada_x"
                                    showButtons :min="0" placeholder="X" fluid
                                    :invalid="submitted && maquina.coordenada_x == null" />
                                <InputNumber id="coordenada_y" name="coordenada_y" v-model="maquina.coordenada_y"
                                    showButtons :min="0" placeholder="Y" fluid
                                    :invalid="submitted && maquina.coordenada_y == null" />
                            </div>
                            <small class="text-red-500"
                                v-if="submitted && (maquina.coordenada_x == null || maquina.coordenada_y == null)">Ambas
                                coordenadas
                                son requeridas.</small>
                        </div>
                        <div>
                            <label for="juego" class="block font-bold mb-3">Juego / Título</label>
                            <InputText id="juego" v-model="maquina.juego" fluid />
                        </div>
                    </div>

                    <!-- Sección 2: Detalles Técnicos -->
                    <div
                        class="font-bold text-lg text-surface-500 border-b border-surface-200 dark:border-surface-700 pb-2 mt-2">
                        Detalles Técnicos</div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="estado_actual" class="block font-bold mb-3">Estado Actual</label>
                            <Select id="estado_actual" v-model="maquina.estado_actual" :options="estados"
                                optionLabel="label" optionValue="value" fluid />
                        </div>
                        <div>
                            <label for="denominaciones" class="block font-bold mb-3">Denominaciones</label>
                            <MultiSelect id="denominaciones" v-model="maquina.denominaciones" :options="denominaciones"
                                optionLabel="etiqueta" optionValue="id" placeholder="Seleccione Denominaciones"
                                display="chip" fluid />
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label for="contador_fallas" class="block font-bold mb-3">Contador Fallas</label>
                            <InputNumber id="contador_fallas" v-model="maquina.contador_fallas" showButtons :min="0"
                                fluid />
                        </div>
                        <div>
                            <label for="ultimo_mantenimiento" class="block font-bold mb-3">Último Mantenimiento</label>
                            <DatePicker id="ultimo_mantenimiento" v-model="maquina.ultimo_mantenimiento"
                                dateFormat="yy-mm-dd" showIcon fluid />
                        </div>
                        <div>
                            <label for="fecha_vencimiento_licencia" class="block font-bold mb-3">Vencimiento
                                Licencia</label>
                            <DatePicker id="fecha_vencimiento_licencia" v-model="maquina.fecha_vencimiento_licencia"
                                dateFormat="yy-mm-dd" showIcon fluid />
                        </div>
                    </div>

                    <div class="flex items-center mt-2">
                        <Checkbox v-model="maquina.esta_activo" :binary="true" inputId="esta_activo" />
                        <label for="esta_activo" class="ml-2">¿Máquina Activa en Sistema?</label>
                    </div>
                </div>
                <template #footer>
                    <Button label="Cancelar" icon="pi pi-times" text @click="hideDialog" />
                    <Button label="Guardar" icon="pi pi-check" @click="saveMaquina" />
                </template>
            </Dialog>
        </div>
    </div>
</template>