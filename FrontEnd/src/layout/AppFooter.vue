<script setup>
import { computed } from 'vue';

const currentYear = computed(() => new Date().getFullYear());

// Variables de entorno
const appName = import.meta.env.VITE_NAMEAPLICATION;
const appVersion = import.meta.env.VITE_VERSIONAPP;
const companyName = import.meta.env.VITE_EMPRESA;
const author = import.meta.env.VITE_AUTHOR;
const authornick = import.meta.env.VITE_AUTHOR_NICK;
</script>

<template>
    <div class="layout-footer flex items-center justify-between w-full">
        <div class="flex items-center gap-2">
            <i class="pi pi-server text-primary text-xl"></i>
            <span class="font-bold text-lg text-slate-700 dark:text-slate-200">{{ appName }}</span>
            <span class="hidden md:inline mx-2 text-slate-300 dark:text-slate-600">|</span>
            <span class="hidden md:inline text-sm text-slate-600 dark:text-slate-400">
                &copy; {{ currentYear }} <span class="font-bold text-primary">{{ companyName }}</span> Todos los derechos reservados
            </span>
            <span class="hidden md:inline mx-2 text-slate-300 dark:text-slate-600">|</span>
            <span class="hidden md:flex text-sm text-slate-600 dark:text-slate-400 items-center gap-1">
                Creado por <span class="font-semibold text-indigo-500">{{ author }}</span> <span class="text-xs text-slate-500">[{{ authornick }}]</span> 👨‍💻
            </span>
        </div>
        <div class="ml-auto flex items-center gap-1 text-xs font-medium text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded-md border border-slate-200 dark:border-slate-700">
            <i class="pi pi-tag text-primary"></i>
            <span>Versión {{ appVersion }}</span>
        </div>
    </div>
</template>
