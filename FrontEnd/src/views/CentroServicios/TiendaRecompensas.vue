<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { getUser } from '@/service/api';
import { tiendaGerencia } from '@/service/wikiService';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

// ─── Usuario y permisos ───────────────────────────────────────────────────────
const usuario  = computed(() => getUser());
const rol      = computed(() => usuario.value?.rol_nombre || '');
const esGerencia = computed(() => rol.value === 'GERENCIA'|| rol.value === 'ADMINISTRADOR' || rol.value === 'BD ADMIN');

const toast   = useToast();
const confirm = useConfirm();

// ─── Estado ───────────────────────────────────────────────────────────────────
const recompensas   = ref([]);
const canjes        = ref([]);
const loading       = ref(false);
const loadingCanjes = ref(false);
const dt            = ref();
const dtCanjes      = ref();
const toolbarRef    = ref();
const tabActivo     = ref(0); // 0=Recompensas, 1=Canjes

useResponsiveDataTable(dt);

const filtros       = ref({ global: { value: null, matchMode: 'contains' } });
const filtrosCanjes = ref({ global: { value: null, matchMode: 'contains' } });

// ─── Estadísticas ─────────────────────────────────────────────────────────────
const stats = computed(() => ({
    total:     recompensas.value.length,
    activas:   recompensas.value.filter(r => r.activo).length,
    inactivas: recompensas.value.filter(r => !r.activo).length,
    canjesPendientes: canjes.value.filter(c => c.estado === 'pendiente').length,
}));

// ─── Dialog CRUD ──────────────────────────────────────────────────────────────
const dialogRecompensa = ref(false);
const loadingGuardar   = ref(false);
const submitted        = ref(false);
const modoEdicion      = ref(false);

const recompensaVacia = () => ({
    titulo:        '',
    descripcion:   '',
    costo_puntos:  50,
    activo:        true,
    stock:         null,
});

const form = ref(recompensaVacia());

// ─── Dialog: nota de entrega de canje ─────────────────────────────────────────
const dialogEntrega      = ref(false);
const canjeSeleccionado  = ref(null);
const notaEntrega        = ref('');
const loadingEntrega     = ref(false);

// ─── Columnas ─────────────────────────────────────────────────────────────────
const columnas = ref([
    { field: 'titulo',          label: 'Recompensa',       visible: true  },
    { field: 'descripcion',     label: 'Descripción',      visible: true  },
    { field: 'costo_puntos',    label: 'Costo (pts)',      visible: true  },
    { field: 'stock',           label: 'Stock',            visible: true  },
    { field: 'activo',          label: 'Estado',           visible: true  },
    { field: 'creado_en',       label: 'Creada el',        visible: false },
]);

const esColumnaVisible = (f) => columnas.value.find(c => c.field === f)?.visible ?? true;

// ─── Sincronizar buscador ─────────────────────────────────────────────────────
watch(() => toolbarRef.value?.busquedaGlobal, (v) => {
    if (filtros.value.global) filtros.value.global.value = v;
}, { deep: true });

// ─── Carga de datos ───────────────────────────────────────────────────────────
const cargarRecompensas = async () => {
    loading.value = true;
    try {
        const { data } = await tiendaGerencia.listarRecompensas();
        recompensas.value = data;
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.error || 'No se pudieron cargar las recompensas', life: 4000 });
    } finally {
        loading.value = false;
    }
};

const cargarCanjes = async () => {
    loadingCanjes.value = true;
    try {
        const { data } = await tiendaGerencia.historialCanjes();
        canjes.value = data.canjes || [];
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.error || 'No se pudieron cargar los canjes', life: 4000 });
    } finally {
        loadingCanjes.value = false;
    }
};

// ─── CRUD Recompensas ─────────────────────────────────────────────────────────
const abrirNueva = () => {
    form.value = recompensaVacia();
    modoEdicion.value = false;
    submitted.value = false;
    dialogRecompensa.value = true;
};

const abrirEditar = (item) => {
    form.value = { ...item };
    modoEdicion.value = true;
    submitted.value = false;
    dialogRecompensa.value = true;
};

const guardarRecompensa = async () => {
    submitted.value = true;
    if (!form.value.titulo?.trim() || !form.value.descripcion?.trim() || !form.value.costo_puntos) {
        toast.add({ severity: 'warn', summary: 'Campos requeridos', detail: 'Completa título, descripción y costo de puntos.', life: 3000 });
        return;
    }
    loadingGuardar.value = true;
    try {
        if (modoEdicion.value) {
            await tiendaGerencia.editarRecompensa(form.value.id, form.value);
            toast.add({ severity: 'success', summary: 'Actualizada', detail: `"${form.value.titulo}" fue actualizada.`, life: 3000 });
        } else {
            await tiendaGerencia.crearRecompensa(form.value);
            toast.add({ severity: 'success', summary: 'Creada', detail: `"${form.value.titulo}" fue agregada a la tienda.`, life: 3000 });
        }
        dialogRecompensa.value = false;
        cargarRecompensas();
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.error || 'No se pudo guardar la recompensa', life: 4000 });
    } finally {
        loadingGuardar.value = false;
    }
};

const confirmarEliminar = (item) => {
    confirm.require({
        message: `¿Eliminar la recompensa "${item.titulo}"? Esta acción es permanente.`,
        header: 'Eliminar Recompensa',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: { label: 'Cancelar', severity: 'secondary', outlined: true },
        acceptProps: { label: 'Eliminar', severity: 'danger' },
        accept: async () => {
            loading.value = true;
            try {
                await tiendaGerencia.eliminar(item.id);
                toast.add({ severity: 'success', summary: 'Eliminada', detail: `"${item.titulo}" fue eliminada.`, life: 3000 });
                cargarRecompensas();
            } catch (e) {
                toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.error || 'No se pudo eliminar', life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

const toggleActivo = async (item) => {
    loading.value = true;
    try {
        const { data } = await tiendaGerencia.toggleActivo(item.id);
        toast.add({ severity: 'success', summary: 'Actualizado', detail: data.mensaje, life: 3000 });
        cargarRecompensas();
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.error || 'No se pudo cambiar estado', life: 3000 });
        loading.value = false;
    }
};

// ─── Gestión de canjes ────────────────────────────────────────────────────────
const abrirEntrega = (canje) => {
    canjeSeleccionado.value = canje;
    notaEntrega.value = '';
    dialogEntrega.value = true;
};

const confirmarEntrega = async () => {
    loadingEntrega.value = true;
    try {
        await tiendaGerencia.entregarCanje(
            canjeSeleccionado.value.recompensa,
            canjeSeleccionado.value.id,
            { nota_gerencia: notaEntrega.value }
        );
        toast.add({ severity: 'success', summary: '✅ Entregado', detail: `Canje de ${canjeSeleccionado.value.usuario_nombre} marcado como entregado.`, life: 4000 });
        dialogEntrega.value = false;
        cargarCanjes();
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.error || 'No se pudo registrar la entrega', life: 4000 });
    } finally {
        loadingEntrega.value = false;
    }
};

// ─── Helpers ─────────────────────────────────────────────────────────────────
const formatFecha = (f) => f
    ? new Date(f).toLocaleString('es-MX', { year: 'numeric', month: '2-digit', day: '2-digit' })
    : 'N/A';

const getCanjeSeverity = (estado) => ({
    pendiente:  'warn',
    entregado:  'success',
    cancelado:  'danger',
}[estado] || 'secondary');

// ─── Tab switch ───────────────────────────────────────────────────────────────
watch(tabActivo, (val) => {
    if (val === 1 && canjes.value.length === 0) cargarCanjes();
});

onMounted(cargarRecompensas);
</script>

<template>
    <div class="flex flex-col gap-6">
        <Toast />
        <ConfirmDialog />

        <!-- ── Acceso denegado ──────────────────────────────────────────── -->
        <div v-if="!esGerencia" class="card text-center py-12">
            <i class="pi pi-lock text-5xl text-surface-300 mb-4 block" />
            <h2 class="text-xl font-semibold text-surface-500">Acceso Restringido</h2>
            <p class="text-surface-400">Solo el personal de Gerencia puede acceder a la Tienda de Recompensas.</p>
        </div>

        <template v-else>
            <!-- ── Encabezado ─────────────────────────────────────────── -->
            <div class="flex flex-col md:flex-row md:items-center gap-4 justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 rounded-xl bg-yellow-100 dark:bg-yellow-900 flex items-center justify-center">
                        <span class="text-2xl">🏆</span>
                    </div>
                    <div>
                        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0 m-0">
                            Tienda de Recompensas
                        </h1>
                        <p class="text-surface-500 text-sm mt-1 m-0">
                            Gestiona los premios de gamificación disponibles para los técnicos.
                        </p>
                    </div>
                </div>
            </div>

            <!-- ── Tarjetas de estadísticas ────────────────────────────── -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="card !p-4 border-l-4 border-l-surface-300">
                    <div class="text-3xl font-bold text-surface-700 dark:text-surface-200">{{ stats.total }}</div>
                    <div class="text-sm text-surface-500 mt-1">Total Recompensas</div>
                </div>
                <div class="card !p-4 border-l-4 border-l-green-500">
                    <div class="text-3xl font-bold text-green-600">{{ stats.activas }}</div>
                    <div class="text-sm text-surface-500 mt-1">Activas (visibles)</div>
                </div>
                <div class="card !p-4 border-l-4 border-l-surface-400">
                    <div class="text-3xl font-bold text-surface-400">{{ stats.inactivas }}</div>
                    <div class="text-sm text-surface-500 mt-1">Desactivadas</div>
                </div>
                <div class="card !p-4 border-l-4 border-l-orange-500 cursor-pointer hover:shadow-md transition-shadow" @click="tabActivo = 1">
                    <div class="text-3xl font-bold text-orange-500">{{ stats.canjesPendientes }}</div>
                    <div class="text-sm text-surface-500 mt-1">
                        Canjes Pendientes
                        <Badge v-if="stats.canjesPendientes > 0" :value="stats.canjesPendientes" severity="warn" class="ml-2" />
                    </div>
                </div>
            </div>

            <!-- ── Tabs ───────────────────────────────────────────────── -->
            <div class="flex gap-2 border-b border-surface-200 dark:border-surface-700 pb-2">
                <Button
                    label="🎁 Recompensas"
                    :severity="tabActivo === 0 ? 'primary' : 'secondary'"
                    :outlined="tabActivo !== 0"
                    size="small"
                    @click="tabActivo = 0"
                />
                <Button
                    label="📦 Historial de Canjes"
                    :severity="tabActivo === 1 ? 'primary' : 'secondary'"
                    :outlined="tabActivo !== 1"
                    size="small"
                    @click="tabActivo = 1"
                />
            </div>

            <!-- ═════════════════════════════════════════════════════════ -->
            <!-- TAB 0: Gestión de Recompensas                             -->
            <!-- ═════════════════════════════════════════════════════════ -->
            <div v-if="tabActivo === 0" class="card">
                <DataTableToolbar
                    ref="toolbarRef"
                    :dt="dt"
                    :datos="recompensas"
                    titulo-reporte="Tienda de Recompensas"
                    nombre-archivo="recompensas_gamificacion"
                    :columnas="columnas"
                    :mostrar-exportacion="true"
                    :mostrar-imprimir="true"
                    :mostrar-refrescar="true"
                    :mostrar-selector-columnas="true"
                    :mostrar-buscador="true"
                    @refrescar="cargarRecompensas"
                    v-model:columnas-seleccionadas="columnas"
                >
                    <template #acciones-extra>
                        <Button icon="pi pi-plus" label="Nueva Recompensa" rounded severity="primary" @click="abrirNueva" />
                    </template>
                </DataTableToolbar>

                <DataTable
                    ref="dt"
                    :value="recompensas"
                    :loading="loading"
                    v-model:filters="filtros"
                    :globalFilterFields="['titulo', 'descripcion']"
                    paginator :rows="10" :rowsPerPageOptions="[5,10,25]"
                    dataKey="id" showGridlines stripedRows class="datatable-mobile"
                >
                    <template #empty>
                        <div class="text-center p-6 text-surface-400">
                            <span class="text-4xl mb-3 block">🎁</span>
                            Aún no hay recompensas. Crea la primera.
                        </div>
                    </template>

                    <!-- Recompensa -->
                    <Column v-if="esColumnaVisible('titulo')" field="titulo" header="Recompensa" sortable style="min-width:14rem">
                        <template #body="{ data }">
                            <div class="flex flex-col">
                                <span class="font-semibold text-surface-800 dark:text-surface-100">{{ data.titulo }}</span>
                                <span class="text-xs text-surface-400 truncate max-w-[200px]">{{ data.descripcion }}</span>
                            </div>
                        </template>
                    </Column>

                    <!-- Descripción -->
                    <Column v-if="esColumnaVisible('descripcion')" field="descripcion" header="Descripción" style="min-width:16rem">
                        <template #body="{ data }">
                            <span class="text-sm text-surface-600 dark:text-surface-300 line-clamp-2">{{ data.descripcion }}</span>
                        </template>
                    </Column>

                    <!-- Costo -->
                    <Column v-if="esColumnaVisible('costo_puntos')" field="costo_puntos" header="Costo" sortable style="min-width:8rem">
                        <template #body="{ data }">
                            <div class="flex items-center gap-1">
                                <span class="text-sm">🏅</span>
                                <span class="font-bold text-yellow-700 dark:text-yellow-300">{{ data.costo_puntos }}</span>
                                <span class="text-xs text-surface-400">pts</span>
                            </div>
                        </template>
                    </Column>

                    <!-- Stock -->
                    <Column v-if="esColumnaVisible('stock')" field="stock" header="Stock" sortable style="min-width:8rem">
                        <template #body="{ data }">
                            <span v-if="data.stock === null || data.stock === undefined" class="text-surface-400 text-sm">∞ Ilimitado</span>
                            <Tag v-else-if="data.stock === 0" value="Agotado" severity="danger" />
                            <span v-else class="font-semibold">{{ data.stock }}</span>
                        </template>
                    </Column>

                    <!-- Estado -->
                    <Column v-if="esColumnaVisible('activo')" field="activo" header="Estado" sortable style="min-width:9rem">
                        <template #body="{ data }">
                            <Tag
                                :value="data.activo ? 'Activa' : 'Desactivada'"
                                :severity="data.activo ? 'success' : 'secondary'"
                            />
                        </template>
                    </Column>

                    <!-- Fecha -->
                    <Column v-if="esColumnaVisible('creado_en')" field="creado_en" header="Creada" sortable style="min-width:9rem">
                        <template #body="{ data }">{{ formatFecha(data.creado_en) }}</template>
                    </Column>

                    <!-- Acciones -->
                    <Column header="Acciones" frozen alignFrozen="right" style="min-width:11rem">
                        <template #body="{ data }">
                            <div class="flex gap-1">
                                <!-- Editar -->
                                <Button
                                    icon="pi pi-pencil"
                                    rounded text severity="info"
                                    v-tooltip.top="'Editar'"
                                    size="small"
                                    @click="abrirEditar(data)"
                                />
                                <!-- Activar / Desactivar -->
                                <Button
                                    :icon="data.activo ? 'pi pi-eye-slash' : 'pi pi-eye'"
                                    rounded text
                                    :severity="data.activo ? 'warn' : 'success'"
                                    :v-tooltip.top="data.activo ? 'Desactivar' : 'Activar'"
                                    size="small"
                                    @click="toggleActivo(data)"
                                />
                                <!-- Eliminar -->
                                <Button
                                    icon="pi pi-trash"
                                    rounded text severity="danger"
                                    v-tooltip.top="'Eliminar'"
                                    size="small"
                                    @click="confirmarEliminar(data)"
                                />
                            </div>
                        </template>
                    </Column>
                </DataTable>
            </div>

            <!-- ═════════════════════════════════════════════════════════ -->
            <!-- TAB 1: Historial de Canjes                                -->
            <!-- ═════════════════════════════════════════════════════════ -->
            <div v-if="tabActivo === 1" class="card">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="font-semibold text-surface-800 dark:text-surface-100 m-0">Canjes Realizados por los Técnicos</h3>
                    <Button icon="pi pi-refresh" severity="secondary" outlined size="small" @click="cargarCanjes" :loading="loadingCanjes" />
                </div>

                <DataTable
                    ref="dtCanjes"
                    :value="canjes"
                    :loading="loadingCanjes"
                    v-model:filters="filtrosCanjes"
                    :globalFilterFields="['usuario_nombre', 'recompensa_titulo', 'estado_display']"
                    paginator :rows="10" :rowsPerPageOptions="[5,10,25]"
                    dataKey="id" showGridlines stripedRows class="datatable-mobile"
                >
                    <template #header>
                        <InputText
                            v-model="filtrosCanjes.global.value"
                            placeholder="Buscar canje..."
                            class="w-full md:w-80"
                        />
                    </template>
                    <template #empty>
                        <div class="text-center py-8 text-surface-400">
                            <i class="pi pi-inbox text-4xl mb-3 block" />
                            No hay canjes registrados.
                        </div>
                    </template>

                    <Column field="usuario_nombre" header="Técnico" sortable style="min-width:10rem">
                        <template #body="{ data }">
                            <div class="flex items-center gap-2">
                                <div class="w-7 h-7 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                                    <i class="pi pi-user text-primary-600 text-xs" />
                                </div>
                                <span class="font-medium">{{ data.usuario_nombre }}</span>
                            </div>
                        </template>
                    </Column>

                    <Column field="recompensa_titulo" header="Recompensa" sortable style="min-width:14rem">
                        <template #body="{ data }">
                            <span class="font-semibold">{{ data.recompensa_titulo }}</span>
                        </template>
                    </Column>

                    <Column field="puntos_descontados" header="Puntos" sortable style="min-width:8rem">
                        <template #body="{ data }">
                            <div class="flex items-center gap-1">
                                <span class="text-sm">🏅</span>
                                <span class="font-bold text-yellow-700 dark:text-yellow-300">{{ data.puntos_descontados }}</span>
                            </div>
                        </template>
                    </Column>

                    <Column field="estado" header="Estado" sortable style="min-width:10rem">
                        <template #body="{ data }">
                            <Tag
                                :value="data.estado_display"
                                :severity="getCanjeSeverity(data.estado)"
                            />
                        </template>
                    </Column>

                    <Column field="creado_en" header="Fecha Canje" sortable style="min-width:10rem">
                        <template #body="{ data }">{{ formatFecha(data.creado_en) }}</template>
                    </Column>

                    <Column field="nota_gerencia" header="Nota" style="min-width:12rem">
                        <template #body="{ data }">
                            <span v-if="data.nota_gerencia" class="text-sm text-surface-500">{{ data.nota_gerencia }}</span>
                            <span v-else class="text-surface-300 text-sm">—</span>
                        </template>
                    </Column>

                    <Column header="Acción" style="min-width:9rem">
                        <template #body="{ data }">
                            <Button
                                v-if="data.estado === 'pendiente'"
                                icon="pi pi-check"
                                label="Entregar"
                                severity="success"
                                outlined
                                size="small"
                                @click="abrirEntrega(data)"
                            />
                            <span v-else class="text-surface-300 text-xs">—</span>
                        </template>
                    </Column>
                </DataTable>
            </div>
        </template>

        <!-- ══════════════════════════════════════════════════════════════════ -->
        <!-- Dialog: CRUD Recompensa                                            -->
        <!-- ══════════════════════════════════════════════════════════════════ -->
        <Dialog
            v-model:visible="dialogRecompensa"
            modal
            :style="{ width: '90vw', maxWidth: '540px' }"
            :header="modoEdicion ? `✏️ Editar: ${form.titulo}` : '🎁 Nueva Recompensa'"
        >
            <div class="flex flex-col gap-5">
                <!-- Título -->
                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Nombre de la Recompensa <span class="text-red-500">*</span></label>
                    <InputText
                        v-model="form.titulo"
                        placeholder="Ej: Día libre adicional, Bono de alimentación..."
                        class="w-full"
                        :class="{ 'p-invalid': submitted && !form.titulo?.trim() }"
                    />
                </div>

                <!-- Descripción -->
                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Descripción <span class="text-red-500">*</span></label>
                    <Textarea
                        v-model="form.descripcion"
                        rows="3"
                        placeholder="Detalla qué incluye la recompensa, cómo se reclama y vigencia..."
                        class="w-full"
                        :class="{ 'p-invalid': submitted && !form.descripcion?.trim() }"
                    />
                </div>

                <!-- Costo y Stock en fila -->
                <div class="grid grid-cols-2 gap-4">
                    <div class="flex flex-col gap-2">
                        <label class="text-sm font-medium">Costo en Puntos <span class="text-red-500">*</span></label>
                        <InputNumber
                            v-model="form.costo_puntos"
                            :min="1"
                            :max="99999"
                            placeholder="50"
                            class="w-full"
                            :class="{ 'p-invalid': submitted && !form.costo_puntos }"
                        />
                        <div class="flex gap-1 flex-wrap">
                            <Button v-for="pts in [25, 50, 100, 200]" :key="pts"
                                :label="`${pts}`" size="small" text severity="secondary"
                                :class="{ 'font-bold underline': form.costo_puntos === pts }"
                                @click="form.costo_puntos = pts"
                            />
                        </div>
                    </div>
                    <div class="flex flex-col gap-2">
                        <label class="text-sm font-medium">
                            Stock
                            <span class="text-surface-400 font-normal">(vacío = ilimitado)</span>
                        </label>
                        <InputNumber
                            v-model="form.stock"
                            :min="0"
                            placeholder="∞"
                            class="w-full"
                        />
                    </div>
                </div>

                <!-- Estado activo -->
                <div class="flex items-center gap-3">
                    <ToggleSwitch v-model="form.activo" inputId="switch_activo" />
                    <label for="switch_activo" class="text-sm font-medium cursor-pointer">
                        {{ form.activo ? '✅ Visible para los técnicos' : '⏸️ Oculta (desactivada)' }}
                    </label>
                </div>
            </div>

            <template #footer>
                <Button label="Cancelar" severity="secondary" outlined @click="dialogRecompensa = false" :disabled="loadingGuardar" />
                <Button
                    :label="modoEdicion ? 'Guardar Cambios' : 'Crear Recompensa'"
                    :icon="modoEdicion ? 'pi pi-save' : 'pi pi-plus'"
                    severity="primary"
                    @click="guardarRecompensa"
                    :loading="loadingGuardar"
                />
            </template>
        </Dialog>

        <!-- ══════════════════════════════════════════════════════════════════ -->
        <!-- Dialog: Confirmar Entrega de Canje                                 -->
        <!-- ══════════════════════════════════════════════════════════════════ -->
        <Dialog v-model:visible="dialogEntrega" modal :style="{ width: '460px' }" header="✅ Confirmar Entrega de Canje">
            <div class="flex flex-col gap-4">
                <p class="text-sm text-surface-600 dark:text-surface-300 m-0">
                    Confirmas que entregaste <strong>{{ canjeSeleccionado?.recompensa_titulo }}</strong>
                    al técnico <strong>{{ canjeSeleccionado?.usuario_nombre }}</strong>.
                </p>
                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Nota de Entrega <span class="text-surface-400">(opcional)</span></label>
                    <Textarea
                        v-model="notaEntrega"
                        rows="3"
                        placeholder="Ej: Entregado en persona el martes, firmó recibo."
                        class="w-full"
                    />
                </div>
            </div>
            <template #footer>
                <Button label="Cancelar" severity="secondary" outlined @click="dialogEntrega = false" :disabled="loadingEntrega" />
                <Button label="Confirmar Entrega" icon="pi pi-check" severity="success" @click="confirmarEntrega" :loading="loadingEntrega" />
            </template>
        </Dialog>
    </div>
</template>
