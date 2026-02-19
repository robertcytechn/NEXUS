<script setup>
import { ref, computed } from 'vue';
import AppMenuItem from './AppMenuItem.vue';
import { getUser, hasRoleAccess } from '@/service/api';

// Definición del menú completo con roles de acceso
// ------------------------------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------------------------------

// roles al 02 de febrero de 2026
// roles: ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA', 'PROVEEDOR', 'SOLICITANTE', 'OBSERVADOR'],
const menuDefinition = [
    {
        label: 'Principal',
        items: [
            {
                label: 'Escritorio',
                icon: 'pi pi-fw pi-home',
                to: '/',
                roles: ['all']  // Todos los usuarios autenticados
            }
        ]
    },
    {
        label: 'Mando Central',
        icon: 'pi pi-fw pi-server',
        roles: ['ADMINISTRADOR'],
        items: [
            {
                label: 'Roles y Permisos',
                icon: 'pi pi-fw pi-lock',
                to: '/admin/roles',
                roles: ['ADMINISTRADOR']
            },
            {
                label: 'Casinos y Salas',
                icon: 'pi pi-fw pi-building',
                to: '/admin/casinos',
                roles: ['ADMINISTRADOR']
            },
            {
                label: 'Usuarios',
                icon: 'pi pi-fw pi-users',
                to: '/admin/usuarios',
                roles: ['ADMINISTRADOR']
            },
            {
                label: 'Proveedores',
                icon: 'pi pi-fw pi-briefcase',
                to: '/admin/proveedores',
                roles: ['ADMINISTRADOR']
            },
            {
                label: 'Modelos de Máquinas',
                icon: 'pi pi-fw pi-cog',
                to: '/admin/modelos',
                roles: ['ADMINISTRADOR']
            },
            {
                label: 'Máquinas',
                icon: 'pi pi-fw pi-desktop',
                to: '/admin/maquinas',
                roles: ['ADMINISTRADOR']
            },
            {
                label: 'Tickets',
                icon: 'pi pi-fw pi-ticket',
                to: '/admin/tickets',
                roles: ['ADMINISTRADOR']
            },
            {
                label: 'Bitácora Técnica',
                icon: 'pi pi-fw pi-file-edit',
                to: '/admin/bitacora-tecnica',
                roles: ['ADMINISTRADOR']
            },
            {
                label: 'Mantenimientos Preventivos',
                icon: 'pi pi-fw pi-calendar',
                to: '/admin/mantenimientos-preventivos',
                roles: ['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO', 'GERENCIA', 'SUPERVISOR SALA']
            },
            {
                label: 'Incidentes de Infraestructura',
                icon: 'pi pi-fw pi-exclamation-triangle',
                to: '/admin/incidentes-infraestructura',
                roles: ['ADMINISTRADOR']
            }
        ]
    },
    {
        label: 'Centro de Servicios y Soporte',
        icon: 'pi pi-fw pi-headset',
        roles: ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA'],
        items: [
            {
                label: 'Usuarios',
                icon: 'pi pi-fw pi-users',
                to: '/centro-servicios/usuarios',
                roles: ['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'GERENCIA', 'SUPERVISOR SALA']
            },
            {
                label: 'Proveedores',
                icon: 'pi pi-fw pi-briefcase',
                to: '/centro-servicios/proveedores',
                roles: ['SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ADMINISTRADOR']
            },
            {
                label: 'Modelos de Máquinas',
                icon: 'pi pi-fw pi-cog',
                to: '/centro-servicios/modelos',
                roles: ['SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ADMINISTRADOR']
            },
            {
                label: 'Maquinas',
                icon: 'pi pi-fw pi-desktop',
                to: '/centro-servicios/maquinas',
                roles: ['SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ADMINISTRADOR']
            },
            {
                label: 'Mapa de Sala',
                icon: 'pi pi-fw pi-map',
                to: '/centro-servicios/mapa-sala',
                roles: ['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'GERENCIA', 'SUPERVISOR SALA', 'TECNICO']
            },
            {
                label: 'Tickets',
                icon: 'pi pi-fw pi-ticket',
                to: '/centro-servicios/tickets',
                roles: ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA']
            },
            {
                label: 'Inventario de Sala',
                icon: 'pi pi-fw pi-box',
                to: '/centro-servicios/inventario',
                roles: ['SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ADMINISTRADOR']
            },
            {
                label: 'Mantenimientos Preventivos',
                icon: 'pi pi-fw pi-calendar',
                to: '/centro-servicios/mantenimientos-preventivos',
                roles: ['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO', 'GERENCIA', 'SUPERVISOR SALA']
            },
            {
                label: 'Incidentes de Infraestructura',
                icon: 'pi pi-fw pi-exclamation-triangle',
                to: '/centro-servicios/incidentes-infraestructura',
                roles: ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA']
            }
        ]

    },
    {
        label: 'Operatividad',
        icon: 'pi pi-fw pi-clock',
        roles: ['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO', 'GERENCIA', 'SUPERVISOR SALA'],
        items: [
            {
                label: 'Auditorías Externas',
                icon: 'pi pi-fw pi-file-check',
                to: '/operatividad/auditorias-externas',
                roles: ['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO', 'GERENCIA', 'SUPERVISOR SALA']
            },
            {
                label: 'Relevo de Turno',
                icon: 'pi pi-fw pi-sync',
                to: '/operatividad/relevo-turno',
                roles: ['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO', 'GERENCIA', 'SUPERVISOR SALA']
            }
        ]
    },
    {
        label: 'Acerca de',
        icon: 'pi pi-fw pi-info-circle',
        items: [
            {
                label: 'Lisencia de Uso',
                icon: 'pi pi-fw pi-file',
                to: '/lisencia'
            },
            {
                label: 'Evolucion NEXUS',
                icon: 'pi pi-fw pi-bolt',
                to: '/evolucion-nexus',
                roles: ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA']
            }
        ]
    }
];
// ------------------------------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------------------------------

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
    return filterMenuByRole(menuDefinition);
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
console.log('Rol del usuario:', user?.rol_nombre);

// Verificar si tiene acceso a ciertos roles
if (hasRoleAccess(['ADMINISTRADOR', 'SUP SISTEMAS'])) {
    // Tiene uno de los roles requeridos
}

DEBUGGING:
----------
Para ver qué ítems están visibles en el menú:
console.log('Menú filtrado:', model.value);

===============================================================================
-->
