<script setup>
// Imágenes de alerta Google Protect
import googleProtect1 from '@/publicActives/google_protect1.jpg';
import googleProtect2 from '@/publicActives/google_protect2.jpg';

// Archivos descargables (Vite los incluye en el bundle con hash)
import apkUrl from '@/publicActives/NEXUS-Android-v2.0.apk?url';
import zipUrl from '@/publicActives/NEXUS-Windows-v1.0.zip?url';

const apkName   = 'NEXUS-Android-v2.0.apk';
const zipName   = 'NEXUS-Windows-v1.0.zip';

const guiaAndroid = [
    {
        paso: 1,
        titulo: 'Descarga el APK',
        descripcion: 'Pulsa el botón "Descargar APK" de esta página. El archivo se guardará en la carpeta de Descargas de tu dispositivo.',
        icono: 'pi pi-download',
        color: 'text-blue-500'
    },
    {
        paso: 2,
        titulo: 'Permite instalar apps externas',
        descripcion: 'Ve a Configuración → Aplicaciones → Instalar apps desconocidas y habilita el permiso para tu navegador o gestor de archivos.',
        icono: 'pi pi-lock-open',
        color: 'text-orange-500'
    },
    {
        paso: 3,
        titulo: 'Ignora la alerta de Google Play Protect',
        descripcion: 'Al abrir el APK, Google Play Protect mostrará una advertencia de seguridad. La app no está en Play Store porque es una aplicación corporativa interna. Pulsa "Instalar de todos modos" o "Más detalles → Instalar de todos modos".',
        icono: 'pi pi-shield',
        color: 'text-yellow-500',
        tieneImagenes: true
    },
    {
        paso: 4,
        titulo: 'Completa la instalación',
        descripcion: 'Sigue los pasos del instalador. Una vez finalizado, abre NEXUS desde tu menú de aplicaciones e inicia sesión con tus credenciales corporativas.',
        icono: 'pi pi-check-circle',
        color: 'text-green-500'
    }
];

const guiaWindows = [
    {
        paso: 1,
        titulo: 'Descarga el archivo ZIP',
        descripcion: 'Pulsa el botón "Descargar para Windows". Se descargará un archivo comprimido con todos los archivos necesarios.',
        icono: 'pi pi-download',
        color: 'text-blue-500'
    },
    {
        paso: 2,
        titulo: 'Extrae el contenido',
        descripcion: 'Haz clic derecho sobre el ZIP → "Extraer todo". Elige una ubicación permanente (ej: C:\\NEXUS\\). No muevas los archivos individualmente, la app es portable y necesita todos sus archivos juntos.',
        icono: 'pi pi-folder-open',
        color: 'text-yellow-500'
    },
    {
        paso: 3,
        titulo: 'Ejecuta NEXUS.exe',
        descripcion: 'Dentro de la carpeta extraída encontrarás NEXUS.exe. Haz doble clic para abrirla. No necesita instalación. Puedes crear un acceso directo en el escritorio.',
        icono: 'pi pi-desktop',
        color: 'text-indigo-500'
    },
    {
        paso: 4,
        titulo: 'Nota de seguridad Windows',
        descripcion: 'Windows SmartScreen puede mostrar un aviso la primera vez. Pulsa "Más información → Ejecutar de todos modos". La app es segura y desarrollada internamente.',
        icono: 'pi pi-info-circle',
        color: 'text-orange-500'
    }
];
</script>

<template>
    <div class="min-h-screen">

        <!-- ── Hero ─────────────────────────────────────────────────────── -->
        <div class="bg-gradient-to-br from-primary-600 to-primary-900 dark:from-primary-800 dark:to-surface-900 rounded-2xl mb-8 p-8 md:p-12 relative overflow-hidden">
            <!-- Fondo decorativo -->
            <div class="absolute inset-0 opacity-10 pointer-events-none"
                style="background-image: radial-gradient(circle at 20% 50%, white 1px, transparent 1px), radial-gradient(circle at 80% 20%, white 1px, transparent 1px); background-size: 60px 60px;"></div>

            <div class="relative z-10 flex flex-col md:flex-row items-center gap-8">
                <div class="flex-1 text-center md:text-left">
                    <div class="inline-flex items-center gap-2 bg-white/10 text-white rounded-full px-4 py-1 text-sm font-medium mb-4">
                        <i class="pi pi-download"></i>
                        Descargas Oficiales
                    </div>
                    <h1 class="text-3xl md:text-5xl font-bold text-white mb-3 leading-tight">
                        NEXUS App
                    </h1>
                    <p class="text-primary-100 text-lg md:text-xl max-w-xl">
                        Disponible para Android y Windows. Accede al sistema de gestión operativa desde cualquier dispositivo.
                    </p>
                    <div class="flex flex-wrap justify-center md:justify-start gap-3 mt-6">
                        <a :href="apkUrl" :download="apkName"
                            class="inline-flex items-center gap-2 bg-white text-primary-700 font-semibold px-6 py-3 rounded-xl shadow-lg hover:bg-primary-50 transition-all hover:scale-105 no-underline">
                            <i class="pi pi-android text-xl"></i>
                            Android APK
                        </a>
                        <a :href="zipUrl" :download="zipName"
                            class="inline-flex items-center gap-2 bg-white/15 border border-white/30 text-white font-semibold px-6 py-3 rounded-xl hover:bg-white/25 transition-all hover:scale-105 no-underline">
                            <i class="pi pi-microsoft text-xl"></i>
                            Windows Portable
                        </a>
                    </div>
                </div>
                <!-- Iconos de plataformas -->
                <div class="flex-shrink-0 hidden md:flex items-center gap-6">
                    <div class="flex flex-col items-center bg-white/10 rounded-2xl p-6 backdrop-blur-sm">
                        <i class="pi pi-android text-6xl text-green-300 mb-2"></i>
                        <span class="text-white text-sm font-medium">Android 14+</span>
                    </div>
                    <div class="flex flex-col items-center bg-white/10 rounded-2xl p-6 backdrop-blur-sm">
                        <i class="pi pi-microsoft text-6xl text-blue-300 mb-2"></i>
                        <span class="text-white text-sm font-medium">Windows 10/11</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">

            <!-- ═══════════════════════════════════════════════════════════
                 COLUMNA ANDROID
            ════════════════════════════════════════════════════════════ -->
            <div class="flex flex-col gap-6">

                <!-- Card de descarga Android -->
                <div class="card border-l-4 border-green-500">
                    <div class="flex items-start gap-4">
                        <div class="flex-shrink-0 w-14 h-14 bg-green-100 dark:bg-green-900/30 rounded-2xl flex items-center justify-center">
                            <i class="pi pi-android text-3xl text-green-600 dark:text-green-400"></i>
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center gap-2 mb-1">
                                <h2 class="font-bold text-xl">Android</h2>
                                <span class="text-xs bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400 px-2 py-0.5 rounded-full font-medium">v2.0</span>
                            </div>
                            <p class="text-surface-500 text-sm mb-1">Requiere Android 14 o superior</p>
                            <p class="text-surface-500 text-sm">Tamaño: ~25 MB · APK independiente</p>
                        </div>
                    </div>
                    <div class="mt-4 pt-4 border-t border-surface-200 dark:border-surface-700">
                        <a :href="apkUrl" :download="apkName"
                            class="w-full inline-flex items-center justify-center gap-3 bg-green-500 hover:bg-green-600 text-white font-semibold px-6 py-3 rounded-xl transition-all hover:scale-[1.02] shadow-md no-underline">
                            <i class="pi pi-download text-lg"></i>
                            Descargar APK
                            <span class="text-green-200 text-xs font-normal">NEXUS-Android-v2.0.apk</span>
                        </a>
                    </div>
                </div>

                <!-- Alerta Google Play Protect -->
                <div class="card border border-yellow-300 dark:border-yellow-700 bg-yellow-50 dark:bg-yellow-950/20">
                    <div class="flex items-start gap-3 mb-4">
                        <div class="flex-shrink-0 w-10 h-10 bg-yellow-200 dark:bg-yellow-900/50 rounded-xl flex items-center justify-center">
                            <i class="pi pi-shield text-yellow-700 dark:text-yellow-400 text-xl"></i>
                        </div>
                        <div>
                            <h3 class="font-semibold text-yellow-800 dark:text-yellow-300">¿Por qué aparece Google Play Protect?</h3>
                            <p class="text-sm text-yellow-700 dark:text-yellow-400 mt-1">
                                NEXUS es una aplicación corporativa interna que <strong>no se distribuye por Google Play Store</strong>. Google muestra esta alerta con cualquier APK instalado fuera de la tienda oficial. La aplicación es completamente segura.
                            </p>
                        </div>
                    </div>
                    <!-- Imágenes de referencia -->
                    <div class="grid grid-cols-2 gap-3">
                        <div class="flex flex-col gap-1">
                            <p class="text-xs text-yellow-700 dark:text-yellow-400 font-medium text-center mb-1">Pantalla de alerta</p>
                            <img :src="googleProtect1" alt="Alerta Google Play Protect paso 1"
                                class="rounded-xl border-2 border-yellow-300 dark:border-yellow-700 w-full object-cover shadow-sm" />
                        </div>
                        <div class="flex flex-col gap-1">
                            <p class="text-xs text-yellow-700 dark:text-yellow-400 font-medium text-center mb-1">Instalar de todos modos</p>
                            <img :src="googleProtect2" alt="Alerta Google Play Protect paso 2"
                                class="rounded-xl border-2 border-yellow-300 dark:border-yellow-700 w-full object-cover shadow-sm" />
                        </div>
                    </div>
                    <p class="text-xs text-yellow-600 dark:text-yellow-500 mt-3 text-center italic">
                        Imágenes de referencia — Las pantallas pueden variar según el fabricante y versión de Android.
                    </p>
                </div>

                <!-- Guía instalación Android -->
                <div class="card">
                    <h3 class="font-bold text-lg mb-4 flex items-center gap-2">
                        <i class="pi pi-list-check text-green-500"></i>
                        Guía de instalación Android
                    </h3>
                    <div class="flex flex-col gap-4">
                        <div v-for="paso in guiaAndroid" :key="paso.paso" class="flex gap-4">
                            <div class="flex-shrink-0 flex flex-col items-center">
                                <div class="w-9 h-9 rounded-full bg-surface-100 dark:bg-surface-800 flex items-center justify-center font-bold text-sm border-2 border-surface-200 dark:border-surface-700">
                                    {{ paso.paso }}
                                </div>
                                <div v-if="paso.paso < guiaAndroid.length"
                                    class="w-0.5 flex-1 bg-surface-200 dark:bg-surface-700 mt-1 min-h-[24px]"></div>
                            </div>
                            <div class="pb-4 flex-1">
                                <div class="flex items-center gap-2 mb-1">
                                    <i :class="[paso.icono, paso.color, 'text-base']"></i>
                                    <span class="font-semibold text-sm">{{ paso.titulo }}</span>
                                </div>
                                <p class="text-sm text-surface-600 dark:text-surface-400 leading-relaxed">{{ paso.descripcion }}</p>
                                <!-- Indicador visual cuando es el paso de Google Protect -->
                                <div v-if="paso.tieneImagenes"
                                    class="mt-2 inline-flex items-center gap-1 text-xs text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-950/30 px-2 py-1 rounded-lg">
                                    <i class="pi pi-images text-xs"></i>
                                    Ver imágenes de referencia arriba
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ═══════════════════════════════════════════════════════════
                 COLUMNA WINDOWS
            ════════════════════════════════════════════════════════════ -->
            <div class="flex flex-col gap-6">

                <!-- Card de descarga Windows -->
                <div class="card border-l-4 border-blue-500">
                    <div class="flex items-start gap-4">
                        <div class="flex-shrink-0 w-14 h-14 bg-blue-100 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center">
                            <i class="pi pi-microsoft text-3xl text-blue-600 dark:text-blue-400"></i>
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center gap-2 mb-1">
                                <h2 class="font-bold text-xl">Windows</h2>
                                <span class="text-xs bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 px-2 py-0.5 rounded-full font-medium">v1.0</span>
                                <span class="text-xs bg-surface-100 dark:bg-surface-700 text-surface-500 px-2 py-0.5 rounded-full font-medium">Portable</span>
                            </div>
                            <p class="text-surface-500 text-sm mb-1">Compatible con Windows 10 / 11 (64-bit)</p>
                            <p class="text-surface-500 text-sm">Sin instalación · Incluye todos los archivos</p>
                        </div>
                    </div>
                    <div class="mt-4 pt-4 border-t border-surface-200 dark:border-surface-700">
                        <a :href="zipUrl" :download="zipName"
                            class="w-full inline-flex items-center justify-center gap-3 bg-blue-500 hover:bg-blue-600 text-white font-semibold px-6 py-3 rounded-xl transition-all hover:scale-[1.02] shadow-md no-underline">
                            <i class="pi pi-download text-lg"></i>
                            Descargar para Windows
                            <span class="text-blue-200 text-xs font-normal">NEXUS-Windows-v1.0.zip</span>
                        </a>
                    </div>
                </div>

                <!-- Aviso app portable -->
                <div class="card border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/20">
                    <div class="flex items-start gap-3">
                        <div class="flex-shrink-0 w-10 h-10 bg-blue-200 dark:bg-blue-900/50 rounded-xl flex items-center justify-center">
                            <i class="pi pi-folder text-blue-700 dark:text-blue-400 text-xl"></i>
                        </div>
                        <div>
                            <h3 class="font-semibold text-blue-800 dark:text-blue-300 mb-1">¿Qué incluye el ZIP?</h3>
                            <p class="text-sm text-blue-700 dark:text-blue-400">
                                El ZIP contiene todos los archivos necesarios para ejecutar NEXUS directamente. Es una aplicación <strong>portable</strong>: no requiere instalación ni modifica el registro del sistema. Simplemente extrae y ejecuta.
                            </p>
                            <ul class="mt-3 flex flex-col gap-1.5 text-sm text-blue-700 dark:text-blue-400">
                                <li class="flex items-center gap-2"><i class="pi pi-check-circle text-blue-500 text-xs"></i> Sin instalación</li>
                                <li class="flex items-center gap-2"><i class="pi pi-check-circle text-blue-500 text-xs"></i> No requiere permisos de administrador</li>
                                <li class="flex items-center gap-2"><i class="pi pi-check-circle text-blue-500 text-xs"></i> No modifica el sistema operativo</li>
                                <li class="flex items-center gap-2"><i class="pi pi-check-circle text-blue-500 text-xs"></i> Todos los archivos deben permanecer juntos</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- Guía instalación Windows -->
                <div class="card">
                    <h3 class="font-bold text-lg mb-4 flex items-center gap-2">
                        <i class="pi pi-list-check text-blue-500"></i>
                        Guía de instalación Windows
                    </h3>
                    <div class="flex flex-col gap-4">
                        <div v-for="paso in guiaWindows" :key="paso.paso" class="flex gap-4">
                            <div class="flex-shrink-0 flex flex-col items-center">
                                <div class="w-9 h-9 rounded-full bg-surface-100 dark:bg-surface-800 flex items-center justify-center font-bold text-sm border-2 border-surface-200 dark:border-surface-700">
                                    {{ paso.paso }}
                                </div>
                                <div v-if="paso.paso < guiaWindows.length"
                                    class="w-0.5 flex-1 bg-surface-200 dark:bg-surface-700 mt-1 min-h-[24px]"></div>
                            </div>
                            <div class="pb-4 flex-1">
                                <div class="flex items-center gap-2 mb-1">
                                    <i :class="[paso.icono, paso.color, 'text-base']"></i>
                                    <span class="font-semibold text-sm">{{ paso.titulo }}</span>
                                </div>
                                <p class="text-sm text-surface-600 dark:text-surface-400 leading-relaxed">{{ paso.descripcion }}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- FAQ rápido -->
                <div class="card">
                    <h3 class="font-bold text-lg mb-4 flex items-center gap-2">
                        <i class="pi pi-question-circle text-indigo-500"></i>
                        Preguntas frecuentes
                    </h3>
                    <div class="flex flex-col gap-3">
                        <div class="p-3 rounded-lg bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700">
                            <p class="font-medium text-sm mb-1">¿Es seguro instalar el APK?</p>
                            <p class="text-xs text-surface-500 leading-relaxed">Sí. La app fue desarrollada internamente por el equipo de sistemas. La alerta de Google Play Protect aparece con cualquier APK externo a Play Store.</p>
                        </div>
                        <div class="p-3 rounded-lg bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700">
                            <p class="font-medium text-sm mb-1">¿Puedo mover la carpeta de Windows a otro lugar?</p>
                            <p class="text-xs text-surface-500 leading-relaxed">Sí, siempre que muevas <strong>toda la carpeta</strong>. Nunca muevas solo el ejecutable .exe sin el resto de archivos.</p>
                        </div>
                        <div class="p-3 rounded-lg bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700">
                            <p class="font-medium text-sm mb-1">¿Necesito conexión a internet?</p>
                            <p class="text-xs text-surface-500 leading-relaxed">Sí. NEXUS se conecta al servidor central. Asegúrate de estar en la red corporativa o con VPN activa.</p>
                        </div>
                        <div class="p-3 rounded-lg bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700">
                            <p class="font-medium text-sm mb-1">¿Cómo actualizo la app?</p>
                            <p class="text-xs text-surface-500 leading-relaxed">Descarga el nuevo APK o ZIP desde esta misma página cuando haya una nueva versión disponible. En Android desinstala la versión anterior primero.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer de soporte -->
        <div class="mt-8 p-6 rounded-2xl bg-surface-100 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 text-center">
            <i class="pi pi-headphones text-2xl text-primary mb-2 block"></i>
            <p class="font-semibold mb-1">¿Problemas con la instalación?</p>
            <p class="text-sm text-surface-500">
                Contacta al equipo de Sistemas mediante un ticket de soporte desde la plataforma web,
                o comunícate directamente con tu Supervisor de Sistemas.
            </p>
        </div>
    </div>
</template>
