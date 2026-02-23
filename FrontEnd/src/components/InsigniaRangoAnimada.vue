<script setup>
/**
 * InsigniaRangoAnimada.vue
 * ========================
 * Muestra el rango de gamificación del técnico con efectos visuales únicos
 * por nivel (1–10). Cada nivel tiene su propia identidad CSS/animación.
 *
 * Props:
 *   nivel       : Number  (1–10) — nivel de rango.
 *   nombreRango : String          — título del rango (ej. "Novato de Mantenimiento").
 *   compact     : Boolean         — modo compacto para el Topbar.
 */
defineProps({
    nivel: {
        type: Number,
        default: 1,
        validator: (v) => v >= 1 && v <= 10,
    },
    nombreRango: {
        type: String,
        default: 'Novato de Mantenimiento',
    },
    compact: {
        type: Boolean,
        default: false,
    },
});
</script>

<template>
    <div
        class="insignia-rango"
        :class="[`insignia-nivel-${nivel}`, { 'insignia-compact': compact }]"
        :title="`Nivel ${nivel} — ${nombreRango}`"
    >
        <!-- Capa de destellos/efectos de fondo (usada según el nivel) -->
        <span class="insignia-fx" aria-hidden="true"></span>

        <!-- Contenido principal -->
        <span class="insignia-inner">
            <span class="insignia-nivel-num">Nv.{{ nivel }}</span>
            <span class="insignia-nombre">{{ nombreRango }}</span>
        </span>
    </div>
</template>

<style scoped>
/* ============================================================
   BASE — compartida por todos los niveles
   ============================================================ */
.insignia-rango {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-radius: 6px;
    border: 2px solid transparent;
    padding: 4px 10px;
    min-width: 140px;
    cursor: default;
    user-select: none;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    transition: transform 0.18s ease, filter 0.18s ease;
}

.insignia-rango:hover {
    transform: scale(1.06) translateY(-1px);
    filter: brightness(1.2);
}

/* Modo compacto (Topbar) */
.insignia-compact {
    min-width: 110px;
    padding: 3px 8px;
    border-radius: 5px;
}

.insignia-compact .insignia-nombre {
    max-width: 110px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.insignia-inner {
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    align-items: center;
    line-height: 1.2;
    gap: 1px;
}

.insignia-nivel-num {
    font-size: 0.6rem;
    font-weight: 900;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    opacity: 0.75;
}

.insignia-nombre {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-align: center;
}

.insignia-fx {
    position: absolute;
    inset: 0;
    z-index: 1;
    pointer-events: none;
}

/* ============================================================
   KEYFRAMES GLOBALES — potenciados
   ============================================================ */

/* ── Nivel 1: parpadeo de corrosión aleatorio ── */
@keyframes oxido-flicker {
    0%, 94%, 100% { opacity: 1; filter: brightness(1); }
    95%           { opacity: 0.7; filter: brightness(0.6) sepia(0.5); }
    97%           { opacity: 0.9; filter: brightness(0.8); }
}
@keyframes oxido-shake {
    0%, 96%, 100% { transform: translate(0); }
    97%           { transform: translate(-1px, 0); }
    98%           { transform: translate(1px, 1px); }
    99%           { transform: translate(-1px, -1px); }
}
@keyframes oxido-scan {
    0%   { top: -100%; }
    100% { top: 200%; }
}

/* ── Nivel 2: shimmer metálico perpetuo ── */
@keyframes metal-shimmer {
    0%   { left: -80%; transform: skewX(-18deg); }
    100% { left: 140%; transform: skewX(-18deg); }
}
@keyframes metal-border-pulse {
    0%, 100% { border-color: #777; box-shadow: inset 0 1px 2px #ffffff15, 0 1px 4px #00000060; }
    50%       { border-color: #bbb; box-shadow: inset 0 1px 4px #ffffff35, 0 2px 10px #ffffff18, 0 1px 4px #00000060; }
}

/* ── Nivel 3: scanlines scrolling + pulso de borde ── */
@keyframes scan-scroll {
    from { background-position: 0 0; }
    to   { background-position: 0 60px; }
}
@keyframes boot-blink {
    0%, 100% { border-color: #2a5faa; box-shadow: 0 0 6px 1px #2a5faa60, inset 0 0 8px #0d2040; }
    45%       { border-color: #4a8fd4; box-shadow: 0 0 14px 3px #4a8fd480, inset 0 0 12px #1a4080; }
    50%       { border-color: #88bbff; box-shadow: 0 0 20px 6px #88bbffa0, inset 0 0 16px #2a5faa60; }
    55%       { border-color: #4a8fd4; box-shadow: 0 0 14px 3px #4a8fd480, inset 0 0 12px #1a4080; }
}
@keyframes text-type-blink {
    0%, 100% { opacity: 1; }
    48%       { opacity: 1; }
    50%       { opacity: 0; }
    52%       { opacity: 0; }
}

/* ── Nivel 4: respiración + pulso texto neón ── */
@keyframes respirar {
    0%, 100% {
        box-shadow: 0 0 4px 1px #00ff6630, inset 0 0 6px #00ff6620;
        border-color: #00cc44;
    }
    50% {
        box-shadow: 0 0 20px 8px #00ff6680, inset 0 0 18px #00ff6650;
        border-color: #00ff88;
    }
}
@keyframes neon-text-pulse {
    0%, 100% { text-shadow: 0 0 4px #00ff6680, 0 0 10px #00ff6640; }
    50%       { text-shadow: 0 0 10px #00ff66ff, 0 0 24px #00ff66b0, 0 0 40px #00ff6660; }
}
@keyframes grid-flow {
    from { background-position: 0 0; }
    to   { background-position: 8px 8px; }
}

/* ── Nivel 5: franjas + peligro pulsante ── */
@keyframes franjas-precaucion {
    from { background-position: 0 0; }
    to   { background-position: 56px 0; }
}
@keyframes hazard-glow {
    0%, 100% {
        box-shadow: 0 0 4px 1px #f5c40040, inset 0 0 8px #f5c40020;
        border-color: #b89200;
    }
    50% {
        box-shadow: 0 0 18px 6px #f5c400a0, inset 0 0 16px #f5c40050;
        border-color: #ffe040;
    }
}
@keyframes hazard-text {
    0%, 100% { text-shadow: 0 0 4px #f5c40060; letter-spacing: 0.04em; }
    50%       { text-shadow: 0 0 12px #f5c400d0, 0 0 24px #ff990060; letter-spacing: 0.08em; }
}

/* ── Nivel 6: glitch RGB + data-stream + flicker border ── */
@keyframes glitch-clip-1 {
    0%, 90%, 100% { clip-path: inset(0 0 100% 0); transform: translate(0); }
    91%           { clip-path: inset(15% 0 65% 0); transform: translate(-4px, 1px) skewX(2deg); }
    93%           { clip-path: inset(55% 0 15% 0); transform: translate(4px, -2px) skewX(-3deg); }
    95%           { clip-path: inset(75% 0 3% 0);  transform: translate(-3px, 2px); }
    98%           { clip-path: inset(8% 0 82% 0);  transform: translate(3px, -1px) skewX(1deg); }
}
@keyframes glitch-clip-2 {
    0%, 88%, 100% { clip-path: inset(0 0 100% 0); transform: translate(0); }
    89%           { clip-path: inset(35% 0 45% 0); transform: translate(5px, -3px) skewX(-2deg); }
    92%           { clip-path: inset(3% 0 88% 0);  transform: translate(-5px, 2px) skewX(3deg); }
    96%           { clip-path: inset(65% 0 25% 0); transform: translate(3px, -3px); }
}
@keyframes glow-glitch-border {
    0%, 85%, 100% { border-color: #1e90ff; box-shadow: 0 0 10px 3px #1e90ff80; }
    87%           { border-color: #ff0040; box-shadow: 0 0 24px 8px #ff004090, 0 0 40px 12px #ff004040; }
    89%           { border-color: #00ffff; box-shadow: 0 0 24px 8px #00ffff80, 0 0 40px 12px #00ffff40; }
    91%           { border-color: #ff00ff; box-shadow: 0 0 16px 5px #ff00ff70; }
    93%           { border-color: #1e90ff; box-shadow: 0 0 10px 3px #1e90ff80; }
}
@keyframes data-stream {
    from { background-position: 0 0; }
    to   { background-position: 0 -80px; }
}

/* ── Nivel 7: barrido holo + rotación de matiz ── */
@keyframes holo-sweep {
    0%   { transform: translateY(-120%) skewY(-8deg); opacity: 0; }
    20%  { opacity: 0.6; }
    80%  { opacity: 0.4; }
    100% { transform: translateY(130%) skewY(-8deg); opacity: 0; }
}
@keyframes holo-sweep-2 {
    0%   { transform: translateY(-120%) skewY(-8deg); opacity: 0; }
    20%  { opacity: 0.3; }
    80%  { opacity: 0.2; }
    100% { transform: translateY(130%) skewY(-8deg); opacity: 0; }
}
@keyframes holo-hue {
    from { filter: hue-rotate(0deg) brightness(1); }
    to   { filter: hue-rotate(360deg) brightness(1.2); }
}
@keyframes holo-glow {
    0%, 100% { box-shadow: 0 0 8px 2px #c44dff60, inset 0 0 8px #c44dff30; border-color: #cc00ff; }
    33%       { box-shadow: 0 0 22px 8px #ff44ddaa, inset 0 0 18px #ff44dd50; border-color: #ff44dd; }
    66%       { box-shadow: 0 0 18px 6px #4444ffaa, inset 0 0 14px #4444ff50; border-color: #6644ff; }
}

/* ── Nivel 8: plasma + temblor de núcleo ── */
@keyframes plasma-bg {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes plasma-glow {
    0%, 100% { box-shadow: 0 0 14px 4px #cc000080, inset 0 0 12px #ff000030; border-color: #cc0000; }
    33%       { box-shadow: 0 0 30px 12px #ff4400c0, inset 0 0 22px #ff330060; border-color: #ff4400; }
    66%       { box-shadow: 0 0 20px 8px #990000a0, inset 0 0 16px #cc000050; border-color: #aa0000; }
}
@keyframes nucleus-shake {
    0%, 90%, 100% { transform: translate(0, 0) rotate(0deg); }
    91%            { transform: translate(-1px, 1px) rotate(-0.5deg); }
    92%            { transform: translate(2px, -1px) rotate(0.5deg); }
    93%            { transform: translate(-2px, 2px) rotate(-0.3deg); }
    94%            { transform: translate(1px, -2px) rotate(0.3deg); }
    95%            { transform: translate(0, 0) rotate(0deg); }
}
@keyframes plasma-text {
    0%, 100% { text-shadow: 0 0 6px #ff0000a0, 0 0 14px #ff440050; }
    50%       { text-shadow: 0 0 14px #ff4400ff, 0 0 28px #cc0000a0, 0 0 40px #ff000060; }
}

/* ── Nivel 9: aura dorada rotatoria + relámpago ── */
@keyframes aura-rotate       { from { transform: rotate(0deg);   } to { transform: rotate(360deg);  } }
@keyframes aura-rotate-rev   { from { transform: rotate(0deg);   } to { transform: rotate(-360deg); } }
@keyframes energy-pulse {
    0%, 100% {
        box-shadow: 0 0 10px 3px #ffd70070, 0 0 24px 8px #ffd70040;
        border-color: #ffd700;
    }
    25% {
        box-shadow: 0 0 24px 8px #ffffffd0, 0 0 40px 14px #ffd700a0, 0 0 60px 20px #ffd70040;
        border-color: #ffffff;
    }
    50% {
        box-shadow: 0 0 14px 4px #ffd70090, 0 0 30px 10px #ffd70060;
        border-color: #ffd700;
    }
    75% {
        box-shadow: 0 0 22px 7px #ffffffc0, 0 0 38px 12px #ffd700a0, 0 0 56px 18px #ffd70040;
        border-color: #ffffd0;
    }
}
@keyframes energy-text {
    0%, 100% { text-shadow: 0 0 8px #ffd700c0, 0 0 18px #ffd70060; color: #fffbe0; }
    50%       { text-shadow: 0 0 16px #fff, 0 0 30px #ffd700ff, 0 0 50px #ffd700a0; color: #ffffff; }
}

/* ── Nivel 10: fuego total + chispas + halo cónico doble ── */
@keyframes leyenda-glow {
    0%, 100% {
        box-shadow:
            0 0 10px  5px #ffd700a0,
            0 0 26px 10px #ff880070,
            0 0 50px 18px #ffd70050,
            0 0 80px 30px #ff440030,
            inset 0 0 20px #ffd70050;
    }
    50% {
        box-shadow:
            0 0 20px  9px #ffd700d0,
            0 0 44px 18px #ff8800a0,
            0 0 80px 30px #ffd70080,
            0 0 110px 45px #ff440055,
            inset 0 0 34px #ffd70080;
    }
}
@keyframes leyenda-text-fire {
    0%, 100% {
        text-shadow: 0 0 4px #fff, 0 0 12px #ffd700, 0 0 24px #ff8800, 0 0 40px #ff4400;
        color: #fffbe6;
        letter-spacing: 0.05em;
    }
    25% {
        text-shadow: 0 0 8px #fff, 0 0 22px #ffd700, 0 0 40px #ff4400, 0 0 60px #ff0000;
        color: #ffffff;
        letter-spacing: 0.08em;
    }
    50% {
        text-shadow: 0 0 6px #fff, 0 0 16px #ffcc00, 0 0 28px #ff6600;
        color: #fff4c0;
        letter-spacing: 0.04em;
    }
    75% {
        text-shadow: 0 0 10px #fff, 0 0 28px #ffd700, 0 0 50px #ff3300, 0 0 70px #ff000080;
        color: #ffffff;
        letter-spacing: 0.1em;
    }
}
@keyframes leyenda-shimmer {
    0%   { left: -80%; }
    100% { left: 150%; }
}
@keyframes leyenda-shimmer-2 {
    0%   { left: -80%; }
    100% { left: 150%; }
}
@keyframes crown-bounce {
    0%, 100% { transform: translateY(0) scale(1); }
    50%       { transform: translateY(-2px) scale(1.06); }
}

/* ============================================================
   NIVEL 1 — Novato de Mantenimiento
   Metal oxidado + parpadeo de corrosión + vibración ocasional
   ============================================================ */
.insignia-nivel-1 {
    background: linear-gradient(135deg, #3a3a3a 0%, #2a2a2a 50%, #323232 100%);
    border-color: #555;
    color: #8a8a8a;
    box-shadow: inset 0 1px 1px #ffffff10, 0 1px 3px #00000080;
    animation: oxido-flicker 7s steps(1) infinite, oxido-shake 9s steps(1) infinite;
}

.insignia-nivel-1 .insignia-nivel-num { color: #777; }
.insignia-nivel-1 .insignia-nombre    { color: #9a9a9a; }

/* Línea de escaneo de corrosión que cae lentamente */
.insignia-nivel-1 .insignia-fx {
    width: 100%;
    height: 6px;
    background: linear-gradient(to bottom, transparent, #ffffff10, transparent);
    animation: oxido-scan 5s linear infinite;
    top: -100%;
    left: 0;
}

/* ============================================================
   NIVEL 2 — Aprendiz de Sala
   Metal pulido + shimmer perpetuo + pulso de borde
   ============================================================ */
.insignia-nivel-2 {
    background: linear-gradient(150deg, #606060 0%, #3e3e3e 40%, #505050 100%);
    border-color: #888;
    color: #d0d0d0;
    box-shadow: inset 0 1px 3px #ffffff20, 0 2px 6px #00000060;
    animation: metal-border-pulse 2.5s ease-in-out infinite;
}

.insignia-nivel-2 .insignia-nivel-num { color: #aaa; }
.insignia-nivel-2 .insignia-nombre    { color: #e0e0e0; }

/* Shimmer que recorre el metal continuamente */
.insignia-nivel-2 .insignia-fx {
    position: absolute;
    top: 0; height: 100%; width: 40%;
    background: linear-gradient(
        105deg,
        transparent 0%,
        #ffffff08 30%,
        #ffffff28 50%,
        #ffffff08 70%,
        transparent 100%
    );
    animation: metal-shimmer 2.2s linear infinite;
}

/* ============================================================
   NIVEL 3 — Técnico de Soporte
   Scanlines scrolling + parpadeo estilo arranque de sistema
   ============================================================ */
.insignia-nivel-3 {
    background: #0b1623;
    border-color: #2a5faa;
    color: #5ba3ff;
    animation: boot-blink 3.5s ease-in-out infinite;
}

.insignia-nivel-3 .insignia-nivel-num {
    color: #3a78d4;
    animation: text-type-blink 3.5s linear infinite 3s;
}
.insignia-nivel-3 .insignia-nombre { color: #80b8ff; }

/* Scanlines que se mueven hacia abajo permanentemente */
.insignia-nivel-3 .insignia-fx {
    background-image: repeating-linear-gradient(
        to bottom,
        transparent,
        transparent 2px,
        #1e90ff0d 2px,
        #1e90ff0d 4px
    );
    background-size: 100% 60px;
    animation: scan-scroll 1.2s linear infinite;
}

/* ============================================================
   NIVEL 4 — Operador de Máquinas
   Sistema en línea. Verde neón con grilla animada + texto pulsante
   ============================================================ */
.insignia-nivel-4 {
    background: linear-gradient(135deg, #031208 0%, #061b0c 100%);
    border-color: #00ee55;
    color: #00ff66;
    animation: respirar 2s ease-in-out infinite;
}

.insignia-nivel-4 .insignia-nivel-num {
    color: #00cc44;
    animation: neon-text-pulse 2s ease-in-out infinite;
}
.insignia-nivel-4 .insignia-nombre {
    color: #00ff66;
    animation: neon-text-pulse 2s ease-in-out infinite 0.3s;
}

/* Cuadrícula que fluye en diagonal */
.insignia-nivel-4 .insignia-fx {
    background-image:
        linear-gradient(#00ff660c 1px, transparent 1px),
        linear-gradient(90deg, #00ff660c 1px, transparent 1px);
    background-size: 8px 8px;
    animation: grid-flow 1.8s linear infinite;
}

/* ============================================================
   NIVEL 5 — Especialista en Hardware
   Industrial. Franjas precaución + peligro pulsante + texto alerta
   ============================================================ */
.insignia-nivel-5 {
    border-color: #f5c400;
    color: #f5c400;
    background-color: #141000;
    box-shadow: 0 0 0 1px #f5c40040, inset 0 0 8px #f5c40020, 0 2px 8px #00000080;
    animation: hazard-glow 1.8s ease-in-out infinite;
}

.insignia-nivel-5 .insignia-nivel-num {
    color: #c8a000;
    font-weight: 900;
}
.insignia-nivel-5 .insignia-nombre {
    animation: hazard-text 1.8s ease-in-out infinite;
}

/* Franjas diagonales que avanzan + capa de destello */
.insignia-nivel-5 .insignia-fx {
    background-image: repeating-linear-gradient(
        -55deg,
        #f5c40016 0px,
        #f5c40016 8px,
        #080600 8px,
        #080600 16px,
        transparent 16px,
        transparent 28px,
        #00000035 28px,
        #00000035 36px
    );
    background-size: 56px 56px;
    animation: franjas-precaucion 2s linear infinite;
}

/* ============================================================
   NIVEL 6 — Técnico Élite
   Sobrecarga táctica. Azul eléctrico + glitch RGB + datastream
   ============================================================ */
.insignia-nivel-6 {
    background: linear-gradient(160deg, #010816 0%, #03122a 50%, #010816 100%);
    border-color: #1e90ff;
    color: #1e90ff;
    animation: glow-glitch-border 5s steps(1) infinite;
    position: relative;
}

.insignia-nivel-6 .insignia-nivel-num {
    color: #4db8ff;
    text-shadow: 0 0 8px #1e90ffb0;
}
.insignia-nivel-6 .insignia-nombre {
    color: #80ccff;
    text-shadow: 0 0 10px #1e90ffc0;
}

/* Caída de datos digitales */
.insignia-nivel-6 .insignia-fx {
    background-image: repeating-linear-gradient(
        to bottom,
        #1e90ff10 0px, #1e90ff10 1px,
        transparent 1px, transparent 6px,
        #1e90ff06 6px, #1e90ff06 7px,
        transparent 7px, transparent 14px
    );
    background-size: 100% 80px;
    animation: data-stream 0.8s linear infinite;
}

/* Capas de glitch RGB */
.insignia-nivel-6::before {
    content: attr(title);
    position: absolute;
    inset: 0; z-index: 3;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.03em;
    pointer-events: none; white-space: nowrap; overflow: hidden;
    color: #ff003c;
    animation: glitch-clip-1 5s steps(1) infinite;
    mix-blend-mode: screen;
}
.insignia-nivel-6::after {
    content: attr(title);
    position: absolute;
    inset: 0; z-index: 3;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.03em;
    pointer-events: none; white-space: nowrap; overflow: hidden;
    color: #00ffff;
    animation: glitch-clip-2 5s steps(1) infinite;
    mix-blend-mode: screen;
}

/* ============================================================
   NIVEL 7 — Maestro Electrónico
   Holograma. Rotación de matiz continua + doble barrido de luz
   ============================================================ */
.insignia-nivel-7 {
    background: linear-gradient(135deg, #160028 0%, #2a0050 30%, #160028 60%, #200040 100%);
    border-color: #cc00ff;
    color: #e070ff;
    animation: holo-glow 3s ease-in-out infinite, holo-hue 6s linear infinite;
}

.insignia-nivel-7 .insignia-nivel-num {
    color: #cc66ff;
    text-shadow: 0 0 8px #cc00ffa0;
}
.insignia-nivel-7 .insignia-nombre {
    color: #ee88ff;
    text-shadow: 0 0 10px #cc00ffc0;
}

/* Doble barrido de luz vertical (uno detrás del otro) */
.insignia-nivel-7 .insignia-fx {
    position: absolute; inset: 0; z-index: 1; pointer-events: none;
}
.insignia-nivel-7 .insignia-fx::before,
.insignia-nivel-7 .insignia-fx::after {
    content: '';
    position: absolute;
    left: 20%; width: 60%;
    background: linear-gradient(
        to bottom,
        transparent 0%,
        #ffffff20 35%,
        #dd88ff40 50%,
        #ffffff20 65%,
        transparent 100%
    );
    top: 0; height: 100%;
    animation: holo-sweep 2.2s ease-in-out infinite;
}
.insignia-nivel-7 .insignia-fx::after {
    left: 35%; width: 30%;
    animation: holo-sweep 2.2s ease-in-out infinite 1.1s;
    opacity: 0.7;
}

/* ============================================================
   NIVEL 8 — Arquitecto de Sala
   Núcleo inestable. Plasma + temblor sísmico ocasional
   ============================================================ */
.insignia-nivel-8 {
    background:
        radial-gradient(ellipse at 20% 50%, #8b0000 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, #cc2200 0%, transparent 40%),
        radial-gradient(ellipse at 60% 80%, #6b0000 0%, transparent 50%),
        #140000;
    background-size: 200% 200%;
    border-color: #cc0000;
    color: #ff5555;
    animation:
        plasma-bg 4s ease infinite,
        plasma-glow 2.8s ease-in-out infinite,
        nucleus-shake 8s steps(1) infinite;
}

.insignia-nivel-8 .insignia-nivel-num {
    color: #ff7777;
    animation: plasma-text 2.8s ease-in-out infinite;
}
.insignia-nivel-8 .insignia-nombre {
    color: #ff9999;
    animation: plasma-text 2.8s ease-in-out infinite 0.4s;
}

/* Burbujas de calor superpuestas en movimiento */
.insignia-nivel-8 .insignia-fx {
    background:
        radial-gradient(circle at 25% 65%, #ff220020 0, transparent 40%),
        radial-gradient(circle at 75% 35%, #cc000025 0, transparent 45%),
        radial-gradient(circle at 55% 80%, #8b000028 0, transparent 35%);
    animation: plasma-bg 2.5s ease infinite reverse;
}

/* ============================================================
   NIVEL 9 — Guardián del Casino
   Pura energía. Pulso eléctrico masivo + aura dorada dual
   ============================================================ */
.insignia-nivel-9 {
    background: linear-gradient(135deg, #0a0800 0%, #181200 50%, #0a0800 100%);
    border-color: #ffd700;
    color: #fff8d0;
    animation: energy-pulse 1.6s ease-in-out infinite;
}

.insignia-nivel-9 .insignia-nivel-num {
    color: #ffd700;
    animation: energy-text 1.6s ease-in-out infinite;
}
.insignia-nivel-9 .insignia-nombre {
    animation: energy-text 1.6s ease-in-out infinite 0.3s;
}

/* Aura cónica exterior (sentido horario) */
.insignia-nivel-9::before {
    content: '';
    position: absolute;
    inset: -4px;
    background: conic-gradient(
        from 0deg,
        transparent 0%, transparent 15%,
        #ffd70080 22%, #ffffff90 30%, #ffd70080 38%,
        transparent 45%, transparent 60%,
        #ffd70060 67%, #ffffff70 75%, #ffd70060 83%,
        transparent 90%, transparent 100%
    );
    border-radius: 9px;
    z-index: 0;
    animation: aura-rotate 1.8s linear infinite;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
    padding: 3px;
}

/* Segunda aura (sentido antihorario, más suave) */
.insignia-nivel-9::after {
    content: '';
    position: absolute;
    inset: -7px;
    background: conic-gradient(
        from 180deg,
        transparent 0%, transparent 70%,
        #ffd70030 78%, #ffffff50 85%, #ffd70030 92%,
        transparent 100%
    );
    border-radius: 12px;
    z-index: 0;
    animation: aura-rotate-rev 2.6s linear infinite;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
    padding: 3px;
}

.insignia-nivel-9 .insignia-fx {
    background: radial-gradient(circle at 50% 50%, #ffd70015 0%, transparent 70%);
    animation: energy-pulse 1.6s ease-in-out infinite;
}

/* ============================================================
   NIVEL 10 — Leyenda de NEXUS
   Espectáculo total. Tres capas de borde cónico + texto de fuego
   ============================================================ */
.insignia-nivel-10 {
    background: linear-gradient(
        135deg,
        #1e0d00 0%, #3a1800 18%, #1e0d00 36%,
        #4a2400 54%, #2a1200 72%, #1e0d00 100%
    );
    background-size: 300% 300%;
    border-color: #ffd700;
    border-width: 2px;
    color: #ffd700;
    animation:
        leyenda-glow 1.8s ease-in-out infinite,
        plasma-bg 6s ease infinite,
        crown-bounce 2.4s ease-in-out infinite;
}

.insignia-nivel-10 .insignia-nivel-num {
    color: #ffec80;
    font-weight: 900;
    letter-spacing: 0.18em;
    animation: leyenda-text-fire 1.4s ease-in-out infinite;
}
.insignia-nivel-10 .insignia-nombre {
    color: #ffe566;
    font-weight: 800;
    animation: leyenda-text-fire 1.8s ease-in-out infinite 0.3s;
}

/* Borde cónico capa 1 — rápido, dorado/naranja */
.insignia-nivel-10::before {
    content: '';
    position: absolute;
    inset: -4px;
    background: conic-gradient(
        from 0deg,
        #ffd700, #ff8800, #ffec00, #ff6600, #ffd700,
        #ffffff, #ffd700, #ff4400, #ffd700
    );
    border-radius: 10px;
    z-index: 0;
    animation: aura-rotate 1.2s linear infinite;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
    padding: 2px;
}

/* Borde cónico capa 2 — más lento, halo exterior */
.insignia-nivel-10::after {
    content: '';
    position: absolute;
    inset: -8px;
    background: conic-gradient(
        from 90deg,
        transparent 0%, transparent 40%,
        #ffd70060 50%, #ff880080 58%, #ffffff60 65%,
        transparent 75%, transparent 100%
    );
    border-radius: 14px;
    z-index: 0;
    animation: aura-rotate-rev 2s linear infinite;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
    padding: 4px;
}

/* Tres shimmers que atraviesan el cuerpo en cascada */
.insignia-nivel-10 .insignia-fx {
    position: absolute; inset: 0; z-index: 1; pointer-events: none; overflow: hidden;
}
.insignia-nivel-10 .insignia-fx::before,
.insignia-nivel-10 .insignia-fx::after {
    content: '';
    position: absolute;
    top: 0; height: 100%; width: 35%;
    background: linear-gradient(
        105deg,
        transparent 0%, #ffffff30 40%, #ffd70060 50%, #ffffff30 60%, transparent 100%
    );
    animation: leyenda-shimmer 1.6s linear infinite;
}
.insignia-nivel-10 .insignia-fx::after {
    width: 20%;
    animation: leyenda-shimmer 1.6s linear infinite 0.55s;
    opacity: 0.7;
}
</style>
