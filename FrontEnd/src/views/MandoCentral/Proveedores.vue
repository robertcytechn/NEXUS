<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '@/service/api'; import { guardarProveedor } from '@/service/proveedorService'; import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import Chart from 'primevue/chart';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';
import ProveedorFormDialog from '@/components/proveedores/ProveedorFormDialog.vue';
import ProveedorDetalleDialog from '@/components/proveedores/ProveedorDetalleDialog.vue';
import { parseServerError } from '@/utils/parseServerError';

const casinos = ref([]);
const proveedores = ref([]);
const maquinas = ref([]);
const modelos = ref([]);
const loading = ref(false);
const dt = ref(); // Referencia al DataTable
const toolbarRef = ref(); // Referencia al Toolbar

useResponsiveDataTable(dt);
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});
const toast = useToast();
const confirm = useConfirm();

// Estado de los Componentes Inteligentes
const dialogFormVisible = ref(false);
const dialogDetalleVisible = ref(false);
const idProveedorForm = ref(null);
const objProveedorDetalle = ref(null);

// Variables para Gráficas
const chartDataProveedores = ref();
const chartOptionsProveedores = ref();
const chartDataMaquinas = ref();
const chartOptionsMaquinas = ref();
const chartDataModelos = ref();
const chartOptionsModelos = ref();
const chartDataEstado = ref();
const chartOptionsEstado = ref();

// Sincronizar buscador del toolbar con filtros del DataTable
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Columnas configurables
const columnas = ref([
    { field: 'nombre', label: 'Razón Social', visible: true },
    { field: 'casino_nombre', label: 'Casino', visible: true },
    { field: 'username', label: 'Usuario', visible: true },
    { field: 'rfc', label: 'RFC', visible: true },
    { field: 'nombre_contacto_tecnico', label: 'Contacto Técnico', visible: true },
    { field: 'telefono_soporte', label: 'Teléfono Soporte', visible: true },
    { field: 'email_corporativo', label: 'Email Corporativo', visible: true },
    { field: 'email_soporte', label: 'Email Soporte', visible: true },
    { field: 'esta_activo', label: 'Estado', visible: true },
    { field: 'creado_en', label: 'Fecha Registro', visible: true }
]);

// Cargar proveedores desde la API
const cargarProveedores = async () => {
    loading.value = true;
    try {
        const response = await api.get('proveedores/lista/');
        proveedores.value = response.data;
        actualizarGraficas();
    } catch (error) {

        toast.add({ severity: 'error', summary: 'Error', detail: parseServerError(error, 'No se pudo cargar la lista de proveedores'), life: 5000 });
    } finally {
        loading.value = false;
    }
};

// Cargar casinos para el selector
const cargarCasinos = async () => {
    try {
        const response = await api.get('casinos/');
        casinos.value = response.data;
    } catch (error) {

    }
};

// Cargar máquinas para estadísticas
const cargarMaquinas = async () => {
    try {
        const response = await api.get('maquinas/');
        maquinas.value = response.data;
        actualizarGraficas();
    } catch (error) {

    }
};

// Cargar modelos para estadísticas
const cargarModelos = async () => {
    try {
        const response = await api.get('modelos/lista/');
        modelos.value = response.data;
    } catch (error) {

    }
};

// Formatear fecha
const formatearFecha = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleString('es-MX', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// Función para verificar si una columna está visible
const esColumnaVisible = (field) => {
    const columna = columnas.value.find(c => c.field === field);
    return columna ? columna.visible : true;
};

// Lógica para Gráficas
const actualizarGraficas = () => {
    if (!proveedores.value.length) return;

    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--p-text-color') || '#334155';
    const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color') || '#64748b';
    const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color') || '#e2e8f0';

    // Opciones Base para Barras
    const barOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: textColor } }
        },
        scales: {
            x: { ticks: { color: textColorSecondary }, grid: { color: surfaceBorder } },
            y: { ticks: { color: textColorSecondary }, grid: { color: surfaceBorder } }
        }
    };

    // 1. Gráfica: Proveedores por Casino
    const provPorCasino = {};
    proveedores.value.forEach(p => {
        const nombre = p.casino_nombre || 'Sin Asignar';
        provPorCasino[nombre] = (provPorCasino[nombre] || 0) + 1;
    });

    chartDataProveedores.value = {
        labels: Object.keys(provPorCasino),
        datasets: [{
            label: 'Proveedores Asignados',
            data: Object.values(provPorCasino),
            backgroundColor: 'rgba(14, 165, 233, 0.6)', // Sky 500
            borderColor: 'rgba(14, 165, 233, 1)',
            borderWidth: 1
        }]
    };
    chartOptionsProveedores.value = barOptions;

    // 2. Gráfica: Máquinas por Casino (Existencia Física)
    if (maquinas.value.length) {
        const maqPorCasino = {};
        maquinas.value.forEach(m => {
            // Intentar obtener nombre del casino del objeto máquina o buscarlo en el catálogo
            let nombre = m.casino_nombre;
            if (!nombre && m.casino && casinos.value.length) {
                const c = casinos.value.find(c => c.id === m.casino);
                nombre = c ? c.nombre : 'Desconocido';
            }
            nombre = nombre || 'Sin Asignar';
            maqPorCasino[nombre] = (maqPorCasino[nombre] || 0) + 1;
        });

        chartDataMaquinas.value = {
            labels: Object.keys(maqPorCasino),
            datasets: [{
                label: 'Máquinas en Sala',
                data: Object.values(maqPorCasino),
                backgroundColor: 'rgba(234, 179, 8, 0.6)', // Yellow 500
                borderColor: 'rgba(234, 179, 8, 1)',
                borderWidth: 1
            }]
        };
        chartOptionsMaquinas.value = barOptions;
    }

    // 3. Gráfica: Modelos de Máquinas (Top 5)
    if (maquinas.value.length) {
        const maqPorModelo = {};
        maquinas.value.forEach(m => {
            let nombre = m.modelo_nombre;
            // Si no viene el nombre, buscarlo en el catálogo de modelos
            if (!nombre && m.modelo && modelos.value.length) {
                const mod = modelos.value.find(mod => mod.id === m.modelo);
                nombre = mod ? mod.nombre : null;
            }
            nombre = nombre || 'Desconocido';
            maqPorModelo[nombre] = (maqPorModelo[nombre] || 0) + 1;
        });

        const sortedModelos = Object.entries(maqPorModelo)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5);

        chartDataModelos.value = {
            labels: sortedModelos.map(item => item[0]),
            datasets: [{
                label: 'Máquinas por Modelo (Top 5)',
                data: sortedModelos.map(item => item[1]),
                backgroundColor: 'rgba(168, 85, 247, 0.6)', // Purple 500
                borderColor: 'rgba(168, 85, 247, 1)',
                borderWidth: 1
            }]
        };
        chartOptionsModelos.value = barOptions;
    }

    // 3. Gráfica: Estado de Proveedores
    const activos = proveedores.value.filter(p => p.esta_activo).length;
    const inactivos = proveedores.value.length - activos;

    chartDataEstado.value = {
        labels: ['Activos', 'Inactivos'],
        datasets: [{
            data: [activos, inactivos],
            backgroundColor: ['#22c55e', '#ef4444'],
            hoverBackgroundColor: ['#16a34a', '#dc2626']
        }]
    };
    chartOptionsEstado.value = {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
            legend: { position: 'bottom', labels: { color: textColor } }
        }
    };
};

// Acciones Componentes Inteligentes
const openNew = () => {
    idProveedorForm.value = null;
    dialogFormVisible.value = true;
};

const editarProveedor = (data) => {
    idProveedorForm.value = data.id;
    dialogFormVisible.value = true;
};

const verDetalles = (data) => {
    objProveedorDetalle.value = { ...data };
    dialogDetalleVisible.value = true;
};

const onProveedorSaved = async () => {
    // Al guardar exitosamente desde el componente, refrescamos la tabla
    await cargarProveedores();
};

const toggleActivarProveedor = (data) => {
    const accion = data.esta_activo ? 'desactivar' : 'activar';

    confirm.require({
        message: `¿Estás seguro de que deseas ${accion} al proveedor "${data.nombre}"?`,
        header: 'Confirmar Acción',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: {
            label: 'Cancelar',
            severity: 'secondary',
            outlined: true
        },
        acceptProps: {
            label: 'Confirmar',
            severity: data.esta_activo ? 'danger' : 'success'
        },
        accept: async () => {
            loading.value = true;
            try {
                await api.patch(`proveedores/${data.id}/switch-estado/`, {});
                toast.add({ severity: 'success', summary: 'Éxito', detail: `Proveedor ${accion === 'activar' ? 'activado' : 'desactivado'} correctamente`, life: 3000 });
                cargarProveedores();
            } catch (error) {

                toast.add({ severity: 'error', summary: 'Error', detail: parseServerError(error, `No se pudo ${accion} el proveedor`), life: 5000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

onMounted(() => {
    cargarProveedores();
    cargarCasinos();
    cargarMaquinas();
    cargarModelos();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <!-- Sección de Estadísticas -->
        <div class="card">
            <div class="font-semibold text-xl mb-4">Métricas de Operación</div>
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-8">
                <!-- Gráfica 1: Proveedores por Casino -->
                <div class="flex flex-col items-center justify-center">
                    <div class="font-semibold mb-2 text-center">Proveedores por Casino</div>
                    <div class="relative w-full h-[200px]">
                        <Chart v-if="chartDataProveedores" type="bar" :data="chartDataProveedores"
                            :options="chartOptionsProveedores" class="h-full w-full" />
                    </div>
                </div>

                <!-- Gráfica 2: Máquinas por Casino -->
                <div class="flex flex-col items-center justify-center">
                    <div class="font-semibold mb-2 text-center">Máquinas por Casino (Carga Física)</div>
                    <div class="relative w-full h-[200px]">
                        <Chart v-if="chartDataMaquinas" type="bar" :data="chartDataMaquinas"
                            :options="chartOptionsMaquinas" class="h-full w-full" />
                        <div v-else class="flex items-center justify-center h-full text-surface-500">Cargando datos...
                        </div>
                    </div>
                </div>

                <!-- Gráfica 3: Top Modelos -->
                <div class="flex flex-col items-center justify-center">
                    <div class="font-semibold mb-2 text-center">Top Modelos</div>
                    <div class="relative w-full h-[200px]">
                        <Chart v-if="chartDataModelos" type="bar" :data="chartDataModelos"
                            :options="chartOptionsModelos" class="h-full w-full" />
                        <div v-else class="flex items-center justify-center h-full text-surface-500">Cargando datos...
                        </div>
                    </div>
                </div>

                <!-- Gráfica 4: Estado de Proveedores -->
                <div class="flex flex-col items-center justify-center">
                    <div class="font-semibold mb-2 text-center">Estado de Proveedores</div>
                    <div class="relative w-full h-[200px] flex justify-center">
                        <Chart v-if="chartDataEstado" type="doughnut" :data="chartDataEstado"
                            :options="chartOptionsEstado" class="h-full w-full" />
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <Toast />
            <ConfirmDialog />

            <!-- Toolbar personalizable -->
            <DataTableToolbar ref="toolbarRef" :dt="dt" :datos="proveedores" titulo-reporte="Gestión de Proveedores"
                nombre-archivo="proveedores" :columnas="columnas" :mostrar-exportacion="true" :mostrar-imprimir="true"
                :mostrar-refrescar="true" :mostrar-selector-columnas="true" :mostrar-buscador="true"
                @refrescar="cargarProveedores" v-model:columnas-seleccionadas="columnas">
                <template #acciones-extra>
                    <Button icon="pi pi-plus" label="Nuevo Proveedor" rounded severity="primary" @click="openNew" />
                </template>
            </DataTableToolbar>

            <DataTable ref="dt" :value="proveedores" :loading="loading" v-model:filters="filtros"
                :globalFilterFields="['nombre', 'rfc', 'nombre_contacto_tecnico', 'email_corporativo', 'email_soporte']"
                paginator :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]" dataKey="id" filterDisplay="menu"
                showGridlines stripedRows class="datatable-mobile">
                <template #empty>
                    <div class="text-center p-4">
                        No se encontraron proveedores registrados.
                    </div>
                </template>

                <template #loading>
                    Cargando información de proveedores...
                </template>

                <Column v-if="esColumnaVisible('nombre')" field="nombre" header="Razón Social" sortable
                    style="min-width: 14rem">
                    <template #body="{ data }">
                        <span class="font-bold">{{ data.nombre }}</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('casino_nombre')" field="casino_nombre" header="Casino" sortable
                    style="min-width: 12rem">
                    <template #body="{ data }">
                        <span class="text-sm">{{ data.casino_nombre || 'N/A' }}</span>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('username')" field="username" header="Usuario" sortable
                    style="min-width: 10rem">
                    <template #body="{ data }">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-user text-surface-500"></i>
                            <span>{{ data.username }}</span>
                        </div>
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('rfc')" field="rfc" header="RFC" sortable style="min-width: 10rem" />

                <Column v-if="esColumnaVisible('nombre_contacto_tecnico')" field="nombre_contacto_tecnico"
                    header="Contacto Técnico" sortable style="min-width: 12rem" />

                <Column v-if="esColumnaVisible('telefono_soporte')" field="telefono_soporte" header="Teléfono Soporte"
                    sortable style="min-width: 10rem" />

                <Column v-if="esColumnaVisible('email_corporativo')" field="email_corporativo"
                    header="Email Corporativo" sortable style="min-width: 14rem" />

                <Column v-if="esColumnaVisible('email_soporte')" field="email_soporte" header="Email Soporte" sortable
                    style="min-width: 14rem" />

                <Column v-if="esColumnaVisible('esta_activo')" field="esta_activo" header="Estado" sortable
                    style="min-width: 8rem">
                    <template #body="{ data }">
                        <Tag :value="data.esta_activo ? 'Activo' : 'Inactivo'"
                            :severity="data.esta_activo ? 'success' : 'danger'" />
                    </template>
                </Column>

                <Column v-if="esColumnaVisible('creado_en')" field="creado_en" header="Fecha Registro" sortable
                    style="min-width: 12rem">
                    <template #body="{ data }">
                        <div class="text-sm">{{ formatearFecha(data.creado_en) }}</div>
                    </template>
                </Column>

                <Column header="Acciones" :exportable="false" style="min-width: 14rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                            <Button icon="pi pi-eye" size="small" severity="secondary" rounded outlined
                                @click="verDetalles(data)" v-tooltip.top="'Ver Detalles'" />
                            <Button icon="pi pi-pencil" size="small" severity="info" rounded outlined
                                @click="editarProveedor(data)" v-tooltip.top="'Editar'" />
                            <Button :icon="data.esta_activo ? 'pi pi-ban' : 'pi pi-check-circle'" size="small"
                                :severity="data.esta_activo ? 'warning' : 'success'" rounded outlined
                                @click="toggleActivarProveedor(data)"
                                v-tooltip.top="data.esta_activo ? 'Desactivar' : 'Activar'" />
                        </div>
                    </template>
                </Column>
            </DataTable>

            <!-- COMPONENTES INTELIGENTES -->
            <ProveedorFormDialog v-model:visible="dialogFormVisible" :proveedorId="idProveedorForm"
                :permitirElegirCasino="true" @saved="onProveedorSaved" />

            <ProveedorDetalleDialog v-model:visible="dialogDetalleVisible" :proveedor="objProveedorDetalle" />
        </div>
    </div>
</template>