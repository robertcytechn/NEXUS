# Layout — Estructura de la Aplicación

**Directorio fuente:** `FrontEnd/src/layout/`

---

## Componentes del Layout

| Componente | Descripción |
|---|---|
| `AppLayout.vue` | Contenedor raíz — integra Topbar, Sidebar y área de contenido |
| `AppTopbar.vue` | Barra superior: búsqueda, notificaciones, rango RPG, perfil |
| `AppSidebar.vue` | Contenedor del menú lateral |
| `AppMenu.vue` | Carga el menú desde la BD y lo filtra por rol |
| `AppMenuItem.vue` | Item individual del menú (soporta submenús) |
| `AppFooter.vue` | Pie de página |
| `AppConfigurator.vue` | Panel de personalización del tema (colores, modo oscuro) |
| `composables/layout.js` | Estado global reactivo del layout |

---

## `layout.js` — Composable Global

Exporta el composable `useLayout()` que gestiona el estado del layout con objetos `reactive`.

### `layoutConfig`

```javascript
const layoutConfig = reactive({
    preset: 'Aura',        // Preset de PrimeVue
    primary: 'cyan',       // Color primario de la app
    surface: 'slate',      // Esquema de superficies
    darkTheme: false,      // Modo oscuro
    menuMode: 'static'     // 'static' | 'overlay'
});
```

> Valores por defecto: tema **Aura**, color primario **cyan**, superficie **slate**, modo **claro**, menú **estático**.

### `layoutState`

```javascript
const layoutState = reactive({
    staticMenuInactive: false,   // Menú colapsado en modo estático
    overlayMenuActive: false,    // Menú hamburguer activo en overlay
    profileSidebarVisible: false,
    configSidebarVisible: false,
    sidebarExpanded: false,
    menuHoverActive: false,
    activeMenuItem: null,
    activePath: null
});
```

### Métodos exportados

| Método | Descripción |
|---|---|
| `toggleDarkMode()` | Activa/desactiva modo oscuro con `View Transitions API` si está disponible |
| `toggleMenu()` | Colapsa o expande el menú según `menuMode` y si es desktop o móvil |
| `toggleConfigSidebar()` | Abre/cierra el panel de configuración del tema |
| `changeMenuMode(event)` | Cambia entre `'static'` y `'overlay'` |
| `isDarkTheme` | `computed` — `true` cuando `darkTheme: true` |
| `isDesktop()` | `window.innerWidth > 991` |

### Transición del modo oscuro

```javascript
const toggleDarkMode = () => {
    if (!document.startViewTransition) {
        executeDarkModeToggle();
        return;
    }
    // View Transitions API → animación suave entre light/dark
    document.startViewTransition(() => executeDarkModeToggle(event));
};
```

---

## `AppMenu.vue` — Menú Dinámico por Rol

### Carga desde la base de datos

```javascript
onMounted(async () => {
    const res = await api.get('menus/activo/');
    if (res.data?.length > 0) menuDefinition.value = res.data;
});
```

El menú se carga al montar el componente. Si falla, queda vacío (sin crashear).

### Filtrado recursivo por rol

```javascript
const filterMenuByRole = (items) => {
    return items.filter(item => {
        const hasAccess = !item.roles || hasRoleAccess(item.roles);
        if (!hasAccess) return false;
        
        // Filtrar sub-ítems recursivamente
        if (item.items?.length > 0) {
            const filteredSubs = filterMenuByRole(item.items);
            if (filteredSubs.length > 0) {
                item.items = filteredSubs;
                return true;
            }
            return false; // Ocultar grupos vacíos
        }
        return true;
    }).map(item => ({ ...item })); // Clonar para no mutar la DB
};
```

> Un grupo de menú se oculta automáticamente si **todos** sus hijos son inaccesibles para el rol actual.

---

## `AppTopbar.vue` — Barra Superior

Documentado en detalle en [Components/AppTopbar](../components/AppTopbar.md).

Responsabilidades:
- Toggle del menú lateral
- Toggle del modo oscuro
- Búsqueda global (`AppSearch`)
- Panel de notificaciones con **polling cada 45 segundos**
- Menú de perfil (Mi Perfil, Cerrar Sesión)
- Insignia del rango RPG reactive (`InsigniaRangoAnimada`)

---

## Diagrama del Layout

```
┌─────────────────────────────────────────┐
│  AppTopbar                              │
│  [☰] NEXUS  [🔍]  [🔔3] [★Técnico II] │
├──────────────┬──────────────────────────┤
│              │                          │
│  AppSidebar  │   <router-view>          │
│  AppMenu     │   (contenido de la ruta) │
│              │                          │
├──────────────┴──────────────────────────┤
│  AppFooter   NEXUS © 2025               │
└─────────────────────────────────────────┘
```

---

## Modos de Menú

| Modo | Comportamiento Desktop | Comportamiento Móvil |
|---|---|---|
| `static` | Siempre visible, se puede colapsar con el botón ☰ | Oculto por defecto, se activa con ☰ |
| `overlay` | Aparece sobre el contenido al hacer clic en ☰ | Igual que desktop |
