<script setup>
import { ref, computed, onMounted } from 'vue';
import AppMenuItem from './AppMenuItem.vue';
import api, { getUser, hasRoleAccess } from '@/service/api';

// Cargar menú siempre desde la base de datos
const menuDefinition = ref([]);

onMounted(async () => {
    try {
        const res = await api.get('menus/activo/');
        if (res.data && res.data.length > 0) {
            menuDefinition.value = res.data;
        } else {
            menuDefinition.value = [];
        }
    } catch (e) {
        menuDefinition.value = [];
    }
});

// Función recursiva para filtrar ítems del menú según el rol del usuario
const filterMenuByRole = (items) => {
    if (!items || !Array.isArray(items)) return [];

    return items.filter(item => {
        // Verificar si el usuario tiene acceso a este ítem según su rol
        const hasAccess = !item.roles || hasRoleAccess(item.roles);

        if (!hasAccess) return false;

        // Si tiene sub-ítems, filtrarlos recursivamente
        if (item.items && item.items.length > 0) {
            const filteredSubItems = filterMenuByRole(item.items);
            // Solo incluir el grupo si tiene al menos un sub-ítem visible
            if (filteredSubItems.length > 0) {
                item.items = filteredSubItems;
                return true;
            }
            return false;
        }

        return true;
    }).map(item => ({ ...item })); // Clonar para evitar mutaciones
};

// Menú filtrado según el rol del usuario
const model = computed(() => {
    return filterMenuByRole(menuDefinition.value);
});
</script>

<template>
    <ul class="layout-menu">
        <template v-for="(item, i) in model" :key="item">
            <app-menu-item v-if="!item.separator" :item="item" :index="i"></app-menu-item>
            <li v-if="item.separator" class="menu-separator"></li>
        </template>
    </ul>
</template>

<style lang="scss" scoped></style>

<!--
===============================================================================
  SISTEMA DE ROLES DE ACCESO AL MENÚ
===============================================================================

CÓMO FUNCIONA:
--------------
1. Al iniciar sesión, el usuario obtiene un campo `rol_nombre` (ej: 'ADMINISTRADOR')
2. Este valor se guarda en localStorage junto con los demás datos del usuario
3. Cada ítem del menú puede tener un campo `roles` con un array de roles permitidos
4. El menú se filtra automáticamente mostrando solo los ítems para los que el 
   usuario tiene permiso

ROLES DISPONIBLES EN EL SISTEMA:
---------------------------------
- ADMINISTRADOR       Control total del sistema
- DB ADMIN            Administración de base de datos
- GERENCIA            Acceso ejecutivo y reportes
- SUP SISTEMAS        Supervisión de sistemas
- TECNICO             Gestión operativa
- SUPERVISOR SALA     Supervisión de operaciones
- ENCARGADO AREA      Gestión de área específica
- PROVEEDOR           Acceso limitado de proveedores
- SOLICITANTE         Reporte de incidencias
- OBSERVADOR          Solo lectura

CÓMO AGREGAR UN NUEVO ÍTEM AL MENÚ:
-----------------------------------
1. Ítem con acceso para todos los usuarios autenticados:
   {
       label: 'Dashboard',
       icon: 'pi pi-fw pi-home',
       to: '/dashboard',
       roles: ['all']  // Todos los usuarios autenticados pueden ver esto
   }

2. Ítem con acceso para un rol específico:
   {
       label: 'Administración',
       icon: 'pi pi-fw pi-cog',
       to: '/admin',
       roles: ['ADMINISTRADOR']  // Solo administradores
   }

3. Ítem con acceso para múltiples roles:
   {
       label: 'Tickets',
       icon: 'pi pi-fw pi-ticket',
       to: '/tickets',
       roles: ['ADMINISTRADOR', 'SUP SISTEMAS', 'TECNICO']  // Cualquiera de estos roles
   }

4. Grupo con sub-ítems (se aplica filtrado recursivo):
   {
       label: 'Gestión',
       icon: 'pi pi-fw pi-cog',
       roles: ['ADMINISTRADOR', 'SUP SISTEMAS'],  // Control del grupo padre
       items: [
           {
               label: 'Usuarios',
               icon: 'pi pi-fw pi-users',
               to: '/gestion/usuarios',
               roles: ['ADMINISTRADOR']  // Más restrictivo que el padre
           },
           {
               label: 'Reportes',
               icon: 'pi pi-fw pi-chart-line',
               to: '/gestion/reportes',
               roles: ['ADMINISTRADOR', 'SUP SISTEMAS']  // Ambos pueden ver
           }
       ]
   }

5. IMPORTANTE: El filtrado es recursivo. Si un grupo no tiene sub-ítems visibles
   para el usuario, el grupo completo no se mostrará.

6. Si NO especificas `roles`, el ítem será visible para TODOS los usuarios
   autenticados (equivalente a roles: ['all']).

SINCRONIZACIÓN CON ROUTER:
-------------------------
Asegúrate de que los roles en el menú coincidan con los del router:

// En router/index.js
{
    path: '/admin/usuarios',
    name: 'adminUsers',
    component: () => import('@/views/admin/Users.vue'),
    meta: { 
        requiresAuth: true,
        roles: ['ADMINISTRADOR']  // Debe coincidir con el del menú
    }
}

// En AppMenu.vue
{
    label: 'Usuarios',
    icon: 'pi pi-fw pi-users',
    to: '/admin/usuarios',
    roles: ['ADMINISTRADOR']  // Mismo rol que en el router
}

VERIFICAR ACCESO EN TIEMPO REAL:
--------------------------------
Para verificar el rol del usuario actual:

import { getUser, hasRoleAccess } from '@/service/api';

// Obtener el rol del usuario
const user = getUser();


// Verificar si tiene acceso a ciertos roles
if (hasRoleAccess(['ADMINISTRADOR', 'SUP SISTEMAS'])) {
    // Tiene uno de los roles requeridos
}

DEBUGGING:
----------
Para ver qué ítems están visibles en el menú:


===============================================================================
-->
