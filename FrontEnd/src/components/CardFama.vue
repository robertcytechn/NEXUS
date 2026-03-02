<script setup>
/**
 * CardFama.vue — StarCraft II Hero Card Edition
 * ================================================
 * Carta de héroe estilo SC2 con efecto 3D, badge de rango SVG
 * centrado en el fondo, nombre del rango en el banner superior.
 */
import { computed, ref } from 'vue';
import api from '@/service/api';

const props = defineProps({
    tecnico: {
        type: Object,
        required: true
    }
});

// ── Datos básicos ──────────────────────────────────────────────────────────
const fullName = computed(() =>
    `${props.tecnico.nombres || ''} ${props.tecnico.apellido_paterno || ''}`.trim()
);
const rango       = computed(() => props.tecnico.rango || {});
const nivel       = computed(() => rango.value.nivel || 1);
const progresoPct = computed(() => Math.min(rango.value.progreso_pct || 0, 100));

const avatarUrl = computed(() => {
    if (props.tecnico.avatar) {
        if (props.tecnico.avatar.startsWith('http')) return props.tecnico.avatar;
        const baseUrl   = api.defaults.baseURL || '';
        const serverUrl = baseUrl.replace(/\/api\/?$/, '');
        return props.tecnico.avatar.startsWith('/')
            ? `${serverUrl}${props.tecnico.avatar}`
            : props.tecnico.avatar;
    }
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(fullName.value)}&background=1a1a2e&color=aaddff&size=200`;
});

// ── Config estética por nivel (paleta SC2) ─────────────────────────────────
const levelConfig = {
    1:  { primary: '#8B6914', secondary: '#5C4008', glow: '#c8933040', bannerBg: '#1a1008', text: '#c89330', border: '#8B6914' },
    2:  { primary: '#A0A0B0', secondary: '#606070', glow: '#b0b0c040', bannerBg: '#141418', text: '#d0d0e0', border: '#909090' },
    3:  { primary: '#2a6fd4', secondary: '#0d2a5c', glow: '#2a6fd450', bannerBg: '#060e1e', text: '#70aaff', border: '#2a6fd4' },
    4:  { primary: '#00cc55', secondary: '#005522', glow: '#00cc5550', bannerBg: '#010d05', text: '#00ff77', border: '#00cc55' },
    5:  { primary: '#d4aa00', secondary: '#5c4a00', glow: '#d4aa0055', bannerBg: '#130f00', text: '#ffd740', border: '#d4aa00' },
    6:  { primary: '#00cfff', secondary: '#004d66', glow: '#00cfff60', bannerBg: '#001520', text: '#60e8ff', border: '#00cfff' },
    7:  { primary: '#bb44ff', secondary: '#4a0080', glow: '#bb44ff60', bannerBg: '#120020', text: '#dd88ff', border: '#bb44ff' },
    8:  { primary: '#dd1111', secondary: '#660000', glow: '#dd111170', bannerBg: '#150000', text: '#ff6666', border: '#dd1111' },
    9:  { primary: '#ffd700', secondary: '#886600', glow: '#ffd70070', bannerBg: '#100d00', text: '#ffe980', border: '#ffd700' },
    10: { primary: '#ff9500', secondary: '#7a3800', glow: '#ff950080', bannerBg: '#1a0800', text: '#ffcc55', border: '#ff7700' },
};

const cfg = computed(() => levelConfig[nivel.value] || levelConfig[1]);

// ── Efecto 3D tilt ─────────────────────────────────────────────────────────
const cardRef   = ref(null);
const tiltX     = ref(0);
const tiltY     = ref(0);
const isHovered = ref(false);
const glowX     = ref(50);
const glowY     = ref(50);

function onMouseMove(e) {
    if (!cardRef.value) return;
    const rect  = cardRef.value.getBoundingClientRect();
    const cx    = rect.left + rect.width  / 2;
    const cy    = rect.top  + rect.height / 2;
    const dx    = (e.clientX - cx) / (rect.width  / 2);
    const dy    = (e.clientY - cy) / (rect.height / 2);
    tiltX.value = -dy * 12;
    tiltY.value =  dx * 12;
    glowX.value = ((e.clientX - rect.left) / rect.width)  * 100;
    glowY.value = ((e.clientY - rect.top)  / rect.height) * 100;
    isHovered.value = true;
}

function onMouseLeave() {
    tiltX.value = 0;
    tiltY.value = 0;
    isHovered.value = false;
}

const cardTransform = computed(() =>
    `perspective(800px) rotateX(${tiltX.value}deg) rotateY(${tiltY.value}deg) scale(${isHovered.value ? 1.04 : 1})`
);
</script>

<template>
    <div
        ref="cardRef"
        class="card-fama-outer"
        @mousemove="onMouseMove"
        @mouseleave="onMouseLeave"
        :style="{ transform: cardTransform, transition: isHovered ? 'transform 0.08s ease-out' : 'transform 0.5s ease' }"
    >
        <!-- ══ Cuerpo de la tarjeta ══════════════════════════════════════ -->
        <div
            class="card-fama-body"
            :style="{
                '--c-primary':   cfg.primary,
                '--c-secondary': cfg.secondary,
                '--c-glow':      cfg.glow,
                '--c-banner':    cfg.bannerBg,
                '--c-text':      cfg.text,
                '--c-border':    cfg.border,
                '--glow-x':      glowX + '%',
                '--glow-y':      glowY + '%',
            }"
        >
            <!-- 1. BANNER SUPERIOR — Nombre del rango ──────────────────── -->
            <div class="rank-banner">
                <div class="rank-banner-inner">
                    <span class="rank-badge-pip">NV.{{ nivel }}</span>
                    <span class="rank-title-text">{{ rango.titulo || 'Novato' }}</span>
                </div>
                <div class="rank-banner-line rank-banner-line--left"></div>
                <div class="rank-banner-line rank-banner-line--right"></div>
            </div>

            <!-- 2. AVATAR ───────────────────────────────────────────────── -->
            <div class="avatar-section">
                <!-- Anillo decorativo del color del rango -->
                <div class="avatar-ring">
                    <img
                        :src="avatarUrl"
                        :alt="fullName"
                        class="avatar-img"
                        @error="$event.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(fullName)}&background=1a1a2e&color=aaddff&size=200`"
                    />
                    <!-- Overlay de color del rango dentro del circulo -->
                    <div class="avatar-rank-overlay"></div>
                    <!-- Resplandor de cursor -->
                    <div
                        class="avatar-hover-glow"
                        :style="{ background: `radial-gradient(circle at ${glowX}% ${glowY}%, var(--c-glow) 0%, transparent 65%)` }"
                    ></div>
                </div>
            </div>

            <!-- 3. INFORMACIÓN ──────────────────────────────────────────── -->
            <div class="info-section">
                <h3 class="tech-name">{{ fullName }}</h3>
                <div class="tech-casino">
                    <i class="pi pi-building text-xs mr-1 opacity-60"></i>
                    {{ tecnico.casino_nombre || 'NEXUS' }}
                </div>

                <!-- Panel XP -->
                <div class="xp-panel">
                    <div class="xp-header">
                        <span class="xp-label">XP</span>
                        <span class="xp-value">{{ tecnico.puntos_gamificacion_historico?.toLocaleString() }}</span>
                    </div>
                    <div class="xp-bar-track">
                        <div v-if="progresoPct >= 100" class="xp-bar-pulse"></div>
                        <div class="xp-bar-fill" :style="{ width: `${progresoPct}%` }"></div>
                    </div>
                    <div class="xp-progress-label">{{ progresoPct.toFixed(0) }}% al siguiente rango</div>
                </div>

                <!-- ══ ESTADÍSTICAS DE ACTIVIDAD ══════════════════════════ -->
                <div class="stats-grid">
                    <div class="stat-item">
                        <i class="pi pi-ticket stat-icon"></i>
                        <span class="stat-value">{{ tecnico.tickets_cerrados ?? '—' }}</span>
                        <span class="stat-label">Tickets</span>
                    </div>
                    <div class="stat-item">
                        <i class="pi pi-book stat-icon"></i>
                        <span class="stat-value">{{ tecnico.wikis_publicadas ?? '—' }}</span>
                        <span class="stat-label">Wikis</span>
                    </div>
                    <div class="stat-item">
                        <i class="pi pi-wrench stat-icon"></i>
                        <span class="stat-value">{{ tecnico.mantenimientos_realizados ?? '—' }}</span>
                        <span class="stat-label">Mttos.</span>
                    </div>
                    <div class="stat-item">
                        <i class="pi pi-pencil stat-icon"></i>
                        <span class="stat-value">{{ tecnico.entradas_bitacora ?? '—' }}</span>
                        <span class="stat-label">Bitácora</span>
                    </div>
                </div>

                <!-- ══ BADGE SVG ═══════════════════════════════════════════ -->
                <div class="rank-badge-bottom">
                    <div class="badge-platform">

                    <!-- NV 1 — Bronce / Novato: Hexágono oxidado -->
                    <svg v-if="nivel===1" viewBox="0 0 100 100" class="badge-svg">
                        <defs>
                            <radialGradient id="b1-bg" cx="50%" cy="40%" r="55%">
                                <stop offset="0%" stop-color="#cc8833"/>
                                <stop offset="100%" stop-color="#4a2808"/>
                            </radialGradient>
                        </defs>
                        <polygon points="50,8 86,28 86,72 50,92 14,72 14,28" fill="url(#b1-bg)" stroke="#8B6914" stroke-width="3"/>
                        <polygon points="50,18 76,33 76,67 50,82 24,67 24,33" fill="none" stroke="#c89330" stroke-width="1.5" opacity="0.5"/>
                        <text x="50" y="56" text-anchor="middle" font-size="22" font-weight="900" fill="#e8aa50" font-family="monospace">I</text>
                        <line x1="30" y1="40" x2="70" y2="40" stroke="#c89330" stroke-width="1" opacity="0.6"/>
                        <line x1="30" y1="66" x2="70" y2="66" stroke="#c89330" stroke-width="1" opacity="0.6"/>
                    </svg>

                    <!-- NV 2 — Plata / Aprendiz: Diamante con chevron -->
                    <svg v-else-if="nivel===2" viewBox="0 0 100 100" class="badge-svg">
                        <defs>
                            <linearGradient id="b2-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#d0d0e0"/>
                                <stop offset="50%" stop-color="#707080"/>
                                <stop offset="100%" stop-color="#c0c0d0"/>
                            </linearGradient>
                        </defs>
                        <polygon points="50,6 92,50 50,94 8,50" fill="url(#b2-bg)" stroke="#aaaacc" stroke-width="2.5"/>
                        <polygon points="50,16 82,50 50,84 18,50" fill="none" stroke="#ffffffa0" stroke-width="1"/>
                        <polyline points="38,60 50,48 62,60" fill="none" stroke="#e0e0f0" stroke-width="3" stroke-linecap="round"/>
                        <polyline points="38,50 50,38 62,50" fill="none" stroke="#ffffffc0" stroke-width="2" stroke-linecap="round"/>
                    </svg>

                    <!-- NV 3 — Azul / Soporte: Escudo Terran con HUD -->
                    <svg v-else-if="nivel===3" viewBox="0 0 100 100" class="badge-svg">
                        <defs>
                            <linearGradient id="b3-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#0d2850"/>
                                <stop offset="100%" stop-color="#051020"/>
                            </linearGradient>
                        </defs>
                        <path d="M50 8 L82 22 L82 58 Q82 78 50 92 Q18 78 18 58 L18 22 Z" fill="url(#b3-bg)" stroke="#2a6fd4" stroke-width="2.5"/>
                        <path d="M50 18 L72 29 L72 56 Q72 70 50 80 Q28 70 28 56 L28 29 Z" fill="none" stroke="#4a8fd4" stroke-width="1" opacity="0.6"/>
                        <line x1="50" y1="18" x2="50" y2="80" stroke="#2a6fd4" stroke-width="1" opacity="0.4"/>
                        <line x1="30" y1="45" x2="70" y2="45" stroke="#2a6fd4" stroke-width="1" opacity="0.4"/>
                        <circle cx="50" cy="45" r="12" fill="none" stroke="#2a6fd4" stroke-width="2"/>
                        <circle cx="50" cy="45" r="5" fill="#2a6fd4"/>
                        <circle cx="50" cy="45" r="2" fill="#70aaff"/>
                    </svg>

                    <!-- NV 4 — Verde / Operador: Diamante grilla neón -->
                    <svg v-else-if="nivel===4" viewBox="0 0 100 100" class="badge-svg">
                        <defs>
                            <linearGradient id="b4-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#011508"/>
                                <stop offset="100%" stop-color="#000a04"/>
                            </linearGradient>
                        </defs>
                        <polygon points="50,5 95,50 50,95 5,50" fill="url(#b4-bg)" stroke="#00cc55" stroke-width="2.5"/>
                        <polygon points="50,18 82,50 50,82 18,50" fill="none" stroke="#00ff7750" stroke-width="1"/>
                        <line x1="20" y1="50" x2="80" y2="50" stroke="#00cc5540" stroke-width="1"/>
                        <line x1="50" y1="20" x2="50" y2="80" stroke="#00cc5540" stroke-width="1"/>
                        <line x1="28" y1="28" x2="72" y2="72" stroke="#00cc5525" stroke-width="1"/>
                        <line x1="72" y1="28" x2="28" y2="72" stroke="#00cc5525" stroke-width="1"/>
                        <circle cx="50" cy="50" r="10" fill="#00cc5530" stroke="#00ff77" stroke-width="2"/>
                        <circle cx="50" cy="50" r="3" fill="#00ff77"/>
                    </svg>

                    <!-- NV 5 — Oro / Especialista: Escudo con 3 chevrones -->
                    <svg v-else-if="nivel===5" viewBox="0 0 100 100" class="badge-svg">
                        <defs>
                            <radialGradient id="b5-bg" cx="50%" cy="35%" r="60%">
                                <stop offset="0%" stop-color="#3a2800"/>
                                <stop offset="100%" stop-color="#150f00"/>
                            </radialGradient>
                        </defs>
                        <path d="M50 5 L85 20 L85 60 Q85 82 50 95 Q15 82 15 60 L15 20 Z" fill="url(#b5-bg)" stroke="#d4aa00" stroke-width="2.5"/>
                        <path d="M50 15 L75 27 L75 58 Q75 74 50 84 Q25 74 25 58 L25 27 Z" fill="none" stroke="#d4aa0080" stroke-width="1"/>
                        <polyline points="36,68 50,55 64,68" fill="none" stroke="#ffd740" stroke-width="2.5" stroke-linecap="round"/>
                        <polyline points="36,57 50,44 64,57" fill="none" stroke="#d4aa00" stroke-width="2" stroke-linecap="round"/>
                        <polyline points="36,46 50,33 64,46" fill="none" stroke="#aa8800" stroke-width="1.5" stroke-linecap="round"/>
                    </svg>

                    <!-- NV 6 — Cyan / Élite: Diamante con alas eléctricas -->
                    <svg v-else-if="nivel===6" viewBox="0 0 100 100" class="badge-svg">
                        <defs>
                            <radialGradient id="b6-core" cx="50%" cy="50%" r="40%">
                                <stop offset="0%" stop-color="#00cfff"/>
                                <stop offset="100%" stop-color="#004466"/>
                            </radialGradient>
                        </defs>
                        <path d="M50,50 L10,35 L20,50 L10,65 Z" fill="#00cfff30" stroke="#00cfff60" stroke-width="1"/>
                        <path d="M50,50 L90,35 L80,50 L90,65 Z" fill="#00cfff30" stroke="#00cfff60" stroke-width="1"/>
                        <polygon points="50,8 72,50 50,92 28,50" fill="url(#b6-core)" stroke="#00cfff" stroke-width="2.5"/>
                        <polygon points="50,20 62,50 50,80 38,50" fill="none" stroke="#60e8ff" stroke-width="1" opacity="0.7"/>
                        <circle cx="50" cy="50" r="8" fill="#00cfff40" stroke="#60e8ff" stroke-width="1.5"/>
                        <circle cx="50" cy="50" r="3" fill="#60e8ff"/>
                    </svg>

                    <!-- NV 7 — Púrpura / Maestro: Corona holográfica -->
                    <svg v-else-if="nivel===7" viewBox="0 0 100 100" class="badge-svg">
                        <defs>
                            <radialGradient id="b7-bg" cx="50%" cy="40%" r="55%">
                                <stop offset="0%" stop-color="#3a0060"/>
                                <stop offset="100%" stop-color="#0d0018"/>
                            </radialGradient>
                        </defs>
                        <polygon points="50,8 86,28 86,72 50,92 14,72 14,28" fill="url(#b7-bg)" stroke="#bb44ff" stroke-width="2.5"/>
                        <path d="M30,65 L30,42 L40,55 L50,30 L60,55 L70,42 L70,65 Z" fill="#bb44ff40" stroke="#dd88ff" stroke-width="2" stroke-linejoin="round"/>
                        <circle cx="30" cy="42" r="4" fill="#cc00ff" stroke="#ee88ff" stroke-width="1"/>
                        <circle cx="50" cy="30" r="5" fill="#dd55ff" stroke="#ee88ff" stroke-width="1"/>
                        <circle cx="70" cy="42" r="4" fill="#cc00ff" stroke="#ee88ff" stroke-width="1"/>
                        <rect x="26" y="63" width="48" height="6" rx="2" fill="#9922cc" stroke="#dd88ff" stroke-width="1"/>
                    </svg>

                    <!-- NV 8 — Rojo / Arquitecto: Escudo plasma inestable -->
                    <svg v-else-if="nivel===8" viewBox="0 0 100 100" class="badge-svg">
                        <defs>
                            <radialGradient id="b8-bg" cx="50%" cy="35%" r="60%">
                                <stop offset="0%" stop-color="#550000"/>
                                <stop offset="100%" stop-color="#150000"/>
                            </radialGradient>
                        </defs>
                        <path d="M50 5 L88 22 L95 55 L50 95 L5 55 L12 22 Z" fill="url(#b8-bg)" stroke="#dd1111" stroke-width="2.5"/>
                        <path d="M50 15 L78 30 L84 55 L50 82 L16 55 L22 30 Z" fill="none" stroke="#ff444440" stroke-width="1"/>
                        <path d="M50,25 L45,42 L55,42 L42,60 L50,60 L38,78" fill="none" stroke="#ff6666" stroke-width="2" stroke-linecap="round"/>
                        <path d="M50,25 L55,40 L47,40 L58,56 L50,56 L62,78" fill="none" stroke="#ff333380" stroke-width="1" stroke-linecap="round"/>
                        <circle cx="50" cy="25" r="4" fill="#ff4444" stroke="#ff8888" stroke-width="1"/>
                    </svg>

                    <!-- NV 9 — Dorado / Guardián: Escudo con alas y gema divina -->
                    <svg v-else-if="nivel===9" viewBox="0 0 100 100" class="badge-svg">
                        <defs>
                            <radialGradient id="b9-gem" cx="50%" cy="50%" r="50%">
                                <stop offset="0%" stop-color="#fff7a0"/>
                                <stop offset="50%" stop-color="#ffd700"/>
                                <stop offset="100%" stop-color="#886600"/>
                            </radialGradient>
                            <radialGradient id="b9-bg" cx="50%" cy="30%" r="60%">
                                <stop offset="0%" stop-color="#2a2000"/>
                                <stop offset="100%" stop-color="#100c00"/>
                            </radialGradient>
                        </defs>
                        <path d="M50,55 C40,45 20,40 8,50 C15,35 35,28 50,38 Z" fill="#ffd70040" stroke="#ffd700" stroke-width="1.5"/>
                        <path d="M50,55 C60,45 80,40 92,50 C85,35 65,28 50,38 Z" fill="#ffd70040" stroke="#ffd700" stroke-width="1.5"/>
                        <path d="M50 10 L80 24 L80 58 Q80 78 50 90 Q20 78 20 58 L20 24 Z" fill="url(#b9-bg)" stroke="#ffd700" stroke-width="2.5"/>
                        <polygon points="50,30 60,50 50,70 40,50" fill="url(#b9-gem)" stroke="#fff7a0" stroke-width="1.5"/>
                        <polygon points="50,38 56,50 50,62 44,50" fill="#fff7a080" stroke="none"/>
                    </svg>

                    <!-- NV 10 — Leyenda de NEXUS: Corona épica con gema central y llamas -->
                    <svg v-else-if="nivel===10" viewBox="0 0 100 100" class="badge-svg badge-leyenda">
                        <defs>
                            <radialGradient id="b10-bg" cx="50%" cy="45%" r="55%">
                                <stop offset="0%" stop-color="#2a1200"/>
                                <stop offset="70%" stop-color="#0d0600"/>
                                <stop offset="100%" stop-color="#060200"/>
                            </radialGradient>
                            <linearGradient id="b10-cg" x1="25%" y1="0%" x2="75%" y2="100%">
                                <stop offset="0%" stop-color="#fffbe6"/>
                                <stop offset="22%" stop-color="#ffd700"/>
                                <stop offset="60%" stop-color="#cc8800"/>
                                <stop offset="100%" stop-color="#7a4400"/>
                            </linearGradient>
                            <radialGradient id="b10-diamond" cx="38%" cy="32%" r="60%">
                                <stop offset="0%" stop-color="#ffffff"/>
                                <stop offset="30%" stop-color="#fffbe0"/>
                                <stop offset="65%" stop-color="#ffd700"/>
                                <stop offset="100%" stop-color="#ff8800"/>
                            </radialGradient>
                            <radialGradient id="b10-ruby" cx="35%" cy="30%" r="60%">
                                <stop offset="0%" stop-color="#ffcccc"/>
                                <stop offset="40%" stop-color="#ff2244"/>
                                <stop offset="100%" stop-color="#660011"/>
                            </radialGradient>
                            <linearGradient id="b10-ring" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#ffd700"/>
                                <stop offset="40%" stop-color="#ffaa00"/>
                                <stop offset="100%" stop-color="#ffd700"/>
                            </linearGradient>
                            <linearGradient id="b10-flame" x1="0%" y1="100%" x2="0%" y2="0%">
                                <stop offset="0%" stop-color="#ff4400"/>
                                <stop offset="55%" stop-color="#ff9900"/>
                                <stop offset="100%" stop-color="#ffee00" stop-opacity="0.1"/>
                            </linearGradient>
                            <radialGradient id="b10-outglow" cx="50%" cy="50%" r="50%">
                                <stop offset="35%" stop-color="transparent"/>
                                <stop offset="100%" stop-color="#ff880022"/>
                            </radialGradient>
                        </defs>

                        <!-- Halo exterior suave -->
                        <circle cx="50" cy="50" r="49" fill="url(#b10-outglow)" stroke="none"/>

                        <!-- Fondo oscuro principal -->
                        <circle cx="50" cy="50" r="45" fill="url(#b10-bg)"/>

                        <!-- Anillo doble decorativo exterior -->
                        <circle cx="50" cy="50" r="45" fill="none" stroke="url(#b10-ring)" stroke-width="2.5"/>
                        <circle cx="50" cy="50" r="41.5" fill="none" stroke="#ffd70035" stroke-width="0.7"/>

                        <!-- 12 marcas de tic en el anillo (cada 30°) -->
                        <line x1="50" y1="5"   x2="50" y2="10"  stroke="#ffd700" stroke-width="1.6" stroke-linecap="round"/>
                        <line x1="72.5" y1="11" x2="70.4" y2="15.1" stroke="#ffd700" stroke-width="1" stroke-linecap="round"/>
                        <line x1="88.9" y1="27.5" x2="85.4" y2="29.6" stroke="#ffd700" stroke-width="1" stroke-linecap="round"/>
                        <line x1="95" y1="50"  x2="90" y2="50"  stroke="#ffd700" stroke-width="1.6" stroke-linecap="round"/>
                        <line x1="88.9" y1="72.5" x2="85.4" y2="70.4" stroke="#ffd700" stroke-width="1" stroke-linecap="round"/>
                        <line x1="72.5" y1="89" x2="70.4" y2="85" stroke="#ffd700" stroke-width="1" stroke-linecap="round"/>
                        <line x1="50" y1="95"  x2="50" y2="90"  stroke="#ffd700" stroke-width="1.6" stroke-linecap="round"/>
                        <line x1="27.5" y1="89" x2="29.6" y2="85" stroke="#ffd700" stroke-width="1" stroke-linecap="round"/>
                        <line x1="11.1" y1="72.5" x2="14.6" y2="70.4" stroke="#ffd700" stroke-width="1" stroke-linecap="round"/>
                        <line x1="5" y1="50"   x2="10" y2="50"  stroke="#ffd700" stroke-width="1.6" stroke-linecap="round"/>
                        <line x1="11.1" y1="27.5" x2="14.6" y2="29.6" stroke="#ffd700" stroke-width="1" stroke-linecap="round"/>
                        <line x1="27.5" y1="11" x2="29.6" y2="15.1" stroke="#ffd700" stroke-width="1" stroke-linecap="round"/>

                        <!-- Diamantes ornamentales en los 4 puntos cardinales del anillo -->
                        <polygon points="50,2 52.5,5 50,8 47.5,5"   fill="#ffd700" stroke="#fff7c0" stroke-width="0.5"/>
                        <polygon points="50,92 52.5,95 50,98 47.5,95" fill="#ffd700" stroke="#fff7c0" stroke-width="0.5"/>
                        <polygon points="92,50 95,52.5 98,50 95,47.5" fill="#ffd700" stroke="#fff7c0" stroke-width="0.5"/>
                        <polygon points="2,50 5,52.5 8,50 5,47.5"   fill="#ffd700" stroke="#fff7c0" stroke-width="0.5"/>

                        <!-- Starburst de 8 rayos tenue detrás de la corona -->
                        <line x1="50" y1="12" x2="50" y2="88" stroke="#ffd70015" stroke-width="9"/>
                        <line x1="12" y1="50" x2="88" y2="50" stroke="#ffd70015" stroke-width="9"/>
                        <line x1="22" y1="22" x2="78" y2="78" stroke="#ffd70010" stroke-width="6"/>
                        <line x1="78" y1="22" x2="22" y2="78" stroke="#ffd70010" stroke-width="6"/>

                        <!-- Llamas que suben desde la base de la corona -->
                        <path d="M33,78 C31,71 29,63 32,57 C34,64 35,71 36,78 Z" fill="url(#b10-flame)" opacity="0.65"/>
                        <path d="M41,78 C39,69 37,60 40,52 C43,61 43,70 44,78 Z" fill="url(#b10-flame)" opacity="0.75"/>
                        <path d="M50,78 C48,67 46,55 50,46 C54,55 52,67 50,78 Z" fill="url(#b10-flame)" opacity="0.85"/>
                        <path d="M59,78 C61,69 63,60 60,52 C57,61 57,70 56,78 Z" fill="url(#b10-flame)" opacity="0.75"/>
                        <path d="M67,78 C69,71 71,63 68,57 C66,64 65,71 64,78 Z" fill="url(#b10-flame)" opacity="0.65"/>

                        <!-- Sombra/glow debajo de la corona -->
                        <ellipse cx="50" cy="79" rx="24" ry="3.5" fill="#ff880045"/>

                        <!-- BASE DE LA CORONA (banda ornamentada) -->
                        <rect x="26" y="73" width="48" height="8" rx="2.5" fill="url(#b10-cg)" stroke="#fff7a070" stroke-width="0.8"/>
                        <line x1="29" y1="76" x2="71" y2="76" stroke="#ffffff35" stroke-width="0.5"/>
                        <line x1="29" y1="78.5" x2="71" y2="78.5" stroke="#00000030" stroke-width="0.5"/>
                        <!-- Notches decorativos en la banda -->
                        <rect x="37" y="74.2" width="5" height="2.5" rx="0.8" fill="#ffffff28"/>
                        <rect x="47" y="74.2" width="6" height="2.5" rx="0.8" fill="#ffffff38"/>
                        <rect x="58" y="74.2" width="5" height="2.5" rx="0.8" fill="#ffffff28"/>

                        <!-- CUERPO DE LA CORONA — 5 puntas, punta central ALTA -->
                        <path d="
                            M26,73
                            L26,61
                            L31,54
                            L36,63
                            L41,40
                            L46,55
                            L50,14
                            L54,55
                            L59,40
                            L64,63
                            L69,54
                            L74,61
                            L74,73
                            Z
                        " fill="url(#b10-cg)" stroke="#fff7a0" stroke-width="1.3" stroke-linejoin="round"/>

                        <!-- Reflejos internos en las caras de la corona -->
                        <line x1="31" y1="54" x2="33.5" y2="63" stroke="#ffffff90" stroke-width="0.7" stroke-linecap="round"/>
                        <line x1="41" y1="40" x2="43"   y2="55" stroke="#ffffff80" stroke-width="0.7" stroke-linecap="round"/>
                        <line x1="50" y1="14" x2="51.5" y2="55" stroke="#ffffff70" stroke-width="0.8" stroke-linecap="round"/>
                        <line x1="69" y1="54" x2="66.5" y2="63" stroke="#ffffff90" stroke-width="0.7" stroke-linecap="round"/>
                        <line x1="59" y1="40" x2="57"   y2="55" stroke="#ffffff80" stroke-width="0.7" stroke-linecap="round"/>

                        <!-- Sombra interior de la corona (profundidad) -->
                        <path d="M26,73 L26,61 L31,54 L36,63 L41,40 L46,55 L50,14 L54,55 L59,40 L64,63 L69,54 L74,61 L74,73 Z"
                              fill="#00000020" stroke="none"
                              transform="translate(1.5, 1.5)"/>

                        <!-- GEMAS EN PUNTAS EXTERIORES (pequeñas, doradas) -->
                        <polygon points="31,54 28.5,58 31,62.5 33.5,58" fill="#ffd700" stroke="#fff7a0" stroke-width="0.7"/>
                        <polygon points="69,54 66.5,58 69,62.5 71.5,58" fill="#ffd700" stroke="#fff7a0" stroke-width="0.7"/>

                        <!-- RUBÍES EN PUNTAS INTERIORES -->
                        <polygon points="41,40 38,43.5 38,48 41,51.5 44,48 44,43.5" fill="url(#b10-ruby)" stroke="#ffaaaa" stroke-width="0.9"/>
                        <polygon points="59,40 56,43.5 56,48 59,51.5 62,48 62,43.5" fill="url(#b10-ruby)" stroke="#ffaaaa" stroke-width="0.9"/>
                        <!-- Reflejo brillo en rubíes -->
                        <ellipse cx="39.5" cy="43.5" rx="1.8" ry="1.1" fill="#ffffff55" transform="rotate(-25 39.5 43.5)"/>
                        <ellipse cx="58.5" cy="43.5" rx="1.8" ry="1.1" fill="#ffffff55" transform="rotate(25 58.5 43.5)"/>

                        <!-- GEMA CENTRAL PRINCIPAL — gran diamante brillante -->
                        <!-- Sombra de la gema -->
                        <polygon points="50,12 56,19 50,30 44,19" fill="#00000040" transform="translate(1,1.5)"/>
                        <!-- Gema principal -->
                        <polygon points="50,11 56,18.5 50,29 44,18.5" fill="url(#b10-diamond)" stroke="#ffffff" stroke-width="1.3"/>
                        <!-- Facetas internas de la gema -->
                        <polygon points="50,11 56,18.5 50,20 44,18.5" fill="#ffffff30"/>
                        <polygon points="50,20 56,18.5 50,29" fill="#00000020"/>
                        <line x1="50" y1="11" x2="50" y2="29" stroke="#ffffff40" stroke-width="0.5"/>
                        <!-- Destello superior de la gema -->
                        <line x1="50" y1="8"  x2="50" y2="12"  stroke="#ffffff" stroke-width="1.2" stroke-linecap="round"/>
                        <line x1="47" y1="9"  x2="48.8" y2="12.5" stroke="#ffffffaa" stroke-width="0.9" stroke-linecap="round"/>
                        <line x1="53" y1="9"  x2="51.2" y2="12.5" stroke="#ffffffaa" stroke-width="0.9" stroke-linecap="round"/>
                        <line x1="45" y1="11" x2="47"   y2="13.5" stroke="#ffffff60" stroke-width="0.7" stroke-linecap="round"/>
                        <line x1="55" y1="11" x2="53"   y2="13.5" stroke="#ffffff60" stroke-width="0.7" stroke-linecap="round"/>
                    </svg>

                    </div><!-- /badge-platform -->
                </div><!-- /rank-badge-bottom -->
            </div><!-- /info-section -->

            <!-- Resplandor de cursor -->
            <div
                class="card-cursor-glow"
                :style="{ background: `radial-gradient(circle at ${glowX}% ${glowY}%, var(--c-glow) 0%, transparent 55%)` }"
            ></div>
        </div>
    </div>
</template>

<style scoped>
/* ── Wrapper externo con perspectiva 3D ──────────────────────────────── */
.card-fama-outer {
    width: 100%;
    max-width: 270px;
    margin: 1rem auto 2rem;
    will-change: transform;
    transform-style: preserve-3d;
}

/* ── Cuerpo de la carta ───────────────────────────────────────────────── */
.card-fama-body {
    position: relative;
    background: #0d0d14;
    border-radius: 12px;
    border: 2px solid var(--c-border);
    overflow: hidden;
    box-shadow:
        0 0 0 1px color-mix(in srgb, var(--c-border) 50%, transparent),
        0 0 20px  var(--c-glow),
        0 0 40px  color-mix(in srgb, var(--c-glow) 40%, transparent),
        0 8px 32px rgba(0, 0, 0, 0.6);
}

/* ── Resplandor seguidor del cursor ─────────────────────────────────── */
.card-cursor-glow {
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 5;
    border-radius: 12px;
    opacity: 0.55;
}

/* ══ 1. RANK BANNER ══════════════════════════════════════════════════ */
.rank-banner {
    position: relative;
    background: var(--c-banner);
    border-bottom: 1px solid color-mix(in srgb, var(--c-border) 60%, transparent);
    padding: 9px 14px 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.rank-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(
        90deg,
        transparent 0%,
        color-mix(in srgb, var(--c-primary) 12%, transparent) 50%,
        transparent 100%
    );
    pointer-events: none;
}

.rank-banner-inner {
    display: flex;
    align-items: center;
    gap: 8px;
    position: relative;
    z-index: 2;
}

.rank-badge-pip {
    font-size: 0.58rem;
    font-weight: 900;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--c-primary);
    background: color-mix(in srgb, var(--c-primary) 15%, transparent);
    border: 1px solid color-mix(in srgb, var(--c-primary) 45%, transparent);
    border-radius: 3px;
    padding: 1px 5px;
    flex-shrink: 0;
}

.rank-title-text {
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--c-text);
    text-shadow: 0 0 12px var(--c-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 170px;
}

.rank-banner-line {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 18px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--c-border));
    opacity: 0.6;
    z-index: 2;
}
.rank-banner-line--left  { left: 8px;  transform: translateY(-50%) scaleX(-1); }
.rank-banner-line--right { right: 8px; }

/* ══ 2. AVATAR ══════════════════════════════════════════════════════ */
.avatar-section {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 16px 12px 10px;
    background: linear-gradient(to bottom, color-mix(in srgb, var(--c-banner) 80%, transparent), #0d0d14);
}

.avatar-ring {
    position: relative;
    width: 110px;
    height: 110px;
    border-radius: 50%;
    padding: 3px;
    background: conic-gradient(
        var(--c-primary) 0deg,
        color-mix(in srgb, var(--c-primary) 50%, white) 90deg,
        var(--c-primary) 180deg,
        color-mix(in srgb, var(--c-primary) 40%, black) 270deg,
        var(--c-primary) 360deg
    );
    box-shadow:
        0 0 10px var(--c-glow),
        0 0 24px color-mix(in srgb, var(--c-glow) 50%, transparent),
        inset 0 0 8px rgba(0,0,0,0.6);
    animation: avatar-ring-spin 8s linear infinite;
    flex-shrink: 0;
}

@keyframes avatar-ring-spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}

/* Contra-rotación de la imagen para que no gire con el anillo */
.avatar-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
    display: block;
    transition: transform 0.6s ease;
    animation: avatar-img-counter 8s linear infinite;
    position: relative;
    z-index: 1;
}

@keyframes avatar-img-counter {
    from { transform: rotate(0deg); }
    to   { transform: rotate(-360deg); }
}

.card-fama-outer:hover .avatar-img {
    filter: brightness(1.1);
}

.avatar-rank-overlay {
    position: absolute;
    inset: 3px;
    border-radius: 50%;
    background: radial-gradient(ellipse at 50% 80%, var(--c-glow) 0%, transparent 70%);
    mix-blend-mode: screen;
    pointer-events: none;
    z-index: 2;
}

.avatar-hover-glow {
    position: absolute;
    inset: 3px;
    border-radius: 50%;
    pointer-events: none;
    mix-blend-mode: screen;
    z-index: 2;
}

/* ══ 3. INFORMACIÓN ═════════════════════════════════════════════════ */
.info-section {
    padding: 8px 14px 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    background: linear-gradient(to bottom, #0d0d14, #10101a);
}

.info-section::before {
    content: '';
    display: block;
    width: 75%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--c-border), transparent);
    margin: 0 auto 2px;
    opacity: 0.4;
}

.tech-name {
    font-size: 0.95rem;
    font-weight: 900;
    color: #e8eaf0;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    text-align: center;
    margin: 0;
    text-shadow: 0 1px 8px rgba(0,0,0,0.8);
}

.tech-casino {
    font-size: 0.65rem;
    font-weight: 600;
    color: #6a6a8a;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* ── XP Panel ─────────────────────────────────────────────────────── */
.xp-panel {
    width: 100%;
    background: rgba(0,0,0,0.35);
    border: 1px solid color-mix(in srgb, var(--c-border) 28%, #333);
    border-radius: 6px;
    padding: 7px 10px;
    margin-top: 5px;
}

.xp-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 5px;
}

.xp-label {
    font-size: 0.56rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: #44445a;
    text-transform: uppercase;
}

.xp-value {
    font-size: 1rem;
    font-weight: 900;
    color: var(--c-text);
    font-family: 'Courier New', monospace;
    text-shadow: 0 0 10px var(--c-primary);
    letter-spacing: -0.02em;
}

.xp-bar-track {
    position: relative;
    width: 100%;
    height: 5px;
    background: #1a1a28;
    border-radius: 99px;
    overflow: hidden;
}

.xp-bar-pulse {
    position: absolute;
    inset: 0;
    background: color-mix(in srgb, var(--c-primary) 20%, transparent);
    animation: xp-pulse-anim 1.5s ease-in-out infinite;
}

@keyframes xp-pulse-anim {
    0%, 100% { opacity: 0.4; }
    50%       { opacity: 1; }
}

.xp-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--c-secondary), var(--c-primary), color-mix(in srgb, var(--c-primary) 65%, white));
    border-radius: 99px;
    transition: width 1.2s ease-out;
    box-shadow: 0 0 8px var(--c-primary);
}

.xp-progress-label {
    font-size: 0.52rem;
    color: #383850;
    letter-spacing: 0.1em;
    text-align: right;
    margin-top: 3px;
}

/* ══ STATS DE ACTIVIDAD ══════════════════════════════════════════════ */
.stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 5px;
    width: 100%;
    margin-top: 7px;
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    background: rgba(0, 0, 0, 0.28);
    border: 1px solid color-mix(in srgb, var(--c-border) 22%, #2a2a3a);
    border-radius: 6px;
    padding: 6px 4px 5px;
    transition: background 0.25s ease, border-color 0.25s ease;
}

.card-fama-outer:hover .stat-item {
    background: color-mix(in srgb, var(--c-primary) 8%, rgba(0,0,0,0.35));
    border-color: color-mix(in srgb, var(--c-border) 40%, transparent);
}

.stat-icon {
    font-size: 0.7rem;
    color: var(--c-primary);
    opacity: 0.8;
}

.stat-value {
    font-size: 0.9rem;
    font-weight: 900;
    color: var(--c-text);
    font-family: 'Courier New', monospace;
    line-height: 1;
    letter-spacing: -0.03em;
}

.stat-label {
    font-size: 0.48rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #44445a;
    line-height: 1;
}

/* ══ BADGE INFERIOR ═════════════════════════════════════════════════════ */
.rank-badge-bottom {
    display: flex;
    justify-content: center;
    align-items: flex-end;
    margin-top: 6px;
    padding-bottom: 8px;
}

/* Plataforma que agrupa SVG + sombra de elevación */
.badge-platform {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
}

/* Sombra de elevación debajo del badge — simula que flota ~6px sobre la tarjeta */
.badge-platform::after {
    content: '';
    display: block;
    width: 62px;
    height: 8px;
    border-radius: 50%;
    background: radial-gradient(
        ellipse,
        rgba(0,0,0,0.75) 0%,
        transparent 70%
    );
    margin-top: -6px;
    filter: blur(4px);
}

/* El SVG del badge */
.badge-svg {
    width: 86px;
    height: 86px;
    display: block;
    /* Sombra de elevación: offset hacia abajo, difusa = objeto flotando */
    filter:
        drop-shadow(0px  6px  8px rgba(0,0,0,0.85))
        drop-shadow(0px 12px 14px rgba(0,0,0,0.55))
        drop-shadow(0   0    7px var(--c-primary))
        drop-shadow(0   0   18px var(--c-glow));
    transition: filter 0.35s ease, transform 0.35s ease;
}

.card-fama-outer:hover .badge-svg {
    filter:
        drop-shadow(0px  8px 10px rgba(0,0,0,0.9))
        drop-shadow(0px 16px 18px rgba(0,0,0,0.6))
        drop-shadow(0   0   11px var(--c-primary))
        drop-shadow(0   0   28px var(--c-primary))
        drop-shadow(0   0   48px var(--c-glow));
    transform: scale(1.08) translateY(-3px);
}

/* Badge Leyenda — glow estático sin color-shift */
.badge-leyenda {
    filter:
        drop-shadow(0px  6px  8px rgba(0,0,0,0.85))
        drop-shadow(0px 12px 14px rgba(0,0,0,0.55))
        drop-shadow(0 0  10px #ff9500)
        drop-shadow(0 0  26px #ff6600)
        drop-shadow(0 0  46px #ff440050);
}

/* Hover del badge Leyenda: mantiene colores fuego, no hereda --c-primary */
.card-fama-outer:hover .badge-leyenda {
    filter:
        drop-shadow(0px  8px 10px rgba(0,0,0,0.9))
        drop-shadow(0px 16px 18px rgba(0,0,0,0.6))
        drop-shadow(0 0  14px #ffcc00)
        drop-shadow(0 0  32px #ff8800)
        drop-shadow(0 0  56px #ff440070);
    transform: scale(1.08) translateY(-3px);
}

/* ══ RESPONSIVE ═══════════════════════════════════════════════════════ */

/* Dispositivos táctiles: desactivar animación del anillo y tilt */
@media (hover: none) and (pointer: coarse) {
    .avatar-ring {
        animation: none;
        background: var(--c-primary);
    }
    .avatar-img {
        animation: none;
    }
    .card-cursor-glow {
        display: none;
    }
}

/* Pantallas muy pequeñas (< 360px) */
@media (max-width: 360px) {
    .card-fama-outer {
        max-width: 100%;
        margin: 0.5rem auto 1.5rem;
    }
    .avatar-ring {
        width: 90px;
        height: 90px;
    }
    .badge-svg {
        width: 70px;
        height: 70px;
    }
    .xp-value {
        font-size: 0.85rem;
    }
    .tech-name {
        font-size: 0.82rem;
    }
}
</style>
