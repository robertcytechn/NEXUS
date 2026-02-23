<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import api, { getUser } from '@/service/api';
import { wikiPublica, wikiCatalogos } from '@/service/wikiService';
import { useToast } from 'primevue/usetoast';

// ─── Usuario y permisos ───────────────────────────────────────────────────────
const usuario     = computed(() => getUser());
const rol         = computed(() => usuario.value?.rol_nombre || '');
const esTecnico         = computed(() => rol.value === 'TECNICO');
const puedeEnviarGuia   = computed(() =>
    ['TECNICO', 'SUP SISTEMAS', 'DB ADMIN', 'ADMINISTRADOR'].includes(rol.value)
);
const puedeVerWiki = computed(() =>
    ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'SUPERVISOR SALA', 'TECNICO'].includes(rol.value)
);

const toast = useToast();

// ─── Estado ───────────────────────────────────────────────────────────────────
const guias        = ref([]);
const misPropuestas = ref([]);
const modelos      = ref([]);
const loading      = ref(false);
const loadingPropuestas = ref(false);
const reglas       = ref([]);

const tabActivo    = ref(0); // 0=Wiki Publicada, 1=Mis Propuestas (solo técnicos)
const mostrarGuia  = ref(false);

// Filtros de la galería
const filtroBusqueda = ref('');
const filtroCategoria = ref('');
const filtroModelo    = ref('');

// ─── Diálog: enviar propuesta ─────────────────────────────────────────────────
const dialogPropuesta = ref(false);
const loadingEnvio    = ref(false);
const formPropuesta   = ref({
    titulo_guia: '',
    categoria: '',
    modelo_relacionado: null,
    archivo_pdf: null,
});
const archivoPdf      = ref(null);
const submitted       = ref(false);

// ─── Diálog: ver detalle / PDF ────────────────────────────────────────────────
const dialogDetalle   = ref(false);
const guiaDetalle     = ref(null);

// ─── Catálogos ────────────────────────────────────────────────────────────────
const categorias = [
    { label: 'Guía de Reparación',            value: 'reparacion'    },
    { label: 'Manual de Configuración',        value: 'configuracion' },
    { label: 'Procedimiento de Limpieza',      value: 'limpieza'      },
    { label: 'Diccionario de Códigos de Error', value: 'error_code'   },
];

const categoriasOpciones = [{ label: 'Todas las categorías', value: '' }, ...categorias];

// ─── Carga de datos ───────────────────────────────────────────────────────────
const cargarDatos = async () => {
    loading.value = true;
    try {
        const [resGuias, resReglas, resModelos] = await Promise.all([
            wikiPublica.listar(),
            wikiPublica.reglas(),
            wikiCatalogos.modelos(),
        ]);
        guias.value   = resGuias.data;
        reglas.value  = resReglas.data?.reglas || [];
        modelos.value = resModelos.data;
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.error || 'No se pudo cargar la wiki', life: 4000 });
    } finally {
        loading.value = false;
    }
};

const cargarMisPropuestas = async () => {
    loadingPropuestas.value = true;
    try {
        const { data } = await wikiPublica.misPropuestas();
        misPropuestas.value = data.propuestas || [];
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar tus propuestas.', life: 3000 });
    } finally {
        loadingPropuestas.value = false;
    }
};

// ─── Galería filtrada ─────────────────────────────────────────────────────────
const guiasFiltradas = computed(() => {
    let lista = guias.value;
    if (filtroBusqueda.value.trim()) {
        const q = filtroBusqueda.value.toLowerCase();
        lista = lista.filter(g =>
            g.titulo_guia.toLowerCase().includes(q) ||
            g.autor_nombre?.toLowerCase().includes(q) ||
            g.modelo_nombre?.toLowerCase().includes(q)
        );
    }
    if (filtroCategoria.value) {
        lista = lista.filter(g => g.categoria === filtroCategoria.value);
    }
    if (filtroModelo.value) {
        lista = lista.filter(g => g.modelo_relacionado === filtroModelo.value);
    }
    return lista;
});

// ─── Helpers ─────────────────────────────────────────────────────────────────
const formatFecha = (f) => f
    ? new Date(f).toLocaleDateString('es-MX', { year: 'numeric', month: 'short', day: 'numeric' })
    : 'N/A';

const getCategoriaIcon = (cat) => ({
    reparacion:    'pi pi-wrench',
    configuracion: 'pi pi-cog',
    limpieza:      'pi pi-sparkles',
    error_code:    'pi pi-exclamation-triangle',
}[cat] || 'pi pi-book');

const getCategoriaColor = (cat) => ({
    reparacion:    'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    configuracion: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    limpieza:      'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    error_code:    'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
}[cat] || 'bg-surface-100 text-surface-600');

const getEstadoPropuestaSeverity = (estado) => ({
    pendiente_revision: 'warn',
    aprobada:           'info',
    publicada:          'success',
    rechazada:          'danger',
}[estado] || 'secondary');

const BASE_MEDIA = `http://${window.location.hostname}:8000`;

const getPdfUrl = (path) => path?.startsWith('http') ? path : `${BASE_MEDIA}${path}`;

const verDetalle = (guia) => {
    guiaDetalle.value = guia;
    dialogDetalle.value = true;
};

// ─── Enviar propuesta ─────────────────────────────────────────────────────────
const abrirPropuesta = () => {
    formPropuesta.value = { titulo_guia: '', categoria: '', modelo_relacionado: null };
    archivoPdf.value = null;
    submitted.value = false;
    dialogPropuesta.value = true;
};

const onFileSelect = (event) => {
    archivoPdf.value = event.files[0];
};

const enviarPropuesta = async () => {
    submitted.value = true;
    const { titulo_guia, categoria, modelo_relacionado } = formPropuesta.value;
    if (!titulo_guia?.trim() || !categoria || !modelo_relacionado || !archivoPdf.value) {
        toast.add({ severity: 'warn', summary: 'Campos requeridos', detail: 'Completa todos los campos y adjunta el PDF.', life: 3000 });
        return;
    }
    loadingEnvio.value = true;
    try {
        const fd = new FormData();
        fd.append('titulo_guia', titulo_guia);
        fd.append('categoria', categoria);
        fd.append('modelo_relacionado', modelo_relacionado);
        fd.append('archivo_pdf', archivoPdf.value);
        await wikiPublica.enviarPropuesta(fd);
        toast.add({
            severity: 'success',
            summary: '📤 Propuesta Enviada',
            detail: 'Tu guía fue enviada al administrador para revisión. ¡Gracias por compartir tu conocimiento!',
            life: 5000
        });
        dialogPropuesta.value = false;
        if (tabActivo.value === 1) cargarMisPropuestas();
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.error || 'No se pudo enviar la propuesta.', life: 4000 });
    } finally {
        loadingEnvio.value = false;
    }
};

// ─── Tab cambio ───────────────────────────────────────────────────────────────
watch(tabActivo, (val) => {
    if (val === 1 && puedeEnviarGuia.value && misPropuestas.value.length === 0) {
        cargarMisPropuestas();
    }
});

onMounted(cargarDatos);
</script>

<template>
    <div class="flex flex-col gap-6">
        <Toast />

        <!-- ── Acceso denegado ──────────────────────────────────────────── -->
        <div v-if="!puedeVerWiki" class="card text-center py-12">
            <i class="pi pi-lock text-5xl text-surface-300 mb-4 block" />
            <h2 class="text-xl font-semibold text-surface-500">Acceso Restringido</h2>
            <p class="text-surface-400">No tienes permisos para acceder al Centro de Servicios.</p>
        </div>

        <template v-else>
            <!-- ── Encabezado ─────────────────────────────────────────── -->
            <div class="flex flex-col md:flex-row md:items-center gap-4 justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                        <i class="pi pi-book text-blue-600 dark:text-blue-300 text-2xl" />
                    </div>
                    <div>
                        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0 m-0">
                            Centro de Servicios — Wiki Técnica
                        </h1>
                        <p class="text-surface-500 text-sm mt-1 m-0">
                            Base de conocimiento técnico verificada por el equipo de administración.
                        </p>
                    </div>
                </div>
                <Button
                    v-if="puedeEnviarGuia"
                    icon="pi pi-upload"
                    label="Enviar mi Guía"
                    severity="primary"
                    @click="abrirPropuesta"
                />
            </div>

            <!-- ── ¿Cómo funciona? ─────────────────────────────────────── -->
            <div class="card !p-0 overflow-hidden border border-blue-200 dark:border-blue-800">
                <!-- Cabecera toggle -->
                <button
                    class="w-full flex items-center justify-between px-5 py-3 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors text-left"
                    @click="mostrarGuia = !mostrarGuia"
                >
                    <div class="flex items-center gap-2">
                        <i class="pi pi-question-circle text-blue-600 dark:text-blue-300" />
                        <span class="font-semibold text-blue-800 dark:text-blue-200 text-sm">¿Cómo funciona la Wiki Técnica?</span>
                    </div>
                    <i :class="mostrarGuia ? 'pi pi-chevron-up' : 'pi pi-chevron-down'" class="text-blue-500 text-sm" />
                </button>

                <!-- Contenido expandible -->
                <div v-if="mostrarGuia" class="p-5 flex flex-col gap-5">

                    <!-- ¿Qué es? -->
                    <p class="text-sm text-surface-600 dark:text-surface-300 m-0 leading-relaxed">
                        La <strong>Wiki Técnica NEXUS</strong> es la base de conocimiento del equipo de mantenimiento.
                        Aquí encontrarás guías paso a paso para diagnóstico, reparación y configuración de máquinas de casino,
                        todas revisadas y aprobadas por el equipo de administración antes de ser publicadas.
                    </p>

                    <!-- Flujo en tarjetas -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                        <div class="rounded-xl p-4 bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700">
                            <div class="text-2xl mb-2">📖</div>
                            <h4 class="text-sm font-bold text-surface-800 dark:text-surface-100 m-0 mb-1">1. Consulta las guías</h4>
                            <p class="text-xs text-surface-500 m-0 leading-relaxed">
                                Busca por modelo, categoría o palabra clave. Abre cualquier guía publicada y
                                descarga el PDF para tenerla a mano en sala.
                            </p>
                        </div>
                        <div class="rounded-xl p-4 bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700">
                            <div class="text-2xl mb-2">✍️</div>
                            <h4 class="text-sm font-bold text-surface-800 dark:text-surface-100 m-0 mb-1">2. Envía tu propuesta</h4>
                            <p class="text-xs text-surface-500 m-0 leading-relaxed">
                                Si sabes algo que no está documentado, haz clic en <em>"Enviar mi Guía"</em>.
                                Completa el formulario y adjunta tu documento PDF con el procedimiento.
                            </p>
                        </div>
                        <div class="rounded-xl p-4 bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700">
                            <div class="text-2xl mb-2">🔍</div>
                            <h4 class="text-sm font-bold text-surface-800 dark:text-surface-100 m-0 mb-1">3. Revisión y aprobación</h4>
                            <p class="text-xs text-surface-500 m-0 leading-relaxed">
                                El equipo de administración revisa tu guía. Puede aprobarla, pedir correcciones
                                o rechazarla con una nota explicativa.
                            </p>
                        </div>
                        <div class="rounded-xl p-4 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700">
                            <div class="text-2xl mb-2">🏅</div>
                            <h4 class="text-sm font-bold text-blue-800 dark:text-blue-200 m-0 mb-1">4. Se publica y ganas puntos</h4>
                            <p class="text-xs text-blue-700 dark:text-blue-300 m-0 leading-relaxed">
                                Cuando tu guía se publica, recibes <strong>puntos de reconocimiento</strong>
                                que suman a tu ranking de gamificación NEXUS.
                            </p>
                        </div>
                    </div>

                    <!-- Estados de propuesta -->
                    <div>
                        <h4 class="text-sm font-semibold text-surface-700 dark:text-surface-200 mb-2">Estados de tu propuesta</h4>
                        <div class="flex flex-wrap gap-2">
                            <div class="flex items-center gap-2 bg-surface-100 dark:bg-surface-800 rounded-lg px-3 py-2">
                                <span class="w-2 h-2 rounded-full bg-yellow-400 inline-block" />
                                <span class="text-xs font-medium">Pendiente de Revisión</span>
                                <span class="text-xs text-surface-400">— En espera de que administración la evalúe</span>
                            </div>
                            <div class="flex items-center gap-2 bg-surface-100 dark:bg-surface-800 rounded-lg px-3 py-2">
                                <span class="w-2 h-2 rounded-full bg-blue-500 inline-block" />
                                <span class="text-xs font-medium">Aprobada</span>
                                <span class="text-xs text-surface-400">— Validada, lista para publicación</span>
                            </div>
                            <div class="flex items-center gap-2 bg-surface-100 dark:bg-surface-800 rounded-lg px-3 py-2">
                                <span class="w-2 h-2 rounded-full bg-green-500 inline-block" />
                                <span class="text-xs font-medium">Publicada</span>
                                <span class="text-xs text-surface-400">— Visible para todo el equipo + puntos acreditados</span>
                            </div>
                            <div class="flex items-center gap-2 bg-surface-100 dark:bg-surface-800 rounded-lg px-3 py-2">
                                <span class="w-2 h-2 rounded-full bg-red-400 inline-block" />
                                <span class="text-xs font-medium">Rechazada</span>
                                <span class="text-xs text-surface-400">— Se incluye nota con el motivo</span>
                            </div>
                        </div>
                    </div>

                    <!-- Ejemplo real -->
                    <div class="rounded-xl border border-dashed border-blue-300 dark:border-blue-700 p-4 bg-blue-50/40 dark:bg-blue-900/10">
                        <div class="flex items-center gap-2 mb-3">
                            <i class="pi pi-lightbulb text-yellow-500" />
                            <span class="text-sm font-semibold text-surface-700 dark:text-surface-200">Ejemplo de uso real</span>
                        </div>
                        <div class="flex flex-col gap-2 text-xs text-surface-600 dark:text-surface-300 leading-relaxed">
                            <p class="m-0">🔧 <strong>Juan</strong> (técnico) detecta un problema recurrente en las máquinas <em>IGT S2000</em>:
                            el display principal reinicia sólo cuando la temperatura supera los 40 °C.</p>
                        <p class="m-0">📝 Documenta el procedimiento de reemplazo del capacitor CE47 y lo sube como guía con su PDF adjunto.</p>
                            <p class="m-0">✅ Administración la revisa, la aprueba y la publica con <strong>75 puntos</strong> de reconocimiento.</p>
                            <p class="m-0">🏅 Juan recibe 75 puntos que se suman a su historial y lo acercan al siguiente rango RPG.</p>
                            <p class="m-0">📚 Todos los técnicos del casino ya pueden consultar la guía y resolver el mismo problema en minutos.</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ── Banner de Reglas (solo técnicos) ──────────────────── -->
            <div v-if="puedeEnviarGuia && reglas.length"
                 class="card !p-5 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800">
                <div class="flex items-center gap-2 mb-4">
                    <i class="pi pi-info-circle text-blue-600 text-lg" />
                    <h3 class="font-bold text-blue-800 dark:text-blue-200 m-0 text-base">
                        Reglas del Centro de Servicios
                    </h3>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div
                        v-for="regla in reglas"
                        :key="regla.numero"
                        class="flex items-start gap-3 bg-white/60 dark:bg-white/5 rounded-lg p-3"
                    >
                        <div class="w-7 h-7 min-w-7 rounded-full bg-blue-600 flex items-center justify-center">
                            <span class="text-white font-bold text-xs">{{ regla.numero }}</span>
                        </div>
                        <p class="text-sm text-blue-900 dark:text-blue-100 m-0 leading-relaxed">
                            {{ regla.texto }}
                        </p>
                    </div>
                </div>
            </div>

            <!-- ── Tabs: Wiki Publicada / Mis Propuestas ─────────────── -->
            <div class="flex gap-2 border-b border-surface-200 dark:border-surface-700 pb-2">
                <Button
                    label="📚 Wiki Publicada"
                    :severity="tabActivo === 0 ? 'primary' : 'secondary'"
                    :outlined="tabActivo !== 0"
                    size="small"
                    @click="tabActivo = 0"
                />
                <Button
                    v-if="puedeEnviarGuia"
                    label="📋 Mis Propuestas"
                    :severity="tabActivo === 1 ? 'primary' : 'secondary'"
                    :outlined="tabActivo !== 1"
                    size="small"
                    @click="tabActivo = 1"
                />
            </div>

            <!-- ═════════════════════════════════════════════════════════ -->
            <!-- TAB 0: Wiki Publicada                                     -->
            <!-- ═════════════════════════════════════════════════════════ -->
            <template v-if="tabActivo === 0">
                <!-- Filtros -->
                <div class="card !p-4">
                    <div class="flex flex-col md:flex-row gap-3">
                        <span class="p-input-icon-left flex-1">
                            <i class="pi pi-search" />
                            <InputText
                                v-model="filtroBusqueda"
                                placeholder="Buscar por título, autor o modelo..."
                                class="w-full"
                            />
                        </span>
                        <Select
                            v-model="filtroCategoria"
                            :options="categoriasOpciones"
                            optionLabel="label"
                            optionValue="value"
                            placeholder="Categoría"
                            class="w-full md:w-52"
                        />
                        <Select
                            v-model="filtroModelo"
                            :options="[{ id: '', nombre_modelo: 'Todos los modelos' }, ...modelos]"
                            optionLabel="nombre_modelo"
                            optionValue="id"
                            placeholder="Modelo de máquina"
                            class="w-full md:w-52"
                        />
                        <Button
                            icon="pi pi-times"
                            severity="secondary"
                            outlined
                            v-tooltip="'Limpiar filtros'"
                            @click="filtroBusqueda = ''; filtroCategoria = ''; filtroModelo = ''"
                        />
                    </div>
                    <div class="mt-2 text-sm text-surface-400">
                        {{ guiasFiltradas.length }} guía{{ guiasFiltradas.length !== 1 ? 's' : '' }} encontrada{{ guiasFiltradas.length !== 1 ? 's' : '' }}
                    </div>
                </div>

                <!-- Loading -->
                <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <Skeleton v-for="n in 6" :key="n" height="10rem" class="rounded-xl" />
                </div>

                <!-- Sin resultados -->
                <div v-else-if="guiasFiltradas.length === 0" class="card text-center py-12">
                    <i class="pi pi-book text-5xl text-surface-200 mb-4 block" />
                    <p class="text-surface-400 font-medium">No hay guías publicadas con esos filtros.</p>
                    <p v-if="puedeEnviarGuia" class="text-sm text-surface-400 mt-1">
                        ¿Conoces la solución? <span class="text-primary-600 cursor-pointer font-semibold" @click="abrirPropuesta">Envía tu guía.</span>
                    </p>
                </div>

                <!-- Tarjetas de guías -->
                <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    <div
                        v-for="guia in guiasFiltradas"
                        :key="guia.id"
                        class="card !p-0 overflow-hidden hover:shadow-lg transition-shadow cursor-pointer border border-surface-200 dark:border-surface-700 flex flex-col"
                        @click="verDetalle(guia)"
                    >
                        <!-- Franja de categoría -->
                        <div :class="['flex items-center gap-2 px-4 py-2 text-xs font-semibold', getCategoriaColor(guia.categoria)]">
                            <i :class="getCategoriaIcon(guia.categoria)" />
                            {{ guia.categoria_display }}
                        </div>

                        <div class="p-4 flex flex-col gap-3 flex-1">
                            <!-- Título -->
                            <h3 class="font-bold text-surface-800 dark:text-surface-100 text-base leading-snug m-0 line-clamp-2">
                                {{ guia.titulo_guia }}
                            </h3>

                            <!-- Modelo -->
                            <div class="flex items-center gap-2">
                                <i class="pi pi-server text-surface-400 text-xs" />
                                <span class="text-sm font-medium text-surface-600 dark:text-surface-300">
                                    {{ guia.modelo_nombre }}
                                </span>
                            </div>

                            <!-- Autor + fecha -->
                            <div class="flex items-center justify-between mt-auto">
                                <div class="flex items-center gap-2">
                                    <div class="w-7 h-7 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                                        <i class="pi pi-user text-primary-600 text-xs" />
                                    </div>
                                    <div>
                                        <p class="text-xs font-semibold text-surface-700 dark:text-surface-200 m-0">
                                            {{ guia.autor_nombres_completos || guia.autor_nombre }}
                                        </p>
                                        <p class="text-xs text-surface-400 m-0">{{ formatFecha(guia.fecha_revision) }}</p>
                                    </div>
                                </div>
                                <div v-if="guia.puntos_reconocimiento > 0"
                                     class="flex items-center gap-1 bg-yellow-50 dark:bg-yellow-900/20 rounded-full px-2 py-1">
                                    <span class="text-xs">🏅</span>
                                    <span class="text-xs font-bold text-yellow-700 dark:text-yellow-300">
                                        {{ guia.puntos_reconocimiento }} pts
                                    </span>
                                </div>
                            </div>
                        </div>

                        <!-- Footer: ver PDF -->
                        <div class="px-4 pb-3">
                            <Button
                                icon="pi pi-file-pdf"
                                label="Ver Guía PDF"
                                severity="secondary"
                                outlined
                                size="small"
                                class="w-full"
                                @click.stop="verDetalle(guia)"
                            />
                        </div>
                    </div>
                </div>
            </template>

            <!-- ═════════════════════════════════════════════════════════ -->
            <!-- TAB 1: Mis Propuestas                                    -->
            <!-- ═════════════════════════════════════════════════════════ -->
            <template v-if="tabActivo === 1 && puedeEnviarGuia">
                <div class="card">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="font-semibold text-surface-800 dark:text-surface-100 m-0">Mis Propuestas Enviadas</h3>
                        <Button icon="pi pi-refresh" severity="secondary" outlined size="small" @click="cargarMisPropuestas" :loading="loadingPropuestas" />
                    </div>

                    <div v-if="loadingPropuestas" class="flex justify-center py-8">
                        <ProgressSpinner style="width:40px;height:40px" />
                    </div>

                    <div v-else-if="misPropuestas.length === 0" class="text-center py-10 text-surface-400">
                        <i class="pi pi-inbox text-4xl mb-3 block" />
                        <p>Aún no has enviado ninguna propuesta.</p>
                        <Button label="Enviar mi primera guía" severity="primary" outlined size="small" @click="abrirPropuesta" class="mt-2" />
                    </div>

                    <DataTable v-else :value="misPropuestas" :loading="loadingPropuestas"
                        paginator :rows="8" dataKey="id" showGridlines stripedRows>
                        <Column field="titulo_guia" header="Título" sortable style="min-width:14rem">
                            <template #body="{ data }">
                                <span class="font-semibold">{{ data.titulo_guia }}</span>
                            </template>
                        </Column>
                        <Column field="modelo_nombre" header="Modelo" sortable style="min-width:10rem" />
                        <Column field="estado" header="Estado" sortable style="min-width:10rem">
                            <template #body="{ data }">
                                <Tag
                                    :value="data.estado?.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())"
                                    :severity="getEstadoPropuestaSeverity(data.estado)"
                                />
                            </template>
                        </Column>
                        <Column field="creado_en" header="Enviada" sortable style="min-width:10rem">
                            <template #body="{ data }">{{ formatFecha(data.creado_en) }}</template>
                        </Column>
                    </DataTable>
                </div>
            </template>
        </template>

        <!-- ══════════════════════════════════════════════════════════════════ -->
        <!-- Dialog: Detalle de Guía + PDF                                      -->
        <!-- ══════════════════════════════════════════════════════════════════ -->
        <Dialog v-model:visible="dialogDetalle" modal :style="{ width: '95vw', maxWidth: '1050px' }"
            :header="guiaDetalle?.titulo_guia">
            <div v-if="guiaDetalle" class="flex flex-col gap-4">
                <!-- Metadata -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div class="flex flex-col gap-1">
                        <span class="text-xs uppercase text-surface-400 font-semibold">Modelo</span>
                        <span class="font-semibold">{{ guiaDetalle.modelo_nombre }}</span>
                    </div>
                    <div class="flex flex-col gap-1">
                        <span class="text-xs uppercase text-surface-400 font-semibold">Autor</span>
                        <span class="font-semibold">{{ guiaDetalle.autor_nombres_completos || guiaDetalle.autor_nombre }}</span>
                    </div>
                    <div class="flex flex-col gap-1">
                        <span class="text-xs uppercase text-surface-400 font-semibold">Categoría</span>
                        <Tag :value="guiaDetalle.categoria_display" severity="secondary" size="small" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <span class="text-xs uppercase text-surface-400 font-semibold">Publicada</span>
                        <span>{{ formatFecha(guiaDetalle.fecha_revision) }}</span>
                    </div>
                </div>

                <!-- PDF Embebido -->
                <iframe
                    :src="getPdfUrl(guiaDetalle.archivo_pdf)"
                    class="w-full rounded-lg border border-surface-200 dark:border-surface-700"
                    style="height: 65vh"
                    type="application/pdf"
                />
                <div class="flex justify-end gap-2">
                    <a :href="getPdfUrl(guiaDetalle.archivo_pdf)" target="_blank" download>
                        <Button icon="pi pi-download" label="Descargar PDF" severity="secondary" outlined size="small" />
                    </a>
                </div>
            </div>
        </Dialog>

        <!-- ══════════════════════════════════════════════════════════════════ -->
        <!-- Dialog: Enviar Propuesta de Guía                                   -->
        <!-- ══════════════════════════════════════════════════════════════════ -->
        <Dialog v-model:visible="dialogPropuesta" modal :style="{ width: '90vw', maxWidth: '580px' }"
            header="📤 Enviar Propuesta de Guía Técnica">
            <div class="flex flex-col gap-5">
                <!-- Aviso informativo -->
                <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4 text-sm text-blue-800 dark:text-blue-200">
                    <div class="flex items-start gap-2">
                        <i class="pi pi-info-circle mt-0.5 shrink-0" />
                        <div>
                            <p class="m-0 font-semibold mb-1">¿Cómo funciona?</p>
                            <p class="m-0">Tu guía será revisada por el equipo de administración antes de publicarse en la Wiki. Si es aprobada y publicada, recibirás puntos de reconocimiento que suman a tu rango en el sistema de gamificación NEXUS.</p>
                        </div>
                    </div>
                </div>

                <!-- Título -->
                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Título de la Guía <span class="text-red-500">*</span></label>
                    <InputText
                        v-model="formPropuesta.titulo_guia"
                        placeholder="Ej: Solución Error E-07 en modelo IGT S3000"
                        class="w-full"
                        :class="{ 'p-invalid': submitted && !formPropuesta.titulo_guia?.trim() }"
                    />
                </div>

                <!-- Categoría -->
                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Categoría <span class="text-red-500">*</span></label>
                    <Select
                        v-model="formPropuesta.categoria"
                        :options="categorias"
                        optionLabel="label"
                        optionValue="value"
                        placeholder="Selecciona una categoría"
                        class="w-full"
                        :class="{ 'p-invalid': submitted && !formPropuesta.categoria }"
                    />
                </div>

                <!-- Modelo de máquina -->
                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Modelo de Máquina <span class="text-red-500">*</span></label>
                    <Select
                        v-model="formPropuesta.modelo_relacionado"
                        :options="modelos"
                        optionLabel="nombre_modelo"
                        optionValue="id"
                        placeholder="Selecciona el modelo"
                        class="w-full"
                        filter
                        :class="{ 'p-invalid': submitted && !formPropuesta.modelo_relacionado }"
                    />
                </div>

                <!-- Archivo PDF -->
                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Archivo PDF <span class="text-red-500">*</span></label>
                    <FileUpload
                        mode="basic"
                        accept="application/pdf"
                        :maxFileSize="10485760"
                        chooseLabel="Seleccionar PDF (máx. 10 MB)"
                        class="w-full"
                        :auto="false"
                        @select="onFileSelect"
                        :class="{ 'p-invalid': submitted && !archivoPdf }"
                    />
                    <div v-if="archivoPdf" class="flex items-center gap-2 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg px-3 py-2">
                        <i class="pi pi-file-pdf text-red-500" />
                        <span class="text-sm text-green-700 dark:text-green-300 font-medium flex-1 truncate">{{ archivoPdf.name }}</span>
                        <span class="text-xs text-surface-400">{{ (archivoPdf.size / 1024 / 1024).toFixed(2) }} MB</span>
                        <Button icon="pi pi-times" text severity="secondary" size="small" @click="archivoPdf = null" class="!p-1" />
                    </div>
                    <small v-if="submitted && !archivoPdf" class="text-red-500">
                        <i class="pi pi-exclamation-circle mr-1" />El archivo PDF es obligatorio.
                    </small>
                    <small class="text-surface-400">Solo archivos PDF. Tamaño máximo: 10 MB.</small>
                </div>
            </div>

            <template #footer>
                <Button label="Cancelar" severity="secondary" outlined @click="dialogPropuesta = false" :disabled="loadingEnvio" />
                <Button
                    label="Enviar para Revisión"
                    icon="pi pi-send"
                    severity="primary"
                    @click="enviarPropuesta"
                    :loading="loadingEnvio"
                />
            </template>
        </Dialog>
    </div>
</template>
