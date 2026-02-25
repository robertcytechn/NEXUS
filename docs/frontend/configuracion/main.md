# main.js — Punto de Entrada de la Aplicación

**Archivo fuente:** `FrontEnd/src/main.js`

---

## Dependencias Principales

| Paquete | Versión | Uso |
|---|---|---|
| `vue` | ^3.4.34 | Framework reactivo |
| `vue-router` | ^4.6.4 | SPA routing |
| `primevue` | ^4.5.4 | Librería de componentes UI |
| `@primeuix/themes` | ^2.0.0 | Temas de PrimeVue (Aura, Lara, Nora) |
| `primeicons` | ^7.0.0 | Iconos (prefijo `pi`) |
| `axios` | ^1.13.5 | Cliente HTTP |
| `chart.js` | 3.3.2 | Gráficas (integrado con PrimeVue Chart) |
| `pinia` | ^3.0.4 | Gestión de estado (declarado pero uso ligero) |
| `dayjs` | ^1.11.19 | Manipulación de fechas |
| `html2pdf.js` | ^0.14.0 | Exportación PDF (tickets, reportes) |
| `jspdf` | ^4.2.0 | Generación de PDF |

---

## Registro de Plugins

```javascript
const app = createApp(App);

app.use(router);              // Vue Router 4
app.use(PrimeVue, { ... });  // UI + tema + locale ES-MX
app.use(ToastService);        // Notificaciones toast globales
app.use(ConfirmationService); // Diálogos de confirmación globales

app.mount('#app');
```

---

## Configuración de PrimeVue

### Tema

```javascript
theme: {
    preset: Aura,                   // Preset visual: 'Aura' (elegante, moderno)
    options: {
        darkModeSelector: '.app-dark', // Se agrega esta clase al <html> para activar dark mode
        cssLayer: false
    }
}
```

### Apariencia

| Opción | Valor | Descripción |
|---|---|---|
| `ripple` | `true` | Efecto onda al hacer clic |
| `inputStyle` | `'outlined'` | Inputs con borde visible |
| `inputVariant` | `'outlined'` | Alias moderno de inputStyle |
| `unstyled` | `false` | Se usan estilos de PrimeVue |

### Z-Index

| Componente | Z-Index |
|---|---|
| `toast` | 1200 |
| `modal` | 1100 |
| `tooltip` | 1100 |
| `overlay` / `menu` | 1000 |

> El toast tiene mayor z-index para siempre aparecer encima de modales.

### Locale (ES-MX)

El locale personalizado configura los textos de todos los componentes interactivos de PrimeVue:

- **Calendar:** nombres de días/meses en español, `firstDayOfWeek: 1` (lunes)
- **DataTable:** labels de filtros en español
- **PasswordStrength:** Débil → Fuerte
- **dateFormat:** `dd/mm/yy`

### Modos de filtro disponibles por tipo

```javascript
filterMatchModeOptions: {
    text:    ['startsWith', 'contains', 'notContains', 'endsWith', 'equals', 'notEquals'],
    numeric: ['equals', 'notEquals', 'lt', 'lte', 'gt', 'gte'],
    date:    ['dateIs', 'dateIsNot', 'dateBefore', 'dateAfter']
}
```

---

## CSS Global

| Archivo | Descripción |
|---|---|
| `@/assets/tailwind.css` | Directivas de Tailwind CSS v4 |
| `@/assets/styles.scss` | Estilos personalizados del proyecto |

---

## Variables de Entorno

No se usan archivos `.env`. La URL del backend se construye dinámicamente en `api.js`:

```javascript
const BASE_URL = `http://${window.location.hostname}:8000/api/`;
```

Esto permite que el frontend funcione tanto en local (`localhost:8000`) como en el servidor (`cytechn.ddns.net:8000`) sin cambiar código.
