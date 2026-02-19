<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import api, { getUser, hasRoleAccess } from '@/service/api';
import { obtenerMapaCasino, actualizarCoordenadas } from '@/service/mapaService';
import { crearTicket, TIPOS_TICKET } from '@/service/ticketService';
import { jsPDF } from 'jspdf';

// ─── ESTADO PRINCIPAL ─────────────────────────────────────────────────────────
const toast = useToast();
const confirm = useConfirm();

const usuario = computed(() => getUser());
const casinoUsuario = computed(() => usuario.value?.casino || null);
const casinoNombre = computed(() => usuario.value?.casino_nombre || '—');

// Config del grid
const gridConfig = ref({ id: null, nombre: '', grid_width: 50, grid_height: 50 });
const maquinas = ref([]);
const loading = ref(false);
const elemento = ref(null); // Referencia para exportar PDF

// Filtros
const pisosDisponibles = ref([]);
const areasDisponibles = ref([]);
const pisoSeleccionado = ref(null);
const areaSeleccionada = ref(null);
const pisoChoices = ref([]);
const salaChoices = ref([]);

// Modo de visualización
const modoVisualizacion = ref('estado'); // 'estado' | 'proveedor'
const coloresProveedor = ref({}); // { proveedor_id: '#hex' }

/**
 * Actualiza el color de un proveedor de forma reactiva.
 * El ColorPicker de PrimeVue devuelve el hex SIN '#', lo añadimos aquí.
 */
function setColorProveedor(id, valor) {
    // valor puede venir con o sin '#'
    const hex = valor?.startsWith?.('#') ? valor : `#${valor}`;
    coloresProveedor.value = { ...coloresProveedor.value, [id]: hex };
}

// Modo edición (drag & drop)
const ROLES_EDICION = ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS'];
const puedeEditar = computed(() => hasRoleAccess(ROLES_EDICION));
const modoEdicion = ref(false);

// Drag & Drop
const draggingMaquina = ref(null);
const dropTargetX = ref(null);
const dropTargetY = ref(null);

// Diálogo de detalle de máquina
const detalleDialog = ref(false);
const maquinaDetalle = ref(null);
const historialTickets = ref([]);
const loadingDetalle = ref(false);

// Búsqueda en mapa
const busqueda = ref('');

// ─── CONSTANTES DE COLORES POR ESTADO ────────────────────────────────────────
const COLORES_ESTADO = {
    OPERATIVA: { bg: '#22c55e', text: '#fff', label: 'Operativa' },
    DAÑADA_OPERATIVA: { bg: '#f97316', text: '#fff', label: 'Dañada (Op.)' },
    DAÑADA: { bg: '#ef4444', text: '#fff', label: 'Dañada' },
    MANTENIMIENTO: { bg: '#eab308', text: '#000', label: 'Mantenimiento' },
    OBSERVACION: { bg: '#8b5cf6', text: '#fff', label: 'Observación' },
    PRUEBAS: { bg: '#06b6d4', text: '#fff', label: 'Pruebas' },
};

const COLORES_PALETA = [
    '#6366f1', '#ec4899', '#14b8a6', '#f59e0b', '#3b82f6',
    '#84cc16', '#f43f5e', '#a855f7', '#0ea5e9', '#10b981',
];

// ─── CARGA DE DATOS ───────────────────────────────────────────────────────────
const cargarMapa = async () => {
    if (!casinoUsuario.value) return;
    loading.value = true;
    try {
        const resultado = await obtenerMapaCasino(
            casinoUsuario.value,
            pisoSeleccionado.value || undefined,
            areaSeleccionada.value || undefined
        );
        if (!resultado.exito) {
            toast.add({ severity: 'error', summary: 'Error', detail: resultado.error, life: 4000 });
            return;
        }
        const data = resultado.data;
        gridConfig.value = data.casino;
        maquinas.value = data.maquinas;
        pisosDisponibles.value = data.pisos_disponibles || [];
        areasDisponibles.value = data.areas_disponibles || [];
        pisoChoices.value = data.piso_choices || [];
        salaChoices.value = data.sala_choices || [];

        // Asignar colores a proveedores nuevos
        data.maquinas.forEach(m => {
            if (m.proveedor_id && !coloresProveedor.value[m.proveedor_id]) {
                const idx = Object.keys(coloresProveedor.value).length % COLORES_PALETA.length;
                coloresProveedor.value[m.proveedor_id] = COLORES_PALETA[idx];
            }
        });
    } finally {
        loading.value = false;
    }
};

onMounted(cargarMapa);

// Re-filtrar cuando cambien piso o área
watch([pisoSeleccionado, areaSeleccionada], cargarMapa);

// ─── COMPUTED ─────────────────────────────────────────────────────────────────
/** Maquinas visibles (ya no filtramos el array completo, solo cambiamos colores) */
const maquinasVisibles = computed(() => maquinas.value);

/** Proveedores únicos en el mapa actual */
const proveedoresUnicos = computed(() => {
    const map = {};
    maquinas.value.forEach(m => {
        if (m.proveedor_id && !map[m.proveedor_id]) {
            map[m.proveedor_id] = m.proveedor_nombre;
        }
    });
    return Object.entries(map).map(([id, nombre]) => ({ id: Number(id), nombre }));
});

/** Opciones de piso para el selector (solo los existentes en el casino) */
const opcionesPiso = computed(() =>
    pisoChoices.value.filter(c => pisosDisponibles.value.includes(c.value))
);

/** Opciones de área para el selector */
const opcionesArea = computed(() =>
    salaChoices.value.filter(c => areasDisponibles.value.includes(c.value))
);

// ─── HELPERS DE COLOR ──────────────────────────────────────────────────────────
function getColorMaquina(m) {
    if (busqueda.value) {
        const q = busqueda.value.toLowerCase();
        const coincide = m.uid_sala?.toLowerCase().includes(q) ||
            m.juego?.toLowerCase().includes(q) ||
            m.modelo_nombre?.toLowerCase().includes(q);
        if (coincide) return '#2563eb'; // azul intenso
        return '#94a3b8'; // gris opaco
    }
    if (modoVisualizacion.value === 'proveedor') {
        return coloresProveedor.value[m.proveedor_id] || '#94a3b8';
    }
    return COLORES_ESTADO[m.estado_actual]?.bg || '#94a3b8';
}

function getTextColor(m) {
    if (busqueda.value) {
        const q = busqueda.value.toLowerCase();
        const coincide = m.uid_sala?.toLowerCase().includes(q) ||
            m.juego?.toLowerCase().includes(q) ||
            m.modelo_nombre?.toLowerCase().includes(q);
        if (coincide) return '#ffffff';
        return '#ffffff';
    }
    if (modoVisualizacion.value === 'proveedor') return '#fff';
    return COLORES_ESTADO[m.estado_actual]?.text || '#fff';
}

function getSeverity(estado) {
    const map = {
        OPERATIVA: 'success', DAÑADA_OPERATIVA: 'warn',
        DAÑADA: 'danger', MANTENIMIENTO: 'info',
        OBSERVACION: 'secondary', PRUEBAS: 'contrast'
    };
    return map[estado] || 'secondary';
}

function labelPiso(val) {
    return pisoChoices.value.find(c => c.value === val)?.label || val || 'Sin piso';
}
function labelSala(val) {
    return salaChoices.value.find(c => c.value === val)?.label || val || 'Sin sala';
}

// ─── DRAG & DROP ──────────────────────────────────────────────────────────────
function onDragStart(event, maquina) {
    if (!modoEdicion.value) return;
    draggingMaquina.value = maquina;
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', maquina.id);
}

function onDragOver(event, x, y) {
    if (!modoEdicion.value || !draggingMaquina.value) return;
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
    dropTargetX.value = x;
    dropTargetY.value = y;
}

function onDragLeave() {
    dropTargetX.value = null;
    dropTargetY.value = null;
}

function onDrop(event, x, y) {
    if (!modoEdicion.value || !draggingMaquina.value) return;
    event.preventDefault();
    dropTargetX.value = null;
    dropTargetY.value = null;

    const maqOrigen = draggingMaquina.value;
    draggingMaquina.value = null;

    // No mover si es la misma celda
    if (maqOrigen.coordenada_x === x && maqOrigen.coordenada_y === y) return;

    // Verificar si hay colisión localmente antes de confirmar
    const ocupada = maquinas.value.find(
        m => m.id !== maqOrigen.id && m.coordenada_x === x && m.coordenada_y === y
    );

    confirm.require({
        message: ocupada
            ? `¡Atención! La celda (${x}, ${y}) ya está ocupada por "${ocupada.uid_sala}". ¿Deseas mover "${maqOrigen.uid_sala}" de todas formas? El backend validará si es posible.`
            : `¿Mover la máquina "${maqOrigen.uid_sala}" a la posición (${x}, ${y})?`,
        header: 'Confirmar movimiento',
        icon: ocupada ? 'pi pi-exclamation-triangle' : 'pi pi-arrows-alt',
        rejectProps: { label: 'Cancelar', severity: 'secondary', outlined: true },
        acceptProps: { label: 'Confirmar', severity: 'primary' },
        accept: () => moverMaquina(maqOrigen, x, y)
    });
}

async function moverMaquina(maquina, x, y) {
    loading.value = true;
    try {
        const resultado = await actualizarCoordenadas(maquina.id, x, y);
        if (!resultado.exito) {
            toast.add({ severity: 'error', summary: 'Error al mover', detail: resultado.error, life: 4000 });
            return;
        }
        // Actualizar en local sin recargar todo el mapa
        const idx = maquinas.value.findIndex(m => m.id === maquina.id);
        if (idx !== -1) {
            maquinas.value[idx] = { ...maquinas.value[idx], coordenada_x: x, coordenada_y: y };
        }
        toast.add({ severity: 'success', summary: '✓ Movida', detail: `${maquina.uid_sala} ahora está en (${x}, ${y})`, life: 3000 });
    } finally {
        loading.value = false;
    }
}

// ─── DETALLE DE MÁQUINA ──────────────────────────────────────────────────────
async function verDetalle(m) {
    maquinaDetalle.value = { ...m };
    detalleDialog.value = true;
    loadingDetalle.value = true;
    historialTickets.value = [];
    try {
        const res = await api.get(`tickets/historial-maquina/${m.id}/`);
        historialTickets.value = res.data.historial || [];
    } catch {
        // Si no hay historial, dejamos array vacío
    } finally {
        loadingDetalle.value = false;
    }
}

const diasDesdeMantenimiento = computed(() => {
    if (!maquinaDetalle.value?.ultimo_mantenimiento) return 'N/A';
    const fecha = new Date(maquinaDetalle.value.ultimo_mantenimiento);
    const diff = Math.floor((new Date() - fecha) / (1000 * 60 * 60 * 24));
    return `${diff} días`;
});

// ─── LEVANTAR INCIDENCIA ──────────────────────────────────────────────────────
async function levantarIncidencia() {
    if (!maquinaDetalle.value) return;
    loading.value = true;
    try {
        const m = maquinaDetalle.value;
        const resultado = await crearTicket({
            maquinaId: m.id,
            maquinaUid: m.uid_sala,
            ...TIPOS_TICKET.INCIDENCIA_RAPIDA,
            reportanteId: usuario.value?.id,
            estadoMaquina: 'DAÑADA',
            incrementarContador: true,
            actualizarEstado: true
        });
        if (!resultado.exito) {
            toast.add({ severity: 'error', summary: resultado.error, detail: resultado.detalle, life: 6000 });
            return;
        }
        toast.add({
            severity: 'success', summary: '✓ Incidencia Creada',
            detail: `Ticket #${resultado.ticket.folio || resultado.ticket.id} creado para "${m.uid_sala}".`,
            life: 6000
        });
        detalleDialog.value = false;
        cargarMapa();
    } catch {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo crear el ticket', life: 4000 });
    } finally {
        loading.value = false;
    }
}

// ─── EXPORTAR PDF (vectorial nativo jsPDF — sin captura de DOM) ──────────────
async function exportarPDF() {
    if (!maquinas.value.length && !gridConfig.value.id) {
        toast.add({ severity: 'warn', summary: 'Aviso', detail: 'No hay datos para exportar', life: 3000 });
        return;
    }
    loading.value = true;
    try {
        await _dibujarYExportar();
        toast.add({ severity: 'success', summary: '✓ PDF exportado', detail: 'El mapa se descargó correctamente', life: 3000 });
    } catch (err) {
        console.error('[exportarPDF]', err);
        toast.add({ severity: 'error', summary: 'Error al exportar', detail: err?.message || 'No se pudo generar el PDF', life: 5000 });
    } finally {
        loading.value = false;
    }
}

// Logo SVG de Nexus — copia exacta de AppTopbar con var(--primary-color) → #2563eb
const NEXUS_SVG = `<svg viewBox="0 0 54 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path fill-rule="evenodd" clip-rule="evenodd" d="M17.1637 19.2467C17.1566 19.4033 17.1529 19.561 17.1529 19.7194C17.1529 25.3503 21.7203 29.915 27.3546 29.915C32.9887 29.915 37.5561 25.3503 37.5561 19.7194C37.5561 19.5572 37.5524 19.3959 37.5449 19.2355C38.5617 19.0801 39.5759 18.9013 40.5867 18.6994L40.6926 18.6782C40.7191 19.0218 40.7326 19.369 40.7326 19.7194C40.7326 27.1036 34.743 33.0896 27.3546 33.0896C19.966 33.0896 13.9765 27.1036 13.9765 19.7194C13.9765 19.374 13.9896 19.0316 14.0154 18.6927L14.0486 18.6994C15.0837 18.9062 16.1223 19.0886 17.1637 19.2467ZM33.3284 11.4538C31.6493 10.2396 29.5855 9.52381 27.3546 9.52381C25.1195 9.52381 23.0524 10.2421 21.3717 11.4603C20.0078 11.3232 18.6475 11.1387 17.2933 10.907C19.7453 8.11308 23.3438 6.34921 27.3546 6.34921C31.36 6.34921 34.9543 8.10844 37.4061 10.896C36.0521 11.1292 34.692 11.3152 33.3284 11.4538ZM43.826 18.0518C43.881 18.6003 43.9091 19.1566 43.9091 19.7194C43.9091 28.8568 36.4973 36.2642 27.3546 36.2642C18.2117 36.2642 10.8 28.8568 10.8 19.7194C10.8 19.1615 10.8276 18.61 10.8816 18.0663L7.75383 17.4411C7.66775 18.1886 7.62354 18.9488 7.62354 19.7194C7.62354 30.6102 16.4574 39.4388 27.3546 39.4388C38.2517 39.4388 47.0855 30.6102 47.0855 19.7194C47.0855 18.9439 47.0407 18.1789 46.9536 17.4267L43.826 18.0518ZM44.2613 9.54743L40.9084 10.2176C37.9134 5.95821 32.9593 3.1746 27.3546 3.1746C21.7442 3.1746 16.7856 5.96385 13.7915 10.2305L10.4399 9.56057C13.892 3.83178 20.1756 0 27.3546 0C34.5281 0 40.8075 3.82591 44.2613 9.54743Z" fill="#2563eb"/>
  <mask id="mask0_1413_1551" style="mask-type:alpha" maskUnits="userSpaceOnUse" x="0" y="8" width="54" height="11">
    <path d="M27 18.3652C10.5114 19.1944 0 8.88892 0 8.88892C0 8.88892 16.5176 14.5866 27 14.5866C37.4824 14.5866 54 8.88892 54 8.88892C54 8.88892 43.4886 17.5361 27 18.3652Z" fill="#2563eb"/>
  </mask>
  <g mask="url(#mask0_1413_1551)">
    <path d="M-4.673e-05 8.88887L3.73084 -1.91434L-8.00806 17.0473L-4.673e-05 8.88887ZM27 18.3652L26.4253 6.95109L27 18.3652ZM54 8.88887L61.2673 17.7127L50.2691 -1.91434L54 8.88887ZM-4.673e-05 8.88887C-8.00806 17.0473 -8.00469 17.0505 -8.00132 17.0538C-8.00018 17.055 -7.99675 17.0583 -7.9944 17.0607C-7.98963 17.0653 -7.98474 17.0701 -7.97966 17.075C-7.96949 17.0849 -7.95863 17.0955 -7.94707 17.1066C-7.92401 17.129 -7.89809 17.1539 -7.86944 17.1812C-7.8122 17.236 -7.74377 17.3005 -7.66436 17.3743C-7.50567 17.5218 -7.30269 17.7063 -7.05645 17.9221C-6.56467 18.3532 -5.89662 18.9125 -5.06089 19.5534C-3.39603 20.83 -1.02575 22.4605 1.98012 24.0457C7.97874 27.2091 16.7723 30.3226 27.5746 29.7793L26.4253 6.95109C20.7391 7.23699 16.0326 5.61231 12.6534 3.83024C10.9703 2.94267 9.68222 2.04866 8.86091 1.41888C8.45356 1.10653 8.17155 0.867278 8.0241 0.738027C7.95072 0.673671 7.91178 0.637576 7.90841 0.634492C7.90682 0.63298 7.91419 0.639805 7.93071 0.65557C7.93897 0.663455 7.94952 0.673589 7.96235 0.686039C7.96883 0.692262 7.97582 0.699075 7.98338 0.706471C7.98719 0.710167 7.99113 0.714014 7.99526 0.718014C7.99729 0.720008 8.00047 0.723119 8.00148 0.724116C8.00466 0.727265 8.00796 0.730446 -4.673e-05 8.88887ZM27.5746 29.7793C37.6904 29.2706 45.9416 26.3684 51.6602 23.6054C54.5296 22.2191 56.8064 20.8465 58.4186 19.7784C59.2265 19.2431 59.873 18.7805 60.3494 18.4257C60.5878 18.2482 60.7841 18.0971 60.9374 17.977C61.014 17.9169 61.0799 17.8645 61.1349 17.8203C61.1624 17.7981 61.1872 17.7781 61.2093 17.7602C61.2203 17.7512 61.2307 17.7427 61.2403 17.7348C61.2452 17.7308 61.2499 17.727 61.2544 17.7233C61.2566 17.7215 61.2598 17.7188 61.261 17.7179C61.2642 17.7153 61.2673 17.7127 54 8.88887C46.7326 0.0650536 46.7357 0.0625219 46.7387 0.0600241C46.7397 0.0592345 46.7427 0.0567658 46.7446 0.0551857C46.7485 0.0520238 46.7521 0.0489887 46.7557 0.0460799C46.7628 0.0402623 46.7694 0.0349487 46.7753 0.0301318C46.7871 0.0204986 46.7966 0.0128495 46.8037 0.00712562C46.818 -0.00431848 46.8228 -0.00808311 46.8184 -0.00463784C46.8096 0.00228345 46.764 0.0378652 46.6828 0.0983779C46.5199 0.219675 46.2165 0.439161 45.7812 0.727519C44.9072 1.30663 43.5257 2.14765 41.7061 3.02677C38.0469 4.79468 32.7981 6.63058 26.4253 6.95109L27.5746 29.7793ZM54 8.88887C50.2691 -1.91433 50.27 -1.91467 50.271 -1.91498C50.2712 -1.91506 50.272 -1.91535 50.2724 -1.9155C50.2733 -1.91581 50.274 -1.91602 50.2743 -1.91616C50.2752 -1.91643 50.275 -1.91636 50.2738 -1.91595C50.2714 -1.91515 50.2652 -1.91302 50.2552 -1.9096C50.2351 -1.90276 50.1999 -1.89078 50.1503 -1.874C50.0509 -1.84043 49.8938 -1.78773 49.6844 -1.71863C49.2652 -1.58031 48.6387 -1.377 47.8481 -1.13035C46.2609 -0.635237 44.0427 0.0249875 41.5325 0.6823C36.215 2.07471 30.6736 3.15796 27 3.15796V26.0151C33.8087 26.0151 41.7672 24.2495 47.3292 22.7931C50.2586 22.026 52.825 21.2618 54.6625 20.6886C55.5842 20.4011 56.33 20.1593 56.8551 19.986C57.1178 19.8993 57.3258 19.8296 57.4735 19.7797C57.5474 19.7548 57.6062 19.7348 57.6493 19.72C57.6709 19.7127 57.6885 19.7066 57.7021 19.7019C57.7089 19.6996 57.7147 19.6976 57.7195 19.696C57.7219 19.6952 57.7241 19.6944 57.726 19.6938C57.7269 19.6934 57.7281 19.693 57.7286 19.6929C57.7298 19.6924 57.7309 19.692 54 8.88887ZM27 3.15796C23.3263 3.15796 17.7849 2.07471 12.4674 0.6823C9.95717 0.0249875 7.73904 -0.635237 6.15184 -1.13035C5.36118 -1.377 4.73467 -1.58031 4.3155 -1.71863C4.10609 -1.78773 3.94899 -1.84043 3.84961 -1.874C3.79994 -1.89078 3.76474 -1.90276 3.74471 -1.9096C3.73469 -1.91302 3.72848 -1.91515 3.72613 -1.91595C3.72496 -1.91636 3.72476 -1.91643 3.72554 -1.91616C3.72593 -1.91602 3.72657 -1.91581 3.72745 -1.9155C3.72789 -1.91535 3.72874 -1.91506 3.72896 -1.91498C3.72987 -1.91467 3.73084 -1.91433 -4.673e-05 8.88887C-3.73093 19.692 -3.72983 19.6924 -3.72868 19.6929C-3.72821 19.693 -3.72698 19.6934 -3.72603 19.6938C-3.72415 19.6944 -3.72201 19.6952 -3.71961 19.696C-3.71482 19.6976 -3.70901 19.6996 -3.7022 19.7019C-3.68858 19.7066 -3.67095 19.7127 -3.6494 19.72C-3.60629 19.7348 -3.54745 19.7548 -3.47359 19.7797C-3.32589 19.8296 -3.11788 19.8993 -2.85516 19.986C-2.33008 20.1593 -1.58425 20.4011 -0.662589 20.6886C1.17485 21.2618 3.74125 22.026 6.67073 22.7931C12.2327 24.2495 20.1913 26.0151 27 26.0151V3.15796Z" fill="#2563eb"/>
  </g>
</svg>`;

async function _logoToPng(wPx, hPx) {
    const blob = new Blob([NEXUS_SVG], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    return new Promise((resolve, reject) => {
        const img = new Image(wPx, hPx);
        img.onload = () => {
            const c = document.createElement('canvas');
            c.width = wPx; c.height = hPx;
            c.getContext('2d').drawImage(img, 0, 0, wPx, hPx);
            URL.revokeObjectURL(url);
            resolve(c.toDataURL('image/png'));
        };
        img.onerror = reject;
        img.src = url;
    });
}

async function _dibujarYExportar() {
    // ── Constantes de layout (mm) ─────────────────────────────────────────────
    const MARGIN = 8;
    const HEADER_H = 16;
    const LEGEND_H = 8;
    const GAP = 0.5;   // gap entre celdas
    const PAGE_W = 420;   // A3 landscape
    const PAGE_H = 297;

    const cols = gridConfig.value.grid_width;
    const rows = gridConfig.value.grid_height;
    const nombrePiso = pisoChoices.value.find(c => c.value === pisoSeleccionado.value)?.label || 'Todos los pisos';
    const nombreArea = salaChoices.value.find(c => c.value === areaSeleccionada.value)?.label || 'Todas las áreas';

    // Tamaño de celda óptimo para llenar la página
    const availW = PAGE_W - MARGIN * 2;
    const availH = PAGE_H - MARGIN * 2 - HEADER_H - LEGEND_H;
    const CELL = Math.min(
        (availW - (cols - 1) * GAP) / cols,
        (availH - (rows - 1) * GAP) / rows
    );
    const STEP = CELL + GAP;

    const pdf = new jsPDF({ unit: 'mm', format: 'a3', orientation: 'landscape' });

    // ── Logo ─────────────────────────────────────────────────────────────────
    const LOGO_W = 14.85;  // 54:40 ratio → 14.85 × 11 mm
    const LOGO_H = 11;
    const logoPng = await _logoToPng(216, 160);  // 3× para nitidez
    pdf.addImage(logoPng, 'PNG', MARGIN, MARGIN + 1, LOGO_W, LOGO_H);

    // ── Encabezado texto ──────────────────────────────────────────────────────
    pdf.setFont('helvetica', 'bold');
    pdf.setFontSize(12);
    pdf.setTextColor('#0f172a');
    pdf.text(`Mapa de Sala — ${gridConfig.value.nombre}`, MARGIN + LOGO_W + 3, MARGIN + 5);

    pdf.setFont('helvetica', 'normal');
    pdf.setFontSize(7.5);
    pdf.setTextColor('#64748b');
    pdf.text(
        `Piso: ${nombrePiso}  |  Área: ${nombreArea}  |  ${new Date().toLocaleString('es-MX')}`,
        MARGIN + LOGO_W + 3, MARGIN + 10
    );

    // Línea separadora
    pdf.setDrawColor('#3b82f6');
    pdf.setLineWidth(0.4);
    pdf.line(MARGIN, MARGIN + HEADER_H - 2, PAGE_W - MARGIN, MARGIN + HEADER_H - 2);

    // ── Leyenda ───────────────────────────────────────────────────────────────
    const legendItems = modoVisualizacion.value === 'estado'
        ? Object.entries(COLORES_ESTADO).map(([, v]) => ({ label: v.label, color: v.bg }))
        : proveedoresUnicos.value.map(p => ({ label: p.nombre, color: coloresProveedor.value[p.id] || '#94a3b8' }));

    pdf.setFontSize(6);
    pdf.setFont('helvetica', 'bold');
    let lx = MARGIN;
    const lY = MARGIN + HEADER_H + 0.5;
    for (const item of legendItems) {
        const tw = pdf.getTextWidth(item.label) + 4;
        if (lx + tw > PAGE_W - MARGIN) break;
        pdf.setFillColor(item.color);
        pdf.roundedRect(lx, lY, tw, 5, 0.8, 0.8, 'F');
        pdf.setTextColor('#ffffff');
        pdf.text(item.label, lx + 2, lY + 3.5);
        lx += tw + 2;
    }

    // ── Grid (100% vectorial) ─────────────────────────────────────────────────
    const gridOffY = MARGIN + HEADER_H + LEGEND_H;
    const maqMap = {};
    for (const m of maquinas.value) {
        maqMap[`${m.coordenada_x}_${m.coordenada_y}`] = m;
    }

    for (let y = 1; y <= rows; y++) {
        for (let x = 1; x <= cols; x++) {
            const px = MARGIN + (x - 1) * STEP;
            const py = gridOffY + (y - 1) * STEP;
            const m = maqMap[`${x}_${y}`];

            if (!m) {
                // Celda vacía
                pdf.setFillColor('#f1f5f9');
                pdf.setDrawColor('#e2e8f0');
                pdf.setLineWidth(0.1);
                pdf.rect(px, py, CELL, CELL, 'FD');
            } else {
                // Chip de máquina
                pdf.setFillColor(getColorMaquina(m));
                pdf.setDrawColor(getColorMaquina(m));
                pdf.roundedRect(px, py, CELL, CELL, 0.8, 0.8, 'F');

                // UID centrado, font auto-size para llenar la celda
                const uid = m.uid_sala || '';
                const fs = _fitFontSize(pdf, uid, CELL * 0.88, 2, 18);
                pdf.setFont('helvetica', 'bold');
                pdf.setFontSize(fs);
                pdf.setTextColor(getTextColor(m));
                pdf.text(uid, px + CELL / 2, py + CELL / 2, {
                    align: 'center', baseline: 'middle'
                });
            }
        }
    }

    pdf.save(`Mapa-${gridConfig.value.nombre}-${new Date().toLocaleDateString('es-MX')}.pdf`);
}

/**
 * Devuelve el font size (pt) más grande tal que el texto cabe en maxW mm.
 * Busca en [minFS, maxFS] con precisión de 0.25 pt.
 */
function _fitFontSize(pdf, text, maxW, minFS, maxFS) {
    let lo = minFS, hi = maxFS, best = minFS;
    while (hi - lo > 0.25) {
        const mid = (lo + hi) / 2;
        pdf.setFontSize(mid);
        if (pdf.getTextWidth(text) <= maxW) { best = mid; lo = mid; }
        else hi = mid;
    }
    return best;
}

// ─── HELPERS DE GRID ──────────────────────────────────────────────────────────
/** Obtiene la máquina en una celda dada (si existe) */
function getMaquinaEnCelda(x, y) {
    return maquinas.value.find(m => m.coordenada_x === x && m.coordenada_y === y) || null;
}

/** Filas visibles del grid (1..grid_height) */
const filas = computed(() => Array.from({ length: gridConfig.value.grid_height }, (_, i) => i + 1));
/** Columnas visibles del grid (1..grid_width) */
const columnas = computed(() => Array.from({ length: gridConfig.value.grid_width }, (_, i) => i + 1));
</script>

<template>
    <div class="flex flex-col gap-4">
        <Toast />
        <ConfirmDialog />

        <!-- ─── TOOLBAR ──────────────────────────────────────────────────── -->
        <div class="card p-4">
            <div class="flex flex-wrap gap-3 items-center justify-between">
                <!-- Título -->
                <div>
                    <div class="text-xl font-bold text-surface-900 dark:text-surface-0 flex items-center gap-2">
                        <i class="pi pi-map text-primary-500 text-2xl"></i>
                        Mapa de Sala — <span class="text-primary-500">{{ casinoNombre }}</span>
                    </div>
                    <div class="text-surface-500 text-sm mt-1">
                        Grid: {{ gridConfig.grid_width }}×{{ gridConfig.grid_height }} celdas ·
                        <span class="font-semibold text-primary-500">{{ maquinas.length }}</span> máquinas
                    </div>
                </div>

                <!-- Controles -->
                <div class="flex flex-wrap gap-2 items-center">
                    <!-- Filtro Piso -->
                    <Select v-model="pisoSeleccionado" :options="opcionesPiso" optionLabel="label" optionValue="value"
                        placeholder="Todos los pisos" showClear class="w-44" />
                    <!-- Filtro Área -->
                    <Select v-model="areaSeleccionada" :options="opcionesArea" optionLabel="label" optionValue="value"
                        placeholder="Todas las áreas" showClear class="w-44" />
                    <!-- Búsqueda -->
                    <InputText v-model="busqueda" placeholder="Buscar UID/Juego..." class="w-44" />

                    <!-- Modo visualización -->
                    <SelectButton v-model="modoVisualizacion"
                        :options="[{ label: 'Estado', value: 'estado', icon: 'pi pi-circle-fill' }, { label: 'Proveedor', value: 'proveedor', icon: 'pi pi-users' }]"
                        optionLabel="label" optionValue="value" />

                    <!-- Switch de edición (solo roles autorizados) -->
                    <div v-if="puedeEditar"
                        class="flex items-center gap-2 bg-surface-100 dark:bg-surface-800 rounded-lg px-3 py-2">
                        <span class="text-sm font-semibold"
                            :class="modoEdicion ? 'text-primary-500' : 'text-surface-400'">
                            <i class="pi pi-lock-open mr-1" v-if="modoEdicion"></i>
                            <i class="pi pi-lock mr-1" v-else></i>
                            Edición
                        </span>
                        <ToggleSwitch v-model="modoEdicion" />
                    </div>

                    <!-- Exportar PDF -->
                    <Button icon="pi pi-file-pdf" label="PDF" severity="danger" outlined @click="exportarPDF"
                        size="small" />
                    <!-- Refrescar -->
                    <Button icon="pi pi-refresh" severity="secondary" outlined @click="cargarMapa" :loading="loading"
                        size="small" />
                </div>
            </div>

            <!-- Aviso modo edición -->
            <div v-if="modoEdicion"
                class="mt-3 bg-amber-50 dark:bg-amber-950 border border-amber-300 dark:border-amber-700 rounded-lg px-3 py-2 text-amber-700 dark:text-amber-300 text-sm flex items-center gap-2">
                <i class="pi pi-info-circle"></i>
                Modo Edición activo — Arrastra y suelta las máquinas para reubicarlas en el mapa.
            </div>
        </div>

        <!-- ─── LEYENDA ──────────────────────────────────────────────────── -->
        <div class="card p-3">
            <div class="flex flex-wrap gap-2 items-center">
                <span class="text-sm font-semibold text-surface-500 mr-2">Leyenda:</span>
                <template v-if="modoVisualizacion === 'estado'">
                    <div v-for="(color, key) in COLORES_ESTADO" :key="key"
                        class="flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-bold"
                        :style="{ background: color.bg, color: color.text }">
                        {{ color.label }}
                    </div>
                </template>
                <template v-else>
                    <div v-for="prov in proveedoresUnicos" :key="prov.id"
                        class="flex items-center gap-2 rounded-full px-3 py-1 text-xs font-bold text-white"
                        :style="{ background: coloresProveedor[prov.id] || '#94a3b8' }">
                        {{ prov.nombre }}
                        <ColorPicker :modelValue="(coloresProveedor[prov.id] || '#94a3b8').replace('#', '')"
                            @update:modelValue="val => setColorProveedor(prov.id, val)"
                            style="width:16px;height:16px;flex-shrink:0;" />
                    </div>
                </template>
            </div>
        </div>

        <!-- ─── MAPA ─────────────────────────────────────────────────────── -->
        <div class="card p-2 overflow-auto" style="touch-action: pan-x pan-y; max-height: calc(100vh - 280px);">
            <div v-if="loading && maquinas.length === 0" class="flex items-center justify-center py-20">
                <ProgressSpinner style="width:60px;height:60px" />
            </div>

            <div v-else-if="!pisoSeleccionado || !areaSeleccionada"
                class="flex flex-col items-center justify-center py-20 border border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-900 rounded-lg">
                <i class="pi pi-map text-6xl text-surface-300 dark:text-surface-600 mb-4"></i>
                <p class="text-surface-500 dark:text-surface-400 text-lg">Por favor, selecciona un piso y un área para
                    visualizar el mapa de la sala.</p>
            </div>

            <div v-else id="mapa-exportar" ref="elemento" :style="{
                display: 'grid',
                gridTemplateColumns: `repeat(${gridConfig.grid_width}, 48px)`,
                gridTemplateRows: `repeat(${gridConfig.grid_height}, 48px)`,
                gap: '2px',
                width: `${gridConfig.grid_width * 50}px`,
                minWidth: `${gridConfig.grid_width * 50}px`,
            }">
                <template v-for="y in filas" :key="`row-${y}`">
                    <div v-for="x in columnas" :key="`cell-${x}-${y}`" class="mapa-celda relative" :class="{
                        'celda-drop-target': modoEdicion && dropTargetX === x && dropTargetY === y,
                    }" :style="{ gridColumn: x, gridRow: y }" @dragover.prevent="onDragOver($event, x, y)"
                        @dragleave="onDragLeave" @drop="onDrop($event, x, y)">
                        <!-- Etiqueta de celda (visible al hover) -->
                        <span class="celda-coords">{{ x }},{{ y }}</span>

                        <!-- Máquina en esta celda -->
                        <template v-if="getMaquinaEnCelda(x, y)">
                            <div class="maquina-chip"
                                :class="{ 'cursor-grab': modoEdicion, 'cursor-pointer': !modoEdicion }" :style="{
                                    background: getColorMaquina(getMaquinaEnCelda(x, y)),
                                    color: getTextColor(getMaquinaEnCelda(x, y)),
                                    opacity: draggingMaquina?.id === getMaquinaEnCelda(x, y).id ? 0.4 : 1
                                }" :draggable="modoEdicion" @dragstart="onDragStart($event, getMaquinaEnCelda(x, y))"
                                @click="verDetalle(getMaquinaEnCelda(x, y))" v-tooltip.top="{
                                    value: `${getMaquinaEnCelda(x, y).uid_sala} | ${getMaquinaEnCelda(x, y).modelo_nombre} | ${getMaquinaEnCelda(x, y).estado_actual}`,
                                    showDelay: 200
                                }">
                                <span class="maquina-uid">{{ getMaquinaEnCelda(x, y).uid_sala }}</span>
                                <span class="maquina-sub">{{ getMaquinaEnCelda(x, y).modelo_nombre?.slice(0, 8)
                                    }}</span>
                            </div>
                        </template>
                    </div>
                </template>
            </div>
        </div>

        <!-- ─── DIÁLOGO DE DETALLE ────────────────────────────────────────── -->
        <Dialog v-model:visible="detalleDialog" :style="{ width: '1000px' }" :breakpoints="{ '960px': '95vw' }"
            header="Ficha Técnica Completa" :modal="true" :maximizable="true">
            <div v-if="maquinaDetalle" class="flex flex-col gap-5">
                <!-- Cabecera -->
                <div
                    class="surface-card border-2 border-primary-200 dark:border-primary-900 rounded-xl p-5 bg-gradient-to-br from-primary-50 to-white dark:from-primary-950 dark:to-surface-900">
                    <div class="flex flex-col md:flex-row items-start md:items-center gap-3 mb-5">
                        <div class="flex items-center gap-3 flex-1">
                            <div class="flex items-center justify-center bg-primary-500 rounded-xl shadow-lg shrink-0"
                                style="width:3rem;height:3rem">
                                <i class="pi pi-desktop text-white text-xl"></i>
                            </div>
                            <div>
                                <h3 class="text-2xl font-bold text-surface-900 dark:text-surface-0">{{
                                    maquinaDetalle.uid_sala
                                }}</h3>
                                <p class="text-surface-500 text-sm">{{ maquinaDetalle.modelo_nombre }} · {{
                                    maquinaDetalle.modelo_producto }}</p>
                            </div>
                        </div>
                        <Tag :value="maquinaDetalle.estado_actual" :severity="getSeverity(maquinaDetalle.estado_actual)"
                            class="text-base px-4 py-2 font-bold" rounded />
                    </div>

                    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                        <!-- Casino -->
                        <div class="info-tile">
                            <div class="info-tile-label"><i class="pi pi-building text-blue-500"></i> Casino</div>
                            <span class="info-tile-value">{{ maquinaDetalle.casino_nombre }}</span>
                        </div>
                        <!-- Piso / Sala -->
                        <div class="info-tile">
                            <div class="info-tile-label"><i class="pi pi-map-marker text-red-500"></i> Ubicación</div>
                            <span class="info-tile-value">{{ labelPiso(maquinaDetalle.ubicacion_piso) }} / {{
                                labelSala(maquinaDetalle.ubicacion_sala) }}</span>
                        </div>
                        <!-- Coordenadas -->
                        <div class="info-tile">
                            <div class="info-tile-label"><i class="pi pi-compass text-purple-500"></i> Coordenadas</div>
                            <Tag :value="`X: ${maquinaDetalle.coordenada_x}, Y: ${maquinaDetalle.coordenada_y}`"
                                severity="secondary" class="text-xs" />
                        </div>
                        <!-- IP -->
                        <div class="info-tile">
                            <div class="info-tile-label"><i class="pi pi-wifi text-green-500"></i> IP</div>
                            <Tag v-if="maquinaDetalle.ip_maquina" :value="maquinaDetalle.ip_maquina" severity="info"
                                class="text-xs font-mono" />
                            <span v-else class="text-surface-400 text-xs">Sin asignar</span>
                        </div>
                        <!-- Serie -->
                        <div class="info-tile">
                            <div class="info-tile-label"><i class="pi pi-hashtag text-indigo-500"></i> No. Serie</div>
                            <span class="info-tile-value">{{ maquinaDetalle.numero_serie }}</span>
                        </div>
                        <!-- Juego -->
                        <div class="info-tile">
                            <div class="info-tile-label"><i class="pi pi-play text-pink-500"></i> Juego</div>
                            <span class="info-tile-value">{{ maquinaDetalle.juego || 'N/A' }}</span>
                        </div>
                        <!-- Mantenimiento -->
                        <div class="info-tile bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
                            <div class="info-tile-label"><i class="pi pi-wrench text-blue-600"></i> Último Mtto.</div>
                            <span class="info-tile-value text-blue-800 dark:text-blue-300">{{
                                maquinaDetalle.ultimo_mantenimiento || 'Sin registro' }}</span>
                            <span v-if="maquinaDetalle.ultimo_mantenimiento" class="text-xs text-blue-600">({{
                                diasDesdeMantenimiento }})</span>
                        </div>
                        <!-- Proveedor -->
                        <div class="info-tile">
                            <div class="info-tile-label"><i class="pi pi-briefcase text-teal-500"></i> Proveedor</div>
                            <span class="info-tile-value">{{ maquinaDetalle.proveedor_nombre || 'N/A' }}</span>
                        </div>
                        <!-- Fallas -->
                        <div class="info-tile"
                            :class="maquinaDetalle.contador_fallas > 5 ? 'bg-red-50 dark:bg-red-950 border-red-300' : 'bg-orange-50 dark:bg-orange-950 border-orange-200'">
                            <div class="info-tile-label"><i class="pi pi-exclamation-triangle text-orange-500"></i>
                                Fallas</div>
                            <span class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{
                                maquinaDetalle.contador_fallas || 0 }}</span>
                        </div>
                        <!-- RFC proveedor -->
                        <div class="info-tile">
                            <div class="info-tile-label"><i class="pi pi-id-card text-gray-500"></i> RFC</div>
                            <Tag v-if="maquinaDetalle.proveedor_rfc" :value="maquinaDetalle.proveedor_rfc"
                                severity="secondary" class="text-xs" />
                            <span v-else class="text-surface-400 text-xs">N/A</span>
                        </div>
                        <!-- Email proveedor -->
                        <div class="info-tile">
                            <div class="info-tile-label"><i class="pi pi-envelope text-blue-500"></i> Email</div>
                            <a v-if="maquinaDetalle.proveedor_email" :href="'mailto:' + maquinaDetalle.proveedor_email"
                                class="text-primary-600 hover:underline text-xs font-medium">{{
                                    maquinaDetalle.proveedor_email
                                }}</a>
                            <span v-else class="text-surface-400 text-xs">N/A</span>
                        </div>
                        <!-- Teléfono proveedor -->
                        <div class="info-tile">
                            <div class="info-tile-label"><i class="pi pi-phone text-green-500"></i> Teléfono</div>
                            <a v-if="maquinaDetalle.proveedor_telefono"
                                :href="'tel:' + maquinaDetalle.proveedor_telefono"
                                class="text-primary-600 hover:underline text-xs font-medium">{{
                                    maquinaDetalle.proveedor_telefono }}</a>
                            <span v-else class="text-surface-400 text-xs">N/A</span>
                        </div>
                        <!-- Instalación -->
                        <div class="info-tile">
                            <div class="info-tile-label"><i class="pi pi-calendar text-cyan-500"></i> Instalación</div>
                            <Tag v-if="maquinaDetalle.fecha_instalacion" :value="maquinaDetalle.fecha_instalacion"
                                severity="contrast" class="text-xs" />
                            <span v-else class="text-surface-400 text-xs">N/A</span>
                        </div>
                        <!-- Licencia -->
                        <div class="info-tile border-2" :class="maquinaDetalle.dias_licencia < 30 && maquinaDetalle.dias_licencia !== 'Indefinida'
                            ? 'bg-red-50 dark:bg-red-950 border-red-300 dark:border-red-800'
                            : 'bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800'">
                            <div class="info-tile-label">
                                <i class="pi pi-shield"
                                    :class="maquinaDetalle.dias_licencia < 30 && maquinaDetalle.dias_licencia !== 'Indefinida' ? 'text-red-600' : 'text-green-600'"></i>
                                <span
                                    :class="maquinaDetalle.dias_licencia < 30 && maquinaDetalle.dias_licencia !== 'Indefinida' ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'">Licencia</span>
                            </div>
                            <span class="info-tile-value block"
                                :class="maquinaDetalle.dias_licencia < 30 && maquinaDetalle.dias_licencia !== 'Indefinida' ? 'text-red-800 dark:text-red-300' : 'text-green-800 dark:text-green-300'">
                                {{ maquinaDetalle.fecha_vencimiento_licencia || 'Indefinida' }}
                            </span>
                            <Tag v-if="maquinaDetalle.dias_licencia && maquinaDetalle.dias_licencia !== 'Indefinida'"
                                :value="`${maquinaDetalle.dias_licencia} días`"
                                :severity="maquinaDetalle.dias_licencia < 30 ? 'danger' : 'success'"
                                class="text-xs mt-1" />
                        </div>
                        <!-- Denominaciones (fila completa) -->
                        <div class="col-span-2 sm:col-span-3 md:col-span-4 info-tile">
                            <div class="info-tile-label"><i class="pi pi-dollar text-emerald-500"></i> Denominaciones
                            </div>
                            <div class="flex flex-wrap gap-1 mt-1">
                                <Tag v-for="denom in maquinaDetalle.denominaciones_info" :key="denom.id"
                                    :value="denom.etiqueta" severity="success" class="text-xs" rounded />
                                <Tag v-if="!maquinaDetalle.denominaciones_info || maquinaDetalle.denominaciones_info.length === 0"
                                    value="Sin configurar" severity="warn" class="text-xs" />
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Historial de Tickets -->
                <div class="surface-card border border-surface-200 dark:border-surface-700 rounded-lg p-5">
                    <div class="flex items-center gap-2 mb-4">
                        <i class="pi pi-history text-xl text-surface-500"></i>
                        <h4 class="font-bold text-xl text-surface-900 dark:text-surface-0">Historial de Intervenciones
                        </h4>
                    </div>
                    <div v-if="loadingDetalle" class="text-center py-8">
                        <ProgressSpinner style="width:50px;height:50px" />
                    </div>
                    <div v-else-if="historialTickets.length === 0" class="text-center py-8 text-surface-400">
                        <i class="pi pi-info-circle text-4xl mb-3 block"></i>
                        No hay tickets registrados para esta máquina
                    </div>
                    <Timeline v-else :value="historialTickets" class="w-full">
                        <template #marker="slotProps">
                            <span
                                class="flex w-8 h-8 items-center justify-center text-white rounded-full z-10 shadow-sm"
                                :class="{
                                    'bg-green-500': slotProps.item.estado_ciclo === 'cerrado',
                                    'bg-blue-500': slotProps.item.estado_ciclo === 'proceso',
                                    'bg-orange-500': slotProps.item.estado_ciclo === 'espera',
                                    'bg-red-500': slotProps.item.estado_ciclo === 'abierto'
                                }">
                                <i class="pi pi-wrench"></i>
                            </span>
                        </template>
                        <template #content="slotProps">
                            <div
                                class="surface-card border-2 border-blue-200 dark:border-blue-800 rounded-xl p-3 md:p-5 mb-4 bg-gradient-to-br from-blue-50 to-white dark:from-blue-950 dark:to-surface-900">
                                <!-- Cabecera del Ticket -->
                                <div class="flex flex-col sm:flex-row justify-between items-start gap-2 mb-4">
                                    <div class="flex items-center gap-2 md:gap-3 flex-wrap">
                                        <div class="flex items-center justify-center bg-blue-500 rounded-lg shadow-md shrink-0"
                                            style="width:2rem;height:2rem">
                                            <i class="pi pi-ticket text-white text-sm"></i>
                                        </div>
                                        <div class="flex items-center gap-2 flex-wrap">
                                            <span
                                                class="font-bold text-lg md:text-2xl text-blue-600 dark:text-blue-400">{{
                                                    slotProps.item.folio }}</span>
                                            <Tag :value="slotProps.item.estado_ciclo"
                                                :severity="slotProps.item.estado_ciclo === 'cerrado' ? 'success' : slotProps.item.estado_ciclo === 'proceso' ? 'info' : 'warn'" />
                                        </div>
                                    </div>
                                    <span class="text-surface-500 text-xs md:text-sm">{{ new
                                        Date(slotProps.item.fecha_creacion).toLocaleDateString('es-MX') }}</span>
                                </div>

                                <!-- Descripción del problema -->
                                <p
                                    class="text-sm md:text-base font-medium text-blue-800 dark:text-blue-300 mb-4 pl-0 md:pl-12">
                                    {{ slotProps.item.descripcion_problema }}</p>

                                <!-- Información del ticket -->
                                <div class="flex flex-wrap gap-3 md:gap-4 mb-4 pl-0 md:pl-12">
                                    <div class="flex items-center gap-1">
                                        <i class="pi pi-tag text-surface-400 text-xs"></i>
                                        <span class="text-surface-500 text-sm">Categoría:</span>
                                        <span class="font-semibold text-surface-900 dark:text-surface-0 text-sm">{{
                                            slotProps.item.categoria }}</span>
                                    </div>
                                    <div class="flex items-center gap-1">
                                        <i class="pi pi-exclamation-circle text-surface-400 text-xs"></i>
                                        <span class="text-surface-500 text-sm">Prioridad:</span>
                                        <Tag :value="slotProps.item.prioridad"
                                            :severity="slotProps.item.prioridad === 'critica' || slotProps.item.prioridad === 'emergencia' ? 'danger' : slotProps.item.prioridad === 'alta' ? 'warn' : 'info'"
                                            class="text-xs" />
                                    </div>
                                    <div class="flex items-center gap-1">
                                        <i class="pi pi-user text-surface-400 text-xs"></i>
                                        <span class="text-surface-500 text-sm">Técnico:</span>
                                        <span class="font-semibold text-surface-900 dark:text-surface-0 text-sm">
                                            {{ slotProps.item.tecnico_asignado?.nombre || 'Sin asignar' }} {{
                                                slotProps.item.tecnico_asignado?.apellidos || '' }}
                                        </span>
                                    </div>
                                </div>

                                <!-- Bitácoras del Ticket -->
                                <div v-if="slotProps.item.bitacoras && slotProps.item.bitacoras.length > 0"
                                    class="mt-4 pl-0 md:pl-12">
                                    <div class="flex items-center gap-2 mb-3">
                                        <i class="pi pi-list text-surface-400 text-sm"></i>
                                        <span
                                            class="text-surface-600 dark:text-surface-400 text-xs md:text-sm font-bold uppercase tracking-wide">Intervenciones
                                            ({{ slotProps.item.bitacoras.length }})</span>
                                    </div>

                                    <!-- Contenedor con línea vertical conectora -->
                                    <div
                                        class="relative pl-4 md:pl-6 border-l-2 border-blue-300 dark:border-blue-700 ml-1 md:ml-2">
                                        <div v-for="(bitacora, idx) in slotProps.item.bitacoras" :key="idx"
                                            class="relative mb-4 last:mb-0">
                                            <!-- Punto de conexión -->
                                            <div
                                                class="absolute -left-[1.6rem] top-3 w-4 h-4 bg-blue-400 dark:bg-blue-600 rounded-full border-2 border-white dark:border-surface-900">
                                            </div>

                                            <!-- Tarjeta de bitácora -->
                                            <div
                                                class="bg-white dark:bg-surface-800 rounded-lg p-3 md:p-4 shadow-sm border border-surface-200 dark:border-surface-700 hover:shadow-md transition-shadow">
                                                <div
                                                    class="flex flex-col sm:flex-row justify-between items-start gap-1 mb-2">
                                                    <div class="flex items-center gap-2">
                                                        <i class="pi pi-user-edit text-blue-500 text-sm"></i>
                                                        <span
                                                            class="text-xs md:text-sm font-bold text-surface-900 dark:text-surface-0">{{
                                                                bitacora.tecnico_nombre }}</span>
                                                    </div>
                                                    <span class="text-xs text-surface-500">{{ new
                                                        Date(bitacora.fecha_registro).toLocaleString('es-MX')
                                                        }}</span>
                                                </div>
                                                <p
                                                    class="text-xs md:text-sm text-surface-700 dark:text-surface-300 mb-3 pl-0 md:pl-6">
                                                    {{ bitacora.descripcion_trabajo }}</p>
                                                <div class="flex flex-wrap gap-2 pl-0 md:pl-6">
                                                    <Tag :value="bitacora.tipo_intervencion" severity="secondary"
                                                        class="text-xs" icon="pi pi-cog" />
                                                    <Tag :value="bitacora.resultado_intervencion"
                                                        :severity="bitacora.resultado_intervencion === 'exitosa' ? 'success' : bitacora.resultado_intervencion === 'parcial' ? 'warn' : 'danger'"
                                                        class="text-xs"
                                                        :icon="bitacora.resultado_intervencion === 'exitosa' ? 'pi pi-check-circle' : 'pi pi-info-circle'" />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </Timeline>
                </div>
            </div>
            <template #footer>
                <Button label="Levantar Incidencia" icon="pi pi-exclamation-triangle" severity="danger"
                    @click="levantarIncidencia" :loading="loading" />
                <Button label="Cerrar" icon="pi pi-times" text @click="detalleDialog = false" />
            </template>
        </Dialog>
    </div>
</template>

<style scoped>
/* ── Celdas del grid ── */
.mapa-celda {
    background: var(--p-surface-50, #f8fafc);
    border: 1px solid var(--p-surface-200, #e2e8f0);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    min-width: 48px;
    min-height: 48px;
    transition: background 0.15s;
}

.dark .mapa-celda {
    background: var(--p-surface-800, #1e293b);
    border-color: var(--p-surface-700, #334155);
}

.mapa-celda:hover {
    background: var(--p-primary-50, #eff6ff);
}

.dark .mapa-celda:hover {
    background: var(--p-surface-700, #334155);
}

.celda-drop-target {
    background: var(--p-primary-100, #dbeafe) !important;
    border: 2px dashed var(--p-primary-400, #60a5fa) !important;
}

/* Etiqueta de coordenadas (visible al hover) */
.celda-coords {
    position: absolute;
    top: 2px;
    left: 3px;
    font-size: 9px;
    color: var(--p-surface-300, #cbd5e1);
    pointer-events: none;
    user-select: none;
    line-height: 1;
}

.mapa-celda:hover .celda-coords {
    color: var(--p-surface-500, #64748b);
}

/* ── Chip de máquina ── */
.maquina-chip {
    width: 44px;
    height: 44px;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2px;
    gap: 1px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0, 0, 0, .3);
    transition: transform 0.12s, box-shadow 0.12s, opacity 0.15s;
    user-select: none;
}

.maquina-chip:hover {
    transform: scale(1.08);
    box-shadow: 0 4px 12px rgba(0, 0, 0, .3);
    z-index: 10;
}

.maquina-chip:active {
    transform: scale(0.96);
}

.maquina-uid {
    font-size: 12px;
    font-weight: 800;
    text-align: center;
    line-height: 1.1;
    max-width: 42px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    letter-spacing: -0.4px;
}

.maquina-sub {
    font-size: 7px;
    opacity: 0.8;
    text-align: center;
    max-width: 42px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Timeline: ocultar lado vacío, mantener línea con marcadores */
:deep(.p-timeline-event-opposite) {
    display: none !important;
}

:deep(.p-timeline-event-content) {
    width: 100% !important;
    padding-left: 1rem !important;
}

/* ── Tiles de info en el diálogo ── */
.info-tile {
    background: white;
    border: 1px solid var(--p-surface-200, #e2e8f0);
    border-radius: 8px;
    padding: 10px 12px;
}

.dark .info-tile {
    background: var(--p-surface-800, #1e293b);
    border-color: var(--p-surface-700, #334155);
}

.info-tile-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 600;
    color: var(--p-surface-500, #64748b);
    margin-bottom: 4px;
}

.info-tile-label i {
    font-size: 12px;
}

.info-tile-value {
    font-size: 13px;
    font-weight: 600;
    color: var(--p-surface-900, #0f172a);
    display: block;
}

.dark .info-tile-value {
    color: var(--p-surface-0, #f8fafc);
}
</style>
