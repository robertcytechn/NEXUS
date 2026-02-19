<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetchNotificacionById, marcarNotificacionLeida } from '@/service/notificationService';
import { useToast } from 'primevue/usetoast';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const notificacion = ref(null);
const loading = ref(true);

// Mapeo de tipos y niveles a configuración visual
const tipoConfigMap = {
    'ticket': { icon: 'pi pi-ticket', color: 'blue', label: 'Gestión de Tickets' },
    'infraestructura': { icon: 'pi pi-exclamation-triangle', color: 'red', label: 'Incidencia de Infraestructura' },
    'wiki': { icon: 'pi pi-book', color: 'green', label: 'Nueva Guía en Wiki' },
    'sistema': { icon: 'pi pi-info-circle', color: 'purple', label: 'Aviso del Sistema' },
    'DIRECTOR': { icon: 'pi pi-star-fill', color: 'yellow', label: 'Mensaje de Dirección' }
};

const nivelConfigMap = {
    'urgente': { severity: 'danger', label: 'Urgente - Acción Inmediata', icon: 'pi pi-times-circle' },
    'alerta': { severity: 'warning', label: 'Alerta - Atención Requerida', icon: 'pi pi-exclamation-triangle' },
    'informativa': { severity: 'info', label: 'Informativa - Solo Lectura', icon: 'pi pi-info-circle' }
};

const tipoConfig = computed(() => {
    if (!notificacion.value) return tipoConfigMap['sistema'];
    return tipoConfigMap[notificacion.value.tipo] || tipoConfigMap['sistema'];
});

const nivelConfig = computed(() => {
    if (!notificacion.value) return nivelConfigMap['informativa'];
    return nivelConfigMap[notificacion.value.nivel] || nivelConfigMap['informativa'];
});

const fechaFormateada = computed(() => {
    if (!notificacion.value || !notificacion.value.creado_en) return '';
    
    const fecha = new Date(notificacion.value.creado_en);
    return fecha.toLocaleString('es-MX', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
});

const emisor = computed(() => {
    if (!notificacion.value) return 'Sistema';
    
    // Si la notificación es del sistema o global
    if (notificacion.value.es_global) return 'Anuncio Global';
    if (notificacion.value.tipo === 'DIRECTOR') return 'Dirección';
    
    return notificacion.value.creado_por || 'Sistema NEXUS';
});

const cargarNotificacion = async () => {
    loading.value = true;
    
    try {
        const notificacionId = route.params.id;
        const response = await fetchNotificacionById(notificacionId);
        
        if (response.success) {
            notificacion.value = response.data;
            
            // Si no está leída, marcarla como leída
            if (!notificacion.value.leido) {
                await marcarNotificacionLeida(notificacionId);
                notificacion.value.leido = true;
            }
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: 'No se pudo cargar la notificación',
                life: 3000
            });
        }
    } catch (error) {
        console.error('Error al cargar notificación:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Ocurrió un error al cargar la notificación',
            life: 3000
        });
    } finally {
        loading.value = false;
    }
};

const volverCentroServicios = () => {
    router.push('/');
};

onMounted(() => {
    cargarNotificacion();
});
</script>

<template>
    <div class="p-6 max-w-4xl mx-auto">
        <!-- Skeleton loader mientras carga -->
        <div v-if="loading" class="flex flex-col gap-4">
            <Skeleton width="100%" height="3rem" />
            <Skeleton width="100%" height="2rem" />
            <Skeleton width="100%" height="15rem" />
        </div>

        <!-- Contenido de la notificación -->
        <div v-else-if="notificacion" class="flex flex-col gap-6">
            <!-- Header con badges -->
            <div class="flex flex-col gap-3">
                <div class="flex justify-between items-start gap-4 flex-wrap">
                    <div class="flex items-center gap-3">
                        <i 
                            :class="[tipoConfig.icon, `text-${tipoConfig.color}-500`, 'text-4xl']"
                        ></i>
                        <div class="flex flex-col gap-1">
                            <h1 class="text-3xl font-bold text-surface-900 dark:text-surface-50">
                                {{ notificacion.titulo }}
                            </h1>
                            <div class="flex gap-2 flex-wrap">
                                <Tag 
                                    :severity="nivelConfig.severity" 
                                    :icon="nivelConfig.icon"
                                    :value="nivelConfig.label"
                                />
                                <Tag 
                                    :icon="tipoConfig.icon" 
                                    :value="tipoConfig.label"
                                    severity="secondary"
                                />
                                <Tag 
                                    v-if="notificacion.tipo === 'DIRECTOR'" 
                                    icon="pi pi-star-fill" 
                                    value="Mensaje de Dirección"
                                    severity="warning"
                                />
                            </div>
                        </div>
                    </div>
                    <Button
                        label="Volver al Centro de Servicios"
                        icon="pi pi-arrow-left"
                        severity="secondary"
                        @click="volverCentroServicios"
                    />
                </div>
            </div>

            <!-- Información metadata -->
            <Card>
                <template #content>
                    <div class="flex flex-col gap-3">
                        <div class="flex items-center gap-2">
                            <i class="pi pi-calendar text-surface-500"></i>
                            <span class="text-surface-600 dark:text-surface-400">
                                <strong>Fecha:</strong> {{ fechaFormateada }}
                            </span>
                        </div>
                        <div class="flex items-center gap-2">
                            <i class="pi pi-user text-surface-500"></i>
                            <span class="text-surface-600 dark:text-surface-400">
                                <strong>Emisor:</strong> {{ emisor }}
                            </span>
                        </div>
                        <div v-if="notificacion.es_global" class="flex items-center gap-2">
                            <i class="pi pi-globe text-surface-500"></i>
                            <span class="text-surface-600 dark:text-surface-400">
                                <strong>Alcance:</strong> Notificación Global
                            </span>
                        </div>
                    </div>
                </template>
            </Card>

            <!-- Mensaje completo -->
            <Card>
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-file-edit"></i>
                        <span>Mensaje Completo</span>
                    </div>
                </template>
                <template #content>
                    <div 
                        class="text-surface-700 dark:text-surface-300 leading-relaxed whitespace-pre-wrap"
                        style="font-size: 1.1rem; line-height: 1.8;"
                    >
                        {{ notificacion.contenido }}
                    </div>
                </template>
            </Card>

            <!-- Footer con acciones -->
            <div class="flex justify-between items-center pt-4 border-t border-surface-200 dark:border-surface-700">
                <div class="flex items-center gap-2">
                    <i 
                        :class="[
                            'pi', 
                            notificacion.leido ? 'pi-check-circle' : 'pi-circle',
                            notificacion.leido ? 'text-green-500' : 'text-gray-400'
                        ]"
                    ></i>
                    <span class="text-surface-600 dark:text-surface-400">
                        {{ notificacion.leido ? 'Leída' : 'No leída' }}
                    </span>
                </div>
                <Button
                    label="Volver"
                    icon="pi pi-home"
                    @click="volverCentroServicios"
                />
            </div>
        </div>

        <!-- Mensaje de error si no existe -->
        <div v-else class="flex flex-col items-center justify-center gap-4 py-12">
            <i class="pi pi-exclamation-circle text-6xl text-surface-400"></i>
            <h2 class="text-2xl font-bold text-surface-600 dark:text-surface-400">
                Notificación no encontrada
            </h2>
            <Button
                label="Volver al Centro de Servicios"
                icon="pi pi-arrow-left"
                @click="volverCentroServicios"
            />
        </div>
    </div>
</template>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>
