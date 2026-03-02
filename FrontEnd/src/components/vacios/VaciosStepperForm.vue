<template>
  <Dialog
    v-model:visible="visible"
    modal
    :style="{ width: '780px', maxWidth: '98vw' }"
    :closable="!guardando"
    header="Nuevo Ticket de Vacío"
    class="vacios-stepper-dialog"
  >
    <!-- ─────────────────────────────  STEPPER PrimeVue 4  ──────────────────── -->
    <Stepper :value="pasoActivo" linear class="w-full">

      <!-- Cabecera de pasos -->
      <StepList>
        <Step value="1">Datos</Step>
        <Step value="2">Evidencias</Step>
        <Step value="3">Resolución</Step>
      </StepList>

      <!-- Paneles de contenido -->
      <StepPanels>

        <!-- ══════════  PASO 1 · Datos del Evento  ══════════ -->
        <StepPanel value="1">
          <div class="grid grid-cols-1 gap-4 mt-4">

            <!-- Máquina -->
            <div class="flex flex-col gap-1">
              <label class="font-semibold text-sm">Máquina <span class="text-red-500">*</span></label>
              <Select
                v-model="form.maquina"
                :options="maquinas"
                optionLabel="uid_sala"
                optionValue="id"
                placeholder="Seleccionar máquina"
                filter
                showClear
                :invalid="!!errores.maquina"
                class="w-full"
              >
                <template #option="{ option }">
                  <span>{{ option.uid_sala }} — {{ option.modelo_nombre }}</span>
                </template>
              </Select>
              <small v-if="errores.maquina" class="p-error">{{ errores.maquina }}</small>
            </div>

            <!-- Casino de la sesión (solo informativo) -->
            <div class="flex flex-col gap-1">
              <label class="font-semibold text-sm">Casino (sesión actual)</label>
              <InputText :value="casinoSesionNombre" disabled class="w-full opacity-60" />
            </div>

            <!-- Nombre del Cliente -->
            <div class="flex flex-col gap-1">
              <label class="font-semibold text-sm">Nombre del Cliente <span class="text-red-500">*</span></label>
              <InputText
                v-model="form.cliente_nombre"
                placeholder="Nombre completo del cliente"
                :invalid="!!errores.cliente_nombre"
                class="w-full"
              />
              <small v-if="errores.cliente_nombre" class="p-error">{{ errores.cliente_nombre }}</small>
            </div>

            <!-- Monto Extraviado -->
            <div class="flex flex-col gap-1">
              <label class="font-semibold text-sm">Monto a Recargar ($) <span class="text-red-500">*</span></label>
              <InputNumber
                v-model="form.monto_extraviado"
                mode="currency"
                currency="MXN"
                locale="es-MX"
                :min="1.00"
                :maxFractionDigits="2"
                :invalid="!!errores.monto_extraviado"
                class="w-full"
              />
              <small v-if="errores.monto_extraviado" class="p-error">{{ errores.monto_extraviado }}</small>
              <small v-if="alertaUmbral" class="text-yellow-600 font-medium">
                ⚠ Este monto supera el umbral del casino y requerirá autorización gerencial.
              </small>
            </div>
          </div>

          <div class="flex justify-end mt-6">
            <Button label="Siguiente" icon="pi pi-arrow-right" iconPos="right" @click="validarPaso1" />
          </div>
        </StepPanel>

        <!-- ══════════  PASO 2 · Evidencias Fotográficas  ══════════ -->
        <StepPanel value="2">
          <p class="text-sm text-surface-500 mt-2 mb-4">
            Las <strong>4 imágenes son obligatorias</strong>. Adjunta capturas claras de pantalla o fotos que demuestren el vacío.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div
              v-for="foto in fotosConfig"
              :key="foto.campo"
              class="flex flex-col gap-2 border border-surface-200 rounded-lg p-3"
            >
              <span class="font-semibold text-sm">{{ foto.label }} <span class="text-red-500">*</span></span>
              <span class="text-xs text-surface-500">{{ foto.descripcion }}</span>

              <FileUpload
                :name="foto.campo"
                accept="image/*"
                :maxFileSize="5000000"
                :auto="false"
                chooseLabel="Seleccionar Imagen"
                :showUploadButton="false"
                :showCancelButton="false"
                @select="(e) => onFotoSeleccionada(e, foto.campo)"
                mode="basic"
                :class="errores[foto.campo] ? 'p-invalid' : ''"
              />

              <!-- Preview compacto -->
              <div v-if="previews[foto.campo]" class="mt-1">
                <img
                  :src="previews[foto.campo]"
                  :alt="foto.label"
                  class="rounded-md max-h-28 w-full object-cover border border-surface-300"
                />
              </div>
              <small v-if="errores[foto.campo]" class="p-error">{{ errores[foto.campo] }}</small>
            </div>
          </div>

          <div class="flex justify-between mt-6">
            <Button label="Anterior" icon="pi pi-arrow-left" severity="secondary" outlined @click="pasoActivo = '1'" />
            <Button label="Siguiente" icon="pi pi-arrow-right" iconPos="right" @click="validarPaso2" />
          </div>
        </StepPanel>

        <!-- ══════════  PASO 3 · Resolución / Dictamen  ══════════ -->
        <StepPanel value="3">
          <div class="grid grid-cols-1 gap-4 mt-4">

            <!-- Motivo de Falla -->
            <div class="flex flex-col gap-1">
              <label class="font-semibold text-sm">Motivo de Falla <span class="text-red-500">*</span></label>
              <Select
                v-model="form.motivo_falla"
                :options="motivosFalla"
                optionLabel="label"
                optionValue="value"
                placeholder="Seleccionar motivo"
                :invalid="!!errores.motivo_falla"
                class="w-full"
              />
              <small v-if="errores.motivo_falla" class="p-error">{{ errores.motivo_falla }}</small>
            </div>

            <!-- Explicación Detallada -->
            <div class="flex flex-col gap-1">
              <label class="font-semibold text-sm">Explicación Detallada <span class="text-red-500">*</span></label>
              <Textarea
                v-model="form.explicacion_detallada"
                rows="5"
                placeholder="Describe con precisión técnica lo que ocurrió: hora aproximada, secuencia de eventos, acciones tomadas, etc."
                :invalid="!!errores.explicacion_detallada"
                class="w-full"
                autoResize
              />
              <small v-if="errores.explicacion_detallada" class="p-error">{{ errores.explicacion_detallada }}</small>
            </div>
          </div>

          <!-- ── Resumen final ── -->
          <div class="mt-5 p-4 bg-surface-50 rounded-xl border border-surface-200">
            <p class="font-bold text-sm mb-2">Resumen del Ticket</p>
            <div class="grid grid-cols-2 gap-x-6 gap-y-1 text-sm">
              <span class="text-surface-500">Máquina:</span>
              <span>{{ maquinaNombreResumen }}</span>
              <span class="text-surface-500">Cliente:</span>
              <span>{{ form.cliente_nombre || '—' }}</span>
              <span class="text-surface-500">Monto:</span>
              <span class="font-semibold text-primary-600">${{ form.monto_extraviado?.toFixed(2) || '0.00' }}</span>
              <span class="text-surface-500">Fotos:</span>
              <span>{{ fotosAdjuntadas }}/4 adjuntadas</span>
            </div>
          </div>

          <div class="flex justify-between mt-6">
            <Button label="Anterior" icon="pi pi-arrow-left" severity="secondary" outlined @click="pasoActivo = '2'" />
            <Button
              label="Crear Ticket de Vacío"
              icon="pi pi-check"
              iconPos="right"
              :loading="guardando"
              @click="submitForm"
            />
          </div>
        </StepPanel>

      </StepPanels>
    </Stepper>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import api, { getUser } from '@/service/api';
import { useToast } from 'primevue/usetoast';

// ── Props & Emits ─────────────────────────────────────────────────────────────
const props = defineProps({
  modelValue: { type: Boolean, default: false },
});
const emit = defineEmits(['update:modelValue', 'ticket-creado']);

// ── Dialog visibility ─────────────────────────────────────────────────────────
const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
});

// ── Composables ───────────────────────────────────────────────────────────────
const toast = useToast();

// ── Datos de sesión ───────────────────────────────────────────────────────────
const usuarioSesion = getUser();
const casinoSesionId = usuarioSesion?.casino ?? null;
const casinoSesionNombre = usuarioSesion?.casino_nombre ?? usuarioSesion?.casino_display ?? String(casinoSesionId ?? '—');

// ── Estado del stepper (PrimeVue 4: value es string) ─────────────────────────
const pasoActivo = ref('1');

// ── Catálogos ─────────────────────────────────────────────────────────────────
const maquinas = ref([]);
const configCasino = ref(null);
const guardando = ref(false);

const motivosFalla = ref([
  { label: 'Error de Red / Timeout',           value: 'error_red' },
  { label: 'Caída del Sistema Central',        value: 'caida_sistema' },
  { label: 'Falla de Software en Máquina',     value: 'falla_software_maquina' },
  { label: 'Desconexión Brusca de Energía',    value: 'desconexion_brusca' },
  { label: 'Error de Billetero / Ticket',      value: 'error_billetero' },
  { label: 'Doble Cobro / Transacción Duplicada', value: 'doble_cobro' },
  { label: 'Otro (ver explicación)',           value: 'otro' },
]);

const fotosConfig = ref([
  {
    campo: 'foto_ultimas_operaciones',
    label: 'Últimas Operaciones',
    descripcion: 'Pantalla de las ultimas operaciones del cliente',
  },
  {
    campo: 'foto_carga_sistema',
    label: 'Carga en Sistema',
    descripcion: 'Pantalla de la carga realizada',
  },
  {
    campo: 'foto_seguimiento_slot',
    label: 'Seguimiento Slot',
    descripcion: 'Vista de seguimiento o historial del slot en el sistema',
  },
  {
    campo: 'foto_recarga_error',
    label: 'Error de Recarga',
    descripcion: 'Captura del mensaje de error mostrado durante la recarga',
  },
]);

// ── Formulario ────────────────────────────────────────────────────────────────
const formVacio = () => ({
  maquina: null,
  cliente_nombre: '',
  monto_extraviado: null,
  motivo_falla: null,
  explicacion_detallada: '',
});

const form = ref(formVacio());
const archivos = ref({});    // { campo: File }
const previews = ref({});    // { campo: dataURL }
const errores = ref({});

// ── Computadas ────────────────────────────────────────────────────────────────
const maquinaSeleccionada = computed(() =>
  maquinas.value.find((m) => m.id === form.value.maquina) || null,
);

const maquinaNombreResumen = computed(() =>
  maquinaSeleccionada.value
    ? `${maquinaSeleccionada.value.uid_sala} (${casinoSesionNombre})`
    : '—',
);

const fotosAdjuntadas = computed(() => Object.keys(archivos.value).length);

const alertaUmbral = computed(() => {
  if (!configCasino.value || form.value.monto_extraviado === null) return false;
  const cfg = configCasino.value;
  return cfg.siempre_requiere_autorizacion || form.value.monto_extraviado >= Number(cfg.umbral_autorizacion);
});

// ── Reset al abrir/cerrar ─────────────────────────────────────────────────────
watch(visible, (v) => {
  if (v) {
    form.value = formVacio();
    archivos.value = {};
    previews.value = {};
    errores.value = {};
    pasoActivo.value = '1';
    cargarMaquinas();
    cargarConfigCasino();
  }
});

// ── Carga de datos ────────────────────────────────────────────────────────────
async function cargarMaquinas() {
  if (!casinoSesionId) {
    toast.add({ severity: 'warn', summary: 'Sin casino', detail: 'Tu usuario no tiene un casino asignado.', life: 5000 });
    return;
  }
  try {
    const res = await api.get(`maquinas/lista-por-casino/${casinoSesionId}/`);
    // El endpoint devuelve { maquinas: [...] } igual que en Tickets.vue
    maquinas.value = res.data?.maquinas ?? res.data?.results ?? res.data ?? [];
  } catch (err) {
    console.error('Error al cargar máquinas del casino', err);
  }
}

async function cargarConfigCasino() {
  if (!casinoSesionId) return;
  try {
    const res = await api.get(`vacios/configuracion/por-casino/${casinoSesionId}/`);
    configCasino.value = res.data;
  } catch {
    // Si no hay configuración creada aún, se ignora (el backend usará defaults)
    configCasino.value = null;
  }
}

onMounted(() => {
  if (visible.value) { cargarMaquinas(); cargarConfigCasino(); }
});

// ── Manejo de fotos ───────────────────────────────────────────────────────────
function onFotoSeleccionada(event, campo) {
  const file = event.files?.[0];
  if (!file) return;
  archivos.value[campo] = file;
  const reader = new FileReader();
  reader.onload = (e) => { previews.value[campo] = e.target.result; };
  reader.readAsDataURL(file);
  // Limpiar error si existía
  if (errores.value[campo]) {
    const { [campo]: _removed, ...resto } = errores.value;
    errores.value = resto;
  }
}

// ── Validaciones por paso ─────────────────────────────────────────────────────
function validarPaso1() {
  const e = {};
  if (!form.value.maquina) e.maquina = 'Selecciona una máquina.';
  if (!form.value.cliente_nombre?.trim()) e.cliente_nombre = 'El nombre del cliente es obligatorio.';
  if (!form.value.monto_extraviado || form.value.monto_extraviado <= 0)
    e.monto_extraviado = 'Ingresa un monto mayor a $0.';
  errores.value = e;
  if (Object.keys(e).length === 0) pasoActivo.value = '2';
}

function validarPaso2() {
  const e = {};
  for (const foto of fotosConfig.value) {
    if (!archivos.value[foto.campo]) e[foto.campo] = 'Esta imagen es obligatoria.';
  }
  errores.value = e;
  if (Object.keys(e).length === 0) pasoActivo.value = '3';
}

// ── Envío del formulario ──────────────────────────────────────────────────────
async function submitForm() {
  const e = {};
  if (!form.value.motivo_falla) e.motivo_falla = 'Selecciona el motivo de falla.';
  if (!form.value.explicacion_detallada?.trim())
    e.explicacion_detallada = 'La explicación detallada es obligatoria.';
  errores.value = e;
  if (Object.keys(e).length > 0) return;

  guardando.value = true;
  try {
    // Construir FormData (multipart para imágenes)
    const payload = new FormData();

    // Campos de texto — casino siempre desde la sesión
    payload.append('maquina', form.value.maquina);
    payload.append('casino', casinoSesionId);
    payload.append('cliente_nombre', form.value.cliente_nombre.trim());
    payload.append('monto_extraviado', form.value.monto_extraviado);
    payload.append('motivo_falla', form.value.motivo_falla);
    payload.append('explicacion_detallada', form.value.explicacion_detallada.trim());

    // Archivos de evidencia
    for (const foto of fotosConfig.value) {
      if (archivos.value[foto.campo]) {
        payload.append(foto.campo, archivos.value[foto.campo]);
      }
    }

    const res = await api.post('vacios/tickets/', payload, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    toast.add({
      severity: 'success',
      summary: 'Ticket creado',
      detail: `Vacío #${res.data.id} registrado. Estado: ${res.data.estado_operativo_display}`,
      life: 5000,
    });

    emit('ticket-creado', res.data);
    visible.value = false;
  } catch (err) {
    const data = err.response?.data;
    if (data && typeof data === 'object') {
      // Mapear errores de campo del backend
      errores.value = Object.fromEntries(
        Object.entries(data).map(([k, v]) => [k, Array.isArray(v) ? v[0] : v])
      );
    }
    toast.add({
      severity: 'error',
      summary: 'Error al crear ticket',
      detail: 'Revisa los campos marcados e intenta de nuevo.',
      life: 5000,
    });
  } finally {
    guardando.value = false;
  }
}
</script>
