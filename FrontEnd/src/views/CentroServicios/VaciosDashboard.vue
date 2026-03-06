<template>
  <div class="p-4 md:p-6 flex flex-col gap-6">

    <!-- ══════════════════════  HEADER  ══════════════════════ -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-surface-800 dark:text-surface-100">
          Gestión de Vacíos
        </h1>
        <p class="text-sm text-surface-500 mt-1">
          Reembolsos forenses por errores de red / software en carga de máquinas
        </p>
      </div>
      <div class="flex gap-2 flex-wrap">
        <Button
          icon="pi pi-refresh"
          severity="secondary"
          outlined
          @click="cargarTickets"
          :loading="cargando"
          v-tooltip.top="'Actualizar'"
        />
        <Button
          v-if="permisos.puedeCrear"
          label="Nuevo Vacío"
          icon="pi pi-plus"
          @click="abrirFormulario"
        />
      </div>
    </div>

    <!-- ══════════════════════  TARJETAS DE ESTADÍSTICAS  ══════════════════════ -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      <div
        v-for="stat in estadisticasCards"
        :key="stat.label"
        class="flex flex-col items-center justify-center bg-white dark:bg-surface-800 rounded-xl shadow-sm border border-surface-200 dark:border-surface-700 p-4 gap-1"
      >
        <span :class="['text-2xl font-bold', stat.colorClass]">{{ stats[stat.key] ?? 0 }}</span>
        <span class="text-xs text-surface-500 text-center">{{ stat.label }}</span>
      </div>
    </div>

    <!-- ══════════════════════  FILTROS RÁPIDOS  ══════════════════════ -->
    <div class="flex flex-wrap gap-2 items-center">
      <span class="font-medium text-sm text-surface-600">Filtrar:</span>
      <Button
        v-for="filtro in filtrosRapidos"
        :key="filtro.value"
        :label="filtro.label"
        :severity="filtroActivo === filtro.value ? 'primary' : 'secondary'"
        size="small"
        outlined
        @click="aplicarFiltro(filtro.value)"
      />
    </div>

    <!-- ══════════════════════  DATA TABLE  ══════════════════════ -->
    <DataTable
      ref="dt"
      v-model:filters="filtros"
      :value="ticketsFiltrados"
      :loading="cargando"
      paginator
      :rows="15"
      :rowsPerPageOptions="[10, 15, 25, 50]"
      filterDisplay="menu"
      sortField="fecha_creacion"
      :sortOrder="-1"
      removableSort
      class="shadow-sm rounded-xl overflow-hidden"
      responsiveLayout="scroll"
      stripedRows
      dataKey="id"
    >
      <!-- Toolbar del DataTable -->
      <template #header>
        <div class="flex justify-between items-center gap-3 flex-wrap">
          <span class="text-sm font-semibold text-surface-600">
            {{ ticketsFiltrados.length }} ticket(s)
          </span>
          <IconField>
            <InputIcon class="pi pi-search" />
            <InputText
              v-model="filtros['global'].value"
              placeholder="Buscar por cliente, máquina…"
              class="text-sm"
            />
          </IconField>
        </div>
      </template>

      <!-- ID -->
      <Column field="id" header="#" sortable style="width: 60px">
        <template #body="{ data }">
          <span class="text-xs font-mono text-surface-400">#{{ data.id }}</span>
        </template>
      </Column>

      <!-- Fecha -->
      <Column field="fecha_creacion" header="Fecha" sortable style="min-width: 130px">
        <template #body="{ data }">
          <span class="text-sm">{{ formatFecha(data.fecha_creacion) }}</span>
        </template>
      </Column>

      <!-- Casino / Máquina -->
      <Column field="casino_nombre" header="Casino / Máquina" sortable style="min-width: 160px">
        <template #body="{ data }">
          <div class="flex flex-col">
            <span class="font-semibold text-sm">{{ data.casino_nombre }}</span>
            <span class="text-xs text-surface-500">{{ data.maquina_uid }}</span>
          </div>
        </template>
      </Column>

      <!-- Cliente -->
      <Column field="cliente_nombre" header="Cliente" sortable style="min-width: 130px">
        <template #body="{ data }">
          <span class="text-sm">{{ data.cliente_nombre }}</span>
        </template>
      </Column>

      <!-- Monto -->
      <Column field="monto_extraviado" header="Monto ($)" sortable style="min-width: 110px">
        <template #body="{ data }">
          <span class="font-bold text-primary-600">${{ Number(data.monto_extraviado).toFixed(2) }}</span>
        </template>
      </Column>

      <!-- Estado Operativo -->
      <Column field="estado_operativo" header="Estado Operativo" style="min-width: 170px">
        <template #body="{ data }">
          <Tag
            :value="data.estado_operativo_display"
            :severity="severidadOperativo(data.estado_operativo)"
            class="text-xs"
          />
        </template>
      </Column>

      <!-- Estado Auditoría -->
      <Column field="estado_auditoria" header="Auditoría" style="min-width: 180px">
        <template #body="{ data }">
          <Tag
            :value="data.estado_auditoria_display"
            :severity="severidadAuditoria(data.estado_auditoria)"
            class="text-xs"
          />
        </template>
      </Column>

      <!-- Técnico -->
      <Column field="tecnico_creador_nombre" header="Técnico" style="min-width: 130px">
        <template #body="{ data }">
          <span class="text-sm">{{ data.tecnico_creador_nombre || '—' }}</span>
        </template>
      </Column>

      <!-- Motivo -->
      <Column field="motivo_falla_display" header="Motivo" style="min-width: 160px">
        <template #body="{ data }">
          <span class="text-sm text-surface-600">{{ data.motivo_falla_display }}</span>
        </template>
      </Column>

      <!-- Acciones -->
      <Column header="Acciones" style="min-width: 140px; text-align: right">
        <template #body="{ data }">
          <div class="flex gap-2 justify-end">
            <!-- Ver detalle: siempre disponible -->
            <Button
              icon="pi pi-eye"
              size="small"
              severity="info"
              outlined
              rounded
              @click="verDetalle(data)"
              v-tooltip.top="'Ver detalle y fotos'"
            />
            <!-- Auditar: solo para Gerencia/Admin, solo si está pendiente -->
            <Button
              v-if="permisos.puedeAuditar && data.estado_auditoria === 'pendiente_revision'"
              icon="pi pi-shield"
              size="small"
              severity="warning"
              rounded
              @click="abrirAuditoria(data)"
              v-tooltip.top="'Emitir veredicto de auditoría'"
            />
            <!-- Confirmar Carga: solo técnico/admin, solo si está autorizado -->
            <Button
              v-if="permisos.puedeCrear && data.estado_operativo === 'autorizado_carga'"
              icon="pi pi-check-circle"
              size="small"
              severity="success"
              rounded
              @click="confirmarCarga(data)"
              v-tooltip.top="'Confirmar recarga al cliente'"
            />
          </div>
        </template>
      </Column>

      <template #empty>
        <div class="flex flex-col items-center gap-2 py-10 text-surface-400">
          <i class="pi pi-inbox text-4xl" />
          <span>No se encontraron tickets de vacíos</span>
        </div>
      </template>
    </DataTable>

    <!-- ══════════════  DIALOG: DETALLE + FOTOS  ══════════════ -->
    <Dialog
      v-model:visible="detalleVisible"
      modal
      header="Detalle del Ticket de Vacío"
      :style="{ width: '820px', maxWidth: '98vw' }"
    >
      <div v-if="ticketDetalle" class="flex flex-col gap-5">

        <!-- Cabecera de estados -->
        <div class="flex gap-3 flex-wrap">
          <Tag
            :value="ticketDetalle.estado_operativo_display"
            :severity="severidadOperativo(ticketDetalle.estado_operativo)"
          />
          <Tag
            :value="ticketDetalle.estado_auditoria_display"
            :severity="severidadAuditoria(ticketDetalle.estado_auditoria)"
          />
        </div>

        <!-- Info básica -->
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          <div v-for="item in campoDetalle(ticketDetalle)" :key="item.label" class="flex flex-col gap-0.5">
            <span class="text-surface-500 text-xs uppercase tracking-wide">{{ item.label }}</span>
            <span class="font-semibold">{{ item.valor }}</span>
          </div>
        </div>

        <Divider />

        <!-- Fotos de evidencia -->
        <div>
          <p class="font-bold text-sm mb-3">Evidencias Fotográficas</p>
          <div class="grid grid-cols-2 gap-3">
            <div
              v-for="foto in fotosDetalle(ticketDetalle)"
              :key="foto.campo"
              class="flex flex-col gap-1"
            >
              <span class="text-xs font-medium text-surface-500">{{ foto.label }}</span>
              <a :href="foto.url" target="_blank" rel="noopener">
                <img
                  :src="foto.url"
                  :alt="foto.label"
                  class="rounded-lg border border-surface-200 max-h-48 w-full object-cover hover:opacity-90 transition-opacity cursor-zoom-in"
                />
              </a>
            </div>
          </div>
        </div>

        <Divider />

        <!-- Explicación detallada -->
        <div>
          <p class="font-bold text-sm mb-1">Explicación Técnica</p>
          <p class="text-sm text-surface-700 dark:text-surface-300 whitespace-pre-line">
            {{ ticketDetalle.explicacion_detallada }}
          </p>
        </div>

        <!-- Firma del auditor (si ya fue auditado) -->
        <div
          v-if="ticketDetalle.gerente_auditor_nombre"
          class="mt-2 p-3 rounded-lg bg-surface-50 dark:bg-surface-700 border border-surface-200 text-sm"
        >
          <span class="font-semibold">Auditado por:</span>
          {{ ticketDetalle.gerente_auditor_nombre }}
          <span v-if="ticketDetalle.fecha_auditoria" class="text-surface-500 ml-2">
            — {{ formatFecha(ticketDetalle.fecha_auditoria) }}
          </span>
        </div>
      </div>
    </Dialog>

    <!-- ══════════════  DIALOG: EMITIR VEREDICTO  ══════════════ -->
    <Dialog
      v-model:visible="auditoriaVisible"
      modal
      header="Emitir Veredicto de Auditoría"
      :style="{ width: '520px', maxWidth: '98vw' }"
    >
      <div v-if="ticketAuditar" class="flex flex-col gap-4">
        <!-- Resumen del ticket -->
        <div class="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 text-sm">
          <p>
            <strong>Ticket #{{ ticketAuditar.id }}</strong> —
            {{ ticketAuditar.cliente_nombre }} —
            <strong class="text-primary-600">${{ Number(ticketAuditar.monto_extraviado).toFixed(2) }}</strong>
          </p>
          <p class="text-surface-500 mt-1">{{ ticketAuditar.casino_nombre }} · {{ ticketAuditar.maquina_uid }}</p>
        </div>

        <!-- Fotos compactas en el dialog de auditoría -->
        <div class="grid grid-cols-2 gap-2">
          <div
            v-for="foto in fotosDetalle(ticketAuditar)"
            :key="foto.campo"
            class="flex flex-col gap-1"
          >
            <span class="text-xs text-surface-500">{{ foto.label }}</span>
            <a :href="foto.url" target="_blank" rel="noopener">
              <img
                :src="foto.url"
                :alt="foto.label"
                class="rounded-md border border-surface-200 max-h-28 w-full object-cover cursor-zoom-in"
              />
            </a>
          </div>
        </div>

        <Divider />

        <!-- Selección de veredicto -->
        <div class="flex flex-col gap-1">
          <label class="font-semibold text-sm">Veredicto <span class="text-red-500">*</span></label>
          <div class="flex gap-3">
            <div
              v-for="op in opcionesVeredicto"
              :key="op.value"
              class="flex items-center gap-2 cursor-pointer"
            >
              <RadioButton
                v-model="formAuditoria.veredicto"
                :value="op.value"
                :inputId="op.value"
              />
              <label :for="op.value" class="cursor-pointer text-sm">{{ op.label }}</label>
            </div>
          </div>
          <small v-if="errorVeredicto" class="p-error">{{ errorVeredicto }}</small>
        </div>

        <!-- Comentario opcional -->
        <div class="flex flex-col gap-1">
          <label class="font-semibold text-sm">Comentario (opcional)</label>
          <Textarea
            v-model="formAuditoria.comentario_auditoria"
            rows="3"
            placeholder="Observaciones del veredicto…"
            autoResize
            class="w-full"
          />
        </div>

        <div class="flex justify-end gap-2 mt-2">
          <Button label="Cancelar" severity="secondary" outlined @click="auditoriaVisible = false" />
          <Button
            :label="formAuditoria.veredicto === 'auditado_aprobado' ? 'Aprobar Auditoría' : 'Rechazar / Investigar'"
            :severity="formAuditoria.veredicto === 'auditado_aprobado' ? 'success' : 'danger'"
            :icon="formAuditoria.veredicto === 'auditado_aprobado' ? 'pi pi-check' : 'pi pi-times'"
            :loading="guardandoAuditoria"
            @click="submitAuditoria"
          />
        </div>
      </div>
    </Dialog>

    <!-- Formulario de creación -->
    <VaciosStepperForm
      v-model="formularioVisible"
      @ticket-creado="onTicketCreado"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { FilterMatchMode } from '@primevue/core/api';
import api, { getUser } from '@/service/api';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import VaciosStepperForm from '@/components/vacios/VaciosStepperForm.vue';
import { parseServerError } from '@/utils/parseServerError';

// ── Composables ───────────────────────────────────────────────────────────────
const toast = useToast();
const confirm = useConfirm();

// ── Estado global ─────────────────────────────────────────────────────────────
const tickets = ref([]);
const cargando = ref(false);
const dt = ref();
const casinoFiltro = ref(null);

// ── Usuario y permisos ────────────────────────────────────────────────────────
const usuario = computed(() => getUser());
const rolUsuario = computed(() => (usuario.value?.rol_nombre || '').toUpperCase());

const ROLES_AUDITORES = ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUPERVISOR SALA', 'SUP SISTEMAS'];
const ROLES_TECNICOS = ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA'];

const permisos = computed(() => ({
  puedeCrear: ROLES_TECNICOS.includes(rolUsuario.value),
  puedeAuditar: ROLES_AUDITORES.includes(rolUsuario.value),
}));

// ── Estadísticas ──────────────────────────────────────────────────────────────
const stats = ref({
  total: 0,
  pendientes_autorizacion: 0,
  autorizados: 0,
  carga_realizada: 0,
  pendientes_auditoria: 0,
  rechazados: 0,
});

const estadisticasCards = [
  { key: 'total',                    label: 'Total',                     colorClass: 'text-surface-700' },
  { key: 'pendientes_autorizacion',  label: 'Pend. Autorización',        colorClass: 'text-blue-500' },
  { key: 'autorizados',              label: 'Autorizados',               colorClass: 'text-cyan-600' },
  { key: 'carga_realizada',          label: 'Carga Realizada',           colorClass: 'text-green-600' },
  { key: 'pendientes_auditoria',     label: 'Pend. Auditoría',           colorClass: 'text-yellow-600' },
  { key: 'rechazados',               label: 'Rechazados',                colorClass: 'text-red-500' },
];

// ── Filtros rápidos ───────────────────────────────────────────────────────────
const filtroActivo = ref('todos');
const filtrosRapidos = [
  { label: 'Todos',                  value: 'todos' },
  { label: 'Pend. Autorización',     value: 'pendiente_autorizacion' },
  { label: 'Autorizado para Carga',  value: 'autorizado_carga' },
  { label: 'Carga Realizada',        value: 'carga_realizada' },
  { label: 'Pend. Auditoría',        value: 'pendiente_auditoria' },
  { label: 'Rechazados',             value: 'rechazado' },
];

function aplicarFiltro(valor) {
  filtroActivo.value = valor;
}

const ticketsFiltrados = computed(() => {
  if (filtroActivo.value === 'todos') return tickets.value;
  if (filtroActivo.value === 'pendiente_auditoria')
    return tickets.value.filter((t) => t.estado_auditoria === 'pendiente_revision');
  if (filtroActivo.value === 'rechazado')
    return tickets.value.filter((t) => t.estado_auditoria === 'rechazado_investigacion');
  return tickets.value.filter((t) => t.estado_operativo === filtroActivo.value);
});

// ── Filtros del DataTable ─────────────────────────────────────────────────────
const filtros = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
});

// ── Carga de datos ────────────────────────────────────────────────────────────
async function cargarTickets() {
  cargando.value = true;
  try {
    const res = await api.get('vacios/tickets/');
    const data = res.data?.results ?? res.data ?? [];
    tickets.value = Array.isArray(data) ? data : data.tickets ?? [];

    // Calcular estadísticas localmente
    stats.value = {
      total: tickets.value.length,
      pendientes_autorizacion: tickets.value.filter((t) => t.estado_operativo === 'pendiente_autorizacion').length,
      autorizados: tickets.value.filter((t) => t.estado_operativo === 'autorizado_carga').length,
      carga_realizada: tickets.value.filter((t) => t.estado_operativo === 'carga_realizada').length,
      pendientes_auditoria: tickets.value.filter((t) => t.estado_auditoria === 'pendiente_revision').length,
      rechazados: tickets.value.filter((t) => t.estado_auditoria === 'rechazado_investigacion').length,
    };
  } catch (err) {
    console.error('Error al cargar tickets de vacíos', err);
    toast.add({ severity: 'error', summary: 'Error', detail: parseServerError(err, 'No se pudieron cargar los tickets de vacíos.'), life: 5000 });
  } finally {
    cargando.value = false;
  }
}

onMounted(cargarTickets);

// ── Severidades / colores de badges ──────────────────────────────────────────
/**
 * Colores del estado operativo:
 *   Azul  → pendiente_autorizacion
 *   Info  → autorizado_carga
 *   Verde → carga_realizada
 */
function severidadOperativo(estado) {
  return {
    pendiente_autorizacion: 'info',
    autorizado_carga: 'secondary',
    carga_realizada: 'success',
  }[estado] ?? 'secondary';
}

/**
 * Colores del estado de auditoría:
 *   Azul (info)    → pendiente_revision
 *   Verde          → auditado_aprobado
 *   Rojo (danger)  → rechazado_investigacion
 */
function severidadAuditoria(estado) {
  return {
    pendiente_revision: 'warn',
    auditado_aprobado: 'success',
    rechazado_investigacion: 'danger',
  }[estado] ?? 'secondary';
}

// ── Helpers de formato ────────────────────────────────────────────────────────
function formatFecha(isoStr) {
  if (!isoStr) return '—';
  const d = new Date(isoStr);
  return d.toLocaleDateString('es-MX', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// ── Modal Detalle ─────────────────────────────────────────────────────────────
const detalleVisible = ref(false);
const ticketDetalle = ref(null);

function verDetalle(ticket) {
  ticketDetalle.value = ticket;
  detalleVisible.value = true;
}

function campoDetalle(t) {
  return [
    { label: 'Casino',         valor: t.casino_nombre },
    { label: 'Máquina',        valor: t.maquina_uid },
    { label: 'Cliente',        valor: t.cliente_nombre },
    { label: 'Monto',          valor: `$${Number(t.monto_extraviado).toFixed(2)}` },
    { label: 'Motivo',         valor: t.motivo_falla_display },
    { label: 'Técnico',        valor: t.tecnico_creador_nombre || '—' },
    { label: 'Creado',         valor: formatFecha(t.fecha_creacion) },
    { label: 'Auditor',        valor: t.gerente_auditor_nombre || 'Sin auditar' },
    { label: 'Fecha Auditoría',valor: formatFecha(t.fecha_auditoria) },
  ];
}

function fotosDetalle(t) {
  const base = api.defaults.baseURL?.replace('/api/', '') ?? '';
  return [
    { campo: 'foto_ultimas_operaciones', label: 'Últimas Operaciones', url: t.foto_ultimas_operaciones ? (t.foto_ultimas_operaciones.startsWith('http') ? t.foto_ultimas_operaciones : `${base}${t.foto_ultimas_operaciones}`) : '' },
    { campo: 'foto_carga_sistema',        label: 'Carga en Sistema',   url: t.foto_carga_sistema        ? (t.foto_carga_sistema.startsWith('http')        ? t.foto_carga_sistema        : `${base}${t.foto_carga_sistema}`)        : '' },
    { campo: 'foto_seguimiento_slot',     label: 'Seguimiento Slot',   url: t.foto_seguimiento_slot     ? (t.foto_seguimiento_slot.startsWith('http')     ? t.foto_seguimiento_slot     : `${base}${t.foto_seguimiento_slot}`)     : '' },
    { campo: 'foto_recarga_error',        label: 'Recarga Error',      url: t.foto_recarga_error        ? (t.foto_recarga_error.startsWith('http')        ? t.foto_recarga_error        : `${base}${t.foto_recarga_error}`)        : '' },
  ].filter((f) => f.url);
}

// ── Modal Auditoría ───────────────────────────────────────────────────────────
const auditoriaVisible = ref(false);
const ticketAuditar = ref(null);
const guardandoAuditoria = ref(false);
const errorVeredicto = ref('');

const formAuditoria = ref({ veredicto: 'auditado_aprobado', comentario_auditoria: '' });

const opcionesVeredicto = [
  { label: 'Aprobar / Legítimo',         value: 'auditado_aprobado' },
  { label: 'Rechazar / Investigación',   value: 'rechazado_investigacion' },
];

function abrirAuditoria(ticket) {
  ticketAuditar.value = ticket;
  formAuditoria.value = { veredicto: 'auditado_aprobado', comentario_auditoria: '' };
  errorVeredicto.value = '';
  auditoriaVisible.value = true;
}

async function submitAuditoria() {
  if (!formAuditoria.value.veredicto) {
    errorVeredicto.value = 'Selecciona un veredicto.';
    return;
  }
  errorVeredicto.value = '';
  guardandoAuditoria.value = true;

  try {
    const res = await api.post(
      `vacios/tickets/${ticketAuditar.value.id}/emitir_veredicto/`,
      formAuditoria.value,
    );

    // Actualizar el ticket en la lista local
    const idx = tickets.value.findIndex((t) => t.id === res.data.id);
    if (idx !== -1) tickets.value.splice(idx, 1, res.data);

    const esAprobado = res.data.estado_auditoria === 'auditado_aprobado';
    toast.add({
      severity: esAprobado ? 'success' : 'error',
      summary: esAprobado ? 'Ticket Aprobado' : 'Ticket Rechazado',
      detail: `Veredicto registrado para Vacío #${res.data.id}`,
      life: 5000,
    });

    auditoriaVisible.value = false;
    // Recalcular estadísticas
    await cargarTickets();
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: err.response?.data?.detail || 'No se pudo emitir el veredicto.',
      life: 5000,
    });
  } finally {
    guardandoAuditoria.value = false;
  }
}

// ── Confirmar Carga ───────────────────────────────────────────────────────────
async function confirmarCarga(ticket) {
  confirm.require({
    message: `¿Confirmas que realizaste la recarga de $${Number(ticket.monto_extraviado).toFixed(2)} al cliente ${ticket.cliente_nombre}?`,
    header: 'Confirmar Recarga',
    icon: 'pi pi-check-circle',
    acceptLabel: 'Sí, recarga hecha',
    rejectLabel: 'Cancelar',
    accept: async () => {
      try {
        const res = await api.patch(`vacios/tickets/${ticket.id}/confirmar_carga/`);
        const idx = tickets.value.findIndex((t) => t.id === res.data.id);
        if (idx !== -1) tickets.value.splice(idx, 1, res.data);
        toast.add({ severity: 'success', summary: 'Recarga Confirmada', detail: `Vacío #${res.data.id} marcado como "Carga Realizada".`, life: 4000 });
        await cargarTickets();
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'No se pudo confirmar la carga.', life: 4000 });
      }
    },
  });
}

// ── Formulario de creación ────────────────────────────────────────────────────
const formularioVisible = ref(false);

function abrirFormulario() {
  formularioVisible.value = true;
}

function onTicketCreado(nuevoTicket) {
  tickets.value.unshift(nuevoTicket);
  cargarTickets();
  toast.add({
    severity: 'success',
    summary: 'Vacío registrado',
    detail: `Ticket #${nuevoTicket.id} creado con estado: ${nuevoTicket.estado_operativo_display}`,
    life: 5000,
  });
}
</script>
