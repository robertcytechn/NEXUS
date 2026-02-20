<script setup>
import { ref, computed, onMounted } from 'vue';
import { getUser, hasRoleAccess } from '@/service/api';

const usuario = ref(null);

onMounted(() => {
    usuario.value = getUser();
});

// Computed properties para permisos (igual que en AuditoriasExternas.vue)
const canCreateAuditoria = computed(() =>
    hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO', 'GERENCIA', 'SUPERVISOR SALA'])
);

const canEditOrDeleteAuditoria = computed(() =>
    hasRoleAccess(['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'GERENCIA', 'SUPERVISOR SALA'])
);

</script>

<template>
    <div class="card">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold mb-4">Manual de Usuario</h1>
            <p class="text-xl text-surface-500">Bienvenido al manual de uso de NEXUS. Selecciona un módulo para ver las
                instrucciones operativas.</p>
        </div>

        <Tabs value="0">
            <TabList>
                <Tab value="0" v-if="canCreateAuditoria">
                    <i class="pi pi-file-check mr-2"></i> Operatividad
                </Tab>
                <!-- Espacio para futuros módulos, como Centro de Servicios -->
            </TabList>

            <TabPanels>
                <!-- Pestaña de Operatividad -->
                <TabPanel value="0" v-if="canCreateAuditoria">
                    <div class="p-4">
                        <h2 class="text-2xl font-bold mb-4 text-primary">Auditorías Externas</h2>
                        <p class="mb-4">
                            El módulo de Auditorías Externas permite registrar el acceso y las actividades de técnicos y
                            personal de proveedores
                            dentro de las instalaciones del casino.
                        </p>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">

                            <!-- Tarjeta 1: Registrar una visita (Todos los que tienen canCreate) -->
                            <div class="border rounded-xl p-5 bg-surface-0 dark:bg-surface-900">
                                <div class="flex items-center mb-4">
                                    <div
                                        class="flex items-center justify-center bg-blue-100 dark:bg-blue-900/50 rounded-full w-12 h-12 mr-3">
                                        <i class="pi pi-plus text-blue-500 text-xl"></i>
                                    </div>
                                    <h3 class="text-xl font-semibold m-0">Registrar una Visita</h3>
                                </div>
                                <ul class="list-none p-0 m-0 space-y-3">
                                    <li class="flex items-start">
                                        <i class="pi pi-check-circle text-green-500 mt-1 mr-2"></i>
                                        <span>Dirígete al menú <strong>Operatividad > Auditorías
                                                Externas</strong>.</span>
                                    </li>
                                    <li class="flex items-start">
                                        <i class="pi pi-check-circle text-green-500 mt-1 mr-2"></i>
                                        <span>Haz clic en el botón <strong>"Registrar Visita"</strong> situado en la
                                            parte superior derecha.</span>
                                    </li>
                                    <li class="flex items-start">
                                        <i class="pi pi-check-circle text-green-500 mt-1 mr-2"></i>
                                        <span>Rellena los campos obligatorios: Empresa (busca por nombre), Técnico
                                            Externo, Área, Tipo de Servicio y Hora de Entrada.</span>
                                    </li>
                                    <li class="flex items-start">
                                        <i class="pi pi-check-circle text-green-500 mt-1 mr-2"></i>
                                        <span>Detalla claramente las <strong>Actividades Realizadas</strong>.</span>
                                    </li>
                                    <li class="flex items-start">
                                        <i class="pi pi-check-circle text-green-500 mt-1 mr-2"></i>
                                        <span>La "Hora de Salida" puedes dejarla en blanco si el técnico aún está
                                            trabajando.</span>
                                    </li>
                                </ul>
                            </div>

                            <!-- Tarjeta 2: Editar o Finalizar (Solo roles con canEditOrDelete) -->
                            <div v-if="canEditOrDeleteAuditoria"
                                class="border rounded-xl p-5 bg-surface-0 dark:bg-surface-900">
                                <div class="flex items-center mb-4">
                                    <div
                                        class="flex items-center justify-center bg-orange-100 dark:bg-orange-900/50 rounded-full w-12 h-12 mr-3">
                                        <i class="pi pi-pencil text-orange-500 text-xl"></i>
                                    </div>
                                    <h3 class="text-xl font-semibold m-0">Finalizar o Editar Visita</h3>
                                </div>
                                <ul class="list-none p-0 m-0 space-y-3">
                                    <li class="flex items-start">
                                        <i class="pi pi-clock text-orange-500 mt-1 mr-2"></i>
                                        <span>Las visitas registradas sin hora de salida aparecerán como <strong>"En
                                                curso"</strong>.</span>
                                    </li>
                                    <li class="flex items-start">
                                        <i class="pi pi-pencil text-orange-500 mt-1 mr-2"></i>
                                        <span>Para añadir la hora de salida o modificar detalles, ubica el registro en
                                            la tabla y presiona el botón <strong>editar (lápiz)</strong>.</span>
                                    </li>
                                    <li class="flex items-start">
                                        <i class="pi pi-check-circle text-orange-500 mt-1 mr-2"></i>
                                        <span>Actualiza la información necesaria y guarda los cambios. El sistema
                                            calculará automáticamente la duración.</span>
                                    </li>
                                    <li class="flex items-start">
                                        <i class="pi pi-trash text-red-500 mt-1 mr-2"></i>
                                        <span>También puedes eliminar registros creados por error usando el botón de
                                            <strong>papelera</strong>. Úsalo con precaución.</span>
                                    </li>
                                </ul>
                            </div>

                            <!-- Tarjeta para roles que NO pueden editar pero sí ver la advertencia de quién lo hace -->
                            <div v-if="!canEditOrDeleteAuditoria"
                                class="border rounded-xl p-5 bg-surface-0 dark:bg-surface-900 flex flex-col justify-center">
                                <div class="flex items-center mb-4">
                                    <div
                                        class="flex items-center justify-center bg-gray-100 dark:bg-gray-800 rounded-full w-12 h-12 mr-3">
                                        <i class="pi pi-info-circle text-gray-500 text-xl"></i>
                                    </div>
                                    <h3 class="text-xl font-semibold m-0">Finalizar una Visita</h3>
                                </div>
                                <p class="text-surface-600 dark:text-surface-400">
                                    Su rol actual le permite reportar el ingreso de proveedores. Para asentar la
                                    <strong>Hora de Salida</strong> o corregir información,
                                    deberá solicitar apoyo al Supervisor de Sala, Gerencia o Mando Central.
                                </p>
                            </div>

                        </div>
                    </div>
                </TabPanel>
            </TabPanels>
        </Tabs>
    </div>
</template>

<style scoped>
/* Ajustes menores si es necesario */
</style>
