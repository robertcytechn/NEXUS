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
    transform: scale(1.03) translateY(-1px);
    /* No se usa filter:brightness en hover — demasiado costoso en GPU */
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
    0%, 100% { border-color: #2a5faa; box-shadow: 0 0 4px 1px #2a5faa40, inset 0 0 6px #0d2040; }
    45%       { border-color: #4a8fd4; box-shadow: 0 0 8px 2px #4a8fd450, inset 0 0 8px #1a4080; }
    50%       { border-color: #88bbff; box-shadow: 0 0 12px 3px #88bbff60, inset 0 0 10px #2a5faa40; }
    55%       { border-color: #4a8fd4; box-shadow: 0 0 8px 2px #4a8fd450, inset 0 0 8px #1a4080; }
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
        box-shadow: 0 0 4px 1px #00ff6625, inset 0 0 4px #00ff6615;
        border-color: #00cc44;
    }
    50% {
        box-shadow: 0 0 12px 3px #00ff6648, inset 0 0 10px #00ff6628;
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
        box-shadow: 0 0 4px 1px #f5c40030, inset 0 0 5px #f5c40015;
        border-color: #b89200;
    }
    50% {
        box-shadow: 0 0 10px 3px #f5c40060, inset 0 0 8px #f5c40030;
        border-color: #ffe040;
    }
}
@keyframes hazard-text {
    0%, 100% { text-shadow: 0 0 4px #f5c40060; }
    50%       { text-shadow: 0 0 10px #f5c400b0, 0 0 18px #ff990040; }
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
    0%, 85%, 100% { border-color: #1e90ff; box-shadow: 0 0 6px 2px #1e90ff50; }
    87%           { border-color: #ff0040; box-shadow: 0 0 12px 3px #ff004060, 0 0 20px 5px #ff004025; }
    89%           { border-color: #00ffff; box-shadow: 0 0 12px 3px #00ffff50, 0 0 20px 5px #00ffff20; }
    91%           { border-color: #ff00ff; box-shadow: 0 0 8px 2px #ff00ff40; }
    93%           { border-color: #1e90ff; box-shadow: 0 0 6px 2px #1e90ff50; }
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
    0%, 100% { box-shadow: 0 0 6px 2px #c44dff40, inset 0 0 5px #c44dff20; border-color: #cc00ff; }
    33%       { box-shadow: 0 0 12px 3px #ff44dd60, inset 0 0 8px #ff44dd30; border-color: #ff44dd; }
    66%       { box-shadow: 0 0 10px 3px #4444ff60, inset 0 0 6px #4444ff30; border-color: #6644ff; }
}

/* ── Nivel 8: plasma + temblor de núcleo ── */
@keyframes plasma-bg {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes plasma-glow {
    0%, 100% { box-shadow: 0 0 8px 2px #cc000050, inset 0 0 6px #ff000018; border-color: #cc0000; }
    33%       { box-shadow: 0 0 16px 5px #ff440070, inset 0 0 10px #ff330030; border-color: #ff4400; }
    66%       { box-shadow: 0 0 10px 3px #99000060, inset 0 0 8px #cc000028; border-color: #aa0000; }
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
        box-shadow: 0 0 6px 2px #ffd70045, 0 0 14px 4px #ffd70025;
        border-color: #ffd700;
    }
    25% {
        box-shadow: 0 0 10px 3px #ffffff90, 0 0 20px 6px #ffd70060, 0 0 30px 8px #ffd70025;
        border-color: #ffffff;
    }
    50% {
        box-shadow: 0 0 8px 2px #ffd70055, 0 0 16px 5px #ffd70035;
        border-color: #ffd700;
    }
    75% {
        box-shadow: 0 0 10px 3px #ffffff80, 0 0 18px 5px #ffd70060, 0 0 28px 7px #ffd70025;
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
            0 0 8px  3px #ffd70060,
            0 0 16px 5px #ff880040,
            0 0 26px 8px #ffd70030,
            inset 0 0 10px #ffd70030;
    }
    50% {
        box-shadow:
            0 0 12px  4px #ffd70090,
            0 0 24px 8px #ff880060,
            0 0 40px 12px #ffd70048,
            0 0 55px 16px #ff440030,
            inset 0 0 18px #ffd70050;
    }
}
@keyframes leyenda-text-fire {
    0%, 100% { text-shadow: 0 0 4px #fff, 0 0 10px #ffd700, 0 0 18px #ff8800; color: #fffbe6; }
    50%       { text-shadow: 0 0 6px #fff, 0 0 16px #ffd700, 0 0 26px #ff6600;  color: #fff4c0; }
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
    animation: oxido-flicker 7s steps(1) infinite;
}

.insignia-nivel-1 .insignia-nivel-num { color: #777; }
.insignia-nivel-1 .insignia-nombre    { color: #9a9a9a; }

/* Línea de escaneo — estática, sin movimiento */
.insignia-nivel-1 .insignia-fx {
    width: 100%;
    height: 6px;
    background: linear-gradient(to bottom, transparent, #ffffff10, transparent);
    top: 40%;
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

/* Shimmer metálico — estático en posición central */
.insignia-nivel-2 .insignia-fx {
    position: absolute;
    top: 0; height: 100%; width: 40%;
    left: 30%;
    background: linear-gradient(
        105deg,
        transparent 0%,
        #ffffff06 30%,
        #ffffff18 50%,
        #ffffff06 70%,
        transparent 100%
    );
}

/* ============================================================
   NIVEL 3 — Técnico de Soporte
   Scanlines scrolling + parpadeo estilo arranque de sistema
   ============================================================ */
.insignia-nivel-3 {
    background: #0b1623;
    border-color: #2a5faa;
    color: #5ba3ff;
    animation: boot-blink 6s ease-in-out infinite;
}

.insignia-nivel-3 .insignia-nivel-num {
    color: #3a78d4;
}
.insignia-nivel-3 .insignia-nombre { color: #80b8ff; }

/* Scanlines estáticas */
.insignia-nivel-3 .insignia-fx {
    background-image: repeating-linear-gradient(
        to bottom,
        transparent,
        transparent 2px,
        #1e90ff0a 2px,
        #1e90ff0a 4px
    );
    background-size: 100% 60px;
}

/* ============================================================
   NIVEL 4 — Operador de Máquinas
   Sistema en línea. Verde neón con grilla animada + texto pulsante
   ============================================================ */
.insignia-nivel-4 {
    background: linear-gradient(135deg, #031208 0%, #061b0c 100%);
    border-color: #00ee55;
    color: #00ff66;
    animation: respirar 4s ease-in-out infinite;
}

.insignia-nivel-4 .insignia-nivel-num {
    color: #00cc44;
    animation: neon-text-pulse 4s ease-in-out infinite;
}
.insignia-nivel-4 .insignia-nombre {
    color: #00ff66;
    animation: neon-text-pulse 4s ease-in-out infinite 0.5s;
}

/* Cuadrícula estática */
.insignia-nivel-4 .insignia-fx {
    background-image:
        linear-gradient(#00ff6609 1px, transparent 1px),
        linear-gradient(90deg, #00ff6609 1px, transparent 1px);
    background-size: 8px 8px;
}

/* ============================================================
   NIVEL 5 — Especialista en Hardware
   Industrial. Franjas precaución + peligro pulsante + texto alerta
   ============================================================ */
.insignia-nivel-5 {
    border-color: #f5c400;
    color: #f5c400;
    background-color: #141000;
    box-shadow: 0 0 0 1px #f5c40030, inset 0 0 6px #f5c40015, 0 2px 8px #00000080;
    animation: hazard-glow 4s ease-in-out infinite;
}

.insignia-nivel-5 .insignia-nivel-num {
    color: #c8a000;
    font-weight: 900;
}
.insignia-nivel-5 .insignia-nombre {
    animation: hazard-text 4s ease-in-out infinite;
}

/* Franjas diagonales estáticas */
.insignia-nivel-5 .insignia-fx {
    background-image: repeating-linear-gradient(
        -55deg,
        #f5c40010 0px,
        #f5c40010 8px,
        #080600 8px,
        #080600 16px,
        transparent 16px,
        transparent 28px,
        #00000025 28px,
        #00000025 36px
    );
    background-size: 56px 56px;
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

/* Líneas de datos estáticas */
.insignia-nivel-6 .insignia-fx {
    background-image: repeating-linear-gradient(
        to bottom,
        #1e90ff0a 0px, #1e90ff0a 1px,
        transparent 1px, transparent 6px,
        #1e90ff04 6px, #1e90ff04 7px,
        transparent 7px, transparent 14px
    );
    background-size: 100% 80px;
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
    animation: holo-glow 8s ease-in-out infinite;
}

.insignia-nivel-7 .insignia-nivel-num {
    color: #cc66ff;
    text-shadow: 0 0 8px #cc00ffa0;
}
.insignia-nivel-7 .insignia-nombre {
    color: #ee88ff;
    text-shadow: 0 0 10px #cc00ffc0;
}

/* Brillo holográfico central — estático */
.insignia-nivel-7 .insignia-fx {
    position: absolute; inset: 0; z-index: 1; pointer-events: none;
    background: linear-gradient(
        to bottom,
        transparent 0%,
        #ffffff0a 35%,
        #dd88ff18 50%,
        #ffffff0a 65%,
        transparent 100%
    );
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
    background-size: 100% 100%;
    border-color: #cc0000;
    color: #ff5555;
    animation: plasma-glow 7s ease-in-out infinite;
}

.insignia-nivel-8 .insignia-nivel-num { color: #ff7777; }
.insignia-nivel-8 .insignia-nombre    { color: #ff9999; }

/* Burbujas de calor — estáticas */
.insignia-nivel-8 .insignia-fx {
    background:
        radial-gradient(circle at 25% 65%, #ff220015 0, transparent 40%),
        radial-gradient(circle at 75% 35%, #cc000018 0, transparent 45%),
        radial-gradient(circle at 55% 80%, #8b000018 0, transparent 35%);
}

/* ============================================================
   NIVEL 9 — Guardián del Casino
   Pura energía. Pulso eléctrico masivo + aura dorada dual
   ============================================================ */
.insignia-nivel-9 {
    background: linear-gradient(135deg, #0a0800 0%, #181200 50%, #0a0800 100%);
    border-color: #ffd700;
    color: #fff8d0;
    animation: energy-pulse 6s ease-in-out infinite;
}

.insignia-nivel-9 .insignia-nivel-num { color: #ffd700; }
.insignia-nivel-9 .insignia-nombre    { color: #fff8d0; }

/* Aura cónica — eliminada, solo pulso de borde */

.insignia-nivel-9 .insignia-fx {
    background: radial-gradient(circle at 50% 50%, #ffd70015 0%, transparent 70%);
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
    background-size: 100% 100%;
    border-color: #ffd700;
    border-width: 2px;
    color: #ffd700;
    animation: leyenda-glow 6s ease-in-out infinite;
}

.insignia-nivel-10 .insignia-nivel-num {
    color: #ffec80;
    font-weight: 900;
    letter-spacing: 0.18em;
}
.insignia-nivel-10 .insignia-nombre {
    color: #ffe566;
    font-weight: 800;
}

/* Bordes cónicos — eliminados, solo pulso de borde */

/* Destello dorado central — estático */
.insignia-nivel-10 .insignia-fx {
    position: absolute; inset: 0; z-index: 1; pointer-events: none; overflow: hidden;
    background: linear-gradient(
        105deg,
        transparent 0%, #ffffff08 40%, #ffd70018 50%, #ffffff08 60%, transparent 100%
    );
}

/* =================================================================
   MÓVIL — @media (hover: none) and (pointer: coarse)
   Sin animaciones. Solo colores, gradientes y box-shadow estáticos
   que conservan la identidad visual de cada nivel.
   ================================================================= */
@media (hover: none) and (pointer: coarse) {

    /* Sin escalado al tocar */
    .insignia-rango:hover { transform: none; }

    /* Desactivar TODO — animaciones y transiciones en todos los hijos */
    .insignia-rango,
    .insignia-rango *,
    .insignia-rango::before,
    .insignia-rango::after {
        animation: none !important;
        transition: none !important;
    }

    /* Ocultar capas de efecto — solo existen para animar */
    .insignia-fx,
    .insignia-fx::before,
    .insignia-fx::after { display: none !important; }

    /* Ocultar pseudo-elementos de bordes/auras rotantes */
    .insignia-nivel-6::before,  .insignia-nivel-6::after,
    .insignia-nivel-9::before,  .insignia-nivel-9::after,
    .insignia-nivel-10::before, .insignia-nivel-10::after { display: none !important; }

    /* ── Nv.1 Novato — metal oscuro mate ─────────────────────────── */
    .insignia-nivel-1 {
        box-shadow: inset 0 1px 1px #ffffff10, 0 1px 3px #00000080;
    }

    /* ── Nv.2 Aprendiz — metal pulido, borde plateado ───────────── */
    .insignia-nivel-2 {
        border-color: #999;
        box-shadow: inset 0 1px 3px #ffffff20, 0 2px 6px #00000060;
    }

    /* ── Nv.3 Técnico de Soporte — aura azul corporativa ────────── */
    .insignia-nivel-3 {
        border-color: #3a78d4;
        box-shadow: 0 0 8px 2px #2a5faa50, inset 0 0 8px #0d2040;
    }

    /* ── Nv.4 Operador — halo verde neón ─────────────────────────── */
    .insignia-nivel-4 {
        border-color: #00cc44;
        box-shadow: 0 0 10px 3px #00ff6640, inset 0 0 8px #00ff6620;
    }
    .insignia-nivel-4 .insignia-nombre { text-shadow: 0 0 6px #00ff6660; }

    /* ── Nv.5 Especialista — halo ámbar industrial ───────────────── */
    .insignia-nivel-5 {
        border-color: #c8a000;
        box-shadow: 0 0 10px 3px #f5c40040, inset 0 0 8px #f5c40020, 0 2px 8px #00000080;
    }

    /* ── Nv.6 Élite — resplandor azul eléctrico ──────────────────── */
    .insignia-nivel-6 {
        border-color: #1e90ff;
        box-shadow: 0 0 12px 4px #1e90ff60, inset 0 0 6px #1e90ff20;
    }
    .insignia-nivel-6 .insignia-nombre { text-shadow: 0 0 8px #1e90ffa0; }

    /* ── Nv.7 Maestro — aura violeta holográfica ─────────────────── */
    .insignia-nivel-7 {
        border-color: #cc00ff;
        box-shadow: 0 0 12px 4px #cc00ff60, inset 0 0 8px #cc00ff20;
    }
    .insignia-nivel-7 .insignia-nombre { text-shadow: 0 0 8px #cc00ffa0; }

    /* ── Nv.8 Arquitecto — núcleo plasma rojo ────────────────────── */
    .insignia-nivel-8 {
        background: radial-gradient(ellipse at 40% 50%, #8b0000 0%, transparent 55%), #140000;
        background-size: 100% 100%;
        border-color: #cc0000;
        box-shadow: 0 0 14px 4px #cc000070, inset 0 0 10px #ff000025;
    }
    .insignia-nivel-8 .insignia-nombre { text-shadow: 0 0 8px #ff0000a0; }

    /* ── Nv.9 Guardián — halo dorado intenso ─────────────────────── */
    .insignia-nivel-9 {
        border-color: #ffd700;
        box-shadow: 0 0 16px 5px #ffd70070, 0 0 30px 10px #ffd70030;
    }
    .insignia-nivel-9 .insignia-nivel-num { text-shadow: 0 0 8px #ffd700c0; }
    .insignia-nivel-9 .insignia-nombre    { text-shadow: 0 0 8px #ffd700c0; }

    /* ── Nv.10 Leyenda — fuego dorado estático ───────────────────── */
    .insignia-nivel-10 {
        background: linear-gradient(135deg, #2a1200 0%, #1e0d00 50%, #3a1800 100%);
        background-size: 100% 100%;
        border-color: #ffd700;
        box-shadow:
            0 0 16px 6px #ffd700a0,
            0 0 32px 12px #ff880060,
            0 0 50px 18px #ffd70038,
            inset 0 0 18px #ffd70040;
    }
    .insignia-nivel-10 .insignia-nivel-num {
        text-shadow: 0 0 6px #fff, 0 0 14px #ffd700, 0 0 26px #ff8800;
    }
    .insignia-nivel-10 .insignia-nombre {
        text-shadow: 0 0 6px #fff, 0 0 14px #ffd700, 0 0 26px #ff8800;
    }
}
</style>
