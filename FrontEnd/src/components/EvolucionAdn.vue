<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
    trigger: {
        type: [String, Number, Object, Boolean],
        default: null
    }
});

const canvasRef = ref(null);
let animationFrameId = null;
let time = 0;
const numStrands = 24;
const strands = [];

// Paleta de colores requerida (Verdes, esmeraldas, oscuros y acentos neón)
const colorNormal1 = '#10b981'; // nexus green
const colorNormal2 = '#047857'; // emerald
const neonColors = ['#00ffff', '#ff00ff', '#ffff00', '#00ff00', '#f59e0b', '#ec4899', '#3b82f6', '#ff4500'];

// Inicializar cadenas de ADN
for (let i = 0; i < numStrands; i++) {
    strands.push({
        offsetPos: i * 16, // spacing vertical o horizontal
        phase: i * 0.38, // espiral
        color: i % 2 === 0 ? colorNormal1 : colorNormal2,
        isMutating: false,
        mutatingTimer: 0,
        newColor: null,
        breakDistance: 0,
        dirX1: 0, dirX2: 0, dirY1: 0, dirY2: 0
    });
}

// --- SISTEMA DE PARTÍCULAS AMBIENTALES (NUEVO) ---
const ambientParticles = [];
const numParticles = 40;
for (let i = 0; i < numParticles; i++) {
    ambientParticles.push({
        x: Math.random(), // Porcentaje 0-1
        y: Math.random(), // Porcentaje 0-1
        size: Math.random() * 2 + 0.5,
        speedX: (Math.random() - 0.5) * 0.5,
        speedY: (Math.random() - 0.5) * 0.5,
        alpha: Math.random() * 0.5 + 0.1,
        color: Math.random() > 0.5 ? colorNormal1 : colorNormal2
    });
}

// --- SISTEMA DE DESTELLOS DE MUTACIÓN (NUEVO) ---
const mutationFlashes = [];

function render() {
    const canvas = canvasRef.value;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Auto-resize para ser responsive
    const parent = canvas.parentElement;
    if (parent && (canvas.width !== parent.clientWidth || canvas.height !== parent.clientHeight)) {
        canvas.width = parent.clientWidth;
        canvas.height = parent.clientHeight;
    }

    // Controles responsivos 
    const isHorizontal = canvas.width > canvas.height;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const amplitude = isHorizontal
        ? Math.min(canvas.height * 0.4, 75)
        : Math.min(canvas.width * 0.4, 75);


    // Motion Blur más pronunciado pero menos oscuro para evitar saturaciones de luz
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = 'rgba(2, 6, 23, 0.25)'; // Aumentar opacidad del clear para borrar halos viejos más rápido (menos resplandor acumulado)
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Composición mágica Luminosa
    ctx.globalCompositeOperation = 'lighter';

    time += 0.015;

    // --- RENDERIZAR PARTÍCULAS DE ENERGÍA AMBIENTALES ---
    ambientParticles.forEach(p => {
        p.x += p.speedX / 100;
        p.y += p.speedY / 100;

        // Loop infinito
        if (p.x < 0) p.x = 1; if (p.x > 1) p.x = 0;
        if (p.y < 0) p.y = 1; if (p.y > 1) p.y = 0;

        const px = p.x * canvas.width;
        const py = p.y * canvas.height;

        ctx.beginPath();
        ctx.arc(px, py, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.alpha * (0.3 + Math.sin(time * 5 + p.x * 10) * 0.2); // Parpadeo
        ctx.fill();
    });

    // --- RENDERIZAR DESTELLOS DE MUTACIÓN ---
    for (let i = mutationFlashes.length - 1; i >= 0; i--) {
        const flash = mutationFlashes[i];
        flash.life -= 0.03;

        if (flash.life <= 0) {
            mutationFlashes.splice(i, 1);
            continue;
        }

        ctx.globalAlpha = flash.life;
        const gradient = ctx.createRadialGradient(flash.px, flash.py, 0, flash.px, flash.py, flash.radius);
        gradient.addColorStop(0, flash.color);
        gradient.addColorStop(1, 'rgba(0,0,0,0)');

        ctx.fillStyle = gradient;
        ctx.fillRect(flash.px - flash.radius, flash.py - flash.radius, flash.radius * 2, flash.radius * 2);
    }

    ctx.globalAlpha = 1;

    // Calcular el inicio del ADN
    const totalSpan = (numStrands - 1) * 16;
    const startPos = (isHorizontal ? centerX : centerY) - (totalSpan / 2);

    strands.forEach((strand) => {
        const offset = startPos + strand.offsetPos;

        // Coordenadas 3D proyectadas a 2D
        let x1, y1, x2, y2;
        const phaseVal1 = Math.sin(time + strand.phase) * amplitude;
        const phaseVal2 = Math.sin(time + strand.phase + Math.PI) * amplitude;
        const z1 = Math.cos(time + strand.phase);
        const z2 = Math.cos(time + strand.phase + Math.PI);

        if (isHorizontal) {
            x1 = offset; y1 = centerY + phaseVal1;
            x2 = offset; y2 = centerY + phaseVal2;
        } else {
            x1 = centerX + phaseVal1; y1 = offset;
            x2 = centerX + phaseVal2; y2 = offset;
        }

        // Lógica de Mutación Estocástica Explosiva
        let currentX1 = x1, currentX2 = x2;
        let currentY1 = y1, currentY2 = y2;
        let opacityMultiplier = 1;

        if (strand.isMutating) {
            strand.mutatingTimer += 0.015;
            if (strand.mutatingTimer > 1) {
                strand.isMutating = false;
                strand.color = strand.newColor;
            } else {
                const progress = strand.mutatingTimer;
                // Efecto de explosión exponencial
                strand.breakDistance += (progress * 2);

                // Rotar las partículas mientras vuelan
                const rotX1 = strand.dirX1 * Math.cos(progress * 10) - strand.dirY1 * Math.sin(progress * 10);
                const rotY1 = strand.dirX1 * Math.sin(progress * 10) + strand.dirY1 * Math.cos(progress * 10);

                const rotX2 = strand.dirX2 * Math.cos(progress * -10) - strand.dirY2 * Math.sin(progress * -10);
                const rotY2 = strand.dirX2 * Math.sin(progress * -10) + strand.dirY2 * Math.cos(progress * -10);

                currentX1 += rotX1 * strand.breakDistance;
                currentX2 += rotX2 * strand.breakDistance;
                currentY1 += rotY1 * strand.breakDistance;
                currentY2 += rotY2 * strand.breakDistance;

                // Curva de desvanecimiento
                opacityMultiplier = 1 - Math.pow(progress, 2);
            }
        }

        // --- Renderizar Línea de Conexión ---
        ctx.beginPath();
        if (strand.isMutating) {
            ctx.moveTo(currentX1, currentY1);
            ctx.lineTo(currentX2, currentY2);
            ctx.strokeStyle = strand.newColor;
            ctx.globalAlpha = Math.max(0, opacityMultiplier * 0.9);
            ctx.lineWidth = 3.5;
        } else {
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.strokeStyle = strand.color;
            ctx.globalAlpha = 0.5 + (z1 > 0 ? 0.4 : 0.1);
            ctx.lineWidth = 2.5;
        }
        ctx.stroke();

        // --- Helper de Glow y Nodos ---
        const drawNode = (cx, cy, radius, baseZ, color, isMutating) => {
            const size = Math.max(0.1, radius + (baseZ * 2));
            ctx.globalAlpha = isMutating ? Math.max(0, opacityMultiplier) : (0.7 + (baseZ >= 0 ? 0.3 : 0.1));

            // Núcleo Blanco brillante para efecto Neón
            ctx.beginPath();
            ctx.arc(cx, cy, size * 0.6, 0, Math.PI * 2);
            ctx.fillStyle = '#ffffff';
            ctx.fill();

            // Halo de Color
            ctx.beginPath();
            ctx.arc(cx, cy, size, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.shadowBlur = isMutating ? 30 : (baseZ > 0 ? 20 : 5);
            ctx.shadowColor = color;
            ctx.fill();
            ctx.shadowBlur = 0; // reset
        };

        const colorL = strand.isMutating ? strand.newColor : colorNormal1;
        const colorR = strand.isMutating ? strand.newColor : colorNormal2;

        // Renderizar nodos considerando rotación Z para orden 3D
        if (z1 < z2) {
            drawNode(currentX1, currentY1, 3.5, z1, colorL, strand.isMutating);
            drawNode(currentX2, currentY2, 3.5, z2, colorR, strand.isMutating);
        } else {
            drawNode(currentX2, currentY2, 3.5, z2, colorR, strand.isMutating);
            drawNode(currentX1, currentY1, 3.5, z1, colorL, strand.isMutating);
        }

        ctx.globalAlpha = 1; // reset global
    });

    animationFrameId = requestAnimationFrame(render);
}

// Escuchar cambios para "Mutación Reactiva Múltiple"
watch(() => props.trigger, () => {
    const availableStrands = strands.filter(s => !s.isMutating);
    if (availableStrands.length === 0) return;

    // Mutar entre 1 y 3 cadenas a la vez, no tan masivo
    const mutationsCount = Math.floor(Math.random() * 2) + 1;

    // Añadir Flash Central de radiación (Mucho más sutil)
    const canvas = canvasRef.value;
    if (canvas && Math.random() > 0.4) { // 60% probabilidad de flash para no marear
        mutationFlashes.push({
            px: canvas.width / 2 + (Math.random() * 60 - 30),
            py: canvas.height / 2 + (Math.random() * 60 - 30),
            radius: (canvas.width > canvas.height ? canvas.height : canvas.width) * 0.8, // Radio más pequeño
            color: neonColors[Math.floor(Math.random() * neonColors.length)],
            life: 0.35 // Vida mucho más corta (era 0.8)
        });
    }

    for (let i = 0; i < mutationsCount && i < availableStrands.length; i++) {
        const idx = Math.floor(Math.random() * availableStrands.length);
        const strand = availableStrands[idx];

        strand.isMutating = true;
        strand.mutatingTimer = 0;
        strand.breakDistance = 0;
        strand.newColor = neonColors[Math.floor(Math.random() * neonColors.length)];

        // Explosión de partículas (Velocidad más controlada)
        const angle1 = Math.random() * Math.PI * 2;
        const angle2 = Math.random() * Math.PI * 2;
        const force = 3 + Math.random() * 4; // Impulso bajado a la mitad

        strand.dirX1 = Math.cos(angle1) * force;
        strand.dirY1 = Math.sin(angle1) * force;
        strand.dirX2 = Math.cos(angle2) * force;
        strand.dirY2 = Math.sin(angle2) * force;

        availableStrands.splice(idx, 1);
    }
}, { deep: true });

onMounted(() => {
    animationFrameId = requestAnimationFrame(render);
});

onUnmounted(() => {
    cancelAnimationFrame(animationFrameId);
});
</script>

<template>
    <div class="w-full h-full relative" style="min-height: 100px;">
        <canvas ref="canvasRef" class="absolute inset-0 w-full h-full mx-auto"></canvas>
    </div>
</template>

<style scoped>
/* Asegurar que el canvas encaja perfecto sin scrollbars */
canvas {
    display: block;
    image-rendering: pixelated;
}
</style>
