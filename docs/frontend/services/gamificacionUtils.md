# gamificacionUtils.js — Utilidades de Gamificación

**Archivo fuente:** `FrontEnd/src/service/gamificacionUtils.js`

Funciones puras para la presentación del sistema de puntos NEXUS en el frontend.

---

## `mostrarToastPuntos(toast, puntos, life?)`

Muestra un toast de PrimeVue con el detalle de puntos obtenidos **y** actualiza el rango en localStorage para reflejarlo en `InsigniaRangoAnimada` sin re-login.

```javascript
import { mostrarToastPuntos } from '@/service/gamificacionUtils'
import { useToast } from 'primevue/usetoast'

const toast = useToast()

// Después de crear una bitácora, ticket, etc.
const result = await crearBitacoraTecnica({ ... })
mostrarToastPuntos(toast, result.puntosNexus)
```

### Comportamiento

1. Si `puntos` es `null` o `puntos_otorgados <= 0` → no hace nada (silencioso)
2. Construye el mensaje: `+20 pts NEXUS — bitácora técnica registrada | Técnico II (Total: 340)`
3. Llama `toast.add({ severity: 'success', group: 'nexus-puntos', ... })`
4. Llama `actualizarRangoLocal(rango)` → actualiza localStorage y emite `nexus:rango-actualizado`

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `toast` | object | requerido | Instancia de `useToast()` |
| `puntos` | object\|null | requerido | Objeto `puntos_nexus` del servidor |
| `life` | number | `5000` | Duración del toast en ms |

---

## `acumularPuntos(base, adicional)`

Combina dos objetos `puntos_nexus` sumando `puntos_otorgados`. Útil cuando una acción genera dos llamadas API (bitácora + cierre de ticket).

```javascript
const puntosBase = bitacoraResult.data?.puntos_nexus      // 20 pts
const puntosExtra = ticketResult.data?.puntos_nexus        // 30 pts

const puntosTotal = acumularPuntos(puntosBase, puntosExtra)
// → puntos_otorgados: 50, mensaje_nexus: "🏅 +50 puntos NEXUS acumulados en esta acción"

mostrarToastPuntos(toast, puntosTotal)
```

### Lógica de combinación

```javascript
// Usa los datos del objeto más reciente (adicional)
// pero suma los puntos_otorgados de ambos
return {
    ...adicional,
    puntos_otorgados: (base.puntos_otorgados || 0) + (adicional.puntos_otorgados || 0),
    mensaje_nexus: `🏅 +${total} puntos NEXUS acumulados en esta acción`
};
```

Maneja casos nulos:
- `acumularPuntos(null, obj)` → devuelve `obj`
- `acumularPuntos(obj, null)` → devuelve `obj`
- `acumularPuntos(null, null)` → devuelve `null`

---

## Estructura del Objeto `puntos_nexus`

El backend devuelve este objeto en la respuesta de operaciones que otorgan puntos:

```json
{
  "puntos_otorgados": 20,
  "puntos_totales": 340,
  "puntos_historico": 840,
  "rango_nivel": 4,
  "rango_titulo": "Técnico III",
  "rango_insignia": "★★★★",
  "progreso_pct": 65.0,
  "puntos_sig": 1000,
  "usuario": "jmartinez",
  "motivo": "bitácora técnica registrada",
  "mensaje_nexus": "🏅 +20 puntos NEXUS — bitácora técnica registrada"
}
```

---

## Flujo Completo del Sistema de Puntos

```
Backend (signal post_save)
    → otorgar_puntos() → F() atomic update
    → set_puntos_context(puntos_nexus)

ViewSet
    → get_puntos_context()
    → response.data['puntos_nexus'] = datos

Vue View
    → result.data.puntos_nexus
    → acumularPuntos() si es necesario
    → mostrarToastPuntos(toast, puntos)
        → toast.add() → PrimeVue Toast visual
        → actualizarRangoLocal(rango)
            → localStorage.user.rango_gamificacion actualizado
            → window.dispatchEvent('nexus:rango-actualizado')
                → AppTopbar escucha → InsigniaRangoAnimada se actualiza
```
