<script setup>
import { ref, computed } from 'vue';
import { getUser, hasRoleAccess } from '@/service/api';

const usuario = ref(getUser() || {});

// === PERMISOS: Incidencias de Infraestructura ===
const canExportInfra = computed(() => hasRoleAccess(['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR']));
const canCreateInfra = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA']));
const isEncargadoAreaInfra = computed(() => usuario.value?.rol_nombre === 'ENCARGADO AREA');

// === PERMISOS: Inventario Sala ===
const canEditInv = computed(() => hasRoleAccess(['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR']));

// === PERMISOS: Mantenimientos Preventivos ===
const canCreateMant = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO']));
const canEditOrDeleteMant = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS']));

// === PERMISOS: Usuarios ===
const canManageUsers = computed(() => hasRoleAccess(['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR', 'GERENCIA']));

// === PERMISOS: Proveedores ===
const canManageSuppliers = computed(() => hasRoleAccess(['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR']));
const canViewSupplierCreds = computed(() => hasRoleAccess(['SUP SISTEMAS', 'ADMINISTRADOR']));

// === PERMISOS: Modelos de Máquinas ===
const canManageModels = computed(() => hasRoleAccess(['SUP SISTEMAS', 'SUPERVISOR SALA', 'ADMINISTRADOR']));
const canDeactivateModels = computed(() => hasRoleAccess(['SUP SISTEMAS', 'ADMINISTRADOR']));

// === PERMISOS: Máquinas ===
const canManageMachines = computed(() => hasRoleAccess(['SUP SISTEMAS', 'ADMINISTRADOR']));
const canViewMachineCharts = computed(() => hasRoleAccess(['SUP SISTEMAS', 'ADMINISTRADOR']));

// === PERMISOS: Mapa de Sala ===
const canEditMap = computed(() => hasRoleAccess(['SUP SISTEMAS', 'GERENCIA', 'ADMINISTRADOR']));

// === PERMISOS: Tickets ===
const canManageTickets = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA']));
const canAddBitacora = computed(() => hasRoleAccess(['SUP SISTEMAS', 'TECNICO', 'ADMINISTRADOR']));
const isEncargadoTickets = computed(() => usuario.value?.rol_nombre === 'ENCARGADO AREA');
// === PERMISOS: Operatividad (Auditorías y Relevos) ===
const canCreateAuditoria = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO', 'GERENCIA', 'SUPERVISOR SALA']));
const canEditAuditoria = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'GERENCIA', 'SUPERVISOR SALA']));
const canCreateRelevo = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO']));
const canEditRelevo = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS']));

// === PERMISOS: Gamificación ===
const participaGamificacion = computed(() => hasRoleAccess(['TECNICO', 'SUP SISTEMAS']));

// === PERMISOS: Tienda de Recompensas ===
const puedeVerTienda = computed(() => hasRoleAccess(['TECNICO', 'SUP SISTEMAS', 'ADMINISTRADOR', 'DB ADMIN', 'GERENCIA']));
const puedeAdminTienda = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA']));
const puedeCanjear = computed(() => hasRoleAccess(['TECNICO', 'SUP SISTEMAS']));

// === PERMISOS: Wiki Técnica ===
const puedeVerWiki = computed(() => hasRoleAccess(['TECNICO', 'SUP SISTEMAS', 'ADMINISTRADOR', 'DB ADMIN', 'GERENCIA']));
const puedeProponer = computed(() => hasRoleAccess(['TECNICO', 'SUP SISTEMAS', 'ADMINISTRADOR', 'DB ADMIN']));
const puedePublicarWiki = computed(() => hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN']));
</script>

<template>
    <div class="flex flex-col gap-4">
        <!-- Encabezado del Manual -->
        <div
            class="card p-6 rounded-2xl shadow-sm bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700">
            <h1 class="text-3xl font-bold mb-2 text-primary flex items-center gap-3">
                <i class="pi pi-book text-3xl"></i>
                Manual del Usuario NEXUS
            </h1>
            <p class="text-surface-600 dark:text-surface-300">
                Guía de uso adaptada a tu perfil de acceso actual:
                <Tag :value="usuario?.rol_nombre || 'Invitado'" severity="info"
                    class="text-sm px-3 py-1 font-bold ml-2" />
            </p>
        </div>

        <!-- Contenedor Principal de Tabs -->
        <div
            class="card p-0 shadow-sm border border-surface-200 dark:border-surface-700 overflow-hidden rounded-2xl relative">

            <div
                class="bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 px-4 py-2 text-sm flex items-center justify-center gap-2 border-b border-blue-100 dark:border-blue-800">
                <i class="pi pi-arrows-h animate-pulse"></i>
                <span><strong>Tip:</strong> Si estás en una pantalla pequeña, usa las flechas <strong>&lt; &gt;</strong>
                    a los lados del menú o desliza para ver todas las pestañas.</span>
            </div>

            <Tabs value="0">
                <TabList
                    class="bg-surface-50 dark:bg-surface-800 border-b border-surface-200 dark:border-surface-700 p-2">
                    <Tab value="0"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-building mr-2 text-blue-500"></i> Incidencias Infraestructura
                    </Tab>
                    <Tab value="1"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-box mr-2 text-primary"></i> Inventario de Sala
                    </Tab>
                    <Tab value="2"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-wrench mr-2 text-purple-500"></i> Mantenimientos Preventivos
                    </Tab>
                    <Tab value="3"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-users mr-2 text-green-500"></i> Gestión de Usuarios
                    </Tab>
                    <Tab value="4"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-briefcase mr-2 text-orange-500"></i> Catálogo de Proveedores
                    </Tab>
                    <Tab value="5"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-box mr-2 text-indigo-500"></i> Modelos de Máquinas
                    </Tab>
                    <Tab value="6"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-desktop mr-2 text-blue-500"></i> Inventario de Máquinas
                    </Tab>
                    <Tab value="7"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-map mr-2 text-teal-500"></i> Mapa de Sala Interactivo
                    </Tab>
                    <Tab value="8"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-ticket mr-2 text-red-500"></i> Mesa de Ayuda (Tickets)
                    </Tab>
                    <Tab value="9"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-id-card mr-2 text-purple-500"></i> Auditorías Externas
                    </Tab>
                    <Tab value="10"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-sync mr-2 text-orange-500"></i> Relevos de Turno
                    </Tab>
                    <Tab value="11"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-compass mr-2 text-indigo-500"></i> Dashboard Principal
                    </Tab>
                    <Tab value="12"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-bell mr-2 text-yellow-500"></i> Notificaciones
                    </Tab>
                    <Tab value="13"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-shield mr-2 text-red-500"></i> Licencia de Uso
                    </Tab>
                    <Tab value="14"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-star mr-2 text-yellow-500"></i> Gamificación NEXUS
                    </Tab>
                    <Tab value="15"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-shopping-bag mr-2 text-pink-500"></i> Tienda de Recompensas
                    </Tab>
                    <Tab value="16"
                        class="font-semibold m-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded-lg transition-colors">
                        <i class="pi pi-book mr-2 text-teal-500"></i> Wiki Técnica
                    </Tab>
                </TabList>

                <TabPanels>
                    <!-- Sección: Incidencias de Infraestructura -->
                    <TabPanel value="0" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                                        <i class="pi pi-info-circle text-2xl"></i>
                                        <span class="text-xl">¿Qué es e información general?</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed">
                                        El módulo de <strong>Incidencias de Infraestructura</strong> permite registrar y
                                        consultar eventos u ocurrencias que afectan las instalaciones del casino (como
                                        fallas eléctricas, problemas de clima, goteras, red, etc.).
                                    </p>

                                    <div v-if="isEncargadoAreaInfra"
                                        class="mt-4 p-4 bg-blue-100 dark:bg-blue-900/40 text-blue-900 dark:text-blue-200 rounded-xl border-l-4 border-blue-500 flex items-start gap-3">
                                        <i class="pi pi-eye mt-1 text-xl"></i>
                                        <div>
                                            <strong class="block mb-1">Nota sobre tu visualización (Encargado de
                                                Área):</strong>
                                            Solo podrás ver las incidencias que tú mismo hayas registrado. Los registros
                                            de otros compañeros están ocultos para tu perfil.
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Acciones (Lo que puede hacer el usuario) -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-green-600 dark:text-green-400">
                                        <i class="pi pi-cog text-2xl"></i>
                                        <span class="text-xl">Lo que puedes hacer</span>
                                    </div>
                                </template>
                                <template #content>
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-primary">
                                                <i class="pi pi-list mr-2"></i> Visualizar Listado
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Puedes ver la
                                                tabla principal con columnas clave. Haz clic en el título de la
                                                incidencia resaltado en azul para abrir la ventana con su detalle
                                                completo (notas internas, auditorías de fechas, etc).</p>
                                        </div>

                                        <div v-if="canCreateInfra"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-red-500">
                                                <i class="pi pi-plus-circle mr-2"></i> Crear Incidencia
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Tienes permisos
                                                para registrar una nueva incidencia utilizando el botón
                                                <Tag value="Nueva Incidencia" severity="danger" class="mx-1" /> en la
                                                parte superior derecha de la tabla.
                                            </p>
                                        </div>

                                        <div v-if="canExportInfra"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-orange-500">
                                                <i class="pi pi-file-export mr-2"></i> Exportar e Imprimir
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Tu perfil tiene
                                                privilegios para descargar el listado de incidencias en formato Excel
                                                (<i class="pi pi-file-excel"></i>) o imprimirlo (<i
                                                    class="pi pi-print"></i>) con los botones de la tabla principal.</p>
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Llenado de Formularios -->
                            <Card v-if="canCreateInfra"
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-purple-600 dark:text-purple-400">
                                        <i class="pi pi-file-edit text-2xl"></i>
                                        <span class="text-xl">Formulario: ¿Cómo reportar una incidencia?</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Al oprimir "Nueva Incidencia", se abrirá una ventana que requiere la siguiente
                                        información:
                                    </p>
                                </template>
                                <template #content>
                                    <ul class="flex flex-col gap-4">
                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-building text-primary"></i>
                                                <strong class="text-lg">Casino Afectado</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Selecciona de la lista el casino donde ocurrió el evento.
                                                <span class="italic font-semibold block mt-1 text-surface-500">Nota: Si
                                                    tu usuario ya pertenece administrativamente a un casino, este campo
                                                    ya vendrá rellenado y bloqueado para evitar errores.</span>
                                            </p>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-shield text-primary"></i>
                                                <strong class="text-lg">Severidad</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
                                                Nivel de urgencia. Por defecto está seleccionado en
                                                <strong>Media</strong>. Determina la urgencia usando estas guías:
                                            </p>
                                            <div class="flex flex-wrap gap-2 text-xs">
                                                <Tag value="Baja (Sin afectación)" severity="info" />
                                                <Tag value="Media (Afectación parcial)" severity="warn" />
                                                <Tag value="Alta (Riesgo operativo)" severity="danger" />
                                                <Tag value="Crítica (Cierre total/parcial)" severity="danger" />
                                            </div>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-pencil text-primary"></i>
                                                <strong class="text-lg">Título del Evento</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Escribe un resumen corto y descriptivo de lo ocurrido. Por ejemplo:
                                                <em>"Apagón zona de máquinas sur"</em> o <em>"Gotera sobre isla 5"</em>.
                                            </p>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-tags text-primary"></i>
                                                <strong class="text-lg">Categoría y Descripción</strong>
                                                <Tag value="Categoría Obligatoria" severity="danger" class="text-xs"
                                                    rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Selecciona el tipo de falla (Falla Eléctrica, Agua, Clima, Red Externa,
                                                etc.) de la lista desplegable. Luego, usa el campo de
                                                <strong>Descripción Detallada</strong> (opcional pero recomendado) para
                                                escribir un relato completo del suceso y las afectaciones visibles.
                                            </p>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-clock text-primary"></i>
                                                <strong class="text-lg">Tiempos</strong>
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                <strong>Hora de Inicio
                                                    <Tag value="Obligatoria" severity="danger" class="text-[10px] ml-1"
                                                        rounded /> :
                                                </strong> Fecha y hora exacta cuando inició el problema.<br>
                                                <strong>Hora de Fin:</strong> Solo llénalo si el evento ya se solucionó.
                                                Si lo dejas en blanco, el sistema lo marcará como <em>"En curso"</em>.
                                            </p>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-check-square text-primary"></i>
                                                <strong class="text-lg">Casillas de Estado</strong>
                                            </div>
                                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                                                <div
                                                    class="p-3 bg-surface-50 dark:bg-surface-800 rounded flex items-start gap-3">
                                                    <Checkbox :modelValue="true" :binary="true" readonly class="mt-1" />
                                                    <div class="text-sm">
                                                        <strong
                                                            class="block text-surface-700 dark:text-surface-200">Afecta
                                                            Operación</strong>
                                                        <span class="text-surface-500">Márcalo si el problema afecta
                                                            parcial o totalmente el de máquinas o clientes. Muestra
                                                            etiqueta roja en toda la tabla.</span>
                                                    </div>
                                                </div>
                                                <div
                                                    class="p-3 bg-surface-50 dark:bg-surface-800 rounded flex items-start gap-3">
                                                    <Checkbox :modelValue="true" :binary="true" readonly class="mt-1" />
                                                    <div class="text-sm">
                                                        <strong
                                                            class="block text-surface-700 dark:text-surface-200">Está
                                                            Activo</strong>
                                                        <span class="text-surface-500">Marcado por defecto. Desmárcalo
                                                            posteriormente (editando) cuando la incidencia esté resulta
                                                            por completo (sirve para cerrar reportes).</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </li>
                                    </ul>
                                </template>
                            </Card>

                        </div>
                    </TabPanel>

                    <!-- Sección: Inventario Sala -->
                    <TabPanel value="1" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                                        <i class="pi pi-info-circle text-2xl"></i>
                                        <span class="text-xl">¿Qué es e información general?</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed">
                                        El módulo de <strong>Inventario de Sala</strong> te permite llevar el control de
                                        las herramientas y consumibles físicamente disponibles en tu casino
                                        correspondiente.
                                        Solo se muestran por defecto en tu visualización los artículos marcados como
                                        activos.
                                    </p>
                                </template>
                            </Card>

                            <!-- Acciones (Lo que puede hacer el usuario) -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-green-600 dark:text-green-400">
                                        <i class="pi pi-cog text-2xl"></i>
                                        <span class="text-xl">Lo que puedes hacer</span>
                                    </div>
                                </template>
                                <template #content>
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-primary">
                                                <i class="pi pi-list mr-2"></i> Visualizar Listado
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Puedes ver todos
                                                los artículos activos en tu casino, incluyendo su cantidad actual y
                                                quién hizo la última modificación.</p>
                                        </div>

                                        <div
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-teal-500">
                                                <i class="pi pi-cloud-download mr-2"></i> Exportar e Imprimir
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Todos los usuarios
                                                pueden descargar el listado de su casino en formato Excel o imprimirlo
                                                directamente con los botones de la barra superior de herramientas de
                                                información.</p>
                                        </div>

                                        <div v-if="canEditInv"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-red-500">
                                                <i class="pi pi-pencil mr-2"></i> Gestionar Artículos
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Tu nivel de acceso
                                                te permite registrar
                                                <Tag value="Nuevo Artículo" severity="primary" class="mx-1 text-xs" />,
                                                así como editar los nombres o existencias utilizando el botón azul (<i
                                                    class="pi pi-pencil"></i>) en la tabla.
                                            </p>
                                        </div>

                                        <div v-if="canEditInv"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-orange-500">
                                                <i class="pi pi-ban mr-2"></i> Activar/Desactivar
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">En la columna de
                                                Acciones, puedes dar clic en el botón <i
                                                    class="pi pi-ban text-red-500"></i> o <i
                                                    class="pi pi-check-circle text-green-500"></i> para inhabilitar /
                                                habilitar un artículo permanentemente.</p>
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Llenado de Formularios -->
                            <Card v-if="canEditInv"
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-purple-600 dark:text-purple-400">
                                        <i class="pi pi-box text-2xl"></i>
                                        <span class="text-xl">Formulario: Detalles del Artículo</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Para registrar un artículo nuevo o modificar uno existente, el sistema requerirá
                                        los siguientes campos:
                                    </p>
                                </template>
                                <template #content>
                                    <ul class="flex flex-col gap-4">
                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-tag text-primary"></i>
                                                <strong class="text-lg">Nombre del Artículo</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Debe ser claro y descriptivo. Ejemplo: <em>"Taladro Percutor"</em>,
                                                <em>"Cinta Aislante"</em> o <em>"Pinzas"</em>.
                                            </p>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-sitemap text-primary"></i>
                                                <strong class="text-lg">Tipo</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
                                                Clasifica visualmente el artículo. Selecciona una de las dos opciones:
                                            </p>
                                            <div class="flex flex-wrap gap-2 text-xs">
                                                <Tag value="HERRAMIENTA" severity="info" />
                                                <Tag value="CONSUMIBLE" severity="warn" />
                                            </div>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-sort-numeric-up-alt text-primary"></i>
                                                <strong class="text-lg">Cantidad Física (Existencia)</strong>
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Indica el número físico de unidades. El conteo mínimo permitido es "0".
                                                Puedes usar los botones internos para sumar o restar rápidamente
                                                cantidades.
                                            </p>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-check-square text-primary"></i>
                                                <strong class="text-lg">¿Está Activo?</strong>
                                            </div>
                                            <div
                                                class="mt-3 p-3 bg-surface-50 dark:bg-surface-800 rounded flex items-start gap-3">
                                                <Checkbox :modelValue="true" :binary="true" readonly class="mt-1" />
                                                <div class="text-sm">
                                                    <strong class="block text-surface-700 dark:text-surface-200">Estado
                                                        del artículo</strong>
                                                    <span class="text-surface-500">Normalmente debe ir seleccionado. Si
                                                        desmarcas esta opción el artículo dejará de aparecer globalmente
                                                        al confirmar y guardar la edición.</span>
                                                </div>
                                            </div>
                                        </li>
                                    </ul>
                                </template>
                            </Card>

                        </div>
                    </TabPanel>

                    <!-- Sección: Mantenimientos Preventivos -->
                    <TabPanel value="2" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                                        <i class="pi pi-info-circle text-2xl"></i>
                                        <span class="text-xl">¿Qué es e información general?</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed">
                                        El módulo de <strong>Mantenimientos Preventivos</strong> permite documentar y
                                        llevar el control de los servicios de soporte y reparación realizados a las
                                        máquinas en tu casino actual. Podrás ver el historial, qué técnico realizó el
                                        mantenimiento y cuál fue el estado en el que quedó la máquina.
                                    </p>
                                </template>
                            </Card>

                            <!-- Acciones (Lo que puede hacer el usuario) -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-green-600 dark:text-green-400">
                                        <i class="pi pi-cog text-2xl"></i>
                                        <span class="text-xl">Lo que puedes hacer</span>
                                    </div>
                                </template>
                                <template #content>
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-primary">
                                                <i class="pi pi-list mr-2"></i> Historial y Búsqueda
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Puedes visualizar
                                                todo el historial de los mantenimientos de tu casino. En la cabecera de
                                                la tabla encontrarás la opción de buscar filtros rápidos por máquina,
                                                técnico u observaciones.</p>
                                        </div>

                                        <div v-if="canCreateMant"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-blue-500">
                                                <i class="pi pi-plus mr-2"></i> Registrar Mantenimiento
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Si posees un
                                                perfil técnico o gerencial, puedes usar el botón
                                                <Tag value="Nuevo" severity="primary" class="mx-1 mt-1 text-xs" /> para
                                                guardar intervenciones que realizaste en las máquinas el día de hoy.
                                            </p>
                                        </div>

                                        <div v-if="canEditOrDeleteMant"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-orange-500">
                                                <i class="pi pi-pencil mr-2"></i> Editar Registro
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Los
                                                administradores y supervisores de sistemas pueden modificar
                                                mantenimientos incorrectos usando el botón verde <i
                                                    class="pi pi-pencil text-green-500"></i> correspondiente en la
                                                columna de Acciones.</p>
                                        </div>

                                        <div v-if="canEditOrDeleteMant"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-red-500">
                                                <i class="pi pi-trash mr-2"></i> Eliminar Registro
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Los roles
                                                autorizados pueden borrar por completo un registro usando el botón rojo
                                                <i class="pi pi-trash text-red-500"></i>. Una ventana de seguridad te
                                                pedirá que confirmes tu decisión antes de proceder.
                                            </p>
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Llenado de Formularios -->
                            <Card v-if="canCreateMant"
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-purple-600 dark:text-purple-400">
                                        <i class="pi pi-wrench text-2xl"></i>
                                        <span class="text-xl">Formulario: Detalles de Mantenimiento</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Esta es la ventana principal que se abre al crear o editar un mantenimiento.
                                        Sigue estas instrucciones:
                                    </p>
                                </template>
                                <template #content>
                                    <ul class="flex flex-col gap-4">
                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-th-large text-primary"></i>
                                                <strong class="text-lg">Máquina (UID o Serie)</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
                                                En este buscador, escribe parte del <strong>UID de sala</strong> o
                                                <strong>Número de Serie</strong> que buscas. El sistema auto-completará
                                                una lista basada únicamente en las máquinas de <strong>tu casino
                                                    asignado</strong>.
                                            </p>
                                            <div
                                                class="flex items-start gap-3 p-3 bg-yellow-50 dark:bg-yellow-900/40 rounded-lg border border-yellow-200 dark:border-yellow-700">
                                                <i class="pi pi-exclamation-triangle mt-1 text-yellow-500"></i>
                                                <span class="text-sm text-yellow-700 dark:text-yellow-200">
                                                    Una vez guardes un mantenimiento por primera vez, este campo quedará
                                                    <strong>bloqueado</strong> si intentas editarlo después. No podrás
                                                    cambiar de máquina.
                                                </span>
                                            </div>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-heart-fill text-primary"></i>
                                                <strong class="text-lg">Estado Resultante (Final)</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
                                                ¿Cómo dejaste la máquina tras tu intervención? Elige una opción:
                                            </p>
                                            <div class="flex flex-wrap gap-2 text-xs">
                                                <Tag value="Operativa" severity="success" />
                                                <Tag value="Dañada pero Operativa" severity="warn" />
                                                <Tag value="Dañada" severity="danger" />
                                                <Tag value="En Observación" severity="info" />
                                            </div>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-calendar text-primary"></i>
                                                <strong class="text-lg">Fecha de Mantenimiento</strong>
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Este campo está intencionalmente automatizado y bloqueado. Todo registro
                                                se guarda bajo la **fecha en la que el sistema captura la captura del
                                                evento** (Hoy).
                                            </p>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-align-left text-primary"></i>
                                                <strong class="text-lg">Observaciones Técnicas</strong>
                                                <Tag value="Opcional" severity="secondary" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Espacio libre (textarea) donde el técnico puede explayarse sobre qué
                                                refacciones utilizó, qué limpieza de hardware aplicó (botones,
                                                validadores) y si notó desgaste de piezas.
                                            </p>
                                        </li>
                                    </ul>
                                </template>
                            </Card>

                        </div>
                    </TabPanel>

                    <!-- Sección: Usuarios -->
                    <TabPanel value="3" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                                        <i class="pi pi-info-circle text-2xl"></i>
                                        <span class="text-xl">¿Qué es el módulo de Usuarios?</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed mb-4">
                                        Es la sección donde puedes administrar al personal o equipo de trabajo con
                                        acceso al sistema dentro de tu casino correspondiente.
                                        Podrás ver estadísticas rápidas del personal Activo e Inactivo.
                                    </p>
                                    <div v-if="!canManageUsers"
                                        class="p-4 bg-orange-50 dark:bg-orange-900/40 border border-orange-200 rounded-lg text-orange-800 dark:text-orange-200">
                                        <i class="pi pi-lock mr-2 text-orange-500"></i>
                                        <strong>Acceso Restringido:</strong> Tu rol actual ({{ usuario?.rol_nombre }})
                                        no cuenta con los permisos necesarios para realizar acciones en este módulo,
                                        solo los roles gerenciales y administrativos pueden hacerlo.
                                    </div>
                                </template>
                            </Card>

                            <!-- Acciones (Lo que puede hacer el usuario) -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-green-600 dark:text-green-400">
                                        <i class="pi pi-cog text-2xl"></i>
                                        <span class="text-xl">Opciones Disponibles</span>
                                    </div>
                                </template>
                                <template #content>
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-primary">
                                                <i class="pi pi-eye mr-2"></i> Ficha Completa
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Al dar clic sobre
                                                el <strong class="text-primary">Nombre</strong> de cualquier usuario en
                                                la tabla principal, se abrirá un modal panorámico con toda su
                                                información detallada de sistema, incluyendo su última IP registrada y
                                                su fecha de alta.</p>
                                        </div>

                                        <div v-if="canManageUsers"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-blue-500">
                                                <i class="pi pi-user-plus mr-2"></i> Registrar Empleado
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Permite dar de
                                                alta personal bajo el botón de
                                                <Tag value="Nuevo Usuario" severity="primary" class="mx-1 text-xs" />.
                                                <em>Nota: El sistema enviará automáticamente notificaciones a la
                                                    gerencia informando del registro.</em>
                                            </p>
                                        </div>

                                        <div v-if="canManageUsers"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-orange-500">
                                                <i class="pi pi-pencil mr-2"></i> Editar Datos
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Con el botón <i
                                                    class="pi pi-pencil text-cyan-500"></i> puedes corregir nombres,
                                                correos electrónicos o incluso cambiar o asignarles roles nuevos al
                                                personal de tu casino.</p>
                                        </div>

                                        <div v-if="canManageUsers"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-red-500">
                                                <i class="pi pi-power-off mr-2"></i> Suspender / Activar Acceso
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Para prevenir el
                                                robo de información, el personal que deje de laborar no se borra, se
                                                desactiva usando el botón <i class="pi pi-ban text-orange-400"></i>. Si
                                                regresan, puedes reactivarlos con <i
                                                    class="pi pi-check-circle text-green-500"></i>.</p>
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Llenado de Formularios -->
                            <Card v-if="canManageUsers"
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-purple-600 dark:text-purple-400">
                                        <i class="pi pi-id-card text-2xl"></i>
                                        <span class="text-xl">Formulario: Control de Acceso</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Existen campos obligatorios y reglas vitales a la hora de manipular la cuenta de
                                        un empleado:
                                    </p>
                                </template>
                                <template #content>
                                    <ul class="flex flex-col gap-4">
                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-user text-primary"></i>
                                                <strong class="text-lg">Información Personal Exigida</strong>
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
                                                Se exige capturar el <strong>Nombre Completo</strong> (Mínimo un
                                                apellido) y contar con un <strong>Email de contacto válido</strong>. El
                                                <em>Casino de asignación</em> no puede elegirse, siempre se limitará y
                                                bloqueará automáticamente al casino donde el administrador actual está
                                                ubicado.
                                            </p>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-key text-primary"></i>
                                                <strong class="text-lg">Credenciales (Logins)</strong>
                                                <Tag value="Cuidado" severity="warn" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
                                                El campo <strong>Usuario</strong>, usualmente un apodo, iniciales o
                                                matrícula, es único en todo el servidor, no puede repetirse. La
                                                <strong>Contraseña</strong> tiene una regla especial:
                                            </p>
                                            <ul class="list-disc ml-5 text-sm text-surface-600 dark:text-surface-400">
                                                <li><strong class="text-primary">Al Crear Nuevo:</strong> Es
                                                    Obligatoria.</li>
                                                <li><strong class="text-primary">Al Editar un Usuario:</strong> Solo
                                                    debes escribir algo aquí si vas a reiniciar (resetear) su
                                                    contraseña. Si dejas el campo vacío, conservará su clave vieja con
                                                    éxito.</li>
                                            </ul>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-star text-primary"></i>
                                                <strong class="text-lg">Roles (Jerarquías)</strong>
                                                <Tag value="Lógica Dinámica" severity="info" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
                                                Por seguridad operacional, la lista de perfiles disponibles en el
                                                selector varía según quién realiza el registro:
                                            </p>
                                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                                                <div
                                                    class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
                                                    <strong class="block text-red-700 dark:text-red-300 mb-1 text-sm">Si
                                                        eres ADMINISTRADOR o DB ADMIN</strong>
                                                    <span class="text-xs text-red-600 dark:text-red-400">Puedes asignar
                                                        prácticamente cualquier cargo a excepción de crear nuevos
                                                        administradores globales.</span>
                                                </div>
                                                <div
                                                    class="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded">
                                                    <strong
                                                        class="block text-blue-700 dark:text-blue-300 mb-1 text-sm">Si
                                                        eres GERENCIA o SUP SISTEMAS</strong>
                                                    <span class="text-xs text-blue-600 dark:text-blue-400">Solo se te
                                                        mostrarán opciones subordinadas menores para elegir:
                                                        <em>Técnicos</em> o <em>Supervisores Sala</em>.</span>
                                                </div>
                                            </div>
                                        </li>
                                    </ul>
                                </template>
                            </Card>

                        </div>
                    </TabPanel>

                    <!-- Sección: Proveedores -->
                    <TabPanel value="4" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                                        <i class="pi pi-info-circle text-2xl"></i>
                                        <span class="text-xl">¿Qué es el Catálogo de Proveedores?</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed mb-4">
                                        Este módulo permite registrar a las empresas (o fabricantes) externos que
                                        suministran diferentes Modelos de Máquinas tragamonedas a tu casino. <br />
                                        También guarda sus datos de acceso para que el proveedor pueda entrar a la App
                                        Mando Central en el futuro, así como sus teléfonos y correos para pedirles
                                        soporte técnico.
                                    </p>
                                    <div v-if="!canManageSuppliers"
                                        class="p-4 bg-orange-50 dark:bg-orange-900/40 border border-orange-200 rounded-lg text-orange-800 dark:text-orange-200">
                                        <i class="pi pi-lock mr-2 text-orange-500"></i>
                                        <strong>Módulo Protegido:</strong> Tu rol ({{ usuario?.rol_nombre }}) clasifica
                                        como perfil sin privilegios de Administración de Proveedores.
                                    </div>
                                </template>
                            </Card>

                            <!-- Acciones -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-green-600 dark:text-green-400">
                                        <i class="pi pi-cog text-2xl"></i>
                                        <span class="text-xl">Herramientas Operativas</span>
                                    </div>
                                </template>
                                <template #content>
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-primary">
                                                <i class="pi pi-id-card mr-2"></i> Tarjeta Detallada
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Pulsa el nombre
                                                del proveedor en color azul para abrir su Tarjeta Detallada. Podrás ver
                                                cuántos modelos de máquina te han suministrado en total y sus datos
                                                fiscales.</p>
                                        </div>

                                        <div v-if="canViewSupplierCreds"
                                            class="p-4 border-2 border-orange-300 dark:border-orange-800 rounded-xl bg-orange-50 dark:bg-orange-950 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-orange-600">
                                                <i class="pi pi-eye mr-2"></i> Revelar Credenciales (Confidencial)
                                            </h3>
                                            <p class="text-sm text-surface-800 dark:text-surface-300">Si eres de
                                                Sistemas o Administración, dentro de la Tarjeta Detallada aparecerá un
                                                panel secreto de <em>Credenciales de Acceso</em>. Haciendo uso del botón
                                                <i class="pi pi-eye mx-1 text-surface-500"></i>, podrás desempaquetar la
                                                contraseña real con la cual tu proveedor ingresa a sus reportes
                                                externos.
                                            </p>
                                        </div>

                                        <div v-if="canManageSuppliers"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-blue-500">
                                                <i class="pi pi-building text-sm mr-2"></i> Alta de Fabricantes
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Permite dar de
                                                alta la relación con una nueva marca bajo el botón
                                                <Tag value="Nuevo Proveedor" severity="primary" class="mx-1 text-xs" />.
                                            </p>
                                        </div>

                                        <div v-if="canManageSuppliers"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-orange-500">
                                                <i class="pi pi-pencil mr-2"></i> Actualizar Listines
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">En todo momento
                                                puedes actualizar los números de contacto o la razón social empleando el
                                                ícono <i class="pi pi-pencil text-cyan-500"></i>.</p>
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Llenado de Formularios -->
                            <Card v-if="canManageSuppliers"
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-purple-600 dark:text-purple-400">
                                        <i class="pi pi-file-edit text-2xl"></i>
                                        <span class="text-xl">Formulario: Datos Fiscales y Soporte</span>
                                    </div>
                                </template>
                                <template #content>
                                    <ul class="flex flex-col gap-4">
                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-building text-primary"></i>
                                                <strong class="text-lg">Información Corporativa y Accesos
                                                    Externos</strong>
                                                <Tag value="Exigido" severity="danger" class="text-xs" />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
                                                La plataforma es estricta con la base de datos de corporativos,
                                                obligándote a cumplir con:
                                            </p>
                                            <ul
                                                class="list-disc ml-5 text-sm font-medium text-surface-700 dark:text-surface-300">
                                                <li class="mb-1">Razón Social y Registro Federal Comercial (RFC -
                                                    <em>Limitado automáticamente a 13 caracteres</em>).
                                                </li>
                                                <li class="mb-1">El Email Corporativo principal de la empresa.</li>
                                                <li class="mb-1">Un <strong>Usuario</strong> y
                                                    <strong>Contraseña</strong> web para que el proveedor en el futuro
                                                    pueda entrar con éxito en portales vinculados al casino.
                                                </li>
                                            </ul>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-headphones text-teal-500"></i>
                                                <strong class="text-lg">Canales de Soporte Técnico</strong>
                                                <Tag value="Opcional" severity="secondary" class="text-xs" />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400 mb-1">
                                                Si el proveedor te asignó a ti o a tu sala un experto en especial,
                                                puedes capturar su <strong>Teléfono</strong>, su <strong>Email Personal
                                                    o Departamental</strong> y su propio <strong>Nombre (Contacto
                                                    Técnico)</strong>. Esta información no bloqueará el formulario si se
                                                ignora al guardar.
                                            </p>
                                        </li>
                                    </ul>
                                </template>
                            </Card>

                        </div>
                    </TabPanel>

                    <!-- Sección: Modelos de Máquinas -->
                    <TabPanel value="5" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                                        <i class="pi pi-info-circle text-2xl"></i>
                                        <span class="text-xl">Módulo de Modelos de Máquinas</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed mb-4">
                                        Este módulo gestiona la información comercial e identidad técnica de todos los
                                        gabinetes / modelos de máquinas que operan dentro del Casino. Es vital
                                        completarlo antes de armar el inventario de la sala, ya que toda máquina nueva
                                        necesita primero pertenecer a un <strong>Modelo Base</strong> y estar ligada a
                                        un <strong>Proveedor</strong> ya existente.
                                    </p>
                                    <div v-if="!canManageModels"
                                        class="p-4 bg-orange-50 dark:bg-orange-900/40 border border-orange-200 rounded-lg text-orange-800 dark:text-orange-200">
                                        <i class="pi pi-lock mr-2 text-orange-500"></i>
                                        <strong>Acceso Restringido:</strong> Solo Supervisores de Sala, Soporte u
                                        Administradores pueden gestionar el catálogo de Modelos de su casino.
                                    </div>
                                </template>
                            </Card>

                            <!-- Acciones (Lo que puede hacer el usuario) -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-green-600 dark:text-green-400">
                                        <i class="pi pi-cog text-2xl"></i>
                                        <span class="text-xl">Comandos del Módulo</span>
                                    </div>
                                </template>
                                <template #content>
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-primary">
                                                <i class="pi pi-box mr-2"></i> Detalles Específicos
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Al dar clic sobre
                                                el <strong class="text-primary">Nombre del Modelo</strong> en color
                                                azul, podrás desplegar un panel con la cantidad exacta de máquinas
                                                activas vinculadas a este equipo específico bajo la marca seleccionada.
                                            </p>
                                        </div>

                                        <div v-if="canManageModels"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-blue-500">
                                                <i class="pi pi-plus mr-2"></i> Nuevo Modelo
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Puedes vincular
                                                una nueva marca al catálogo utilizando
                                                <Tag value="Nuevo Modelo" severity="primary" class="mx-1 text-xs" />.
                                            </p>
                                        </div>

                                        <div v-if="canManageModels"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-orange-500">
                                                <i class="pi pi-pencil mr-2"></i> Editar Atributos
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Con el botón <i
                                                    class="pi pi-pencil text-cyan-500"></i> podrás corregir un error de
                                                dedo en el nombre del modelo o actualizar la descripción técnica si algo
                                                cambió.</p>
                                        </div>

                                        <div v-if="canDeactivateModels"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-red-500">
                                                <i class="pi pi-ban mr-2"></i> Suspender
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Si por problemas
                                                de licencias de proveedor, la gerencia exige inhabilitar ese modelo, el
                                                nivel de jerarquía (Administrativa o Sistemas) permite desactivar dicho
                                                modelo utilizando el comando <i class="pi pi-ban text-orange-400"></i>.
                                            </p>
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Llenado de Formularios -->
                            <Card v-if="canManageModels"
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-purple-600 dark:text-purple-400">
                                        <i class="pi pi-file-edit text-2xl"></i>
                                        <span class="text-xl">Formulario: Alta de Modelos</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Pasos requeridos antes de que puedas añadir máquinas al inventario de red.
                                    </p>
                                </template>
                                <template #content>
                                    <ul class="flex flex-col gap-4">
                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-briefcase text-primary"></i>
                                                <strong class="text-lg text-primary">Paso 1: Selector de
                                                    Proveedor</strong>
                                                <Tag value="Dependencia" severity="info" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
                                                Todo modelo de máquina necesita forzosamente un fabricante. Si el
                                                proveedor no aparece en la lista desplegable, debes ir antes al módulo
                                                <span class="font-bold text-orange-500"><i
                                                        class="pi pi-briefcase mx-1"></i> Catálogo de Proveedores</span>
                                                para registrarlo en el sistema.
                                            </p>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-tags text-primary"></i>
                                                <strong class="text-lg">Clasificación Principal</strong>
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
                                                Aquí se exige anotar tanto el <strong>Nombre del Modelo</strong> (ej.
                                                <em>Bally Alpha 2 Pro Curve</em>) como la <strong>Marca /
                                                    Producto</strong> (ej. <em>Quick Hit</em> o el juego principal que
                                                la corona).
                                            </p>
                                        </li>

                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-align-left text-primary"></i>
                                                <strong class="text-lg">Descripción Técnica</strong>
                                                <Tag value="Opcional" severity="secondary" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
                                                Es un campo de varias líneas ideal para dejar notas al personal de
                                                mantenimiento. Podrías informar aquí sobre "Compatibilidad con
                                                ticketadoras de marca X" o "Fuente de energía con regulador especial".
                                            </p>
                                        </li>
                                    </ul>
                                </template>
                            </Card>

                        </div>
                    </TabPanel>

                    <!-- Sección: Máquinas -->
                    <TabPanel value="6" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                                        <i class="pi pi-info-circle text-2xl"></i>
                                        <span class="text-xl">Inventario de Máquinas</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed mb-4">
                                        Esta es el área principal operativa de la sala. Aquí se concentra todo el
                                        inventario de las máquinas en piso. El módulo permite consultar la ficha
                                        individual de cada equipo (incluyendo contadores de fallas e historial técnico),
                                        así como realizar el Alta (si eres Administrador / Soporte) ubicando la máquina
                                        físicamente en sus respectivas coordenadas.
                                    </p>
                                    <div v-if="!canManageMachines"
                                        class="p-4 bg-orange-50 dark:bg-orange-900/40 border border-orange-200 rounded-lg text-orange-800 dark:text-orange-200">
                                        <i class="pi pi-lock mr-2 text-orange-500"></i>
                                        <strong>Acceso Restricto:</strong> Tu perfil ({{ usuario?.rol_nombre }}) te
                                        permite consultar la tabla y visualizar el estado de las máquinas, pero la
                                        facultad de registrar nuevos equipos, modificar sus coordenadas o editar
                                        atributos está reservada estrictamente a la Gerencia de Soporte de Sistemas y
                                        Administración.
                                    </div>
                                </template>
                            </Card>

                            <!-- Acciones (Lo que puede hacer el usuario) -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-green-600 dark:text-green-400">
                                        <i class="pi pi-cog text-2xl"></i>
                                        <span class="text-xl">Comandos del Módulo</span>
                                    </div>
                                </template>
                                <template #content>
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-primary">
                                                <i class="pi pi-file-o mr-2"></i> Ficha Técnica Completa
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Pulsar sobre el
                                                <strong class="text-primary">UID de Sala</strong> (Ej. A01) abre una
                                                pantalla panorámica. Aquí no solo verás qué juego tiene, número de serie
                                                o IP, sino también una línea de tiempo dinámica <strong
                                                    class="text-blue-600">Historial de Intervenciones</strong> que
                                                desglosa todas las reparaciones históricas que ha tenido el equipo.
                                            </p>
                                        </div>

                                        <div
                                            class="p-4 border-2 border-red-300 dark:border-red-800 rounded-xl bg-red-50 dark:bg-red-950 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-red-600">
                                                <i class="pi pi-exclamation-circle mr-2"></i> Levantar Incidencia (Botón
                                                Rápido)
                                            </h3>
                                            <p class="text-sm text-surface-800 dark:text-surface-300">Dentro de la Ficha
                                                Técnica, abajo del todo se encuentra un botón rojo <strong>Pánico /
                                                    Incidencia</strong>. Al presionarlo, el sistema emitirá
                                                automáticamente un reporte rápido al área de Infraestructura notificando
                                                que esa máquina requiere auxilio urgente, auto-incrementando su
                                                <Tag value="Contador de Fallas" severity="warn" class="text-[10px]" />.
                                            </p>
                                        </div>

                                        <div v-if="canViewMachineCharts"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-yellow-500">
                                                <i class="pi pi-chart-pie mr-2"></i> Analíticas de Daño
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Para roles
                                                operativos superiores, la página arranca mostrando tarjetas rápidas
                                                inteligentes indicando qué porcentaje de esa sala se encuentra
                                                inoperativa o con defectos graves.</p>
                                        </div>

                                        <div v-if="canManageMachines"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-orange-500">
                                                <i class="pi pi-map mr-2"></i> Operaciones en Piso (Alta y Edición)
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Si un equipo
                                                cambia de lugar en el casino o llega de fábrica, con los botones <i
                                                    class="pi pi-plus rounded bg-primary text-white p-1 pb-[2px] text-xs"></i>
                                                o <i class="pi pi-pencil text-cyan-500"></i> podrás establecer su zona,
                                                sala, y posicionamiento en ejes <strong>X, Y</strong> dentro del mapa
                                                arquitectónico.</p>
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Llenado de Alta -->
                            <Card v-if="canManageMachines"
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-purple-600 dark:text-purple-400">
                                        <i class="pi pi-file-edit text-2xl"></i>
                                        <span class="text-xl">Formulario: Alta de Equipos</span>
                                    </div>
                                </template>
                                <template #content>
                                    <ul class="flex flex-col gap-4">
                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-sitemap text-primary"></i>
                                                <strong class="text-lg">Dependencias (Selectores Bloqueados)</strong>
                                                <Tag value="Exigido" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Al crear una máquina, <strong>Casino</strong> figurará bloqueado (por
                                                seguridad a tu centro actual). El <strong>Modelo</strong> es vital; el
                                                sistema solo te presentará modelos de máquina que le pertenezcan al
                                                sistema (que se hayan capturado en el módulo anterior).
                                            </p>
                                        </li>
                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-id-card text-primary"></i>
                                                <strong class="text-lg">Identificadores Físicos</strong>
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                El <strong>UID Sala</strong> es el nombre corto con el que el staff
                                                identifica la máquina en piso (ej. M14, AB02). El <strong>No. de
                                                    Serie</strong> es el identificador legal del chasis en aduana.
                                                <strong>Ambos son completamente obligatorios.</strong>
                                            </p>
                                        </li>
                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-compass text-primary"></i>
                                                <strong class="text-lg">Geolocalización In-House</strong>
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Deberás obligar a seleccionar a qué Piso/Área y Sala van ubicadas.
                                                Además, las <strong>Coordenadas X y Y</strong> no pueden estar vacías
                                                (requieren al menos estar en 0). Esto es para que en futuras versiones,
                                                la App Mobile pueda trazar la ruta de reparación en un mapa del local.
                                            </p>
                                        </li>
                                        <li
                                            class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-wrench text-primary"></i>
                                                <strong class="text-lg">Detalles Técnicos (Dinámicos)</strong>
                                                <Tag value="Opcional" severity="secondary" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Estos datos (Denominaciones de la máquina, Estado de la Operatividad
                                                Base y Calendarios de mantenimiento) pueden alterarse en cualquier
                                                momento y no rompen el sistema si no se ingresan, aunque se recomiendo
                                                fuertemente indicar el estado operativo.
                                            </p>
                                        </li>
                                    </ul>
                                </template>
                            </Card>

                        </div>
                    </TabPanel>

                    <!-- Sección: Mapa de Sala -->
                    <TabPanel value="7" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-teal-600 dark:text-teal-400">
                                        <i class="pi pi-map text-3xl"></i>
                                        <span class="text-2xl font-bold">Mapa de Sala Interactivo</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Una herramienta de vanguardia que digitaliza el layout de tu casino en tiempo
                                        real.
                                    </p>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed mb-4">
                                        El módulo <strong class="text-teal-600 dark:text-teal-400">Mapa de Sala (Layout
                                            In-House)</strong> es posiblemente la pantalla operativa más avanzada de
                                        NEXUS. Transforma la cuadrícula de datos tradicional en una vista aérea
                                        arquitectónica donde cada slot es un bloque inteligente. Permite desde ubicar
                                        rápidamente máquinas apagadas, agrupar las islas por distribuidor, o incluso
                                        rediseñar la sala usando <em>Arrastrar y Soltar</em>.
                                    </p>
                                    <div class="flex flex-wrap gap-2 mt-2">
                                        <Tag value="Visualización Táctica" severity="info" rounded />
                                        <Tag value="Planimetría Vectorial PDF" severity="danger" rounded />
                                        <Tag value="ColorPicker Dinámico" severity="success" rounded />
                                        <Tag v-if="canEditMap" value="Drag & Drop Activo" severity="warn" rounded />
                                    </div>
                                </template>
                            </Card>

                            <!-- Inteligencia Visual (Capas) -->
                            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                    <template #title>
                                        <div class="flex items-center gap-2 text-primary">
                                            <i class="pi pi-palette text-xl"></i>
                                            <span class="text-lg">Inteligencia Visual (Modos)</span>
                                        </div>
                                    </template>
                                    <template #content>
                                        <p class="text-sm text-surface-600 dark:text-surface-400 mb-4">
                                            El mapa cuenta con 3 lentes o "Capas" para diagnosticar la sala de
                                            inmediato:
                                        </p>
                                        <ul class="flex flex-col gap-3">
                                            <li class="flex gap-3">
                                                <div
                                                    class="flex items-center justify-center bg-blue-100 dark:bg-blue-900 rounded shrink-0 h-8 w-8">
                                                    <i class="pi pi-circle-fill text-blue-500"></i>
                                                </div>
                                                <div>
                                                    <strong class="text-surface-900 dark:text-surface-0">Por Estado
                                                        Técnico:</strong>
                                                    <p class="text-xs text-surface-500 mt-1">Colorea el mapa tipo
                                                        semáforo. Verde (Operativa), Rojo (Dañada), Amarillo (Mantto).
                                                    </p>
                                                </div>
                                            </li>
                                            <li class="flex gap-3">
                                                <div
                                                    class="flex items-center justify-center bg-orange-100 dark:bg-orange-900 rounded shrink-0 h-8 w-8">
                                                    <i class="pi pi-users text-orange-500"></i>
                                                </div>
                                                <div>
                                                    <strong class="text-surface-900 dark:text-surface-0">Por
                                                        Proveedor:</strong>
                                                    <p class="text-xs text-surface-500 mt-1">Genera colores aleatorios
                                                        para saber cuánto territorio abarca Aristocrat, Merkur o IGT.
                                                        <em class="text-teal-500">Puedes cambiar el color al vuelo dando
                                                            clic al cuadro de la leyenda.</em>
                                                    </p>
                                                </div>
                                            </li>
                                            <li class="flex gap-3">
                                                <div
                                                    class="flex items-center justify-center bg-indigo-100 dark:bg-indigo-900 rounded shrink-0 h-8 w-8">
                                                    <i class="pi pi-desktop text-indigo-500"></i>
                                                </div>
                                                <div>
                                                    <strong class="text-surface-900 dark:text-surface-0">Por
                                                        Modelo:</strong>
                                                    <p class="text-xs text-surface-500 mt-1">Distingue entre gabinetes
                                                        Slant Top, Upright o VIP. También personalizables.</p>
                                                </div>
                                            </li>
                                        </ul>
                                    </template>
                                </Card>

                                <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                    <template #title>
                                        <div class="flex items-center gap-2 text-cyan-600 dark:text-cyan-400">
                                            <i class="pi pi-filter text-xl"></i>
                                            <span class="text-lg">Herramientas de Exploración</span>
                                        </div>
                                    </template>
                                    <template #content>
                                        <div class="flex flex-col gap-4">
                                            <div
                                                class="p-3 bg-surface-50 dark:bg-surface-800 rounded-lg border border-surface-200 dark:border-surface-700">
                                                <h4 class="font-bold text-sm mb-1"><i
                                                        class="pi pi-search text-surface-400 mr-1"></i> Buscador
                                                    Spot-Light</h4>
                                                <p class="text-xs text-surface-600 dark:text-surface-400">Al escribir un
                                                    UID de máquina (ej. B04) o Juego en la barra superior, el mapa se
                                                    apaga (Gris) y "Enciende" de color Azul Intenso únicamente lo que
                                                    coincide. Perfecto para localizar equipos perdidos en el piso.</p>
                                            </div>

                                            <div
                                                class="p-3 bg-red-50 dark:bg-red-900/30 rounded-lg border border-red-200 dark:border-red-900">
                                                <div class="flex items-center justify-between mb-1">
                                                    <h4 class="font-bold text-sm text-red-700 dark:text-red-400"><i
                                                            class="pi pi-file-pdf mr-1"></i> Renderizado a PDF
                                                        (Planimetría)</h4>
                                                    <Tag value="Cálculo Matemático" severity="danger"
                                                        class="text-[10px]"></Tag>
                                                </div>
                                                <p class="text-xs text-red-600 dark:text-red-300">
                                                    El botón <strong
                                                        class="px-1 border border-red-300 rounded bg-white dark:bg-red-950">PDF</strong>
                                                    genera remotamente un Archivo A3 Horizontal. No es un pantallazo: es
                                                    un renderizado vectorial que calcula cuadrículas vacías, respeta los
                                                    colores elegidos en leyenda, e imprime el folio con sello de agua.
                                                </p>
                                            </div>
                                        </div>
                                    </template>
                                </Card>
                            </div>

                            <!-- MODO ARQUITECTO (Arrastrar y Soltar) -->
                            <Card
                                class="border-2 border-amber-200 dark:border-amber-800 bg-gradient-to-br from-amber-50 to-white dark:from-amber-950 dark:to-surface-900 shadow-sm overflow-hidden relative">
                                <template #title>
                                    <div class="flex items-center gap-3">
                                        <div
                                            class="flex items-center justify-center w-10 h-10 rounded-full bg-amber-500 text-white shadow-md">
                                            <i class="pi pi-arrows-alt text-xl"></i>
                                        </div>
                                        <div>
                                            <h3 class="text-xl font-bold text-amber-700 dark:text-amber-400">Modo
                                                Edición / Remodelación</h3>
                                            <p class="text-xs font-normal text-amber-600 dark:text-amber-500 mt-1">
                                                Manipulación arquitectónica en tiempo real de la sala.</p>
                                        </div>
                                    </div>
                                </template>
                                <template #content>
                                    <div v-if="!canEditMap"
                                        class="p-4 bg-white/60 dark:bg-surface-900/60 rounded-lg border border-amber-200 dark:border-amber-800 backdrop-blur-sm relative z-10 flex items-start gap-4 mb-4">
                                        <i class="pi pi-lock text-2xl text-amber-500 mt-1"></i>
                                        <div>
                                            <h4 class="font-bold text-surface-900 dark:text-surface-0">Función
                                                Restringida</h4>
                                            <p class="text-sm text-surface-600 dark:text-surface-400 mt-1">Modificar la
                                                cuadrícula física arrastrando elementos requiere un perfil de
                                                <strong>Gerencia</strong> o <strong>Soporte de Sistemas</strong>. Tu
                                                perfil no cumple este rol, por lo que el "Switch / Candado" no te será
                                                visible y solo puedes navegar visualmente por el mapa interactivo.
                                            </p>
                                        </div>
                                    </div>

                                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 relative z-10">
                                        <div
                                            class="col-span-1 border-r border-amber-200/50 dark:border-amber-800/50 pr-4">
                                            <ol
                                                class="flex flex-col gap-3 text-sm text-amber-800 dark:text-amber-200/80">
                                                <li class="flex items-center gap-2">
                                                    <span class="font-black">1.</span> Activa el switch
                                                    <Tag value="Edición" severity="warn" icon="pi pi-lock-open"
                                                        class="text-[10px]" /> arriba.
                                                </li>
                                                <li class="flex items-center gap-2">
                                                    <span class="font-black">2.</span> El cursor cambiará a una mano
                                                    ('Grab').
                                                </li>
                                                <li class="flex items-center gap-2">
                                                    <span class="font-black">3.</span> Haz clic sostenido en un cuadro
                                                    de máquina.
                                                </li>
                                                <li class="flex items-center gap-2">
                                                    <span class="font-black">4.</span> Suéltalo en una celda vacía de la
                                                    cuadrícula.
                                                </li>
                                            </ol>
                                        </div>
                                        <div class="col-span-2 text-sm text-surface-700 dark:text-surface-300 pl-2">
                                            <strong
                                                class="block text-amber-700 dark:text-amber-400 mb-2">Consideraciones
                                                Físicas de Seguridad</strong>
                                            Al soltar la máquina en nuevas coordenadas, el sistema alertará: <em
                                                class="text-red-500 font-semibold px-1">"¿Mover máquina X a posición
                                                (10, 5)?"</em>. Si autorizas, las coordenadas se ligan y guardan solas
                                            en base de datos.
                                            <br><br>
                                            <i class="pi pi-shield text-amber-500 mr-1"></i>
                                            <strong>Anti-Colisión:</strong> El sistema detectará si arrastras el equipo
                                            a una loseta donde ya hay otro asignado, lanzando una advertencia crítica
                                            para evitar empalmes.
                                        </div>
                                    </div>

                                    <!-- Decorative watermark -->
                                    <i
                                        class="pi pi-expand absolute -bottom-10 -right-4 text-[12rem] opacity-[0.03] rotate-12 text-black dark:text-white pointer-events-none"></i>
                                </template>
                            </Card>

                        </div>
                    </TabPanel>

                    <!-- Sección: Tickets / Mesa de Ayuda -->
                    <TabPanel value="8" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-red-600 dark:text-red-400">
                                        <i class="pi pi-ticket text-3xl"></i>
                                        <span class="text-2xl font-bold">Mesa de Ayuda (Tickets)</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Sistema de seguimiento de incidencias, bitácoras técnicas y ciclo de vida de
                                        fallas.
                                    </p>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed mb-4">
                                        El módulo de <strong>Tickets</strong> es el corazón operativo del equipo
                                        técnico. Aquí se registran todas las fallas reportadas por el personal de sala,
                                        se asignan a los técnicos correspondientes, y se lleva una <strong>Bitácora de
                                            Intervenciones</strong> inmutable hasta la resolución del problema.
                                    </p>
                                    <div class="flex flex-wrap gap-2 mt-2">
                                        <Tag value="SLA Automático" severity="info" rounded />
                                        <Tag value="Bitácora Inmutable" severity="success" rounded />
                                        <Tag value="Cierre Estricto" severity="danger" rounded />
                                    </div>

                                    <div v-if="isEncargadoTickets"
                                        class="mt-4 p-3 bg-blue-50 dark:bg-blue-900 border-l-4 border-blue-500 rounded text-blue-900 dark:text-blue-100 text-sm">
                                        <i class="pi pi-info-circle mr-1"></i> Por tu perfil de <strong>Encargado de
                                            Área</strong>, esta vista está filtrada para mostrar <strong>únicamente los
                                            tickets que tú has reportado</strong>.
                                    </div>
                                </template>
                            </Card>

                            <!-- Componentes Principales -->
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                    <template #title>
                                        <div class="flex items-center gap-2 text-indigo-600 dark:text-indigo-400">
                                            <i class="pi pi-list text-xl"></i>
                                            <span class="text-lg">Dashboard y Listado</span>
                                        </div>
                                    </template>
                                    <template #content>
                                        <ul class="flex flex-col gap-3 text-sm text-surface-700 dark:text-surface-300">
                                            <li>
                                                <i class="pi pi-chart-bar text-indigo-500 mr-2"></i>
                                                <strong>KPIs Superiores:</strong> Tres métricas vitales: Tickets Totales
                                                Abiertos, Tickets Críticos y Tickets Sin Técnico Asignado.
                                            </li>
                                            <li>
                                                <i class="pi pi-clock text-indigo-500 mr-2"></i>
                                                <strong>Semáforo de Antigüedad (SLA):</strong> Calcula los días abierto.
                                                <span class="text-green-600 font-bold ml-1">0-3d Reciente</span>,
                                                <span class="text-orange-500 font-bold ml-1">4-8d Atención</span>,
                                                <span class="text-red-500 font-bold ml-1">9-15d Crítico</span>.
                                            </li>
                                            <li>
                                                <i class="pi pi-plus text-indigo-500 mr-2"></i>
                                                <strong>Creación:</strong> Al levantar un ticket, el sistema
                                                automáticamente <em>aumenta el contador de fallas</em> de la máquina
                                                seleccionada.
                                            </li>
                                        </ul>
                                    </template>
                                </Card>

                                <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                    <template #title>
                                        <div class="flex items-center gap-2 text-green-600 dark:text-green-400">
                                            <i class="pi pi-wrench text-xl"></i>
                                            <span class="text-lg">Bitácora Técnica</span>
                                        </div>
                                    </template>
                                    <template #content>
                                        <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
                                            Dando clic sobre el Folio de un ticket, se despliega la <strong>Ficha
                                                Completa</strong>.
                                        </p>
                                        <p class="text-sm text-surface-700 dark:text-surface-300 mb-3">
                                            La bitácora es una línea de tiempo donde los técnicos agregan sus
                                            "Intervenciones".
                                            <span v-if="!canAddBitacora"
                                                class="text-red-500 font-semibold block mt-1"><i class="pi pi-ban"></i>
                                                Tu perfil no tiene permisos para redactar entradas de bitácora
                                                técnica.</span>
                                        </p>
                                        <div v-if="canAddBitacora"
                                            class="p-3 bg-surface-100 dark:bg-surface-800 rounded border border-surface-200 dark:border-surface-700">
                                            <h4 class="font-bold text-sm mb-2">Formulario de Intervención:</h4>
                                            <ul
                                                class="text-xs text-surface-600 dark:text-surface-400 pl-4 list-disc space-y-1">
                                                <li><strong>Tipo:</strong> Diagnóstico, Reparación, Ajuste...</li>
                                                <li><strong>Descripción:</strong> Relato detallado del trabajo
                                                    realizado.</li>
                                                <li><strong>Resultado:</strong> Reparación Exitosa, Parcial, Fallida...
                                                </li>
                                                <li><strong>Estado Máquina Resultante:</strong> ¿Cómo quedó la máquina
                                                    tras la revisión?</li>
                                            </ul>
                                        </div>
                                    </template>
                                </Card>
                            </div>

                            <!-- Bloque: Reglas de Cierre -->
                            <Card
                                class="border-2 border-red-200 dark:border-red-900 bg-red-50/50 dark:bg-red-900/10 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-red-700 dark:text-red-400">
                                        <i class="pi pi-lock text-xl"></i>
                                        <span class="text-lg">Reglas Estrictas de Cierre</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-sm text-surface-700 dark:text-surface-300 mb-4">
                                        Un ticket no se puede cerrar simplemente haciendo clic en un botón. NEXUS
                                        implementa una validación lógica para prevenir cierres accidentales o
                                        incompletos.
                                    </p>
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div
                                            class="p-3 bg-white dark:bg-surface-800 rounded border border-red-200 dark:border-red-800">
                                            <span class="block font-bold text-red-600 dark:text-red-400 mb-2"><i
                                                    class="pi pi-times-circle"></i> Bloqueo de Cierre</span>
                                            <p class="text-xs text-surface-600 dark:text-surface-400">
                                                Si al marcar la casilla <strong>"¿Esta intervención cierra el
                                                    ticket?"</strong> no se cumplen las condiciones de éxito, el sistema
                                                bloqueará el guardado. Es decir, un ticket no se puede cerrar si el
                                                informe técnico dice "Prueba Fallida" o si la máquina queda como
                                                "Dañada".
                                            </p>
                                        </div>
                                        <div
                                            class="p-3 bg-white dark:bg-surface-800 rounded border border-green-200 dark:border-green-800">
                                            <span class="block font-bold text-green-600 dark:text-green-400 mb-2"><i
                                                    class="pi pi-check-circle"></i> Condiciones para Cerrar</span>
                                            <ul class="text-xs text-surface-600 dark:text-surface-400 space-y-2">
                                                <li><i class="pi pi-check text-green-500"></i> Resultado Intervención:
                                                    <strong>Exitosa</strong>.
                                                </li>
                                                <li><i class="pi pi-check text-green-500"></i> Estado Máquina
                                                    Resultante: <strong>Operativa</strong>.</li>
                                                <li><i class="pi pi-check text-green-500"></i> Llenar obligatoriamente
                                                    la <strong>"Explicación del Cierre"</strong>.</li>
                                            </ul>
                                        </div>
                                    </div>
                                    <div class="mt-4 text-xs font-semibold text-red-800 dark:text-red-300 text-center">
                                        Una vez cerrado el ticket (Candado apareciendo en pantalla), la bitácora queda
                                        petrificada visualmente y NO se aceptan intervenciones adicionales.
                                    </div>
                                </template>
                            </Card>

                        </div>
                    </TabPanel>

                    <!-- Sección: Auditorías Externas -->
                    <TabPanel value="9" class="p-6">
                        <div class="flex flex-col gap-6">
                            <!-- Introducción -->
                            <Card
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-purple-600 dark:text-purple-400">
                                        <i class="pi pi-id-card text-3xl"></i>
                                        <span class="text-2xl font-bold">Auditorías Externas (Visitas Técnicas)</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Control de acceso y registro de actividades para proveedores externos en las
                                        instalaciones.
                                    </p>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed mb-4">
                                        El módulo de <strong>Auditorías Externas</strong> sirve como una bitácora de
                                        seguridad y control operativo. Registra la entrada, permanencia y salida de
                                        cualquier técnico externo (proveedores de internet, mantenimiento de clima,
                                        técnicos de máquinas, etc.) que ingrese a las instalaciones del casino.
                                    </p>
                                    <div class="flex flex-wrap gap-2 mt-2">
                                        <Tag value="Control de Acceso Seguro" severity="info" rounded />
                                        <Tag value="Cronometría de Visita" severity="warn" rounded />
                                        <Tag value="Registro de Áreas Sensibles" severity="danger" rounded />
                                    </div>
                                </template>
                            </Card>

                            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <!-- Funcionamiento -->
                                <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                    <template #title>
                                        <div class="flex items-center gap-2 text-primary">
                                            <i class="pi pi-directions text-xl"></i>
                                            <span class="text-lg">Proceso de Registro</span>
                                        </div>
                                    </template>
                                    <template #content>
                                        <ol
                                            class="flex flex-col gap-3 text-sm text-surface-700 dark:text-surface-300 list-decimal pl-4">
                                            <li class="pl-1">
                                                <strong>Selección de Proveedor:</strong> El sistema se autocompleta con
                                                el catálogo oficial de proveedores (incluyendo el RFC).
                                            </li>
                                            <li class="pl-1">
                                                <strong>Técnico y Área:</strong> Se captura el nombre de la persona que
                                                ingresa y se restringe a un área física autorizada (ej. <em>Bóveda /
                                                    Conteo</em>, <em>Site de Servidores</em>, <em>Piso de
                                                    Máquinas</em>).
                                            </li>
                                            <li class="pl-1">
                                                <strong>Cronometría:</strong> Se registra la Hora de Entrada exacta. Al
                                                marcar la Hora de Salida, NEXUS calcula automáticamente la
                                                <strong>Duración (minutos u horas)</strong> de la visita.
                                            </li>
                                            <li class="pl-1">
                                                <strong>Firma Electrónica:</strong> El usuario de NEXUS que registra la
                                                visita, queda ligado de por vida como el <em>"Supervisor"</em>
                                                responsable de ese acceso.
                                            </li>
                                        </ol>

                                        <div
                                            class="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                                            <i class="pi pi-exclamation-triangle text-yellow-500 mr-2"></i>
                                            <span class="text-xs font-semibold text-yellow-700 dark:text-yellow-300">Si
                                                un registro aparece como "En curso", significa que el técnico externo
                                                aún no ha entregado su gafete de salida.</span>
                                        </div>
                                    </template>
                                </Card>

                                <!-- Permisos -->
                                <Card
                                    class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800">
                                    <template #title>
                                        <div class="flex items-center gap-2 text-surface-600 dark:text-surface-300">
                                            <i class="pi pi-shield text-xl"></i>
                                            <span class="text-lg">Permisos del Módulo</span>
                                        </div>
                                    </template>
                                    <template #content>
                                        <ul class="flex flex-col gap-4 text-sm text-surface-700 dark:text-surface-300">
                                            <li
                                                class="flex items-center justify-between border-b border-surface-200 dark:border-surface-600 pb-2">
                                                <span><i class="pi pi-eye text-blue-500 mr-2"></i>Ver Registros /
                                                    Exportar:</span>
                                                <Tag value="Cualquier perfil operativo" severity="info" />
                                            </li>
                                            <li
                                                class="flex items-center justify-between border-b border-surface-200 dark:border-surface-600 pb-2">
                                                <div class="flex items-center">
                                                    <i class="pi pi-plus text-green-500 mr-2"></i>
                                                    <span
                                                        :class="{ 'line-through text-surface-400': !canCreateAuditoria }">Registrar
                                                        Visita (Entrada/Salida):</span>
                                                </div>
                                                <Tag :value="canCreateAuditoria ? 'Tienes Acceso' : 'Restringido'"
                                                    :severity="canCreateAuditoria ? 'success' : 'secondary'" />
                                            </li>
                                            <li class="flex items-center justify-between pb-2">
                                                <div class="flex items-center">
                                                    <i class="pi pi-pencil text-red-500 mr-2"></i>
                                                    <span
                                                        :class="{ 'line-through text-surface-400': !canEditAuditoria }">Editar/Eliminar
                                                        Registro:</span>
                                                </div>
                                                <Tag :value="canEditAuditoria ? 'Tienes Acceso' : 'Restringido'"
                                                    :severity="canEditAuditoria ? 'warn' : 'secondary'" />
                                            </li>
                                        </ul>
                                    </template>
                                </Card>
                            </div>
                        </div>
                    </TabPanel>

                    <!-- Sección: Relevos de Turno -->
                    <TabPanel value="10" class="p-6">
                        <div class="flex flex-col gap-6">
                            <!-- Introducción -->
                            <Card
                                class="border-2 border-orange-200 dark:border-orange-900 shadow-none bg-gradient-to-r from-orange-50 to-white dark:from-orange-950 dark:to-surface-900">
                                <template #title>
                                    <div class="flex items-center gap-2 text-orange-600 dark:text-orange-400">
                                        <i class="pi pi-sync text-3xl"></i>
                                        <span class="text-2xl font-bold">Relevos de Turno (Handover)</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Documentación oficial de entrega física y técnica de la sala entre el personal
                                        corporativo.
                                    </p>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed mb-4">
                                        El módulo de <strong>Relevos de Turno</strong> reemplaza las bitácoras físicas
                                        de papel usadas durante el cambio de guardia de técnicos y supervisores.
                                        Funciona como un <em>Timeline</em> (línea de tiempo) cronológico que muestra
                                        exactamente en qué condiciones recibió la sala el personal del nuevo turno.
                                    </p>

                                    <!-- Semáforo de Estado de Entrega -->
                                    <div
                                        class="flex flex-col gap-3 p-4 bg-white dark:bg-surface-800 rounded-xl border border-surface-200 dark:border-surface-700 mt-4">
                                        <strong class="text-sm border-b pb-2">Semáforo de Entrega de Sala:</strong>
                                        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                                            <div
                                                class="flex items-center gap-2 text-sm text-green-700 dark:text-green-400 p-2 bg-green-50 dark:bg-green-900/10 rounded">
                                                <i class="pi pi-check-circle text-lg"></i>
                                                <span class="font-bold">Limpia / Operativa</span>
                                            </div>
                                            <div
                                                class="flex items-center gap-2 text-sm text-yellow-700 dark:text-yellow-400 p-2 bg-yellow-50 dark:bg-yellow-900/10 rounded">
                                                <i class="pi pi-exclamation-circle text-lg"></i>
                                                <span class="font-bold">Con Pendientes Menores</span>
                                            </div>
                                            <div
                                                class="flex items-center gap-2 text-sm text-red-700 dark:text-red-400 p-2 bg-red-50 dark:bg-red-900/10 rounded">
                                                <i class="pi pi-times-circle text-lg"></i>
                                                <span class="font-bold">Situación Crítica / Urgente</span>
                                            </div>
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <!-- Firmas Digitales -->
                                <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                    <template #title>
                                        <div class="flex items-center gap-2 text-primary">
                                            <i class="pi pi-users text-xl"></i>
                                            <span class="text-lg">Actoría y Responsabilidad</span>
                                        </div>
                                    </template>
                                    <template #content>
                                        <div
                                            class="flex items-center justify-between bg-surface-50 dark:bg-surface-900 p-4 rounded-xl border border-surface-100 dark:border-surface-700 mb-4">
                                            <div class="flex flex-col items-center">
                                                <i class="pi pi-user-minus text-red-500 text-2xl mb-1"></i>
                                                <span class="text-xs font-bold text-surface-500">ENTREGA</span>
                                                <span class="text-sm font-semibold max-w-[80px] text-center mt-1">Tu
                                                    Usuario <br />(Automático)</span>
                                            </div>
                                            <i class="pi pi-arrow-right text-surface-300 text-2xl"></i>
                                            <div class="flex flex-col items-center">
                                                <i class="pi pi-user-plus text-green-500 text-2xl mb-1"></i>
                                                <span class="text-xs font-bold text-surface-500">RECIBE</span>
                                                <span
                                                    class="text-sm font-semibold max-w-[80px] text-center mt-1">Técnico/Sup.
                                                    <br />(Seleccionado)</span>
                                            </div>
                                        </div>
                                        <p class="text-sm text-surface-600 dark:text-surface-400">
                                            Al crear un relevo, el sistema automáticamente captura <strong>tu sesión
                                                activa</strong> como la persona que se retira del turno. Tu única
                                            responsabilidad de sistema es elegir en el buscador a quién le entregas
                                            físicamente la sala. La hora de salida se graba al segundo exacto.
                                        </p>
                                    </template>
                                </Card>

                                <!-- Información Adjunta -->
                                <Card
                                    class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800">
                                    <template #title>
                                        <div class="flex items-center gap-2 text-surface-600 dark:text-surface-300">
                                            <i class="pi pi-file-edit text-xl"></i>
                                            <span class="text-lg">Campos de Información</span>
                                        </div>
                                    </template>
                                    <template #content>
                                        <ul class="flex flex-col gap-4 text-sm text-surface-700 dark:text-surface-300">
                                            <li class="border-b border-surface-200 dark:border-surface-600 pb-3">
                                                <strong
                                                    class="text-yellow-600 dark:text-yellow-500 flex items-center mb-1"><i
                                                        class="pi pi-wrench mr-2"></i> Pendientes Técnicos:</strong>
                                                Lista escrita de máquinas abiertas, piezas por cambiar o tickets en
                                                proceso que el turno entrante debe retomar.
                                            </li>
                                            <li class="pb-3">
                                                <strong
                                                    class="text-blue-600 dark:text-blue-500 flex items-center mb-1"><i
                                                        class="pi pi-info-circle mr-2"></i> Novedades
                                                    Generales:</strong>
                                                Anotaciones libres sobre visitas corporativas, incidentes con clientes,
                                                o particularidades del piso durante la guardia.
                                            </li>
                                        </ul>
                                        <div v-if="!canCreateRelevo"
                                            class="mt-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-3">
                                            <i class="pi pi-lock text-red-500 text-xl"></i>
                                            <span class="text-xs text-red-700 dark:text-red-300">Debido a tu rol actual,
                                                no tienes los permisos técnicos requeridos para ejecutar "Registros de
                                                Cambio de Turno".</span>
                                        </div>
                                    </template>
                                </Card>
                            </div>
                        </div>
                    </TabPanel>

                    <!-- Sección: Dashboard Principal -->
                    <TabPanel value="11" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-indigo-600 dark:text-indigo-400">
                                        <i class="pi pi-compass text-2xl"></i>
                                        <span class="text-xl">Centro de Comando NEXUS (Dashboard)</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed">
                                        El <strong>Dashboard Principal</strong> es la primera pantalla que ves al
                                        iniciar sesión. Está diseñado para ofrecer una vista panorámica del estado de la
                                        operación, permitiéndote tomar acciones rápidas y visualizar la actividad
                                        reciente del sistema.
                                    </p>
                                </template>
                            </Card>

                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

                                <!-- Accesos Rápidos -->
                                <Card class="shadow-sm hover:shadow-md transition-shadow">
                                    <template #title>
                                        <div class="flex items-center gap-2 border-b pb-2">
                                            <i class="pi pi-bolt text-yellow-500 text-xl"></i>
                                            <span class="text-lg">Acciones Rápidas (Quick Actions)</span>
                                        </div>
                                    </template>
                                    <template #content>
                                        <p class="text-sm text-surface-700 dark:text-surface-300 mb-4">
                                            Ubicados en la parte central superior, estos botones te permiten atajar
                                            tareas comunes sin necesidad de navegar a través del menú lateral.
                                        </p>
                                        <ul class="space-y-3">
                                            <li class="flex items-start gap-2">
                                                <i class="pi pi-ticket text-blue-500 mt-1"></i>
                                                <span class="text-sm text-surface-700 dark:text-surface-300">
                                                    <strong>Nuevo Ticket:</strong> Abre un diálogo para reportar una
                                                    falla en segundos (solo necesitas máquina, categoría y
                                                    descripción).
                                                </span>
                                            </li>
                                            <li class="flex items-start gap-2">
                                                <i class="pi pi-user-plus text-green-500 mt-1"></i>
                                                <span class="text-sm text-surface-700 dark:text-surface-300">
                                                    <strong>Crear Usuario:</strong> (Para perfiles con permisos)
                                                    Registra a un nuevo integrante del equipo rellenando los campos
                                                    básicos de acceso.
                                                </span>
                                            </li>
                                            <li class="flex items-start gap-2">
                                                <i class="pi pi-exclamation-circle text-orange-500 mt-1"></i>
                                                <span class="text-sm text-surface-700 dark:text-surface-300">
                                                    <strong>Reportar Error:</strong> (Módulo Evolución NEXUS) Si el
                                                    sistema presenta un "bug" o tienes una sugerencia, puedes enviarla
                                                    directamente a los desarrolladores.
                                                </span>
                                            </li>
                                        </ul>
                                    </template>
                                </Card>

                                <!-- Actividad Reciente -->
                                <Card class="shadow-sm hover:shadow-md transition-shadow">
                                    <template #title>
                                        <div class="flex items-center gap-2 border-b pb-2">
                                            <i class="pi pi-history text-purple-500 text-xl"></i>
                                            <span class="text-lg">Feed de Actividad (Actividad Reciente)</span>
                                        </div>
                                    </template>
                                    <template #content>
                                        <p class="text-sm text-surface-700 dark:text-surface-300 mb-4">
                                            Es un registro en tiempo real de lo que está ocurriendo en tu sala asignada.
                                            El sistema te avisa cuando:
                                        </p>
                                        <ul class="space-y-3">
                                            <li
                                                class="flex items-center gap-2 text-sm text-surface-700 dark:text-surface-300">
                                                <i class="pi pi-check text-green-500"></i> Se crean o cierran tickets.
                                            </li>
                                            <li
                                                class="flex items-center gap-2 text-sm text-surface-700 dark:text-surface-300">
                                                <i class="pi pi-check text-green-500"></i> Alguien reporta una
                                                incidencia de infraestructura.
                                            </li>
                                            <li
                                                class="flex items-center gap-2 text-sm text-surface-700 dark:text-surface-300">
                                                <i class="pi pi-check text-green-500"></i> Se agregan máquinas nuevas o
                                                se actualizan inventarios.
                                            </li>
                                            <li
                                                class="flex items-center gap-2 text-sm text-surface-700 dark:text-surface-300">
                                                <i class="pi pi-check text-green-500"></i> Se envían reportes de la
                                                Wiki u operaciones de mantenimiento.
                                            </li>
                                        </ul>
                                    </template>
                                </Card>
                            </div>

                            <Card v-if="hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA'])"
                                class="shadow-sm bg-blue-50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800">
                                <template #title>
                                    <div class="flex items-center gap-2 text-blue-800 dark:text-blue-300">
                                        <i class="pi pi-chart-bar text-xl"></i>
                                        <span class="font-bold">Indicadores Clave (Solo Gerencia/Admin)</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-sm text-surface-700 dark:text-surface-300">
                                        Los roles de mayor jerarquía verán un bloque central llamado
                                        <strong>"Estado del Sistema"</strong> que totaliza la cantidad de usuarios,
                                        tickets pendientes por resolver y tickets levantados en urgencia ("Críticos").
                                    </p>
                                </template>
                            </Card>
                        </div>
                    </TabPanel>

                    <!-- Sección: Notificaciones -->
                    <TabPanel value="12" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-yellow-600 dark:text-yellow-400">
                                        <i class="pi pi-bell text-2xl"></i>
                                        <span class="text-xl">Gestión de Notificaciones (Alertas)</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed">
                                        El sistema te notifica activamente cuando ocurre algo importante que requiere de
                                        tu atención. A diferencia del Feed de Actividad, las notificaciones apuntan
                                        directamente a <strong>ti o a tu rol.</strong>
                                    </p>
                                </template>
                            </Card>

                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

                                <!-- Visualización y Topbar -->
                                <Card class="shadow-sm hover:shadow-md transition-shadow">
                                    <template #title>
                                        <div class="flex items-center gap-2 border-b pb-2">
                                            <i class="pi pi-window-maximize text-blue-500 text-xl"></i>
                                            <span class="text-lg">¿Cómo leer las Notificaciones?</span>
                                        </div>
                                    </template>
                                    <template #content>
                                        <p class="text-sm text-surface-700 dark:text-surface-300 mb-4">
                                            En la esquina superior derecha <i>(Topbar)</i>, observarás permanentemente
                                            el ícono de la campanita. Un globo rojo indicará cuántas
                                            notificaciones <strong>nuevas y no leídas</strong> tienes pendientes.
                                        </p>
                                        <ul class="space-y-3">
                                            <li class="flex items-start gap-2">
                                                <i class="pi pi-eye text-surface-500 mt-1"></i>
                                                <span class="text-sm text-surface-700 dark:text-surface-300">
                                                    Al dar clic, se despliega una barra lateral con la lista de tus
                                                    alertas.
                                                </span>
                                            </li>
                                            <li class="flex items-start gap-2">
                                                <i class="pi pi-check-circle text-green-500 mt-1"></i>
                                                <span class="text-sm text-surface-700 dark:text-surface-300">
                                                    Para limpiar tu bandeja rápidamente, puedes dar clic en
                                                    <i>"Marcar todas como leídas"</i>.
                                                </span>
                                            </li>
                                        </ul>
                                    </template>
                                </Card>

                                <!-- Detalles Visuales -->
                                <Card class="shadow-sm hover:shadow-md transition-shadow">
                                    <template #title>
                                        <div class="flex items-center gap-2 border-b pb-2">
                                            <i class="pi pi-external-link text-purple-500 text-xl"></i>
                                            <span class="text-lg">Apertura del Mensaje</span>
                                        </div>
                                    </template>
                                    <template #content>
                                        <p class="text-sm text-surface-700 dark:text-surface-300 mb-4">
                                            A veces la notificación conlleva mucha información (Ej: Un mensaje del
                                            director,
                                            un ticket urgente). Al dar clic en ella, NEXUS te llevará a una pantalla
                                            exclusiva a pantalla completa para que la leas a detalle.
                                        </p>
                                        <div class="p-3 bg-surface-100 dark:bg-surface-800 rounded">
                                            <strong class="block mb-2 text-sm text-surface-900 dark:text-surface-100">
                                                Semáforo de Severidad:
                                            </strong>
                                            <div class="flex flex-wrap gap-2">
                                                <Tag severity="danger" value="Urgente - Acción Inmediata"></Tag>
                                                <Tag severity="warning" value="Alerta - Atención Requerida"></Tag>
                                                <Tag severity="info" value="Informativa - Solo Lectura"></Tag>
                                            </div>
                                        </div>
                                    </template>
                                </Card>
                            </div>
                        </div>
                    </TabPanel>

                    <!-- Sección: EULA Licencia -->
                    <TabPanel value="13" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card
                                class="border border-red-200 dark:border-red-800 shadow-none bg-red-50 dark:bg-red-900/10">
                                <template #title>
                                    <div class="flex items-center gap-2 text-red-600 dark:text-red-400">
                                        <i class="pi pi-shield text-2xl"></i>
                                        <span class="text-xl">Acuerdo de Licencia de Uso (EULA)</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed text-justify">
                                        NEXUS es un software blindado desarrollado por <strong>CYTECHNOLOGIES</strong> y
                                        se
                                        riguriza bajo los más estrictos estándares de la <strong>Ley Federal del Derecho
                                            de Autor y Propiedad Industrial</strong> Mexicana. Todos los usuarios que
                                        deseen
                                        el alta y operación activa en el sistema están obligados a leer y aceptar sus
                                        12 Artículos en la primera conexión.
                                    </p>
                                    <p class="text-sm text-surface-600 dark:text-surface-400 mt-2 font-bold italic">
                                        El sistema no puede utilizarse hasta que se hace scroll completo al documento y
                                        se presiona
                                        "Estoy de acuerdo".
                                    </p>
                                </template>
                            </Card>

                            <div class="grid grid-cols-1 gap-6">
                                <Card class="shadow-sm hover:shadow-md transition-shadow">
                                    <template #title>
                                        <div class="flex items-center gap-2 border-b pb-2">
                                            <i class="pi pi-ban text-red-500 text-xl"></i>
                                            <span class="text-lg">¿Qué prohibe estrictamente la Licencia de
                                                NEXUS?</span>
                                        </div>
                                    </template>
                                    <template #content>
                                        <div class="flex flex-col md:flex-row gap-6 items-start">
                                            <div class="flex-1">
                                                <p
                                                    class="text-sm text-surface-700 dark:text-surface-300 mb-4 font-bold">
                                                    ARTÍCULOS 4 Y 5: Prohibiciones Absolutas (Para todo uso en la App
                                                    Web o Móvil Android)
                                                </p>
                                                <ul class="space-y-4">
                                                    <li class="flex items-start gap-3">
                                                        <i
                                                            class="pi pi-camera text-surface-800 dark:text-surface-200 text-xl font-bold mt-1"></i>
                                                        <div class="flex flex-col">
                                                            <span class="font-bold text-red-600 dark:text-red-400">Zero
                                                                Capturas / Grabaciones</span>
                                                            <span
                                                                class="text-sm text-surface-600 dark:text-surface-400">
                                                                El sistema implementa bloqueos a nivel nativo en Android
                                                                (App de Tablet) para impedir
                                                                las capturas de pantalla, pero la licencia penaliza
                                                                severamente el intento de fotografiar
                                                                los inventarios y datos con dispositivos externos.
                                                            </span>
                                                        </div>
                                                    </li>
                                                    <li class="flex items-start gap-3">
                                                        <i
                                                            class="pi pi-code text-surface-800 dark:text-surface-200 text-xl font-bold mt-1"></i>
                                                        <div class="flex flex-col">
                                                            <span
                                                                class="font-bold text-red-600 dark:text-red-400">Prohibición
                                                                de Ingeniería Inversa / Extracción de Datos</span>
                                                            <span
                                                                class="text-sm text-surface-600 dark:text-surface-400">
                                                                El robo intelectual de la estructura relacional, copiar
                                                                el frontend, extraer los logs,
                                                                inyecciones o modificaciones al código fuente de
                                                                producción implican Sanciones Penales y demanda de
                                                                indemnización.
                                                            </span>
                                                        </div>
                                                    </li>
                                                </ul>
                                            </div>
                                            <!-- Panel de información técnica -->
                                            <div
                                                class="w-full md:w-1/3 bg-surface-100 dark:bg-surface-800 rounded p-4 border border-surface-200 dark:border-surface-700">
                                                <div
                                                    class="font-bold border-b pb-2 mb-2 text-surface-900 dark:text-surface-100 flex items-center gap-2">
                                                    <i class="pi pi-server text-blue-500"></i> Artículo 8: Auditoría
                                                </div>
                                                <p class="text-sm text-surface-600 dark:text-surface-400 text-justify">
                                                    NEXUS documenta internamente todo. Quien hace un Cierre, quien
                                                    agrega una máquina, qué Encargado levantó qué ticket
                                                    y desde dónde. Esto no es solo trazabilidad técnica, sirve para
                                                    levantar evidencias con peso probatorio legal en caso de
                                                    malas prácticas.
                                                </p>
                                            </div>
                                        </div>
                                    </template>
                                </Card>
                            </div>
                        </div>
                    </TabPanel>
                    <!-- ═══════════════════════════════════════════════════════════════
                         SECCIÓN 14 — GAMIFICACIÓN NEXUS
                    ═══════════════════════════════════════════════════════════════ -->
                    <TabPanel value="14" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-yellow-600 dark:text-yellow-400">
                                        <i class="pi pi-star text-2xl"></i>
                                        <span class="text-xl">¿Qué es la Gamificación NEXUS?</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed">
                                        La <strong>Gamificación NEXUS</strong> es un sistema de recompensas RPG integrado
                                        en la plataforma que <strong>premia automáticamente</strong> a los técnicos por
                                        su trabajo diario. Cada acción relevante suma puntos a tu cuenta sin que tengas
                                        que hacer nada extra: simplemente trabaja bien y los puntos llegarán solos.
                                    </p>
                                    <div v-if="!participaGamificacion"
                                        class="mt-4 p-4 bg-amber-50 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200 rounded-xl border-l-4 border-amber-400 flex items-start gap-3">
                                        <i class="pi pi-info-circle mt-1 text-xl"></i>
                                        <div>
                                            <strong class="block mb-1">Nota sobre tu rol:</strong>
                                            Tu perfil actual no acumula puntos de gamificación. Solo los roles
                                            <Tag value="TECNICO" severity="warning" class="mx-1 text-xs" /> y
                                            <Tag value="SUP SISTEMAS" severity="warning" class="mx-1 text-xs" />
                                            participan en el sistema de rangos.
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Puntos por acción -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-green-600 dark:text-green-400">
                                        <i class="pi pi-bolt text-2xl"></i>
                                        <span class="text-xl">¿Cómo se ganan los puntos?</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Los puntos se acreditan <strong>automáticamente</strong> al completar cada acción.
                                        Verás un toast dorado en pantalla confirmando cada ingreso.
                                    </p>
                                </template>
                                <template #content>
                                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                        <div class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-2 flex items-center gap-2 text-blue-500">
                                                <i class="pi pi-file-edit"></i> Bitácora Técnica
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Registrar una entrada de bitácora sobre una intervención en un ticket.</p>
                                            <Tag value="+2 puntos" severity="success" class="mt-3 text-sm" />
                                        </div>
                                        <div class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-2 flex items-center gap-2 text-red-500">
                                                <i class="pi pi-check-circle"></i> Ticket Cerrado
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Cerrar correctamente un ticket de falla con la máquina en estado operativo.</p>
                                            <Tag value="+2 puntos" severity="success" class="mt-3 text-sm" />
                                        </div>
                                        <div class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-2 flex items-center gap-2 text-orange-500">
                                                <i class="pi pi-sync"></i> Relevo de Turno
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Documentar formalmente el traspaso de responsabilidades al terminar el turno.</p>
                                            <Tag value="+2 puntos" severity="success" class="mt-3 text-sm" />
                                        </div>
                                        <div class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-2 flex items-center gap-2 text-indigo-500">
                                                <i class="pi pi-send"></i> Evolución NEXUS
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Enviar un reporte de bug o propuesta de mejora para la plataforma NEXUS.</p>
                                            <Tag value="+15 puntos" severity="info" class="mt-3 text-sm" />
                                        </div>
                                        <div class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-2 flex items-center gap-2 text-teal-500">
                                                <i class="pi pi-check-square"></i> Tarea Especial
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Completar una tarea especial asignada por el supervisor o administrador.</p>
                                            <Tag value="+20 puntos" severity="info" class="mt-3 text-sm" />
                                        </div>
                                        <div class="p-4 border border-yellow-300 dark:border-yellow-700 rounded-xl bg-yellow-50 dark:bg-yellow-900/20 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-2 flex items-center gap-2 text-yellow-600">
                                                <i class="pi pi-wrench"></i> Mantenimiento Preventivo
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Registrar un mantenimiento preventivo realizado a una máquina de la sala.</p>
                                            <Tag value="+50 puntos" severity="warn" class="mt-3 text-sm" />
                                        </div>
                                        <div class="p-4 border border-purple-200 dark:border-purple-700 rounded-xl bg-purple-50 dark:bg-purple-900/20 hover:shadow-md transition-shadow md:col-span-2 lg:col-span-3">
                                            <h3 class="font-bold mb-2 flex items-center gap-2 text-purple-600">
                                                <i class="pi pi-book"></i> Guía Wiki Publicada
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">Cuando el administrador publica una guía técnica que tú redactaste, recibirás los puntos que él determine según la calidad y utilidad del documento.</p>
                                            <Tag value="Variable (lo define el admin)" severity="secondary" class="mt-3 text-sm" />
                                        </div>
                                    </div>
                                    <div class="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200 rounded-xl border-l-4 border-blue-400 flex items-start gap-3">
                                        <i class="pi pi-info-circle mt-1 text-xl"></i>
                                        <div class="text-sm">
                                            <strong class="block mb-1">💡 Consejo:</strong>
                                            Si cierras un ticket (bitácora + cierre en la misma acción), acumulas
                                            <strong>+4 puntos</strong> de un solo movimiento.
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Tipos de puntos -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-purple-600 dark:text-purple-400">
                                        <i class="pi pi-database text-2xl"></i>
                                        <span class="text-xl">Tipos de puntos</span>
                                    </div>
                                </template>
                                <template #content>
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div class="p-4 border border-green-200 dark:border-green-700 rounded-xl bg-green-50 dark:bg-green-900/20">
                                            <h3 class="font-bold mb-2 flex items-center gap-2 text-green-600">
                                                <i class="pi pi-shopping-cart"></i> Puntos Disponibles
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Son los puntos que tienes para gastar en la Tienda de Recompensas.
                                                <strong>Suben</strong> al ganar reconocimientos y
                                                <strong>bajan</strong> al canjear recompensas.
                                            </p>
                                        </div>
                                        <div class="p-4 border border-purple-200 dark:border-purple-700 rounded-xl bg-purple-50 dark:bg-purple-900/20">
                                            <h3 class="font-bold mb-2 flex items-center gap-2 text-purple-600">
                                                <i class="pi pi-history"></i> Puntos Históricos
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                El total acumulado de toda tu trayectoria en NEXUS.
                                                <strong>Nunca disminuyen</strong>, ni al canjear recompensas.
                                                Son los que determinan tu <strong>rango</strong>.
                                            </p>
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Tabla de rangos -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-yellow-600 dark:text-yellow-400">
                                        <i class="pi pi-trophy text-2xl"></i>
                                        <span class="text-xl">Rangos de Gamificación</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Los rangos suben automáticamente conforme acumulas puntos históricos.
                                        No hay que hacer nada para "subir de nivel".
                                    </p>
                                </template>
                                <template #content>
                                    <div class="overflow-x-auto">
                                        <table class="w-full text-sm border-collapse">
                                            <thead>
                                                <tr class="bg-surface-100 dark:bg-surface-800">
                                                    <th class="p-3 text-left border border-surface-200 dark:border-surface-700">Nivel</th>
                                                    <th class="p-3 text-left border border-surface-200 dark:border-surface-700">Rango</th>
                                                    <th class="p-3 text-center border border-surface-200 dark:border-surface-700">Insignia</th>
                                                    <th class="p-3 text-right border border-surface-200 dark:border-surface-700">Puntos mínimos</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr class="border border-surface-200 dark:border-surface-700 bg-yellow-50 dark:bg-yellow-900/20">
                                                    <td class="p-3 font-bold text-center">10</td>
                                                    <td class="p-3 font-bold text-yellow-700 dark:text-yellow-300">Leyenda de NEXUS</td>
                                                    <td class="p-3 text-center text-xl">⭐⭐⭐⭐⭐</td>
                                                    <td class="p-3 text-right font-mono">4,500</td>
                                                </tr>
                                                <tr class="border border-surface-200 dark:border-surface-700">
                                                    <td class="p-3 font-bold text-center">9</td>
                                                    <td class="p-3 font-bold">Guardián del Casino</td>
                                                    <td class="p-3 text-center text-xl">⭐⭐⭐⭐</td>
                                                    <td class="p-3 text-right font-mono">3,600</td>
                                                </tr>
                                                <tr class="border border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800/50">
                                                    <td class="p-3 font-bold text-center">8</td>
                                                    <td class="p-3 font-bold">Arquitecto de Sala</td>
                                                    <td class="p-3 text-center text-xl">🔷🔷🔷🔷</td>
                                                    <td class="p-3 text-right font-mono">2,800</td>
                                                </tr>
                                                <tr class="border border-surface-200 dark:border-surface-700">
                                                    <td class="p-3 font-bold text-center">7</td>
                                                    <td class="p-3 font-bold">Maestro Electrónico</td>
                                                    <td class="p-3 text-center text-xl">🔷🔷🔷</td>
                                                    <td class="p-3 text-right font-mono">2,100</td>
                                                </tr>
                                                <tr class="border border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800/50">
                                                    <td class="p-3 font-bold text-center">6</td>
                                                    <td class="p-3 font-bold">Técnico Élite</td>
                                                    <td class="p-3 text-center text-xl">🔷🔷</td>
                                                    <td class="p-3 text-right font-mono">1,500</td>
                                                </tr>
                                                <tr class="border border-surface-200 dark:border-surface-700">
                                                    <td class="p-3 font-bold text-center">5</td>
                                                    <td class="p-3 font-bold">Especialista en Hardware</td>
                                                    <td class="p-3 text-center text-xl">🔷</td>
                                                    <td class="p-3 text-right font-mono">1,000</td>
                                                </tr>
                                                <tr class="border border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800/50">
                                                    <td class="p-3 font-bold text-center">4</td>
                                                    <td class="p-3 font-bold">Operador de Máquinas</td>
                                                    <td class="p-3 text-center text-xl">🔶🔶🔶</td>
                                                    <td class="p-3 text-right font-mono">600</td>
                                                </tr>
                                                <tr class="border border-surface-200 dark:border-surface-700">
                                                    <td class="p-3 font-bold text-center">3</td>
                                                    <td class="p-3 font-bold">Técnico de Soporte</td>
                                                    <td class="p-3 text-center text-xl">🔶🔶</td>
                                                    <td class="p-3 text-right font-mono">300</td>
                                                </tr>
                                                <tr class="border border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800/50">
                                                    <td class="p-3 font-bold text-center">2</td>
                                                    <td class="p-3 font-bold">Aprendiz de Sala</td>
                                                    <td class="p-3 text-center text-xl">🔶</td>
                                                    <td class="p-3 text-right font-mono">100</td>
                                                </tr>
                                                <tr class="border border-surface-200 dark:border-surface-700">
                                                    <td class="p-3 font-bold text-center">1</td>
                                                    <td class="p-3 font-bold text-surface-500">Novato de Mantenimiento</td>
                                                    <td class="p-3 text-center text-xl">🔩</td>
                                                    <td class="p-3 text-right font-mono">0</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                    <div class="mt-4 p-4 bg-surface-50 dark:bg-surface-800 rounded-xl border border-surface-200 dark:border-surface-700">
                                        <p class="text-sm text-surface-600 dark:text-surface-400">
                                            <i class="pi pi-info-circle mr-2 text-blue-500"></i>
                                            Tu rango actual y la barra de progreso hacia el siguiente nivel se muestran
                                            en la <strong>Tienda de Recompensas</strong>.
                                        </p>
                                    </div>
                                </template>
                            </Card>

                        </div>
                    </TabPanel>

                    <!-- ═══════════════════════════════════════════════════════════════
                         SECCIÓN 15 — TIENDA DE RECOMPENSAS
                    ═══════════════════════════════════════════════════════════════ -->
                    <TabPanel value="15" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-pink-600 dark:text-pink-400">
                                        <i class="pi pi-info-circle text-2xl"></i>
                                        <span class="text-xl">¿Qué es e información general?</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed">
                                        La <strong>Tienda de Recompensas</strong> permite a los técnicos canjear sus
                                        <strong>puntos NEXUS disponibles</strong> por recompensas reales: días libres
                                        adicionales, bonos de alimentación, membresías y más, según lo que la gerencia
                                        de cada casino configure.
                                    </p>
                                    <div class="mt-4 p-4 bg-pink-50 dark:bg-pink-900/30 text-pink-800 dark:text-pink-200 rounded-xl border-l-4 border-pink-400 flex items-start gap-3">
                                        <i class="pi pi-shield mt-1 text-xl"></i>
                                        <div class="text-sm">
                                            <strong class="block mb-1">Regla importante:</strong>
                                            Canjear recompensas descuenta de tus <strong>puntos disponibles</strong>,
                                            pero <strong>nunca afecta tu rango</strong>. Los puntos históricos siempre
                                            se mantienen sin importar cuánto canjees.
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Lo que puedes hacer -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-green-600 dark:text-green-400">
                                        <i class="pi pi-cog text-2xl"></i>
                                        <span class="text-xl">Lo que puedes hacer</span>
                                    </div>
                                </template>
                                <template #content>
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div v-if="puedeCanjear"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-pink-500">
                                                <i class="pi pi-shopping-bag mr-2"></i> Canjear Recompensas
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Explora el catálogo de tu casino, revisa el costo en puntos de cada
                                                recompensa y haz clic en <Tag value="Canjear" severity="danger" class="mx-1 text-xs" />
                                                cuando tengas suficientes puntos disponibles.
                                            </p>
                                        </div>
                                        <div v-if="puedeCanjear"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-primary">
                                                <i class="pi pi-list mr-2"></i> Historial de Canjes
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                En la sección <strong>"Mis Canjes"</strong> de la tienda puedes ver
                                                todos los canjes realizados y su estado actual (Pendiente / Entregado /
                                                Cancelado).
                                            </p>
                                        </div>
                                        <div v-if="puedeAdminTienda"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-blue-500">
                                                <i class="pi pi-plus mr-2"></i> Crear Recompensas
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Tu perfil puede crear nuevas recompensas para los técnicos de tu casino.
                                                Define el título, descripción, costo en puntos y stock disponible.
                                            </p>
                                        </div>
                                        <div v-if="puedeAdminTienda"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-orange-500">
                                                <i class="pi pi-check-circle mr-2"></i> Confirmar Entregas
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Cuando entregues físicamente una recompensa al técnico, marca el canje
                                                como <Tag value="Entregado" severity="success" class="mx-1 text-xs" />
                                                desde el panel de administración.
                                            </p>
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Estados de un canje -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-purple-600 dark:text-purple-400">
                                        <i class="pi pi-tag text-2xl"></i>
                                        <span class="text-xl">Estados de un canje</span>
                                    </div>
                                </template>
                                <template #content>
                                    <ul class="flex flex-col gap-3">
                                        <li class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm flex items-start gap-4">
                                            <Tag value="Pendiente" severity="warn" class="mt-1 text-xs shrink-0" />
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                El canje fue realizado y los puntos ya fueron descontados. El
                                                administrador aún no ha entregado la recompensa físicamente.
                                            </p>
                                        </li>
                                        <li class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm flex items-start gap-4">
                                            <Tag value="Entregado" severity="success" class="mt-1 text-xs shrink-0" />
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                El administrador confirmó que la recompensa fue entregada al técnico.
                                            </p>
                                        </li>
                                        <li class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm flex items-start gap-4">
                                            <Tag value="Cancelado" severity="danger" class="mt-1 text-xs shrink-0" />
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                El canje fue cancelado antes de la entrega.
                                            </p>
                                        </li>
                                    </ul>
                                </template>
                            </Card>

                            <!-- Formulario: Crear recompensa (solo admin) -->
                            <Card v-if="puedeAdminTienda"
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                                        <i class="pi pi-file-edit text-2xl"></i>
                                        <span class="text-xl">Formulario: Crear una recompensa nueva</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Al hacer clic en <strong>"+ Nueva Recompensa"</strong>, el sistema solicitará:
                                    </p>
                                </template>
                                <template #content>
                                    <ul class="flex flex-col gap-4">
                                        <li class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-tag text-primary"></i>
                                                <strong class="text-lg">Título</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Nombre atractivo y claro. Ej: <em>"Día libre adicional"</em>,
                                                <em>"Bono de alimentación $200"</em>.
                                            </p>
                                        </li>
                                        <li class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-align-left text-primary"></i>
                                                <strong class="text-lg">Descripción</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Explica qué incluye, cómo se reclama y si aplican condiciones o fechas
                                                de vigencia.
                                            </p>
                                        </li>
                                        <li class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-star text-primary"></i>
                                                <strong class="text-lg">Costo en Puntos</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Cuántos puntos disponibles debe gastar el técnico para canjearla.
                                            </p>
                                        </li>
                                        <li class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-box text-primary"></i>
                                                <strong class="text-lg">Stock</strong>
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Cantidad máxima de canjes permitidos. Si se deja vacío, el stock es
                                                <strong>ilimitado</strong>.
                                            </p>
                                        </li>
                                    </ul>
                                </template>
                            </Card>

                        </div>
                    </TabPanel>

                    <!-- ═══════════════════════════════════════════════════════════════
                         SECCIÓN 16 — WIKI TÉCNICA
                    ═══════════════════════════════════════════════════════════════ -->
                    <TabPanel value="16" class="p-6">
                        <div class="flex flex-col gap-6">

                            <!-- Introducción -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-teal-600 dark:text-teal-400">
                                        <i class="pi pi-info-circle text-2xl"></i>
                                        <span class="text-xl">¿Qué es e información general?</span>
                                    </div>
                                </template>
                                <template #content>
                                    <p class="text-surface-700 dark:text-surface-300 leading-relaxed">
                                        La <strong>Wiki Técnica</strong> es la base de conocimiento colectivo del equipo.
                                        Contiene guías de reparación, manuales de configuración, procedimientos de
                                        limpieza y diccionarios de códigos de error escritos por los mismos técnicos,
                                        validados y publicados por el administrador.
                                    </p>
                                    <div class="mt-4 p-4 bg-teal-50 dark:bg-teal-900/30 text-teal-800 dark:text-teal-200 rounded-xl border-l-4 border-teal-400 flex items-start gap-3">
                                        <i class="pi pi-globe mt-1 text-xl"></i>
                                        <div class="text-sm">
                                            <strong class="block mb-1">Wiki compartida:</strong>
                                            Las guías son visibles para <strong>todos los casinos</strong>.
                                            Puedes filtrar por casino de origen para ver las soluciones registradas
                                            en cada sucursal específica.
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Flujo de vida de una guía -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                                        <i class="pi pi-arrows-v text-2xl"></i>
                                        <span class="text-xl">Ciclo de vida de una guía</span>
                                    </div>
                                </template>
                                <template #content>
                                    <div class="flex flex-col md:flex-row items-center justify-around gap-4 py-2">
                                        <div class="flex flex-col items-center gap-2 text-center">
                                            <div class="w-14 h-14 rounded-full bg-blue-100 dark:bg-blue-900/40 flex items-center justify-center">
                                                <i class="pi pi-upload text-2xl text-blue-500"></i>
                                            </div>
                                            <Tag value="Pendiente de Revisión" severity="secondary" class="text-xs" />
                                            <p class="text-xs text-surface-500 max-w-32">El técnico sube el PDF y envía la propuesta</p>
                                        </div>
                                        <i class="pi pi-arrow-right text-surface-400 hidden md:block text-2xl"></i>
                                        <i class="pi pi-arrow-down text-surface-400 md:hidden text-2xl"></i>
                                        <div class="flex flex-col items-center gap-2 text-center">
                                            <div class="w-14 h-14 rounded-full bg-green-100 dark:bg-green-900/40 flex items-center justify-center">
                                                <i class="pi pi-check text-2xl text-green-500"></i>
                                            </div>
                                            <Tag value="Aprobada" severity="success" class="text-xs" />
                                            <p class="text-xs text-surface-500 max-w-32">El admin revisó y aprobó, aún no es pública</p>
                                        </div>
                                        <i class="pi pi-arrow-right text-surface-400 hidden md:block text-2xl"></i>
                                        <i class="pi pi-arrow-down text-surface-400 md:hidden text-2xl"></i>
                                        <div class="flex flex-col items-center gap-2 text-center">
                                            <div class="w-14 h-14 rounded-full bg-yellow-100 dark:bg-yellow-900/40 flex items-center justify-center">
                                                <i class="pi pi-globe text-2xl text-yellow-500"></i>
                                            </div>
                                            <Tag value="Publicada" severity="warn" class="text-xs" />
                                            <p class="text-xs text-surface-500 max-w-32">Visible para todos + puntos acreditados al autor</p>
                                        </div>
                                        <div class="hidden md:flex items-center text-surface-300">|</div>
                                        <div class="flex flex-col items-center gap-2 text-center">
                                            <div class="w-14 h-14 rounded-full bg-red-100 dark:bg-red-900/40 flex items-center justify-center">
                                                <i class="pi pi-times text-2xl text-red-500"></i>
                                            </div>
                                            <Tag value="Rechazada" severity="danger" class="text-xs" />
                                            <p class="text-xs text-surface-500 max-w-32">El admin rechazó con una nota de retroalimentación</p>
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Lo que puedes hacer -->
                            <Card class="border border-surface-200 dark:border-surface-700 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-green-600 dark:text-green-400">
                                        <i class="pi pi-cog text-2xl"></i>
                                        <span class="text-xl">Lo que puedes hacer</span>
                                    </div>
                                </template>
                                <template #content>
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div v-if="puedeVerWiki"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-teal-500">
                                                <i class="pi pi-list mr-2"></i> Consultar guías publicadas
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Accede al catálogo completo de guías publicadas. Filtra por modelo de
                                                máquina, categoría, casino de origen o usa el buscador de texto libre.
                                            </p>
                                        </div>
                                        <div v-if="puedeVerWiki"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-blue-500">
                                                <i class="pi pi-download mr-2"></i> Descargar PDF
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Cada guía publicada tiene un botón para descargar el PDF original
                                                directamente en tu dispositivo.
                                            </p>
                                        </div>
                                        <div v-if="puedeProponer"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-purple-500">
                                                <i class="pi pi-upload mr-2"></i> Proponer nueva guía
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Usa el botón <Tag value="+ Proponer Guía" severity="primary" class="mx-1 text-xs" />
                                                para subir un PDF con tu documentación técnica. El administrador la
                                                revisará y, si la aprueba y publica, recibirás puntos NEXUS.
                                            </p>
                                        </div>
                                        <div v-if="puedePublicarWiki"
                                            class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900 hover:shadow-md transition-shadow">
                                            <h3 class="font-bold mb-3 flex items-center text-yellow-500">
                                                <i class="pi pi-star mr-2"></i> Aprobar, Publicar y Rechazar
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Tu perfil puede revisar las guías en estado <Tag value="Pendiente" severity="secondary" class="mx-1 text-xs" />,
                                                aprobarlas, publicarlas asignando puntos al autor, o rechazarlas con
                                                una nota de retroalimentación.
                                            </p>
                                        </div>
                                    </div>
                                </template>
                            </Card>

                            <!-- Formulario: proponer guía -->
                            <Card v-if="puedeProponer"
                                class="border border-surface-200 dark:border-surface-700 shadow-none bg-surface-50 dark:bg-surface-800/50">
                                <template #title>
                                    <div class="flex items-center gap-2 text-purple-600 dark:text-purple-400">
                                        <i class="pi pi-file-edit text-2xl"></i>
                                        <span class="text-xl">Formulario: Proponer una guía técnica</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Al hacer clic en <strong>"+ Proponer Guía"</strong>, el sistema pedirá:
                                    </p>
                                </template>
                                <template #content>
                                    <ul class="flex flex-col gap-4">
                                        <li class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-pencil text-primary"></i>
                                                <strong class="text-lg">Título de la Guía</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Debe ser claro y específico. Incluye el código de error o el modelo de
                                                máquina. Ej: <em>"Solución error E-34 en IGT Gemini 2"</em>.
                                            </p>
                                        </li>
                                        <li class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-sitemap text-primary"></i>
                                                <strong class="text-lg">Categoría</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <div class="flex flex-wrap gap-2 mt-2">
                                                <Tag value="Guía de Reparación" severity="danger" class="text-xs" />
                                                <Tag value="Manual de Configuración" severity="info" class="text-xs" />
                                                <Tag value="Procedimiento de Limpieza" severity="success" class="text-xs" />
                                                <Tag value="Diccionario de Códigos de Error" severity="warn" class="text-xs" />
                                            </div>
                                        </li>
                                        <li class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-desktop text-primary"></i>
                                                <strong class="text-lg">Modelo de Máquina</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Selecciona el modelo exacto de máquina al que aplica la guía.
                                            </p>
                                        </li>
                                        <li class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-building text-primary"></i>
                                                <strong class="text-lg">Casino de Origen</strong>
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Casino donde ocurrió el caso y se desarrolló la solución documentada.
                                            </p>
                                        </li>
                                        <li class="p-4 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 shadow-sm">
                                            <div class="flex items-center gap-2 mb-2">
                                                <i class="pi pi-file-pdf text-primary"></i>
                                                <strong class="text-lg">Archivo PDF</strong>
                                                <Tag value="Obligatorio" severity="danger" class="text-xs" rounded />
                                            </div>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Sube el documento en formato PDF con el procedimiento completo.
                                                Asegúrate de que sea legible, con pasos numerados y resultados
                                                verificados.
                                            </p>
                                        </li>
                                    </ul>

                                    <!-- Buenas prácticas -->
                                    <div class="mt-6 p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-700">
                                        <h4 class="font-bold text-green-700 dark:text-green-300 mb-3 flex items-center gap-2">
                                            <i class="pi pi-lightbulb"></i> Buenas prácticas para que aprueben tu guía
                                        </h4>
                                        <ul class="space-y-2 text-sm text-surface-600 dark:text-surface-400">
                                            <li class="flex items-start gap-2">
                                                <i class="pi pi-check-circle text-green-500 mt-0.5 shrink-0"></i>
                                                <span><strong>Título específico:</strong> incluye el código de error o el modelo exacto.</span>
                                            </li>
                                            <li class="flex items-start gap-2">
                                                <i class="pi pi-check-circle text-green-500 mt-0.5 shrink-0"></i>
                                                <span><strong>PDF legible:</strong> letras de tamaño adecuado, fotos del procedimiento si es posible.</span>
                                            </li>
                                            <li class="flex items-start gap-2">
                                                <i class="pi pi-check-circle text-green-500 mt-0.5 shrink-0"></i>
                                                <span><strong>Pasos numerados:</strong> ordenados lógicamente de inicio a fin.</span>
                                            </li>
                                            <li class="flex items-start gap-2">
                                                <i class="pi pi-check-circle text-green-500 mt-0.5 shrink-0"></i>
                                                <span><strong>Soluciones verificadas:</strong> documenta solo procedimientos que ya probaste y funcionaron.</span>
                                            </li>
                                        </ul>
                                    </div>
                                </template>
                            </Card>

                            <!-- Sección para administradores: publicar con puntos -->
                            <Card v-if="puedePublicarWiki"
                                class="border border-surface-200 dark:border-surface-700 shadow-none">
                                <template #title>
                                    <div class="flex items-center gap-2 text-yellow-600 dark:text-yellow-400">
                                        <i class="pi pi-star-fill text-2xl"></i>
                                        <span class="text-xl">Publicar guía y otorgar puntos</span>
                                    </div>
                                    <p class="mt-2 text-sm font-normal text-surface-600 dark:text-surface-400">
                                        Al publicar una guía aprobada, debes indicar cuántos puntos NEXUS
                                        recibirá el técnico autor como reconocimiento.
                                    </p>
                                </template>
                                <template #content>
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div class="p-4 border border-surface-200 dark:border-surface-700 rounded-xl bg-surface-0 dark:bg-surface-900">
                                            <h3 class="font-bold mb-2 flex items-center gap-2 text-surface-700 dark:text-surface-200">
                                                <i class="pi pi-info-circle text-blue-500"></i> ¿Cómo funciona?
                                            </h3>
                                            <ol class="text-sm text-surface-600 dark:text-surface-400 space-y-2 list-decimal list-inside">
                                                <li>Abre la guía en estado <Tag value="Aprobada" severity="success" class="mx-1 text-xs" /> o <Tag value="Pendiente" severity="secondary" class="mx-1 text-xs" /></li>
                                                <li>Haz clic en el botón <strong>"Publicar"</strong></li>
                                                <li>Selecciona los puntos a otorgar (25, 50, 75 ó 100)</li>
                                                <li>Confirma. La guía queda pública y los puntos se acreditan al autor</li>
                                            </ol>
                                        </div>
                                        <div class="p-4 border border-yellow-200 dark:border-yellow-700 rounded-xl bg-yellow-50 dark:bg-yellow-900/20">
                                            <h3 class="font-bold mb-2 flex items-center gap-2 text-yellow-700 dark:text-yellow-300">
                                                <i class="pi pi-shield"></i> Impacto en la cuenta del técnico
                                            </h3>
                                            <p class="text-sm text-surface-600 dark:text-surface-400">
                                                Los puntos asignados se suman tanto a sus
                                                <strong>puntos disponibles</strong> (para canjear en la tienda) como a
                                                su <strong>historial acumulado</strong> (para su rango). La publicación
                                                de una buena guía puede subir significativamente el nivel del técnico.
                                            </p>
                                        </div>
                                    </div>
                                </template>
                            </Card>

                        </div>
                    </TabPanel>

                </TabPanels>
            </Tabs>
        </div>
    </div>
</template>

<style scoped>
/* Transiciones suaves en hover */
.transition-shadow {
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.hover\:shadow-md:hover {
    transform: translateY(-2px);
}
</style>
