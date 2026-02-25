# Componentes Reutilizables

**Directorio fuente:** `FrontEnd/src/components/`

---

## InsigniaRangoAnimada.vue

**Propósito:** Muestra la insignia de rango RPG del técnico con efectos visuales únicos por nivel.

### Props

| Prop | Tipo | Default | Notas |
|---|---|---|---|
| `nivel` | Number | `1` | Rango 1–10; validado por vue prop validator |
| `nombreRango` | String | `'Novato de Mantenimiento'` | Texto del título |
| `compact` | Boolean | `false` | Modo compacto para el Topbar (min-width 110px) |

### Clases dinámicas

Se aplica `insignia-nivel-{nivel}` como clase CSS → cada nivel tiene identidad visual propia (colores, animaciones, gradientes). Además `insignia-compact` en modo compacto.

### Uso

```vue
<InsigniaRangoAnimada :nivel="5" nombreRango="Artesano de Sala" :compact="true" />
```

Usado en: `AppTopbar.vue` (compact=true) y `EvolucionNexus.vue` (tamaño completo).

---

## TopBarraHerramientas.vue

**Propósito:** Barra flotante que expone la acción "Ticket de Pánico" — reporte rápido de máquina averiada sin abrir el módulo completo.

### Estado interno principal

| Ref | Tipo | Descripción |
|---|---|---|
| `panicoDialog` | Boolean | Visibilidad del diálogo |
| `uidMaquina` | String | UID capturado por el usuario |
| `loading` | Boolean | Estado de creación del ticket |
| `submitted` | Boolean | Control de validación |
| `usuario` | Object | `getUser()` de `api.js` |

### Computed de permisos

```javascript
const puedeReportarMaquina = computed(() => hasRoleAccess([
    'SUPERVISOR SALA', 'ENCARGADO AREA', 'TECNICO',
    'SUP SISTEMAS', 'GERENCIA', 'DB ADMIN', 'ADMINISTRADOR'
]));
```

### Flujo "Pánico"

1. `abrirPanico()` — valida que `casinoId` y `puedeReportarMaquina` sean verdaderos.
2. Usuario ingresa el UID de la máquina.
3. `crearTicketPanico()` — llama a `crearTicket()` de `ticketService.js` con `tipo: TIPOS_TICKET.PANICO`.

---

## DataTableToolbar.vue

**Propósito:** Barra de herramientas genérica para los DataTables del sistema. Unifica exportación, impresión, búsqueda global y selector de columnas en todos los módulos.

### Props

| Prop | Default | Descripción |
|---|---|---|
| `dt` | `null` | Ref al PrimeVue DataTable (para exportación CSV) |
| `datos` | `[]` | Array de datos para impresión HTML |
| `tituloReporte` | `'Reporte'` | Título h1 del reporte impreso |
| `nombreArchivo` | `'export'` | Nombre base del archivo exportado |
| `mostrarExportacion` | `true` | Muestra/oculta botón exportar |
| `mostrarImprimir` | `true` | Muestra/oculta botón imprimir |
| `mostrarRefrescar` | `true` | Muestra/oculta botón refrescar |
| `mostrarSelectorColumnas` | `true` | Muestra/oculta selector de columnas |
| `columnas` | `[]` | Columnas disponibles para toggle |
| `columnasSeleccionadas` | `[]` | Columnas activas (`v-model`) |
| `mostrarBuscador` | `true` | Muestra/oculta field de búsqueda |
| `incluirFechaEnNombre` | `true` | Agrega fecha ISO al nombre del archivo |

### Emits

| Evento | Descripción |
|---|---|
| `refrescar` | El usuario presionó "Refrescar" |
| `update:columnasSeleccionadas` | Cambio de columnas visibles (`v-model`) |

### Detección de plataforma

```javascript
const canWebShare = () =>
    typeof navigator.share === 'function' && typeof navigator.canShare === 'function';
```
- Escritorio: descarga directa de archivo.
- Móvil / WebView: menú nativo `navigator.share`.

### Uso típico

```vue
<DataTableToolbar
    :dt="dtRef"
    :datos="maquinas"
    titulo-reporte="Inventario de Máquinas"
    nombre-archivo="maquinas"
    :columnas="columnasDisponibles"
    v-model:columnas-seleccionadas="columnasVisibles"
    @refrescar="cargarMaquinas"
/>
```

---

## DashboardCharts.vue

**Propósito:** Conjunto de gráficas Chart.js para el Dashboard de roles analíticos.

- **Visibilidad:** Solo cuando `canViewCharts` = true (roles: ADMINISTRADOR, DB ADMIN, SUP SISTEMAS, GERENCIA).
- **Gráficas incluidas:** Estado de máquinas (Pie/Doughnut), tendencia de tickets (Line/Bar), indicadores de mantenimiento.

---

## AppSearch.vue

**Propósito:** Buscador global del sistema accesible desde el Topbar. Busca a través de múltiples recursos del backend según el término ingresado.

---

## DnaBackground.vue

**Propósito:** Animación decorativa de fondo (doble hélice de ADN) para la vista `EvolucionNexus.vue`. Puramente visual, sin estado.

---

## EvolucionAdn.vue

**Propósito:** Componente visual complementario a `DnaBackground.vue` — renderiza el ADN con SVG/CSS animation para los créditos de versión.

---

## FloatingConfigurator.vue

**Propósito:** Panel flotante de configuración de tema accesible en toda la app. Permite cambiar:
- Modo oscuro/claro.
- Color primary (cyan, blue, purple…).
- Color surface (slate, gray, zinc…).
- Modo de menú (static, overlay, slim).

Utiliza `useLayout()` internamente.
