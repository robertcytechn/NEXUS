<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { $t } from '@primeuix/themes';
import Aura from '@primeuix/themes/aura';
import { useLayout } from '@/layout/composables/layout';
import { acceptEULA, logout, getUser } from '@/service/api';

const router = useRouter();
const route = useRoute();
const { layoutConfig } = useLayout();

const agreed = ref(false);
const scrolledToBottom = ref(false);
const licenseContainer = ref(null);
const loading = ref(false);
const errorMessage = ref('');
const licenseAlreadyAccepted = ref(false);
const haySessionActiva = ref(false);

// Configuración de colores cyan/slate
const primaryColors = {
    cyan: { 
        50: '#ecfeff', 
        100: '#cffafe', 
        200: '#a5f3fc', 
        300: '#67e8f9', 
        400: '#22d3ee', 
        500: '#06b6d4', 
        600: '#0891b2', 
        700: '#0e7490', 
        800: '#155e75', 
        900: '#164e63', 
        950: '#083344' 
    }
};

const surfaces = {
    slate: { 
        0: '#ffffff', 
        50: '#f8fafc', 
        100: '#f1f5f9', 
        200: '#e2e8f0', 
        300: '#cbd5e1', 
        400: '#94a3b8', 
        500: '#64748b', 
        600: '#475569', 
        700: '#334155', 
        800: '#1e293b', 
        900: '#0f172a', 
        950: '#020617' 
    }
};

function getPresetExt() {
    const primaryPalette = primaryColors.cyan;
    
    return {
        semantic: {
            primary: primaryPalette,
            colorScheme: {
                light: {
                    primary: {
                        color: '{primary.500}',
                        contrastColor: '#ffffff',
                        hoverColor: '{primary.600}',
                        activeColor: '{primary.700}'
                    },
                    highlight: {
                        background: '{primary.50}',
                        focusBackground: '{primary.100}',
                        color: '{primary.700}',
                        focusColor: '{primary.800}'
                    }
                },
                dark: {
                    primary: {
                        color: '{primary.400}',
                        contrastColor: '{surface.900}',
                        hoverColor: '{primary.300}',
                        activeColor: '{primary.200}'
                    },
                    highlight: {
                        background: 'color-mix(in srgb, {primary.400}, transparent 84%)',
                        focusBackground: 'color-mix(in srgb, {primary.400}, transparent 76%)',
                        color: 'rgba(255,255,255,.87)',
                        focusColor: 'rgba(255,255,255,.87)'
                    }
                }
            }
        }
    };
}

const handleScroll = (event) => {
    const element = event.target;
    const isAtBottom = element.scrollHeight - element.scrollTop <= element.clientHeight + 50;
    if (isAtBottom && !scrolledToBottom.value) {
        scrolledToBottom.value = true;
    }
};

const handleAccept = async () => {
    loading.value = true;
    errorMessage.value = '';
    
    try {
        // Llamar a la API para aceptar la EULA
        const result = await acceptEULA();
        
        if (result.success) {
            // Guardar también en localStorage como respaldo
            localStorage.setItem('license_accepted', 'true');
            localStorage.setItem('license_accepted_date', new Date().toISOString());
            
            // Redirigir a la ruta original o al dashboard
            const redirectPath = route.query.redirect || '/';
            router.push(redirectPath);
        } else {
            errorMessage.value = result.error || 'Error al aceptar los términos y condiciones';
        }
    } catch (error) {
        errorMessage.value = 'Error de conexión con el servidor';

    } finally {
        loading.value = false;
    }
};

const handleReject = () => {
    // Si rechaza los términos, cerrar sesión y redirigir al login
    logout();
    router.push('/auth/login');
};

onMounted(async () => {
    const surfacePalette = surfaces.slate;
    
    $t()
        .preset(Aura)
        .preset(getPresetExt())
        .surfacePalette(surfacePalette)
        .use({ useDefaultOptions: true });
    
    // Verificar si hay sesión activa y si el usuario ya aceptó la licencia
    const currentUser = getUser();
    if (currentUser) {
        haySessionActiva.value = true;
        if (currentUser.EULAAceptada === true) {
            licenseAlreadyAccepted.value = true;
        }
    }
    
    await nextTick();
});

const goToDashboard = () => {
    const redirectPath = route.query.redirect || '/';
    router.push(redirectPath);
};
</script>

<template>
    <div class="bg-surface-50 dark:bg-surface-950 min-h-screen min-w-[100vw] overflow-hidden relative">
        <!-- Decoradores de fondo -->
        <div class="absolute w-full h-full overflow-hidden pointer-events-none">
            <div class="absolute top-[10%] left-[10%] w-96 h-96 bg-[var(--primary-color)] opacity-20 rounded-full blur-[100px]"></div>
            <div class="absolute bottom-[10%] right-[10%] w-96 h-96 bg-[var(--primary-color)] opacity-20 rounded-full blur-[100px]"></div>
        </div>

        <!-- Contenedor principal -->
        <div class="relative z-10 container mx-auto px-4 py-8 max-w-7xl">
            <!-- Header -->
            <div class="text-center mb-8">
                <div class="inline-flex items-center justify-center mb-6">
                    <svg viewBox="0 0 54 40" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-16 h-16 mr-4">
                        <path
                            fill-rule="evenodd"
                            clip-rule="evenodd"
                            d="M17.1637 19.2467C17.1566 19.4033 17.1529 19.561 17.1529 19.7194C17.1529 25.3503 21.7203 29.915 27.3546 29.915C32.9887 29.915 37.5561 25.3503 37.5561 19.7194C37.5561 19.5572 37.5524 19.3959 37.5449 19.2355C38.5617 19.0801 39.5759 18.9013 40.5867 18.6994L40.6926 18.6782C40.7191 19.0218 40.7326 19.369 40.7326 19.7194C40.7326 27.1036 34.743 33.0896 27.3546 33.0896C19.966 33.0896 13.9765 27.1036 13.9765 19.7194C13.9765 19.374 13.9896 19.0316 14.0154 18.6927L14.0486 18.6994C15.0837 18.9062 16.1223 19.0886 17.1637 19.2467ZM33.3284 11.4538C31.6493 10.2396 29.5855 9.52381 27.3546 9.52381C25.1195 9.52381 23.0524 10.2421 21.3717 11.4603C20.0078 11.3232 18.6475 11.1387 17.2933 10.907C19.7453 8.11308 23.3438 6.34921 27.3546 6.34921C31.36 6.34921 34.9543 8.10844 37.4061 10.896C36.0521 11.1292 34.692 11.3152 33.3284 11.4538ZM43.826 18.0518C43.881 18.6003 43.9091 19.1566 43.9091 19.7194C43.9091 28.8568 36.4973 36.2642 27.3546 36.2642C18.2117 36.2642 10.8 28.8568 10.8 19.7194C10.8 19.1615 10.8276 18.61 10.8816 18.0663L7.75383 17.4411C7.66775 18.1886 7.62354 18.9488 7.62354 19.7194C7.62354 30.6102 16.4574 39.4388 27.3546 39.4388C38.2517 39.4388 47.0855 30.6102 47.0855 19.7194C47.0855 18.9439 47.0407 18.1789 46.9536 17.4267L43.826 18.0518ZM44.2613 9.54743L40.9084 10.2176C37.9134 5.95821 32.9593 3.1746 27.3546 3.1746C21.7442 3.1746 16.7856 5.96385 13.7915 10.2305L10.4399 9.56057C13.892 3.83178 20.1756 0 27.3546 0C34.5281 0 40.8075 3.82591 44.2613 9.54743Z"
                            fill="var(--primary-color)"
                        />
                    </svg>
                    <div>
                        <h1 class="text-4xl font-bold text-surface-900 dark:text-surface-0">Core Nexus Manager &reg;</h1>
                        <p class="text-lg text-surface-600 dark:text-surface-400 mt-1">CYTECHNOLOGIES &copy; 2026</p>
                    </div>
                </div>
                <div class="inline-block px-6 py-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg border-2 border-primary-500">
                    <h2 class="text-2xl font-semibold text-primary-700 dark:text-primary-300">
                        Acuerdo de Licencia de Uso de Software
                    </h2>
                </div>
            </div>

            <!-- Contenedor del documento -->
            <div class="bg-surface-0 dark:bg-surface-900 rounded-3xl shadow-2xl border border-surface-200 dark:border-surface-800 overflow-hidden">
                <!-- Contenido de la licencia -->
                <div 
                    ref="licenseContainer"
                    @scroll="handleScroll"
                    class="p-8 md:p-12 overflow-y-auto license-content"
                    style="max-height: calc(100vh - 350px);"
                >
                    <!-- Advertencia importante -->
                    <div class="mb-8 p-6 bg-amber-50 dark:bg-amber-900/20 border-l-4 border-amber-500 rounded-lg">
                        <div class="flex items-start">
                            <svg class="w-6 h-6 text-amber-600 dark:text-amber-400 mr-3 flex-shrink-0 mt-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                            </svg>
                            <div>
                                <h3 class="text-lg font-bold text-amber-900 dark:text-amber-200 mb-2">DOCUMENTO LEGAL VINCULANTE</h3>
                                <p class="text-sm text-amber-800 dark:text-amber-300">
                                    Lea cuidadosamente este acuerdo antes de utilizar el software. 
                                    El uso del sistema constituye la aceptación de todos los términos aquí establecidos.
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Documento de licencia -->
                    <div class="prose prose-slate dark:prose-invert max-w-none prose-headings:text-primary-700 dark:prose-headings:text-primary-300">
                        <p class="text-surface-700 dark:text-surface-300 mb-6">
                            El presente instrumento constituye un acuerdo legal vinculante entre <strong>CYTECHNOLOGIES</strong>, 
                            con domicilio en los Estados Unidos Mexicanos, representada por su titular de derechos y autor original 
                            <strong>José Roberto Tamayo Montejano</strong> (en adelante, "EL LICENCIANTE"), y la persona física o moral 
                            que acceda, utilice o interactúe con el sistema de software denominado Core Nexus Manager 
                            (en adelante, "EL USUARIO" o "EL LICENCIATARIO").
                        </p>

                        <div class="mb-6 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
                            <p class="text-sm font-semibold text-primary-900 dark:text-primary-100">
                                <strong>FECHA DE VIGENCIA:</strong> Este acuerdo entra en vigor a partir del momento en que EL USUARIO 
                                recibe credenciales de acceso, inicia sesión en la plataforma o utiliza cualquier módulo, 
                                componente o funcionalidad del software.
                            </p>
                        </div>

                        <h2 class="text-2xl font-bold mb-4 mt-8 text-primary-700 dark:text-primary-300 border-b-2 border-primary-300 dark:border-primary-700 pb-2">
                            ARTÍCULO 1. DEFINICIONES Y CONCEPTOS
                        </h2>
                        
                        <p class="mb-4">Para efectos del presente contrato, se entenderá por:</p>

                        <div class="space-y-4 mb-6">
                            <div class="bg-surface-100 dark:bg-surface-800 p-4 rounded-lg">
                                <h4 class="font-bold text-surface-900 dark:text-surface-100 mb-2">1.1. SOFTWARE</h4>
                                <p class="text-sm text-surface-700 dark:text-surface-300">
                                    El sistema informático integral denominado Core Nexus Manager (CNM), que incluye sin limitación: 
                                    código fuente (frontend y backend), bases de datos, esquemas relacionales, interfaces gráficas, 
                                    documentación técnica, APIs, módulos, componentes, actualizaciones, y cualquier material relacionado o derivado.
                                </p>
                            </div>

                            <div class="bg-surface-100 dark:bg-surface-800 p-4 rounded-lg">
                                <h4 class="font-bold text-surface-900 dark:text-surface-100 mb-2">1.2. LICENCIA DE USO</h4>
                                <p class="text-sm text-surface-700 dark:text-surface-300">
                                    Autorización no exclusiva, temporal, revocable e intransferible otorgada por EL LICENCIANTE a EL USUARIO 
                                    para acceder y utilizar el SOFTWARE exclusivamente en el ámbito de sus funciones laborales autorizadas.
                                </p>
                            </div>

                            <div class="bg-surface-100 dark:bg-surface-800 p-4 rounded-lg">
                                <h4 class="font-bold text-surface-900 dark:text-surface-100 mb-2">1.3. PROPIEDAD INTELECTUAL</h4>
                                <p class="text-sm text-surface-700 dark:text-surface-300">
                                    Todos los derechos de autor, derechos patrimoniales, derechos morales, derechos conexos, marcas, 
                                    nombres comerciales, secretos industriales y cualquier otro derecho de propiedad intelectual e industrial 
                                    reconocido por la legislación mexicana y tratados internacionales aplicables.
                                </p>
                            </div>

                            <div class="bg-surface-100 dark:bg-surface-800 p-4 rounded-lg">
                                <h4 class="font-bold text-surface-900 dark:text-surface-100 mb-2">1.4. USO AUTORIZADO</h4>
                                <p class="text-sm text-surface-700 dark:text-surface-300">
                                    Toda operación, consulta o interacción con el SOFTWARE que se realice dentro de los límites establecidos 
                                    por el rol, permisos y funciones asignadas por la administración del sistema.
                                </p>
                            </div>

                            <div class="bg-surface-100 dark:bg-surface-800 p-4 rounded-lg">
                                <h4 class="font-bold text-surface-900 dark:text-surface-100 mb-2">1.5. CONTENIDO CONFIDENCIAL</h4>
                                <p class="text-sm text-surface-700 dark:text-surface-300">
                                    Toda información, dato, registro, documento, reporte, estadística, esquema o cualquier tipo de contenido 
                                    almacenado, procesado, generado o visualizado a través del SOFTWARE.
                                </p>
                            </div>
                        </div>

                        <h2 class="text-2xl font-bold mb-4 mt-8 text-primary-700 dark:text-primary-300 border-b-2 border-primary-300 dark:border-primary-700 pb-2">
                            ARTÍCULO 2. DECLARACIONES DE PROPIEDAD INTELECTUAL
                        </h2>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">2.1. Autoría y Titularidad Original</h3>
                        
                        <p class="mb-4">
                            Se reconoce de manera irrevocable, expresa e inequívoca que <strong class="text-primary-700 dark:text-primary-300">José Roberto Tamayo Montejano</strong> 
                            es el único y exclusivo autor intelectual del SOFTWARE Core Nexus Manager (CNM), habiendo concebido, 
                            desarrollado y materializado la totalidad de:
                        </p>

                        <ul class="list-disc pl-6 mb-6 space-y-2 text-surface-700 dark:text-surface-300">
                            <li>La arquitectura de software y diseño de sistemas</li>
                            <li>La lógica de negocio y algoritmos implementados</li>
                            <li>El código fuente completo (incluyendo frontend y backend)</li>
                            <li>Los esquemas de bases de datos y estructuras relacionales</li>
                            <li>El diseño de interfaces de usuario y experiencia de usuario</li>
                            <li>La documentación técnica y funcional</li>
                            <li>Cualquier componente, módulo o funcionalidad integrada</li>
                        </ul>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">2.2. Titularidad de Derechos Patrimoniales</h3>
                        
                        <p class="mb-6">
                            <strong>CYTECHNOLOGIES</strong> ostenta la titularidad exclusiva de todos los derechos patrimoniales derivados del SOFTWARE, 
                            incluyendo sin limitación los derechos de reproducción, distribución, comunicación pública, transformación, 
                            y cualquier forma de explotación económica, conforme a lo establecido en la Ley Federal del Derecho de Autor 
                            vigente en los Estados Unidos Mexicanos.
                        </p>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">2.3. Protección Legal y Registro</h3>
                        
                        <div class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border-l-4 border-red-500">
                            <p class="font-semibold mb-2 text-red-900 dark:text-red-100">El SOFTWARE está protegido por:</p>
                            <ul class="list-disc pl-6 space-y-1 text-sm text-red-800 dark:text-red-200">
                                <li><strong>Ley Federal del Derecho de Autor</strong> (Última reforma publicada en el Diario Oficial de la Federación)</li>
                                <li><strong>Código Penal Federal</strong> en sus disposiciones sobre delitos contra el derecho de autor</li>
                                <li><strong>Ley de la Propiedad Industrial</strong> en lo aplicable</li>
                                <li><strong>Tratados Internacionales</strong> de los que México es parte, incluyendo el Convenio de Berna, 
                                    el Tratado de la OMPI sobre Derecho de Autor (WCT) y el Acuerdo sobre los ADPIC</li>
                                <li><strong>Legislación civil y mercantil</strong> en materia de contratos y obligaciones</li>
                            </ul>
                        </div>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">2.4. Derechos Morales del Autor</h3>
                        
                        <p class="mb-4">
                            Sin perjuicio de la titularidad patrimonial de CYTECHNOLOGIES, EL USUARIO reconoce que 
                            José Roberto Tamayo Montejano conserva perpetuamente sus derechos morales como autor conforme 
                            al artículo 21 de la Ley Federal del Derecho de Autor, incluyendo:
                        </p>

                        <ul class="list-disc pl-6 mb-6 space-y-2 text-surface-700 dark:text-surface-300">
                            <li>Derecho de paternidad (reconocimiento de autoría)</li>
                            <li>Derecho de integridad (oposición a modificaciones)</li>
                            <li>Derecho de divulgación</li>
                            <li>Derecho de retracto en los casos permitidos por ley</li>
                        </ul>

                        <h2 class="text-2xl font-bold mb-4 mt-8 text-primary-700 dark:text-primary-300 border-b-2 border-primary-300 dark:border-primary-700 pb-2">
                            ARTÍCULO 3. NATURALEZA Y ALCANCE DE LA LICENCIA
                        </h2>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">3.1. Aceptación del Acuerdo</h3>
                        
                        <p class="mb-6">
                            La recepción de credenciales de acceso (nombre de usuario y contraseña), el primer inicio de sesión en la plataforma, 
                            o cualquier uso del SOFTWARE constituye la <strong>aceptación plena, voluntaria, informada e irrevocable</strong> 
                            de todos los términos y condiciones establecidos en el presente acuerdo.
                        </p>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">3.2. Carácter de la Licencia</h3>
                        
                        <p class="mb-3">La presente licencia es:</p>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
                            <div class="bg-surface-100 dark:bg-surface-800 p-3 rounded-lg">
                                <p class="font-semibold text-surface-900 dark:text-surface-100">No exclusiva</p>
                                <p class="text-sm text-surface-600 dark:text-surface-400">EL LICENCIANTE puede otorgar licencias a otros usuarios</p>
                            </div>
                            <div class="bg-surface-100 dark:bg-surface-800 p-3 rounded-lg">
                                <p class="font-semibold text-surface-900 dark:text-surface-100">Temporal</p>
                                <p class="text-sm text-surface-600 dark:text-surface-400">Vigente únicamente durante la relación laboral o contractual autorizada</p>
                            </div>
                            <div class="bg-surface-100 dark:bg-surface-800 p-3 rounded-lg">
                                <p class="font-semibold text-surface-900 dark:text-surface-100">Revocable</p>
                                <p class="text-sm text-surface-600 dark:text-surface-400">EL LICENCIANTE puede cancelarla en cualquier momento</p>
                            </div>
                            <div class="bg-surface-100 dark:bg-surface-800 p-3 rounded-lg">
                                <p class="font-semibold text-surface-900 dark:text-surface-100">Intransferible</p>
                                <p class="text-sm text-surface-600 dark:text-surface-400">Prohibida su cesión, préstamo o transferencia a terceros</p>
                            </div>
                            <div class="bg-surface-100 dark:bg-surface-800 p-3 rounded-lg">
                                <p class="font-semibold text-surface-900 dark:text-surface-100">Personal</p>
                                <p class="text-sm text-surface-600 dark:text-surface-400">Vinculada exclusivamente a la identidad del USUARIO autorizado</p>
                            </div>
                            <div class="bg-surface-100 dark:bg-surface-800 p-3 rounded-lg">
                                <p class="font-semibold text-surface-900 dark:text-surface-100">Limitada</p>
                                <p class="text-sm text-surface-600 dark:text-surface-400">Restringida al uso profesional autorizado</p>
                            </div>
                        </div>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">3.3. No Transferencia de Propiedad</h3>
                        
                        <div class="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                            <p class="mb-3 font-semibold text-amber-900 dark:text-amber-100">
                                EL USUARIO reconoce expresamente que esta licencia <strong>NO constituye ni conferirá en ningún momento:</strong>
                            </p>
                            <ul class="list-disc pl-6 space-y-1 text-sm text-amber-800 dark:text-amber-200">
                                <li>Propiedad sobre el SOFTWARE</li>
                                <li>Derechos de autor o patrimoniales</li>
                                <li>Participación en beneficios económicos</li>
                                <li>Derechos sobre mejoras o actualizaciones</li>
                                <li>Expectativas de derecho adquirido</li>
                            </ul>
                            <p class="mt-3 text-sm text-amber-800 dark:text-amber-200">
                                El uso del SOFTWARE es únicamente una herramienta de trabajo proporcionada temporalmente para el desempeño de funciones específicas.
                            </p>
                        </div>

                        <h2 class="text-2xl font-bold mb-4 mt-8 text-primary-700 dark:text-primary-300 border-b-2 border-primary-300 dark:border-primary-700 pb-2">
                            ARTÍCULO 4. OBLIGACIONES Y CONDUCTA DEL USUARIO
                        </h2>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">4.1. Uso Responsable y Profesional</h3>
                        
                        <p class="mb-3">EL USUARIO se obliga a:</p>
                        <ul class="list-disc pl-6 mb-6 space-y-2 text-surface-700 dark:text-surface-300">
                            <li>Utilizar el SOFTWARE exclusivamente para los fines autorizados</li>
                            <li>Mantener la confidencialidad de sus credenciales de acceso</li>
                            <li>Reportar inmediatamente cualquier incidente de seguridad</li>
                            <li>Cumplir con las políticas de seguridad informática establecidas</li>
                            <li>Respetar los límites de acceso y permisos asignados a su perfil</li>
                            <li>Abstenerse de realizar acciones que comprometan la integridad del sistema</li>
                        </ul>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">4.2. Protección de Credenciales</h3>
                        
                        <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                            <p class="mb-2 font-semibold text-blue-900 dark:text-blue-100">EL USUARIO será único responsable de:</p>
                            <ul class="list-disc pl-6 space-y-1 text-sm text-blue-800 dark:text-blue-200">
                                <li>La custodia y confidencialidad de sus credenciales</li>
                                <li>Todas las acciones realizadas bajo su cuenta</li>
                                <li>No compartir, prestar o divulgar sus datos de acceso</li>
                                <li>Cerrar sesión al terminar su jornada o alejarse del equipo</li>
                            </ul>
                        </div>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">4.3. Integridad del Sistema</h3>
                        
                        <div class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border-l-4 border-red-500">
                            <p class="mb-3 font-semibold text-red-900 dark:text-red-100">Queda estrictamente prohibido:</p>
                            <ul class="list-disc pl-6 space-y-2 text-sm text-red-800 dark:text-red-200">
                                <li>Intentar vulnerar, eludir o desactivar medidas de seguridad</li>
                                <li>Realizar ingeniería inversa, descompilación o desensamblado del SOFTWARE</li>
                                <li>Modificar, alterar o crear obras derivadas del código fuente</li>
                                <li>Intentar acceder a funcionalidades no autorizadas para su perfil</li>
                                <li>Manipular URLs, peticiones API o parámetros del sistema para acceder a información restringida</li>
                                <li>Ejecutar scripts, inyecciones SQL o cualquier tipo de ataque informático</li>
                                <li>Interferir con el funcionamiento normal del sistema</li>
                            </ul>
                        </div>

                        <h2 class="text-2xl font-bold mb-4 mt-8 text-primary-700 dark:text-primary-300 border-b-2 border-primary-300 dark:border-primary-700 pb-2">
                            ARTÍCULO 5. PROHIBICIONES ABSOLUTAS Y RÉGIMEN DE CONFIDENCIALIDAD
                        </h2>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">5.1. Prohibición de Registro y Reproducción</h3>
                        
                        <div class="mb-6 p-5 bg-red-50 dark:bg-red-900/20 rounded-lg border-2 border-red-500">
                            <p class="mb-4 font-bold text-lg text-red-900 dark:text-red-100">
                                Queda TERMINANTEMENTE PROHIBIDO bajo cualquier circunstancia:
                            </p>
                            
                            <div class="mb-4">
                                <h4 class="font-bold text-red-900 dark:text-red-100 mb-2">A) Capturas y Grabaciones:</h4>
                                <ul class="list-disc pl-6 space-y-1 text-sm text-red-800 dark:text-red-200">
                                    <li>Tomar capturas de pantalla (screenshots) de cualquier interfaz del sistema</li>
                                    <li>Realizar grabaciones de video de pantalla (screen recording)</li>
                                    <li>Fotografiar con dispositivos externos (celulares, cámaras) la pantalla o información del sistema</li>
                                    <li>Utilizar cualquier método de registro visual, auditivo o multimedia del SOFTWARE</li>
                                </ul>
                            </div>

                            <div>
                                <h4 class="font-bold text-red-900 dark:text-red-100 mb-2">B) Reproducción y Copia:</h4>
                                <ul class="list-disc pl-6 space-y-1 text-sm text-red-800 dark:text-red-200">
                                    <li>Copiar, transcribir o reproducir información del sistema por cualquier medio</li>
                                    <li>Imprimir reportes, documentos o datos sin autorización expresa</li>
                                    <li>Guardar archivos, exportar datos o crear respaldos no autorizados</li>
                                    <li>Replicar estructuras, diseños o funcionalidades del SOFTWARE</li>
                                </ul>
                            </div>
                        </div>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">5.2. Confidencialidad y No Divulgación</h3>
                        
                        <p class="mb-4">
                            Todo CONTENIDO CONFIDENCIAL visualizado o procesado a través del SOFTWARE tiene carácter estrictamente 
                            confidencial y reservado. EL USUARIO se obliga a:
                        </p>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                            <div class="bg-surface-100 dark:bg-surface-800 p-4 rounded-lg">
                                <h4 class="font-bold text-surface-900 dark:text-surface-100 mb-2">A) No Divulgar:</h4>
                                <ul class="list-disc pl-6 space-y-1 text-sm text-surface-700 dark:text-surface-300">
                                    <li>Información operativa de los establecimientos</li>
                                    <li>Datos de inventarios, maquinaria o equipos</li>
                                    <li>Información técnica de la Wiki o manuales</li>
                                    <li>Estructuras o metodologías del SOFTWARE</li>
                                    <li>Datos personales de otros usuarios</li>
                                </ul>
                            </div>

                            <div class="bg-surface-100 dark:bg-surface-800 p-4 rounded-lg">
                                <h4 class="font-bold text-surface-900 dark:text-surface-100 mb-2">B) No Transmitir:</h4>
                                <ul class="list-disc pl-6 space-y-1 text-sm text-surface-700 dark:text-surface-300">
                                    <li>Enviar información a terceros no autorizados</li>
                                    <li>Compartir datos por medios electrónicos</li>
                                    <li>Discutir aspectos técnicos públicamente</li>
                                    <li>Revelar vulnerabilidades o errores</li>
                                    <li>Divulgar aspectos de seguridad del sistema</li>
                                </ul>
                            </div>
                        </div>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">5.3. Consecuencias del Incumplimiento</h3>
                        
                        <div class="mb-6 p-4 bg-red-100 dark:bg-red-900/30 rounded-lg border-2 border-red-600">
                            <p class="mb-3 font-bold text-red-900 dark:text-red-100">
                                La violación de las prohibiciones establecidas constituirá:
                            </p>
                            <ul class="list-disc pl-6 space-y-2 text-sm text-red-800 dark:text-red-200">
                                <li><strong>Espionaje Industrial:</strong> Conforme al artículo 223 del Código Penal Federal</li>
                                <li><strong>Violación de Secretos Industriales:</strong> Según la Ley de la Propiedad Industrial</li>
                                <li><strong>Robo de Propiedad Intelectual:</strong> Tipificado en el artículo 424 bis del Código Penal Federal</li>
                                <li><strong>Incumplimiento Contractual:</strong> Con todas las consecuencias civiles aplicables</li>
                            </ul>
                        </div>

                        <h2 class="text-2xl font-bold mb-4 mt-8 text-primary-700 dark:text-primary-300 border-b-2 border-primary-300 dark:border-primary-700 pb-2">
                            ARTÍCULO 6. VIOLACIONES AL DERECHO DE AUTOR Y SANCIONES
                        </h2>

                                                <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">6.1. Conductas Sancionables</h3>
                        
                        <p class="mb-3">
                            Además de las prohibiciones específicas, constituyen violaciones graves a este acuerdo y 
                            a la legislación autoral mexicana:
                        </p>

                        <div class="mb-6 space-y-4">
                            <div class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border-l-4 border-red-500">
                                <h4 class="font-bold text-red-900 dark:text-red-100 mb-2">
                                    A) Delitos contra el Derecho de Autor (Artículos 424 a 429 del Código Penal Federal):
                                </h4>
                                <ul class="list-disc pl-6 space-y-1 text-sm text-red-800 dark:text-red-200">
                                    <li>Reproducción, publicación o utilización no autorizada del SOFTWARE</li>
                                    <li>Fabricación o comercialización de copias del sistema</li>
                                    <li>Almacenamiento intencional de copias no autorizadas</li>
                                    <li>Transmisión o retransmisión no autorizada del SOFTWARE</li>
                                </ul>
                            </div>

                            <div class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border-l-4 border-red-500">
                                <h4 class="font-bold text-red-900 dark:text-red-100 mb-2">B) Gestión Electrónica de Derechos:</h4>
                                <ul class="list-disc pl-6 space-y-1 text-sm text-red-800 dark:text-red-200">
                                    <li>Elusión de medidas tecnológicas de protección</li>
                                    <li>Supresión o alteración de información sobre gestión de derechos</li>
                                    <li>Distribución de dispositivos o servicios para vulnerar protecciones</li>
                                </ul>
                            </div>
                        </div>

                        <div class="mb-6 p-5 bg-red-100 dark:bg-red-900/30 rounded-lg border-2 border-red-600">
                            <h3 class="text-xl font-semibold mb-3 text-red-900 dark:text-red-100">6.2. Sanciones Penales Aplicables</h3>
                            
                            <p class="mb-3 text-red-800 dark:text-red-200">
                                Conforme a la legislación penal federal mexicana vigente en 2026, las conductas descritas pueden ser sancionadas con:
                            </p>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <div class="bg-red-200 dark:bg-red-900/50 p-3 rounded">
                                    <p class="font-bold text-red-900 dark:text-red-100">Prisión</p>
                                    <p class="text-sm text-red-800 dark:text-red-200">6 meses a 10 años</p>
                                </div>
                                <div class="bg-red-200 dark:bg-red-900/50 p-3 rounded">
                                    <p class="font-bold text-red-900 dark:text-red-100">Multas</p>
                                    <p class="text-sm text-red-800 dark:text-red-200">300 a 3,000 días de salario mínimo</p>
                                </div>
                                <div class="bg-red-200 dark:bg-red-900/50 p-3 rounded">
                                    <p class="font-bold text-red-900 dark:text-red-100">Decomiso</p>
                                    <p class="text-sm text-red-800 dark:text-red-200">De instrumentos y productos</p>
                                </div>
                                <div class="bg-red-200 dark:bg-red-900/50 p-3 rounded">
                                    <p class="font-bold text-red-900 dark:text-red-100">Clausura</p>
                                    <p class="text-sm text-red-800 dark:text-red-200">Temporal o definitiva</p>
                                </div>
                            </div>
                        </div>

                                                <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">6.3. Responsabilidad Civil</h3>
                        
                        <div class="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                            <p class="mb-3 font-semibold text-amber-900 dark:text-amber-100">
                                Independientemente de las sanciones penales, EL USUARIO será responsable civilmente por:
                            </p>
                            <ul class="list-disc pl-6 space-y-2 text-sm text-amber-800 dark:text-amber-200">
                                <li><strong>Daños y perjuicios</strong> causados al LICENCIANTE</li>
                                <li><strong>Lucro cesante</strong> derivado de la violación</li>
                                <li><strong>Reparación del daño moral</strong> al autor</li>
                                <li><strong>Costas y honorarios</strong> de abogados y peritos</li>
                                <li><strong>Publicación de la sentencia</strong> en medios de comunicación (cuando proceda)</li>
                            </ul>
                        </div>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">6.4. Medidas Precautorias</h3>
                        
                        <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                            <p class="mb-3 font-semibold text-blue-900 dark:text-blue-100">
                                EL LICENCIANTE podrá solicitar ante autoridades competentes:
                            </p>
                            <ul class="list-disc pl-6 space-y-2 text-sm text-blue-800 dark:text-blue-200">
                                <li>Embargo precautorio de bienes</li>
                                <li>Aseguramiento de evidencias</li>
                                <li>Suspensión de actividades infractoras</li>
                                <li>Garantía del interés fiscal</li>
                                <li>Cualquier otra medida cautelar procedente</li>
                            </ul>
                        </div>

                        <h2 class="text-2xl font-bold mb-4 mt-8 text-primary-700 dark:text-primary-300 border-b-2 border-primary-300 dark:border-primary-700 pb-2">
                            ARTÍCULO 7. REVOCACIÓN Y TERMINACIÓN DE LA LICENCIA
                        </h2>

                        <p class="mb-4">
                            EL LICENCIANTE se reserva el derecho de revocar inmediatamente la licencia sin necesidad de declaración 
                            judicial ni aviso previo por incumplimiento de cualquier cláusula, uso indebido, violación a prohibiciones, 
                            intento de vulnerar la seguridad, o decisión discrecional por motivos de seguridad.
                        </p>

                        <div class="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                            <p class="font-semibold text-amber-900 dark:text-amber-100 mb-2">EL USUARIO acepta expresamente que:</p>
                            <ul class="list-disc pl-6 space-y-1 text-sm text-amber-800 dark:text-amber-200">
                                <li>La revocación puede ocurrir de forma instantánea y automática</li>
                                <li>EL LICENCIANTE no está obligado a proporcionar explicaciones</li>
                                <li>No existe derecho de audiencia, apelación o recurso administrativo previo</li>
                                <li>La decisión es inapelable al ser un software de uso privado corporativo</li>
                            </ul>
                        </div>

                        <h2 class="text-2xl font-bold mb-4 mt-8 text-primary-700 dark:text-primary-300 border-b-2 border-primary-300 dark:border-primary-700 pb-2">
                            ARTÍCULO 8. AUDITORÍA Y MONITOREO DE ACTIVIDADES
                        </h2>

                        <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                            <p class="mb-3 font-semibold text-blue-900 dark:text-blue-100">
                                EL USUARIO reconoce y acepta que el SOFTWARE cuenta con sistemas automáticos de registro (logs) 
                                que documentan todas las actividades, con pleno valor probatorio conforme a la legislación mexicana.
                            </p>
                            <p class="text-sm text-blue-800 dark:text-blue-200">
                                Los registros incluyen: sesiones, páginas consultadas, operaciones realizadas, exportaciones, 
                                intentos de acceso no autorizado y anomalías detectadas.
                            </p>
                        </div>

                                                <h2 class="text-2xl font-bold mb-4 mt-8 text-primary-700 dark:text-primary-300 border-b-2 border-primary-300 dark:border-primary-700 pb-2">
                            ARTÍCULO 9. LIMITACIÓN DE RESPONSABILIDAD Y GARANTÍAS
                        </h2>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">9.1. Disponibilidad del Sistema</h3>
                        
                        <p class="mb-3">
                            EL LICENCIANTE realizará esfuerzos razonables para mantener la operación continua del SOFTWARE, sin embargo:
                        </p>

                        <div class="mb-6 p-4 bg-surface-100 dark:bg-surface-800 rounded-lg">
                            <ul class="list-disc pl-6 space-y-2 text-sm text-surface-700 dark:text-surface-300">
                                <li>No garantiza disponibilidad ininterrumpida del 100% del tiempo</li>
                                <li>No se hace responsable por interrupciones causadas por fallas de infraestructura de terceros 
                                    (proveedores de internet, servicios en la nube, energía eléctrica)</li>
                                <li>Puede realizar mantenimientos programados con afectación temporal del servicio</li>
                                <li>No garantiza tiempos específicos de respuesta o rendimiento</li>
                            </ul>
                        </div>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">9.2. Exactitud de la Información</h3>
                        
                        <div class="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                            <p class="mb-3 text-amber-900 dark:text-amber-100">
                                El SOFTWARE funciona como herramienta de apoyo administrativo y operativo:
                            </p>
                            <ul class="list-disc pl-6 space-y-2 text-sm text-amber-800 dark:text-amber-200">
                                <li>EL LICENCIANTE no garantiza la exactitud absoluta de datos ingresados por usuarios</li>
                                <li>La interpretación y uso de la información es responsabilidad exclusiva del USUARIO</li>
                                <li>EL USUARIO debe validar datos críticos antes de tomar decisiones basadas en ellos</li>
                                <li>EL LICENCIANTE no será responsable por decisiones operativas o estratégicas tomadas 
                                    con base en información del sistema</li>
                            </ul>
                        </div>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">9.3. Exclusión de Garantías Implícitas</h3>
                        
                        <p class="mb-3">En la máxima medida permitida por la ley, se excluyen garantías implícitas de:</p>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
                            <div class="bg-surface-100 dark:bg-surface-800 p-3 rounded-lg">
                                <p class="font-semibold text-surface-900 dark:text-surface-100">• Comerciabilidad</p>
                            </div>
                            <div class="bg-surface-100 dark:bg-surface-800 p-3 rounded-lg">
                                <p class="font-semibold text-surface-900 dark:text-surface-100">• Adecuación para un propósito particular</p>
                            </div>
                            <div class="bg-surface-100 dark:bg-surface-800 p-3 rounded-lg">
                                <p class="font-semibold text-surface-900 dark:text-surface-100">• No infracción de derechos de terceros</p>
                            </div>
                            <div class="bg-surface-100 dark:bg-surface-800 p-3 rounded-lg">
                                <p class="font-semibold text-surface-900 dark:text-surface-100">• Resultados específicos o precisión absoluta</p>
                            </div>
                        </div>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">9.4. Limitación de Daños</h3>
                        
                        <div class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border-l-4 border-red-500">
                            <p class="mb-3 font-semibold text-red-900 dark:text-red-100">
                                En ningún caso EL LICENCIANTE será responsable por:
                            </p>
                            <ul class="list-disc pl-6 space-y-1 text-sm text-red-800 dark:text-red-200">
                                <li>Daños indirectos, incidentales o consecuenciales</li>
                                <li>Pérdida de beneficios o datos</li>
                                <li>Interrupción de negocios</li>
                                <li>Daños morales derivados del uso o imposibilidad de uso del SOFTWARE</li>
                            </ul>
                        </div>

                                                <h2 class="text-2xl font-bold mb-4 mt-8 text-primary-700 dark:text-primary-300 border-b-2 border-primary-300 dark:border-primary-700 pb-2">
                            ARTÍCULO 10. MODIFICACIONES AL ACUERDO
                        </h2>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">10.1. Derecho de Modificación Unilateral</h3>
                        
                        <p class="mb-6">
                            EL LICENCIANTE se reserva el derecho de modificar, actualizar o sustituir los términos del presente acuerdo 
                            en cualquier momento, sin necesidad de consentimiento expreso de EL USUARIO.
                        </p>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">10.2. Notificación de Cambios</h3>
                        
                        <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                            <p class="mb-3 font-semibold text-blue-900 dark:text-blue-100">Las modificaciones podrán notificarse mediante:</p>
                            <ul class="list-disc pl-6 space-y-2 text-sm text-blue-800 dark:text-blue-200">
                                <li>Publicación en el sistema al momento del inicio de sesión</li>
                                <li>Comunicación por correo electrónico institucional</li>
                                <li>Notificación dentro de la plataforma</li>
                                <li>Actualización de este documento en el repositorio del SOFTWARE</li>
                            </ul>
                        </div>

                        <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">10.3. Aceptación de Modificaciones</h3>
                        
                        <div class="mb-6 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg border-2 border-primary-400">
                            <p class="text-sm font-semibold text-primary-900 dark:text-primary-100">
                                El uso continuado del SOFTWARE después de la notificación de cambios constituye 
                                la aceptación plena de las nuevas condiciones.
                            </p>
                        </div>

                        <h2 class="text-2xl font-bold mb-4 mt-8 text-primary-700 dark:text-primary-300 border-b-2 border-primary-300 dark:border-primary-700 pb-2">
                            ARTÍCULO 11. JURISDICCIÓN Y LEY APLICABLE
                        </h2>

                        <p class="mb-4">
                            Este acuerdo se rige por la <strong>Ley Federal del Derecho de Autor</strong>, <strong>Código Penal Federal</strong>, 
                            <strong>Ley de la Propiedad Industrial</strong>, <strong>Código Civil Federal</strong>, 
                            <strong>Código de Comercio</strong> y <strong>Tratados Internacionales</strong> suscritos por México.
                        </p>

                        <p class="mb-6">
                            Las partes se someten a los <strong>Tribunales Federales competentes</strong>, 
                            <strong>Juzgados de Distrito</strong> y al <strong>Instituto Mexicano de la Propiedad Industrial (IMPI)</strong>. 
                            EL USUARIO renuncia expresamente a cualquier otro fuero.
                        </p>

                                                <h2 class="text-2xl font-bold mb-4 mt-8 text-primary-700 dark:text-primary-300 border-b-2 border-primary-300 dark:border-primary-700 pb-2">
                            ARTÍCULO 12. DISPOSICIONES GENERALES Y FINALES
                        </h2>

                        <div class="space-y-6 mb-8">
                            <div>
                                <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">12.1. Integralidad del Acuerdo</h3>
                                <p class="text-surface-700 dark:text-surface-300">
                                    Este documento constituye el acuerdo completo entre las partes respecto al uso del SOFTWARE 
                                    y sustituye cualquier comunicación, acuerdo o entendimiento previo, verbal o escrito.
                                </p>
                            </div>

                            <div>
                                <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">12.2. Divisibilidad</h3>
                                <p class="text-surface-700 dark:text-surface-300">
                                    Si cualquier disposición de este acuerdo fuera declarada inválida, ilegal o inaplicable por 
                                    autoridad competente, las demás cláusulas mantendrán plena vigencia y efectos.
                                </p>
                            </div>

                            <div>
                                <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">12.3. No Renuncia</h3>
                                <p class="text-surface-700 dark:text-surface-300">
                                    La omisión o tolerancia por parte de EL LICENCIANTE en exigir el cumplimiento estricto de 
                                    cualquier disposición no constituirá renuncia a sus derechos ni impedirá su ejercicio posterior.
                                </p>
                            </div>

                            <div>
                                <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">12.4. Independencia de las Partes</h3>
                                <p class="text-surface-700 dark:text-surface-300">
                                    Este acuerdo no crea ninguna relación de sociedad, asociación, agencia o empleo entre las partes. 
                                    Cada parte es un contratante independiente.
                                </p>
                            </div>

                            <div>
                                <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">12.5. Idioma</h3>
                                <p class="text-surface-700 dark:text-surface-300">
                                    El presente acuerdo se ha redactado en idioma español. Cualquier traducción es únicamente 
                                    para conveniencia y prevalecerá siempre la versión en español en caso de discrepancia.
                                </p>
                            </div>

                            <div>
                                <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">12.6. Notificaciones</h3>
                                <div class="bg-surface-100 dark:bg-surface-800 p-4 rounded-lg">
                                    <p class="mb-3 font-semibold text-surface-900 dark:text-surface-100">
                                        Todas las notificaciones relacionadas con este acuerdo deberán realizarse por escrito 
                                        y se considerarán válidas cuando:
                                    </p>
                                    <ul class="list-disc pl-6 space-y-1 text-sm text-surface-700 dark:text-surface-300">
                                        <li>Sean entregadas personalmente</li>
                                        <li>Sean enviadas por correo electrónico institucional verificado</li>
                                        <li>Sean publicadas en el sistema para conocimiento del USUARIO</li>
                                    </ul>
                                </div>
                            </div>

                            <div>
                                <h3 class="text-xl font-semibold mb-3 text-primary-600 dark:text-primary-400">12.7. Sobrevivencia de Obligaciones</h3>
                                <div class="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                                    <p class="text-sm font-semibold text-amber-900 dark:text-amber-100">
                                        Las disposiciones relacionadas con confidencialidad, propiedad intelectual, 
                                        limitación de responsabilidad y jurisdicción sobrevivirán a la terminación de este acuerdo.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <h2 class="text-2xl font-bold mb-4 mt-8 text-primary-700 dark:text-primary-300 border-b-2 border-primary-300 dark:border-primary-700 pb-2">
                            ARTÍCULO 13. ACEPTACIÓN Y CONSENTIMIENTO
                        </h2>

                        <div class="mb-8 p-5 bg-primary-50 dark:bg-primary-900/20 rounded-lg border-2 border-primary-500">
                            <p class="mb-3 font-semibold text-primary-900 dark:text-primary-100">
                                Al acceder y utilizar el SOFTWARE Core Nexus Manager (CNM), EL USUARIO declara expresamente que:
                            </p>
                            <ol class="list-decimal pl-6 space-y-2 text-sm text-primary-800 dark:text-primary-200">
                                <li>Ha leído íntegramente el presente acuerdo</li>
                                <li>Comprende todos sus términos y condiciones</li>
                                <li>Acepta quedar legal y voluntariamente obligado por todas sus disposiciones</li>
                                <li>Reconoce la autoría de José Roberto Tamayo Montejano y la titularidad de CYTECHNOLOGIES</li>
                                <li>Se somete a la legislación mexicana y a los tribunales competentes</li>
                                <li>Renuncia a cualquier reclamación futura derivada de la aceptación de estos términos</li>
                            </ol>
                        </div>

                        <!-- Información Legal -->
                        <div class="mt-8 pt-6 border-t-2 border-surface-300 dark:border-surface-700">
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                                <div>
                                    <p class="text-xs font-bold text-surface-600 dark:text-surface-400 mb-1">TITULAR DE DERECHOS PATRIMONIALES</p>
                                    <p class="text-sm font-semibold text-surface-900 dark:text-surface-100">CYTECHNOLOGIES S.A. DE C.V. DE R.L. <br><span>  Colinas del Cimatario, Cerro Escondido # 380 Querétaro, Qro. México</span></p>
                                </div>
                                <div>
                                    <p class="text-xs font-bold text-surface-600 dark:text-surface-400 mb-1">AUTOR INTELECTUAL</p>
                                    <p class="text-sm font-semibold text-surface-900 dark:text-surface-100">José Roberto Tamayo Montejano<br> <span> <a href="mailto:robert-cyby@hotmail.com">robert-cyby@hotmail.com</a></span> <span>[cy Tamayo]</span></p>
                                </div>
                                <div>
                                    <p class="text-xs font-bold text-surface-600 dark:text-surface-400 mb-1">SOFTWARE</p>
                                    <p class="text-sm font-semibold text-surface-900 dark:text-surface-100">Core Nexus Manager (CNM)</p>
                                </div>
                                <div>
                                    <p class="text-xs font-bold text-surface-600 dark:text-surface-400 mb-1">VERSIÓN DEL DOCUMENTO</p>
                                    <p class="text-sm font-semibold text-surface-900 dark:text-surface-100">2.0 - Febrero 2026</p>
                                </div>
                            </div>

                            <div class="text-center">
                                <p class="text-sm font-bold text-primary-700 dark:text-primary-300 mb-2">
                                    PROTEGIDO POR LA LEY FEDERAL DEL DERECHO DE AUTOR
                                </p>
                                <p class="text-sm font-bold text-primary-700 dark:text-primary-300">
                                    TODOS LOS DERECHOS RESERVADOS © 2026 CYTECHNOLOGIES
                                </p>
                                <p class="text-xs text-surface-600 dark:text-surface-400 mt-4 italic">
                                    Este documento tiene carácter legal vinculante. La violación de sus disposiciones constituye 
                                    incumplimiento contractual y puede derivar en responsabilidades civiles y penales conforme 
                                    a las leyes de los Estados Unidos Mexicanos.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Indicador de scroll -->
                <div v-if="!scrolledToBottom" class="px-8 py-3 bg-amber-100 dark:bg-amber-900/30 border-t border-amber-300 dark:border-amber-700">
                    <div class="flex items-center justify-center">
                        <svg class="w-5 h-5 text-amber-600 dark:text-amber-400 animate-bounce mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                        </svg>
                        <p class="text-sm font-medium text-amber-800 dark:text-amber-200">
                            Por favor, desplácese hasta el final del documento para continuar
                        </p>
                    </div>
                </div>

                <!-- Footer con acciones -->
                <div class="px-8 py-6 bg-surface-100 dark:bg-surface-800 border-t border-surface-200 dark:border-surface-700">
                    <!-- Mensaje de licencia ya aceptada -->
                    <div v-if="licenseAlreadyAccepted" class="text-center my-2">
                        <div class="inline-flex items-center justify-center px-5 py-2.5 bg-green-50 dark:bg-green-900/30 border border-green-500 rounded-lg mb-4">
                            <svg class="w-5 h-5 text-green-600 dark:text-green-400 mr-2.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                            </svg>
                            <div class="text-left">
                                <h3 class="text-base font-semibold text-green-800 dark:text-green-200 leading-tight">Licencia Aceptada</h3>
                                <p class="text-xs text-green-700 dark:text-green-300 mt-0.5">Ya has aceptado los términos y condiciones de uso</p>
                            </div>
                        </div> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;
                        <Button 
                            label="Continuar al Sistema" 
                            @click="goToDashboard"
                            icon="pi pi-arrow-right"
                            iconPos="right"
                            class="px-6"
                        />
                    </div>

                    <!-- Controles de aceptación (solo si hay sesión activa y NO ha aceptado) -->
                    <div v-else-if="haySessionActiva">
                        <!-- Mensaje de error -->
                        <Message v-if="errorMessage" severity="error" :closable="false" class="mb-4">
                            {{ errorMessage }}
                        </Message>

                        <div class="flex items-center justify-between flex-wrap gap-4">
                            <div class="flex items-center">
                                <Checkbox v-model="agreed" inputId="agree" :binary="true" :disabled="!scrolledToBottom || loading" />
                                <label for="agree" class="ml-3 text-sm" :class="!scrolledToBottom || loading ? 'text-surface-400 dark:text-surface-600' : 'text-surface-900 dark:text-surface-100 cursor-pointer'">
                                    He leído y acepto los términos y condiciones del Acuerdo de Licencia
                                </label>
                            </div>
                            
                            <div class="flex gap-3">
                                <Button 
                                    label="Rechazar" 
                                    severity="secondary" 
                                    outlined
                                    @click="handleReject"
                                    icon="pi pi-times"
                                    class="px-6"
                                    :disabled="loading"
                                />
                                <Button 
                                    label="Aceptar y Continuar" 
                                    :disabled="!agreed || loading"
                                    @click="handleAccept"
                                    :loading="loading"
                                    icon="pi pi-check"
                                    class="px-6"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Nota adicional -->
            <div class="text-center mt-6">
                <p class="text-sm text-surface-600 dark:text-surface-400">
                    Si tiene dudas sobre este acuerdo, por favor contacte al administrador del sistema antes de aceptar.
                </p>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Estilos personalizados para el contenido de la licencia */
.license-content {
    scroll-behavior: smooth;
}

.license-content::-webkit-scrollbar {
    width: 10px;
}

.license-content::-webkit-scrollbar-track {
    background: var(--surface-100);
    border-radius: 10px;
}

.license-content::-webkit-scrollbar-thumb {
    background: var(--primary-400);
    border-radius: 10px;
}

.license-content::-webkit-scrollbar-thumb:hover {
    background: var(--primary-500);
}

/* Estilos para modo oscuro */
.dark .license-content::-webkit-scrollbar-track {
    background: var(--surface-800);
}

.dark .license-content::-webkit-scrollbar-thumb {
    background: var(--primary-600);
}

.dark .license-content::-webkit-scrollbar-thumb:hover {
    background: var(--primary-500);
}

/* Animación suave para el indicador de scroll */
@keyframes bounce {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(5px);
    }
}

.animate-bounce {
    animation: bounce 1s infinite;
}
</style>
