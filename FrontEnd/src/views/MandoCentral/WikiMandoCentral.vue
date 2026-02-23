<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import api, { getUser } from '@/service/api';
import { wikiAdmin } from '@/service/wikiService';
import DataTableToolbar from '@/components/DataTableToolbar.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useResponsiveDataTable } from '@/composables/useResponsiveDataTable';

// ─── Estado general ──────────────────────────────────────────────────────────
const guias          = ref([]);
const loading        = ref(false);
const dt             = ref();
const toolbarRef     = ref();
const tabActivo      = ref(0);  // 0=Todas, 1=Pendientes, 2=Aprobadas, 3=Publicadas, 4=Rechazadas

useResponsiveDataTable(dt);

const filtros = ref({ global: { value: null, matchMode: 'contains' } });
const toast   = useToast();
const confirm = useConfirm();

// ─── Dialogs ─────────────────────────────────────────────────────────────────
const dialogAprobar   = ref(false);
const dialogPublicar  = ref(false);
const dialogRechazar  = ref(false);
const dialogVerPdf    = ref(false);

const guiaSeleccionada = ref(null);
const loadingAccion    = ref(false);
const formAprobar      = ref({ nota_revision: '' });
const formPublicar     = ref({ puntos_reconocimiento: 50, nota_revision: '' });
const formRechazar     = ref({ nota_revision: '' });
const urlPdfPreview    = ref('');

// ─── Columnas ─────────────────────────────────────────────────────────────────
const columnas = ref([
    { field: 'titulo_guia',         label: 'Título',          visible: true  },
    { field: 'modelo_nombre',       label: 'Modelo Máquina',  visible: true  },
    { field: 'autor_nombre',        label: 'Técnico Autor',   visible: true  },
    { field: 'casino_nombre',       label: 'Casino Origen',   visible: true  },
    { field: 'categoria_display',   label: 'Categoría',       visible: true  },
    { field: 'estado_display',      label: 'Estado',          visible: true  },
    { field: 'puntos_reconocimiento', label: 'Puntos',        visible: true  },
    { field: 'creado_en',           label: 'Fecha Envío',     visible: true  },
]);

const esColumnaVisible = (f) => columnas.value.find(c => c.field === f)?.visible ?? true;

// ─── Filtro por tab ───────────────────────────────────────────────────────────
const estadosPorTab = ['', 'pendiente_revision', 'aprobada', 'publicada', 'rechazada'];

const guiasFiltradas = computed(() => {
    const estado = estadosPorTab[tabActivo.value];
    if (!estado) return guias.value;
    return guias.value.filter(g => g.estado === estado);
});

// ─── Estadísticas ─────────────────────────────────────────────────────────────
const stats = computed(() => ({
    total:      guias.value.length,
    pendientes: guias.value.filter(g => g.estado === 'pendiente_revision').length,
    publicadas: guias.value.filter(g => g.estado === 'publicada').length,
    rechazadas: guias.value.filter(g => g.estado === 'rechazada').length,
}));

// ─── Buscador sinc. con toolbar ───────────────────────────────────────────────
watch(() => toolbarRef.value?.busquedaGlobal, (v) => {
    if (filtros.value.global) filtros.value.global.value = v;
}, { deep: true });

// ─── Carga de datos ───────────────────────────────────────────────────────────
const cargarDatos = async () => {
    loading.value = true;
    try {
        const { data } = await wikiAdmin.listar();
        guias.value = data;
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.error || 'No se pudieron cargar las guías', life: 4000 });
    } finally {
        loading.value = false;
    }
};

// ─── Helpers de estilo ────────────────────────────────────────────────────────
const getEstadoSeverity = (estado) => ({
    pendiente_revision: 'warn',
    aprobada:           'info',
    publicada:          'success',
    rechazada:          'danger',
}[estado] || 'secondary');

const getEstadoIcon = (estado) => ({
    pendiente_revision: 'pi pi-clock',
    aprobada:           'pi pi-check-circle',
    publicada:          'pi pi-globe',
    rechazada:          'pi pi-times-circle',
}[estado] || 'pi pi-question-circle');

const formatFecha = (f) => f
    ? new Date(f).toLocaleString('es-MX', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
    : 'N/A';

const BASE_MEDIA = `http://${window.location.hostname}:8000`;

// ─── Acciones ─────────────────────────────────────────────────────────────────
const verPdf = (guia) => {
    const url = guia.archivo_pdf?.startsWith('http')
        ? guia.archivo_pdf
        : `${BASE_MEDIA}${guia.archivo_pdf}`;
    urlPdfPreview.value = url;
    guiaSeleccionada.value = guia;
    dialogVerPdf.value = true;
};

const abrirAprobar = (guia) => {
    guiaSeleccionada.value = guia;
    formAprobar.value = { nota_revision: '' };
    dialogAprobar.value = true;
};

const abrirPublicar = (guia) => {
    guiaSeleccionada.value = guia;
    formPublicar.value = { puntos_reconocimiento: 50, nota_revision: '' };
    dialogPublicar.value = true;
};

const abrirRechazar = (guia) => {
    guiaSeleccionada.value = guia;
    formRechazar.value = { nota_revision: '' };
    dialogRechazar.value = true;
};

const confirmarAprobar = async () => {
    loadingAccion.value = true;
    try {
        await wikiAdmin.aprobar(guiaSeleccionada.value.id, formAprobar.value);
        toast.add({ severity: 'success', summary: '✅ Guía Aprobada', detail: `"${guiaSeleccionada.value.titulo_guia}" fue aprobada. Pendiente de publicación.`, life: 4000 });
        dialogAprobar.value = false;
        cargarDatos();
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.error || 'No se pudo aprobar la guía', life: 4000 });
    } finally {
        loadingAccion.value = false;
    }
};

const confirmarPublicar = async () => {
    if (!formPublicar.value.puntos_reconocimiento && formPublicar.value.puntos_reconocimiento !== 0) {
        toast.add({ severity: 'warn', summary: 'Campo requerido', detail: 'Debes indicar cuántos puntos otorgar (puede ser 0)', life: 3000 });
        return;
    }
    loadingAccion.value = true;
    try {
        const { data } = await wikiAdmin.publicar(guiaSeleccionada.value.id, formPublicar.value);
        toast.add({
            severity: 'success',
            summary: '🌐 Guía Publicada',
            detail: data.mensaje || 'La guía fue publicada exitosamente.',
            life: 5000
        });
        dialogPublicar.value = false;
        cargarDatos();
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.error || 'No se pudo publicar la guía', life: 4000 });
    } finally {
        loadingAccion.value = false;
    }
};

const confirmarRechazar = async () => {
    if (!formRechazar.value.nota_revision?.trim()) {
        toast.add({ severity: 'warn', summary: 'Campo requerido', detail: 'Debes escribir el motivo del rechazo.', life: 3000 });
        return;
    }
    loadingAccion.value = true;
    try {
        await wikiAdmin.rechazar(guiaSeleccionada.value.id, formRechazar.value);
        toast.add({ severity: 'info', summary: '❌ Guía Rechazada', detail: `"${guiaSeleccionada.value.titulo_guia}" fue notificada al técnico.`, life: 4000 });
        dialogRechazar.value = false;
        cargarDatos();
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.error || 'No se pudo rechazar la guía', life: 4000 });
    } finally {
        loadingAccion.value = false;
    }
};

const confirmarEliminar = (guia) => {
    confirm.require({
        message: `¿Eliminar permanentemente la guía "${guia.titulo_guia}"? Esta acción no se puede deshacer.`,
        header: 'Eliminar Guía',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: { label: 'Cancelar', severity: 'secondary', outlined: true },
        acceptProps: { label: 'Eliminar', severity: 'danger' },
        accept: async () => {
            loading.value = true;
            try {
                await wikiAdmin.eliminar(guia.id);
                toast.add({ severity: 'success', summary: 'Eliminada', detail: 'La guía fue eliminada.', life: 3000 });
                cargarDatos();
            } catch (e) {
                toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.error || 'No se pudo eliminar', life: 3000 });
            } finally {
                loading.value = false;
            }
        }
    });
};

onMounted(cargarDatos);
</script>

<template>
    <div class="flex flex-col gap-6">
        <Toast />
        <ConfirmDialog />

        <!-- ── Encabezado ─────────────────────────────────────────────── -->
        <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                <i class="pi pi-book text-primary-600 dark:text-primary-300 text-2xl" />
            </div>
            <div>
                <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0 m-0">
                    Centro de Mando — Wiki Técnica
                </h1>
                <p class="text-surface-500 dark:text-surface-400 text-sm mt-1 m-0">
                    Revisa, aprueba y publica las guías técnicas enviadas por los equipos de cada casino.
                </p>
            </div>
        </div>

        <!-- ── Tarjetas de estadísticas ────────────────────────────────── -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="card !p-4 border-l-4 border-l-surface-300 cursor-pointer hover:shadow-md transition-shadow"
                 @click="tabActivo = 0">
                <div class="text-3xl font-bold text-surface-700 dark:text-surface-200">{{ stats.total }}</div>
                <div class="text-sm text-surface-500 mt-1">Total de Guías</div>
            </div>
            <div class="card !p-4 border-l-4 border-l-orange-500 cursor-pointer hover:shadow-md transition-shadow"
                 @click="tabActivo = 1">
                <div class="text-3xl font-bold text-orange-500">{{ stats.pendientes }}</div>
                <div class="text-sm text-surface-500 mt-1">
                    Pendientes
                    <Badge v-if="stats.pendientes > 0" :value="stats.pendientes" severity="warn" class="ml-2" />
                </div>
            </div>
            <div class="card !p-4 border-l-4 border-l-green-500 cursor-pointer hover:shadow-md transition-shadow"
                 @click="tabActivo = 3">
                <div class="text-3xl font-bold text-green-600">{{ stats.publicadas }}</div>
                <div class="text-sm text-surface-500 mt-1">Publicadas</div>
            </div>
            <div class="card !p-4 border-l-4 border-l-red-500 cursor-pointer hover:shadow-md transition-shadow"
                 @click="tabActivo = 4">
                <div class="text-3xl font-bold text-red-500">{{ stats.rechazadas }}</div>
                <div class="text-sm text-surface-500 mt-1">Rechazadas</div>
            </div>
        </div>

        <!-- ── Tabla principal ────────────────────────────────────────── -->
        <div class="card">
            <!-- Tabs de filtro -->
            <div class="flex gap-2 flex-wrap mb-4 border-b border-surface-200 dark:border-surface-700 pb-3">
                <Button
                    v-for="(tab, i) in ['Todas', 'Pendientes', 'Aprobadas', 'Publicadas', 'Rechazadas']"
                    :key="i"
                    :label="tab"
                    :severity="tabActivo === i ? 'primary' : 'secondary'"
                    size="small"
                    :outlined="tabActivo !== i"
                    @click="tabActivo = i"
                />
            </div>

            <DataTableToolbar
                ref="toolbarRef"
                :dt="dt"
                :datos="guiasFiltradas"
                titulo-reporte="Wiki Técnica — Centro de Mando"
                nombre-archivo="wiki_mando_central"
                :columnas="columnas"
                :mostrar-exportacion="true"
                :mostrar-imprimir="true"
                :mostrar-refrescar="true"
                :mostrar-selector-columnas="true"
                :mostrar-buscador="true"
                @refrescar="cargarDatos"
                v-model:columnas-seleccionadas="columnas"
            />

            <DataTable
                ref="dt"
                :value="guiasFiltradas"
                :loading="loading"
                v-model:filters="filtros"
                :globalFilterFields="['titulo_guia', 'autor_nombre', 'modelo_nombre', 'casino_nombre', 'categoria_display', 'estado_display']"
                paginator :rows="10" :rowsPerPageOptions="[5,10,25,50]"
                dataKey="id" showGridlines stripedRows class="datatable-mobile"
            >
                <template #empty>
                    <div class="text-center p-6 text-surface-400">
                        <i class="pi pi-book text-4xl mb-3 block" />
                        No hay guías en este estado.
                    </div>
                </template>

                <!-- Título -->
                <Column v-if="esColumnaVisible('titulo_guia')" field="titulo_guia" header="Título" sortable style="min-width:14rem">
                    <template #body="{ data }">
                        <span class="font-semibold text-surface-800 dark:text-surface-100">{{ data.titulo_guia }}</span>
                    </template>
                </Column>

                <!-- Modelo -->
                <Column v-if="esColumnaVisible('modelo_nombre')" field="modelo_nombre" header="Modelo" sortable style="min-width:10rem" />

                <!-- Autor -->
                <Column v-if="esColumnaVisible('autor_nombre')" field="autor_nombre" header="Técnico Autor" sortable style="min-width:10rem">
                    <template #body="{ data }">
                        <div class="flex flex-col">
                            <span class="font-medium">{{ data.autor_nombre }}</span>
                            <span class="text-xs text-surface-400">
                                {{ data.puntos_gamificacion_autor ?? '—' }} pts actuales
                            </span>
                        </div>
                    </template>
                </Column>

                <!-- Casino origen -->
                <Column v-if="esColumnaVisible('casino_nombre')" field="casino_nombre" header="Casino" sortable style="min-width:10rem" />

                <!-- Categoría -->
                <Column v-if="esColumnaVisible('categoria_display')" field="categoria_display" header="Categoría" sortable style="min-width:10rem">
                    <template #body="{ data }">
                        <Tag :value="data.categoria_display" severity="secondary" />
                    </template>
                </Column>

                <!-- Estado -->
                <Column v-if="esColumnaVisible('estado_display')" field="estado_display" header="Estado" sortable style="min-width:10rem">
                    <template #body="{ data }">
                        <Tag
                            :value="data.estado_display"
                            :severity="getEstadoSeverity(data.estado)"
                            :icon="getEstadoIcon(data.estado)"
                        />
                    </template>
                </Column>

                <!-- Puntos -->
                <Column v-if="esColumnaVisible('puntos_reconocimiento')" field="puntos_reconocimiento" header="Puntos" sortable style="min-width:7rem">
                    <template #body="{ data }">
                        <span v-if="data.puntos_reconocimiento > 0" class="font-bold text-yellow-600">
                            🏅 {{ data.puntos_reconocimiento }}
                        </span>
                        <span v-else class="text-surface-400">—</span>
                    </template>
                </Column>

                <!-- Fecha -->
                <Column v-if="esColumnaVisible('creado_en')" field="creado_en" header="Enviada el" sortable style="min-width:11rem">
                    <template #body="{ data }">{{ formatFecha(data.creado_en) }}</template>
                </Column>

                <!-- Acciones -->
                <Column header="Acciones" frozen alignFrozen="right" style="min-width:12rem">
                    <template #body="{ data }">
                        <div class="flex gap-1 flex-wrap">
                            <!-- Ver PDF -->
                            <Button
                                icon="pi pi-file-pdf"
                                rounded text severity="secondary"
                                v-tooltip.top="'Ver PDF'"
                                size="small"
                                @click="verPdf(data)"
                            />
                            <!-- Aprobar (solo desde pendiente) -->
                            <Button
                                v-if="data.estado === 'pendiente_revision'"
                                icon="pi pi-check"
                                rounded text severity="info"
                                v-tooltip.top="'Aprobar'"
                                size="small"
                                @click="abrirAprobar(data)"
                            />
                            <!-- Publicar (desde pendiente o aprobada) -->
                            <Button
                                v-if="['pendiente_revision', 'aprobada'].includes(data.estado)"
                                icon="pi pi-globe"
                                rounded text severity="success"
                                v-tooltip.top="'Publicar y otorgar puntos'"
                                size="small"
                                @click="abrirPublicar(data)"
                            />
                            <!-- Rechazar (no publicadas) -->
                            <Button
                                v-if="data.estado !== 'publicada'"
                                icon="pi pi-times"
                                rounded text severity="warn"
                                v-tooltip.top="'Rechazar'"
                                size="small"
                                @click="abrirRechazar(data)"
                            />
                            <!-- Eliminar -->
                            <Button
                                icon="pi pi-trash"
                                rounded text severity="danger"
                                v-tooltip.top="'Eliminar permanentemente'"
                                size="small"
                                @click="confirmarEliminar(data)"
                            />
                        </div>
                    </template>
                </Column>
            </DataTable>
        </div>

        <!-- ══════════════════════════════════════════════════════════════════ -->
        <!-- Dialog: Ver PDF                                                    -->
        <!-- ══════════════════════════════════════════════════════════════════ -->
        <Dialog v-model:visible="dialogVerPdf" modal :style="{ width: '90vw', maxWidth: '1000px' }"
            :header="`📄 ${guiaSeleccionada?.titulo_guia}`">
            <div class="flex flex-col gap-3">
                <div class="grid grid-cols-3 gap-3 text-sm">
                    <div><span class="text-surface-500">Modelo:</span> <strong>{{ guiaSeleccionada?.modelo_nombre }}</strong></div>
                    <div><span class="text-surface-500">Autor:</span> <strong>{{ guiaSeleccionada?.autor_nombres_completos }}</strong></div>
                    <div><span class="text-surface-500">Casino:</span> <strong>{{ guiaSeleccionada?.casino_nombre || 'Global' }}</strong></div>
                </div>
                <iframe
                    :src="urlPdfPreview"
                    class="w-full rounded-lg border border-surface-200"
                    style="height: 65vh"
                    type="application/pdf"
                />
                <div class="flex gap-2 justify-end">
                    <a :href="urlPdfPreview" target="_blank" download>
                        <Button icon="pi pi-download" label="Descargar PDF" severity="secondary" outlined size="small" />
                    </a>
                </div>
            </div>
        </Dialog>

        <!-- ══════════════════════════════════════════════════════════════════ -->
        <!-- Dialog: Aprobar                                                    -->
        <!-- ══════════════════════════════════════════════════════════════════ -->
        <Dialog v-model:visible="dialogAprobar" modal :style="{ width: '480px' }" header="✅ Aprobar Guía">
            <div class="flex flex-col gap-4">
                <p class="text-surface-600 dark:text-surface-300 text-sm m-0">
                    Estás aprobando <strong>"{{ guiaSeleccionada?.titulo_guia }}"</strong> de
                    <strong>{{ guiaSeleccionada?.autor_nombre }}</strong>.
                    La guía quedará lista para ser publicada.
                </p>
                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Nota para el técnico <span class="text-surface-400">(opcional)</span></label>
                    <Textarea
                        v-model="formAprobar.nota_revision"
                        rows="3"
                        placeholder="Comentario de aprobación..."
                        class="w-full"
                    />
                </div>
            </div>
            <template #footer>
                <Button label="Cancelar" severity="secondary" outlined @click="dialogAprobar = false" :disabled="loadingAccion" />
                <Button label="Aprobar Guía" icon="pi pi-check" severity="info" @click="confirmarAprobar" :loading="loadingAccion" />
            </template>
        </Dialog>

        <!-- ══════════════════════════════════════════════════════════════════ -->
        <!-- Dialog: Publicar + Otorgar puntos                                  -->
        <!-- ══════════════════════════════════════════════════════════════════ -->
        <Dialog v-model:visible="dialogPublicar" modal :style="{ width: '520px' }" header="🌐 Publicar Guía y Otorgar Puntos">
            <div class="flex flex-col gap-5">
                <p class="text-surface-600 dark:text-surface-300 text-sm m-0">
                    Publicar <strong>"{{ guiaSeleccionada?.titulo_guia }}"</strong> la hará visible
                    para todos los casinos en el Centro de Servicios.
                    Los puntos se sumarán automáticamente al perfil de
                    <strong>{{ guiaSeleccionada?.autor_nombre }}</strong>.
                </p>

                <!-- Selector de puntos -->
                <div class="card !p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700">
                    <div class="flex items-center gap-3 mb-3">
                        <span class="text-2xl">🏅</span>
                        <div>
                            <p class="font-semibold text-sm m-0">Puntos de Gamificación a Otorgar</p>
                            <p class="text-xs text-surface-400 m-0">Se suman al histórico del técnico. Su rango puede subir.</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-4">
                        <div class="flex gap-2 flex-wrap">
                            <Button
                                v-for="pts in [25, 50, 75, 100, 150, 200]"
                                :key="pts"
                                :label="`${pts}`"
                                :severity="formPublicar.puntos_reconocimiento === pts ? 'warning' : 'secondary'"
                                :outlined="formPublicar.puntos_reconocimiento !== pts"
                                size="small"
                                @click="formPublicar.puntos_reconocimiento = pts"
                            />
                        </div>
                        <InputNumber
                            v-model="formPublicar.puntos_reconocimiento"
                            :min="0"
                            :max="9999"
                            class="w-28"
                            placeholder="Pts"
                        />
                    </div>
                    <p class="text-xs text-surface-400 mt-2 m-0">
                        Puntos actuales del autor:
                        <strong class="text-surface-700 dark:text-surface-200">
                            {{ guiaSeleccionada?.puntos_gamificacion_autor ?? '—' }} pts
                        </strong>
                    </p>
                </div>

                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Nota de publicación <span class="text-surface-400">(opcional)</span></label>
                    <Textarea
                        v-model="formPublicar.nota_revision"
                        rows="3"
                        placeholder="Ej: Excelente guía, muy completa para el modelo X."
                        class="w-full"
                    />
                </div>
            </div>
            <template #footer>
                <Button label="Cancelar" severity="secondary" outlined @click="dialogPublicar = false" :disabled="loadingAccion" />
                <Button
                    label="Publicar y Otorgar Puntos"
                    icon="pi pi-globe"
                    severity="success"
                    @click="confirmarPublicar"
                    :loading="loadingAccion"
                />
            </template>
        </Dialog>

        <!-- ══════════════════════════════════════════════════════════════════ -->
        <!-- Dialog: Rechazar                                                   -->
        <!-- ══════════════════════════════════════════════════════════════════ -->
        <Dialog v-model:visible="dialogRechazar" modal :style="{ width: '460px' }" header="❌ Rechazar Guía">
            <div class="flex flex-col gap-4">
                <p class="text-surface-600 dark:text-surface-300 text-sm m-0">
                    Estás rechazando <strong>"{{ guiaSeleccionada?.titulo_guia }}"</strong>.
                    El técnico recibirá una notificación con tu comentario.
                </p>
                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">
                        Motivo del rechazo <span class="text-red-500">*</span>
                    </label>
                    <Textarea
                        v-model="formRechazar.nota_revision"
                        rows="4"
                        placeholder="Explica por qué no cumple con los criterios de publicación..."
                        class="w-full"
                    />
                    <small class="text-red-500" v-if="!formRechazar.nota_revision?.trim()">
                        El motivo es obligatorio.
                    </small>
                </div>
            </div>
            <template #footer>
                <Button label="Cancelar" severity="secondary" outlined @click="dialogRechazar = false" :disabled="loadingAccion" />
                <Button label="Rechazar" icon="pi pi-times" severity="danger" @click="confirmarRechazar" :loading="loadingAccion" />
            </template>
        </Dialog>
    </div>
</template>
