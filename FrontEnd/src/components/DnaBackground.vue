<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';

const props = defineProps({
    trigger: {
        type: [String, Number, Object],
        default: null
    },
    count: {
        type: Number,
        default: 15
    },
    opacity: {
        type: String,
        default: 'opacity-10 dark:opacity-20'
    }
});

const baseColors = [
    'var(--p-primary-color)',
    '#3b82f6', // blue
    '#10b981', // green
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // purple
    '#06b6d4', // cyan
];

const getRandomColor = () => baseColors[Math.floor(Math.random() * baseColors.length)];

const strands = ref(Array.from({ length: props.count }, (_, i) => ({
    id: i,
    color1: getRandomColor(),
    color2: getRandomColor(),
    isMutating: false
})));

let mutationTimeout = null;

watch(() => props.trigger, (newVal, oldVal) => {
    // Evitar que el cambio sea nulo
    if (newVal === oldVal) return;

    // Mutar una cadena de ADN aleatoria cuando hay un trigger (edición)
    const randomIndex = Math.floor(Math.random() * strands.value.length);
    const strand = strands.value[randomIndex];

    strand.isMutating = true;

    clearTimeout(mutationTimeout);
    mutationTimeout = setTimeout(() => {
        strand.color1 = getRandomColor();
        strand.color2 = getRandomColor();
        strand.isMutating = false;
    }, 400); // Tiempo que dura la animación de salida/entrada
}, { deep: true });

onUnmounted(() => {
    clearTimeout(mutationTimeout);
});
</script>

<template>
    <div class="dna-manager absolute inset-0 overflow-hidden pointer-events-none flex items-center justify-center z-0"
        :class="opacity">
        <div class="dna-helix flex flex-col gap-6 w-full max-w-sm px-10">
            <TransitionGroup name="mutation">
                <div v-for="(strand, index) in strands" :key="strand.id"
                    class="dna-strand relative w-full h-1 flex items-center justify-between"
                    :style="{ animationDelay: `-${index * 0.25}s` }">

                    <!-- Left Node -->
                    <div class="dna-node absolute left-0 w-4 h-4 rounded-full shadow-[0_0_10px_currentColor] transition-all duration-300"
                        :class="{ 'opacity-0 scale-50': strand.isMutating }"
                        :style="{ backgroundColor: strand.color1, color: strand.color1, animationDelay: `-${index * 0.25}s` }">
                    </div>

                    <!-- Connection Line -->
                    <div
                        class="dna-connection absolute left-4 right-4 h-[2px] bg-surface-500/30 dark:bg-surface-400/30">
                    </div>

                    <!-- Right Node -->
                    <div class="dna-node absolute right-0 w-4 h-4 rounded-full shadow-[0_0_10px_currentColor] transition-all duration-300"
                        :class="{ 'opacity-0 scale-50': strand.isMutating }"
                        :style="{ backgroundColor: strand.color2, color: strand.color2, animationDelay: `-${index * 0.25}s` }">
                    </div>
                </div>
            </TransitionGroup>
        </div>
    </div>
</template>

<style scoped>
.dna-manager {
    mask-image: linear-gradient(to bottom, transparent, black 15%, black 85%, transparent);
}

.dna-helix {
    perspective: 800px;
    transform-style: preserve-3d;
}

.dna-strand {
    transform-style: preserve-3d;
    animation: rotateStrand 4s linear infinite;
}

.dna-node {
    animation: counterRotate 4s linear infinite;
}

@keyframes rotateStrand {
    0% {
        transform: rotateY(0deg);
    }

    100% {
        transform: rotateY(360deg);
    }
}

@keyframes counterRotate {
    0% {
        transform: rotateY(0deg) scale(1);
    }

    25% {
        transform: rotateY(-90deg) scale(0.8);
    }

    50% {
        transform: rotateY(-180deg) scale(1);
        z-index: -1;
    }

    75% {
        transform: rotateY(-270deg) scale(1.2);
        z-index: 1;
    }

    100% {
        transform: rotateY(-360deg) scale(1);
    }
}

/* Mutation Transitions */
.mutation-enter-active,
.mutation-leave-active {
    transition: all 0.4s ease;
}

.mutation-enter-from,
.mutation-leave-to {
    opacity: 0;
    transform: scale(0.5);
}
</style>
