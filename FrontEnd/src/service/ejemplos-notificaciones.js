/**
 * ============================================================================
 * EJEMPLOS DE USO - NOTIFICATION SERVICE
 * ============================================================================
 * 
 * Este archivo contiene ejemplos prácticos de cómo usar el servicio de
 * notificaciones en componentes Vue.js del frontend NEXUS.
 * 
 * IMPORTANTE: Entender cómo funciona la tabla intermedia NotificacionUsuario
 * 
 * ============================================================================
 */

// ============================================================================
// IMPORTACIONES
// ============================================================================

// Opción 1: Importar funciones específicas (RECOMENDADO)
import { 
  fetchNotificaciones, 
  fetchNotificacionesNoLeidas,
  marcarNotificacionLeida,
  marcarTodasLeidas
} from '@/service/notificationService';

// Opción 2: Importar todo el servicio
import notificationService from '@/service/notificationService';
// Usar como: notificationService.fetchNotificaciones()


// ============================================================================
// EJEMPLO 1: COMPONENTE BÁSICO CON LISTA DE NOTIFICACIONES
// ============================================================================

/**
 * Este es el caso más común: mostrar lista de notificaciones
 * 
 * FLUJO:
 * ------
 * 1. Usuario hace login → localStorage guarda token
 * 2. Componente carga notificaciones con fetchNotificaciones()
 * 3. Backend filtra automáticamente por usuario/casino/rol
 * 4. Backend calcula campo 'leido' para cada notificación
 * 5. Frontend muestra lista con indicador visual (leído/no leído)
 * 6. Usuario hace clic → llama a marcarNotificacionLeida()
 * 7. Backend crea registro en NotificacionUsuario
 * 8. Próxima carga: la notificación aparece como 'leido: true'
 */

// ComponenteNotificaciones.vue
/*
<template>
  <div class="notificaciones-panel">
    <h2>Notificaciones</h2>
    
    <!-- Badge con count de no leídas -->
    <span class="badge" v-if="countNoLeidas > 0">
      {{ countNoLeidas }}
    </span>
    
    <!-- Lista de notificaciones -->
    <div 
      v-for="notif in notificaciones" 
      :key="notif.id"
      :class="['notificacion-item', { 'no-leida': !notif.leido }]"
      @click="handleClickNotificacion(notif)"
    >
      <div class="header">
        <span class="titulo">{{ notif.titulo }}</span>
        <span v-if="!notif.leido" class="badge-nuevo">NUEVO</span>
      </div>
      <p class="contenido">{{ notif.contenido }}</p>
      <span class="fecha">{{ formatFecha(notif.fecha_creacion) }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { fetchNotificaciones, marcarNotificacionLeida } from '@/service/notificationService';

const notificaciones = ref([]);
const countNoLeidas = ref(0);

// Cargar notificaciones al montar el componente
onMounted(async () => {
  await cargarNotificaciones();
});

// Función para cargar notificaciones
const cargarNotificaciones = async () => {
  const response = await fetchNotificaciones();
  
  if (response.success) {
    notificaciones.value = response.data;
    
    // Contar no leídas localmente
    countNoLeidas.value = response.data.filter(n => !n.leido).length;
  } else {
    console.error('Error al cargar notificaciones:', response.error);
  }
};

// Handler cuando usuario hace clic en una notificación
const handleClickNotificacion = async (notificacion) => {
  // Si ya está leída, no hacer nada
  if (notificacion.leido) {
    return;
  }
  
  // Marcar como leída
  const response = await marcarNotificacionLeida(notificacion.id);
  
  if (response.success) {
    console.log('✅ Notificación marcada como leída');
    
    // QUÉ PASÓ EN EL BACKEND:
    // ------------------------
    // 1. Backend recibió PATCH /notificaciones/{id}/marcar-leida/
    // 2. Verificó que el usuario tiene acceso a esa notificación
    // 3. Ejecutó: NotificacionUsuario.objects.get_or_create(
    //              notificacion=notificacion,
    //              usuario=request.user
    //            )
    // 4. Creó registro en la tabla intermedia:
    //    +----+--------------+------------+---------------------+
    //    | id | notificacion | usuario    | fecha_visto         |
    //    +----+--------------+------------+---------------------+
    //    | 1  | 16           | 3          | 2026-02-17 10:30:00 |
    //    +----+--------------+------------+---------------------+
    // 5. Retornó { success: true, message: "..." }
    
    // Actualizar localmente (optimista)
    notificacion.leido = true;
    countNoLeidas.value--;
    
    // O recargar todas las notificaciones (más seguro)
    // await cargarNotificaciones();
    
  } else {
    console.error('❌ Error al marcar como leída:', response.error);
  }
};

// Formatear fecha
const formatFecha = (fecha) => {
  return new Date(fecha).toLocaleString('es-MX');
};
</script>
*/


// ============================================================================
// EJEMPLO 2: POLLING - ACTUALIZACIÓN AUTOMÁTICA CADA 45 SEGUNDOS
// ============================================================================

/**
 * Sistema de polling para actualizar notificaciones automáticamente
 * 
 * FLUJO:
 * ------
 * 1. Componente se monta → inicia intervalo de 45s
 * 2. Cada 45s llama a fetchNotificacionesNoLeidas() (solo count, más rápido)
 * 3. Si el count cambió, muestra badge actualizado
 * 4. Usuario abre panel → carga notificaciones completas con fetchNotificaciones()
 * 5. Componente se desmonta → limpia intervalo
 */

// AppTopbar.vue (header con ícono de campana)
/*
<template>
  <div class="topbar">
    <!-- Ícono de notificaciones con badge -->
    <button @click="togglePanel" class="notif-button">
      🔔
      <span v-if="countNoLeidas > 0" class="badge">
        {{ countNoLeidas }}
      </span>
    </button>
    
    <!-- Panel de notificaciones (dropdown) -->
    <div v-if="panelAbierto" class="notif-panel">
      <div class="header">
        <h3>Notificaciones</h3>
        <button @click="marcarTodasComoLeidas">Marcar todas como leídas</button>
      </div>
      
      <div v-if="cargando">Cargando...</div>
      
      <div v-else class="notif-lista">
        <div 
          v-for="notif in notificaciones" 
          :key="notif.id"
          :class="['notif-item', { 'no-leida': !notif.leido }]"
          @click="handleClick(notif)"
        >
          <span class="icono">{{ getIcono(notif.nivel) }}</span>
          <div class="contenido">
            <strong>{{ notif.titulo }}</strong>
            <p>{{ notif.contenido.substring(0, 100) }}...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { 
  fetchNotificacionesNoLeidas, 
  fetchNotificaciones,
  marcarNotificacionLeida,
  marcarTodasLeidas as marcarTodasLeidasService,
  getIconoNivel
} from '@/service/notificationService';

const countNoLeidas = ref(0);
const notificaciones = ref([]);
const panelAbierto = ref(false);
const cargando = ref(false);
let pollingInterval = null;

// Iniciar polling al montar componente
onMounted(() => {
  iniciarPolling();
});

// Limpiar intervalo al desmontar componente
onUnmounted(() => {
  if (pollingInterval) {
    clearInterval(pollingInterval);
  }
});

// Función para iniciar el polling
const iniciarPolling = () => {
  // Cargar count inicial
  actualizarCount();
  
  // Configurar intervalo de 45 segundos
  pollingInterval = setInterval(() => {
    actualizarCount();
  }, 45000); // 45 segundos
};

// Actualizar solo el count (optimizado, no trae notificaciones completas)
const actualizarCount = async () => {
  const response = await fetchNotificacionesNoLeidas();
  
  if (response.success) {
    countNoLeidas.value = response.count;
    
    // NOTA: En este punto NO se han traído las notificaciones completas
    // Solo el count. Esto es más eficiente para polling.
    // Las notificaciones completas se cargan cuando el usuario abre el panel.
  }
};

// Toggle del panel
const togglePanel = async () => {
  panelAbierto.value = !panelAbierto.value;
  
  // Si se abre el panel, cargar notificaciones completas
  if (panelAbierto.value) {
    await cargarNotificacionesCompletas();
  }
};

// Cargar notificaciones completas
const cargarNotificacionesCompletas = async () => {
  cargando.value = true;
  
  const response = await fetchNotificaciones();
  
  if (response.success) {
    notificaciones.value = response.data;
  }
  
  cargando.value = false;
};

// Handler de clic en notificación
const handleClick = async (notif) => {
  if (!notif.leido) {
    await marcarNotificacionLeida(notif.id);
    
    // Actualizar localmente
    notif.leido = true;
    countNoLeidas.value = Math.max(0, countNoLeidas.value - 1);
  }
  
  // Navegar o mostrar modal con detalle
  // router.push(`/notificaciones/${notif.id}`);
};

// Marcar todas como leídas
const marcarTodasComoLeidas = async () => {
  const response = await marcarTodasLeidasService();
  
  if (response.success) {
    console.log(`✅ ${response.marcadas} notificaciones marcadas como leídas`);
    
    // Actualizar localmente
    notificaciones.value.forEach(n => n.leido = true);
    countNoLeidas.value = 0;
  }
};

// Obtener ícono según nivel
const getIcono = (nivel) => {
  return getIconoNivel(nivel);
};
</script>
*/


// ============================================================================
// EJEMPLO 3: CREAR NOTIFICACIÓN (Solo Administradores)
// ============================================================================

/**
 * Componente para crear notificaciones (panel de administrador)
 * 
 * IMPORTANTE: AL CREAR LA NOTIFICACIÓN, LA TABLA INTERMEDIA NO SE LLENA
 * 
 * ¿POR QUÉ?
 * ---------
 * Las notificaciones empiezan como "no leídas" para todos los usuarios.
 * La tabla NotificacionUsuario se llena SOLO cuando un usuario marca
 * la notificación como leída.
 * 
 * FLUJO:
 * ------
 * 1. Administrador crea notificación → se guarda en tabla Notificacion
 * 2. Tabla NotificacionUsuario queda VACÍA (sin registros para esa notificación)
 * 3. Usuarios ven la notificación con 'leido: false'
 * 4. Usuario A hace clic → Se crea registro en NotificacionUsuario para Usuario A
 * 5. Usuario A la ve con 'leido: true', Usuario B sigue viéndola con 'leido: false'
 */

// ComponenteCrearNotificacion.vue
/*
<template>
  <div class="crear-notificacion">
    <h2>Crear Nueva Notificación</h2>
    
    <form @submit.prevent="handleSubmit">
      <!-- Título -->
      <div class="field">
        <label>Título</label>
        <input v-model="form.titulo" type="text" required />
      </div>
      
      <!-- Contenido -->
      <div class="field">
        <label>Contenido</label>
        <textarea v-model="form.contenido" rows="5" required></textarea>
      </div>
      
      <!-- Nivel -->
      <div class="field">
        <label>Nivel</label>
        <select v-model="form.nivel" required>
          <option value="informativa">Informativa</option>
          <option value="alerta">Alerta</option>
          <option value="urgente">Urgente</option>
        </select>
      </div>
      
      <!-- Tipo -->
      <div class="field">
        <label>Tipo</label>
        <select v-model="form.tipo" required>
          <option value="sistema">Sistema</option>
          <option value="infraestructura">Infraestructura</option>
          <option value="DIRECTOR">Mensaje del Director</option>
        </select>
      </div>
      
      <!-- Alcance -->
      <div class="field">
        <label>Alcance</label>
        <select v-model="alcance" @change="handleAlcanceChange">
          <option value="global">🌍 Global (Todos los usuarios)</option>
          <option value="casino">🎰 Por Casino</option>
          <option value="casino_rol">👥 Por Casino y Rol</option>
          <option value="usuario">👤 Usuario Específico</option>
        </select>
      </div>
      
      <!-- Casino (si aplica) -->
      <div v-if="alcance === 'casino' || alcance === 'casino_rol'" class="field">
        <label>Casino</label>
        <select v-model="form.casino_destino">
          <option :value="null">-- Seleccionar --</option>
          <option v-for="casino in casinos" :key="casino.id" :value="casino.id">
            {{ casino.nombre }}
          </option>
        </select>
      </div>
      
      <!-- Rol (si aplica) -->
      <div v-if="alcance === 'casino_rol'" class="field">
        <label>Rol</label>
        <select v-model="form.rol_destino">
          <option :value="null">-- Seleccionar --</option>
          <option v-for="rol in roles" :key="rol.id" :value="rol.id">
            {{ rol.nombre }}
          </option>
        </select>
      </div>
      
      <!-- Usuario (si aplica) -->
      <div v-if="alcance === 'usuario'" class="field">
        <label>Usuario</label>
        <select v-model="form.usuario_destino">
          <option :value="null">-- Seleccionar --</option>
          <option v-for="user in usuarios" :key="user.id" :value="user.id">
            {{ user.nombres }} {{ user.apellido_paterno }}
          </option>
        </select>
      </div>
      
      <!-- Botón submit -->
      <button type="submit" :disabled="enviando">
        {{ enviando ? 'Creando...' : 'Crear Notificación' }}
      </button>
    </form>
    
    <!-- Explicación -->
    <div class="info-box">
      <h3>ℹ️ ¿Cómo funciona?</h3>
      <p>
        Al crear la notificación, se guarda en la tabla <code>Notificacion</code>.
      </p>
      <p>
        <strong>La tabla intermedia <code>NotificacionUsuario</code> NO se llena automáticamente.</strong>
      </p>
      <p>
        Los usuarios verán la notificación como "no leída". Cuando un usuario la marque 
        como leída, se creará un registro en <code>NotificacionUsuario</code> solo para ese usuario.
      </p>
      <p>
        Ejemplo: Si creas una notificación global, todos los usuarios la verán. 
        Conforme cada usuario la marque como leída, se irá llenando la tabla intermedia.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { crearNotificacion } from '@/service/notificationService';

const form = reactive({
  titulo: '',
  contenido: '',
  nivel: 'informativa',
  tipo: 'sistema',
  es_global: false,
  casino_destino: null,
  rol_destino: null,
  usuario_destino: null
});

const alcance = ref('global');
const enviando = ref(false);
const casinos = ref([]); // Cargar desde API
const roles = ref([]); // Cargar desde API
const usuarios = ref([]); // Cargar desde API

// Handler cambio de alcance
const handleAlcanceChange = () => {
  // Resetear campos
  form.es_global = alcance.value === 'global';
  form.casino_destino = null;
  form.rol_destino = null;
  form.usuario_destino = null;
};

// Handler submit
const handleSubmit = async () => {
  enviando.value = true;
  
  // Configurar campos según alcance
  if (alcance.value === 'global') {
    form.es_global = true;
  }
  
  // Crear notificación
  const response = await crearNotificacion(form);
  
  if (response.success) {
    console.log('✅ Notificación creada:', response.data);
    
    // QUÉ PASÓ EN EL BACKEND:
    // ------------------------
    // 1. Se creó registro en tabla Notificacion:
    //    +----+------------------+--------+------+-----------+
    //    | id | titulo           | nivel  | tipo | es_global |
    //    +----+------------------+--------+------+-----------+
    //    | 21 | "Nueva notif..." | alerta | sist | true      |
    //    +----+------------------+--------+------+-----------+
    //
    // 2. Tabla NotificacionUsuario quedó VACÍA (aún no hay lecturas)
    //
    // 3. Cuando un usuario la vea y haga clic:
    //    - Se ejecuta marcarNotificacionLeida(21)
    //    - Se crea registro en NotificacionUsuario:
    //      +----+--------------+------------+---------------------+
    //      | id | notificacion | usuario    | fecha_visto         |
    //      +----+--------------+------------+---------------------+
    //      | 5  | 21           | 3          | 2026-02-17 11:00:00 |
    //      +----+--------------+------------+---------------------+
    //    - Ese usuario ahora la ve con 'leido: true'
    //    - Otros usuarios siguen viéndola con 'leido: false'
    
    // Limpiar formulario
    Object.assign(form, {
      titulo: '',
      contenido: '',
      nivel: 'informativa',
      tipo: 'sistema',
      es_global: false,
      casino_destino: null,
      rol_destino: null,
      usuario_destino: null
    });
    
    alcance.value = 'global';
    
    alert('Notificación creada exitosamente');
  } else {
    console.error('❌ Error:', response.error);
    alert('Error al crear notificación: ' + response.error);
  }
  
  enviando.value = false;
};
</script>
*/


// ============================================================================
// EJEMPLO 4: VISTA DE DETALLE DE NOTIFICACIÓN
// ============================================================================

/**
 * Vista para mostrar una notificación específica
 * 
 * FLUJO:
 * ------
 * 1. Usuario hace clic en notificación desde lista
 * 2. Router navega a /notificaciones/:id
 * 3. Componente carga notificación con fetchNotificacionById()
 * 4. Si no está leída, la marca como leída automáticamente
 * 5. Backend crea registro en NotificacionUsuario si no existe
 */

// DetalleNotificacion.vue
/*
<template>
  <div class="detalle-notificacion">
    <div v-if="cargando">Cargando...</div>
    
    <div v-else-if="notificacion" class="notificacion-completa">
      <!-- Header -->
      <div class="header">
        <span :class="['nivel-badge', notificacion.nivel]">
          {{ getIcono(notificacion.nivel) }} {{ notificacion.nivel.toUpperCase() }}
        </span>
        <span class="fecha">{{ formatFecha(notificacion.fecha_creacion) }}</span>
      </div>
      
      <!-- Título -->
      <h1>{{ notificacion.titulo }}</h1>
      
      <!-- Contenido -->
      <div class="contenido">
        <pre>{{ notificacion.contenido }}</pre>
      </div>
      
      <!-- Meta información -->
      <div class="meta">
        <span>Tipo: {{ notificacion.tipo }}</span>
        <span v-if="notificacion.es_global">Alcance: Global</span>
        <span v-if="notificacion.casino_destino">
          Casino: {{ notificacion.casino_destino.nombre }}
        </span>
        <span v-if="notificacion.rol_destino">
          Rol: {{ notificacion.rol_destino.nombre }}
        </span>
      </div>
      
      <!-- Indicador de lectura -->
      <div v-if="notificacion.leido" class="leido-badge">
        ✓ Leída
      </div>
    </div>
    
    <div v-else>
      Notificación no encontrada
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { 
  fetchNotificacionById, 
  marcarNotificacionLeida,
  getIconoNivel 
} from '@/service/notificationService';

const route = useRoute();
const notificacion = ref(null);
const cargando = ref(true);

onMounted(async () => {
  await cargarNotificacion();
});

const cargarNotificacion = async () => {
  const id = route.params.id;
  
  const response = await fetchNotificacionById(id);
  
  if (response.success) {
    notificacion.value = response.data;
    
    // Si no está leída, marcarla automáticamente
    if (!notificacion.value.leido) {
      await marcarComoLeida();
    }
  } else {
    console.error('Error al cargar notificación:', response.error);
  }
  
  cargando.value = false;
};

const marcarComoLeida = async () => {
  const response = await marcarNotificacionLeida(notificacion.value.id);
  
  if (response.success) {
    console.log('✅ Notificación marcada como leída');
    notificacion.value.leido = true;
    
    // EN ESTE MOMENTO EN EL BACKEND:
    // -------------------------------
    // Se creó (o ya existía) un registro en NotificacionUsuario:
    //
    // +----+--------------+------------+---------------------+
    // | id | notificacion | usuario    | fecha_visto         |
    // +----+--------------+------------+---------------------+
    // | 6  | 16           | 3          | 2026-02-17 11:15:00 |
    // +----+--------------+------------+---------------------+
    //
    // Ahora, cuando este usuario consulte esta notificación:
    // - En la lista: aparecerá con 'leido: true'
    // - El count de no leídas no incluirá esta notificación
    // - Otros usuarios seguirán viéndola como 'leido: false'
  }
};

const getIcono = (nivel) => {
  return getIconoNivel(nivel);
};

const formatFecha = (fecha) => {
  return new Date(fecha).toLocaleString('es-MX', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>
*/


// ============================================================================
// EJEMPLO 5: COMPOSABLE REUTILIZABLE (Vue 3 Composition API)
// ============================================================================

/**
 * Crear un composable para reutilizar lógica de notificaciones
 * 
 * USO:
 * ----
 * En cualquier componente:
 * 
 * const { 
 *   notificaciones, 
 *   countNoLeidas, 
 *   cargar, 
 *   marcarLeida 
 * } = useNotificaciones();
 */

// composables/useNotificaciones.js
/*
import { ref } from 'vue';
import { 
  fetchNotificaciones, 
  fetchNotificacionesNoLeidas,
  marcarNotificacionLeida 
} from '@/service/notificationService';

export function useNotificaciones() {
  const notificaciones = ref([]);
  const countNoLeidas = ref(0);
  const cargando = ref(false);
  const error = ref(null);
  
  // Cargar notificaciones
  const cargar = async () => {
    cargando.value = true;
    error.value = null;
    
    const response = await fetchNotificaciones();
    
    if (response.success) {
      notificaciones.value = response.data;
      countNoLeidas.value = response.data.filter(n => !n.leido).length;
    } else {
      error.value = response.error;
    }
    
    cargando.value = false;
  };
  
  // Actualizar solo count
  const actualizarCount = async () => {
    const response = await fetchNotificacionesNoLeidas();
    
    if (response.success) {
      countNoLeidas.value = response.count;
    }
  };
  
  // Marcar como leída
  const marcarLeida = async (id) => {
    const response = await marcarNotificacionLeida(id);
    
    if (response.success) {
      // Actualizar localmente
      const notif = notificaciones.value.find(n => n.id === id);
      if (notif) {
        notif.leido = true;
        countNoLeidas.value = Math.max(0, countNoLeidas.value - 1);
      }
    }
    
    return response;
  };
  
  return {
    notificaciones,
    countNoLeidas,
    cargando,
    error,
    cargar,
    actualizarCount,
    marcarLeida
  };
}
*/

// Usar en componente:
/*
<script setup>
import { onMounted } from 'vue';
import { useNotificaciones } from '@/composables/useNotificaciones';

const { 
  notificaciones, 
  countNoLeidas, 
  cargando, 
  cargar, 
  marcarLeida 
} = useNotificaciones();

onMounted(() => {
  cargar();
});

const handleClick = async (notif) => {
  if (!notif.leido) {
    await marcarLeida(notif.id);
  }
};
</script>
*/


// ============================================================================
// RESUMEN: CUÁNDO SE LLENA LA TABLA NotificacionUsuario
// ============================================================================

/*
PREGUNTA: ¿Cuándo se llena la tabla intermedia NotificacionUsuario?
--------

RESPUESTA:
----------

❌ NO se llena automáticamente al crear la notificación
❌ NO se llena cuando el usuario ve o recibe la notificación
✅ SÍ se llena cuando el usuario MARCA la notificación como leída

FLUJO DETALLADO:
----------------

1. CREAR NOTIFICACIÓN (Backend o Admin):
   ----------------------------------------
   POST /notificaciones/
   Body: { titulo: "...", contenido: "...", es_global: true }
   
   Resultado:
   - Tabla Notificacion: Se crea 1 registro nuevo
   - Tabla NotificacionUsuario: Queda VACÍA (0 registros)

2. USUARIO VE LA NOTIFICACIÓN:
   -----------------------------
   GET /notificaciones/
   
   Resultado:
   - Backend filtra notificaciones visibles para el usuario
   - Backend calcula campo 'leido' dinámicamente:
     * Verifica si existe registro en NotificacionUsuario
     * Si NO existe → leido: false
     * Si existe → leido: true
   - Frontend muestra lista con badge "NUEVO" o círculo rojo

3. USUARIO HACE CLIC (Marcar como leída):
   ----------------------------------------
   PATCH /notificaciones/{id}/marcar-leida/
   
   Resultado:
   - Backend ejecuta: NotificacionUsuario.objects.get_or_create(
                        notificacion=id,
                        usuario=request.user,
                        defaults={'fecha_visto': timezone.now()}
                      )
   - Tabla NotificacionUsuario: Se crea 1 registro nuevo
     +----+--------------+------------+---------------------+
     | id | notificacion | usuario    | fecha_visto         |
     +----+--------------+------------+---------------------+
     | 1  | 16           | 3          | 2026-02-17 11:00:00 |
     +----+--------------+------------+---------------------+
   
4. PRÓXIMA VEZ QUE EL USUARIO VE LA LISTA:
   ----------------------------------------
   GET /notificaciones/
   
   Resultado:
   - Backend calcula 'leido' dinámicamente
   - Como YA existe registro en NotificacionUsuario → leido: true
   - Frontend muestra la notificación sin badge "NUEVO"

NOTA IMPORTANTE:
----------------
- Cada usuario tiene su propio registro en NotificacionUsuario
- Usuario A marca como leída → solo Usuario A la ve como leída
- Usuario B sigue viendo la misma notificación como "no leída"
- Constraint unique_together=['notificacion', 'usuario'] previene duplicados

EJEMPLO CON 3 USUARIOS:
------------------------

Notificación ID 16 (Global):
- Usuario 1 hace clic → se crea registro (notif=16, usuario=1)
- Usuario 2 NO hace clic → no hay registro
- Usuario 3 hace clic → se crea registro (notif=16, usuario=3)

Tabla NotificacionUsuario:
+----+--------------+------------+---------------------+
| id | notificacion | usuario    | fecha_visto         |
+----+--------------+------------+---------------------+
| 1  | 16           | 1          | 2026-02-17 10:30:00 |
| 2  | 16           | 3          | 2026-02-17 11:00:00 |
+----+--------------+------------+---------------------+

Cuando cada usuario consulta GET /notificaciones/:
- Usuario 1: ve notif 16 con leido: true (existe registro)
- Usuario 2: ve notif 16 con leido: false (NO existe registro)
- Usuario 3: ve notif 16 con leido: true (existe registro)

*/


// ============================================================================
// EXPORTACIÓN (Para que este archivo pueda ser importado como referencia)
// ============================================================================

export default {
  mensaje: 'Este archivo contiene ejemplos de uso del notificationService.js',
  ubicacion: '@/service/notificationService.js',
  documentacion: 'Ver comentarios en este archivo para ejemplos completos'
};
