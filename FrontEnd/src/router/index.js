import AppLayout from '@/layout/AppLayout.vue';
import { createRouter, createWebHistory } from 'vue-router';
import { getAuthToken, getUser, hasRoleAccess } from '@/service/api';

import defaultMenuData from '@/config/menu.json';

const savedMenuConfig = localStorage.getItem('nexusMenuConfig');
const menuData = savedMenuConfig ? JSON.parse(savedMenuConfig) : defaultMenuData;

const viewModules = import.meta.glob('/src/views/**/*.vue');
const dynamicRoutes = [];

const extractRoutes = (items) => {
    for (const item of items) {
        if (item.to && item.componentPath) {
            const loadComponent = viewModules[item.componentPath];
            if (loadComponent) {
                dynamicRoutes.push({
                    path: item.to,
                    component: loadComponent,
                    meta: {
                        title: item.title || item.label,
                        requiresAuth: true,
                        roles: item.roles || ['all']
                    }
                });
            } else {
                console.warn(`Componente no encontrado para la ruta ${item.to}: ${item.componentPath}`);
            }
        }
        if (item.items) {
            extractRoutes(item.items);
        }
    }
};

extractRoutes(menuData);

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            component: AppLayout,
            children: [
                ...dynamicRoutes,
                {
                    path: '/profile',
                    name: 'profile',
                    component: () => import('@/views/pages/Profile.vue'),
                    meta: {
                        title: 'Mi Perfil',
                        requiresAuth: true,
                        roles: ['all']
                    }
                },
                {
                    path: '/notificaciones/:id',
                    component: () => import('@/views/NotificacionDetail.vue'),
                    meta: {
                        title: 'Detalle de Notificación',
                        requiresAuth: true,
                        roles: ['all']
                    }
                }
            ]
        },
        {
            path: '/pages/notfound',
            name: 'notfound',
            component: () => import('@/views/pages/NotFound.vue'),
            meta: {
                title: 'Página No Encontrada',
                isPublic: true
            }
        },
        {
            path: '/auth/login',
            name: 'login',
            component: () => import('@/views/pages/auth/Login.vue'),
            meta: {
                title: 'Iniciar Sesión',
                isPublic: true // Página pública, no requiere autenticación
            }
        },
        {
            path: '/auth/access',
            name: 'accessDenied',
            component: () => import('@/views/pages/auth/Access.vue'),
            meta: {
                title: 'Acceso Denegado',
                isPublic: true
            }
        },
        {
            path: '/auth/error',
            name: 'error',
            component: () => import('@/views/pages/auth/Error.vue'),
            meta: {
                title: 'Error del Sistema',
                isPublic: true
            }
        },
        {
            path: '/lisencia',
            name: 'lisencia',
            component: () => import('@/views/pages/public/lisencia.vue'),
            meta: {
                title: 'Acuerdo de Licencia de Uso',
                isPublic: true,
                allowAuthenticatedAccess: true // Permite acceso tanto a usuarios autenticados como no autenticados
            }
        }
    ]
});

// Guard de navegación - Verificar autenticación y permisos
router.beforeEach((to, from, next) => {
    // ========== GESTIÓN DE TÍTULOS ==========
    if (to.meta.title) {
        document.title = `${to.meta.title} - NEXUS`;
    } else {
        document.title = 'NEXUS |CNM|';
    }

    const token = getAuthToken();
    const user = getUser();
    const isAuthenticated = !!token && !!user;

    // Si la ruta es pública, permitir acceso
    if (to.meta.isPublic) {
        // Si ya está autenticado y trata de ir al login, redirigir al dashboard
        if (to.name === 'login' && isAuthenticated) {
            next({ path: '/' });
        } else {
            next();
        }
        return;
    }

    // Si la ruta requiere autenticación
    if (to.meta.requiresAuth) {
        // Verificar si hay sesión
        if (!isAuthenticated) {
            // No hay sesión, redirigir al login
            next({
                name: 'login',
                query: { redirect: to.fullPath } // Guardar ruta destino para redirigir después del login
            });
            return;
        }

        // ========== VERIFICACIÓN DE ACEPTACIÓN DE EULA ==========
        // Si el usuario no ha aceptado la EULA, redirigir a la página de licencia
        if (user.EULAAceptada === false && to.path !== '/lisencia') {
            next({
                path: '/lisencia',
                query: { redirect: to.fullPath } // Guardar ruta destino para después de aceptar
            });
            return;
        }

        // ========== VERIFICACIÓN DE ROLES ==========
        // Verificar si el usuario tiene el rol requerido para acceder a esta ruta
        if (to.meta.roles) {
            const hasAccess = hasRoleAccess(to.meta.roles);
            if (!hasAccess) {
                // No tiene el rol requerido
                next({ name: 'accessDenied' });
                return;
            }
        }

        // Si llegó aquí, tiene autenticación y permisos
        next();
        return;
    }

    // Ruta sin restricciones específicas
    next();
});

export default router;

/*
===============================================================================
  GUÍA PARA AGREGAR RUTAS CON RESTRICCIONES DE SEGURIDAD
===============================================================================

SISTEMA DE ROLES:
-----------------
El sistema utiliza nombres de roles en lugar de niveles numéricos para gestionar
el acceso a las rutas. Los roles se obtienen desde el endpoint: api/roles/lista/

ROLES DISPONIBLES:
- ADMINISTRADOR      Control total del sistema
- DB ADMIN           Administración de base de datos
- GERENCIA           Acceso ejecutivo y reportes
- SUP SISTEMAS       Supervisión de sistemas
- TECNICO            Gestión operativa
- SUPERVISOR SALA    Supervisión de operaciones
- ENCARGADO AREA     Gestión de área específica
- PROVEEDOR          Acceso limitado de proveedores
- SOLICITANTE        Reporte de incidencias
- OBSERVADOR         Solo lectura

1. RUTA PÚBLICA (sin autenticación requerida):
   ------------------------------------------
   {
       path: '/about',
       name: 'about',
       component: () => import('@/views/About.vue'),
       meta: { 
           title: 'Acerca de',
           isPublic: true 
       }
   }

2. RUTA PROTEGIDA (requiere estar autenticado, cualquier rol):
   -----------------------------------------------------------
   {
       path: '/profile',
       name: 'profile',
       component: () => import('@/views/Profile.vue'),
       meta: { 
           title: 'Mi Perfil',
           requiresAuth: true,
           roles: ['all']  // Acceso para todos los usuarios autenticados
       }
   }

3. RUTA CON ROL ESPECÍFICO:
   ------------------------
   {
       path: '/admin/users',
       name: 'adminUsers',
       component: () => import('@/views/admin/Users.vue'),
       meta: { 
           requiresAuth: true,
           roles: ['ADMINISTRADOR']  // Solo usuarios con rol ADMINISTRADOR
       }
   }

4. RUTA CON MÚLTIPLES ROLES PERMITIDOS:
   ------------------------------------
   {
       path: '/tickets',
       name: 'tickets',
       component: () => import('@/views/Tickets.vue'),
       meta: { 
           requiresAuth: true,
           roles: ['ADMINISTRADOR', 'SUP SISTEMAS', 'TECNICO']  // Varios roles permitidos
       }
   }

EJEMPLO COMPLETO DE MÓDULO:
---------------------------
{
    path: '/tickets',
    component: AppLayout,
    children: [
        {
            path: '',
            name: 'ticketsList',
            component: () => import('@/views/tickets/List.vue'),
            meta: { 
                requiresAuth: true,
                roles: ['all']  // Todos los usuarios autenticados
            }
        },
        {
            path: 'create',
            name: 'ticketsCreate',
            component: () => import('@/views/tickets/Create.vue'),
            meta: { 
                requiresAuth: true,
                roles: ['TECNICO', 'SUP SISTEMAS', 'ADMINISTRADOR']
            }
        },
        {
            path: 'manage',
            name: 'ticketsManage',
            component: () => import('@/views/tickets/Manage.vue'),
            meta: { 
                requiresAuth: true,
                roles: ['SUP SISTEMAS', 'ADMINISTRADOR']  // Solo supervisores+
            }
        },
        {
            path: ':id',
            name: 'ticketsDetail',
            component: () => import('@/views/tickets/Detail.vue'),
            meta: { 
                requiresAuth: true,
                roles: ['all']
            }
        }
    ]
}

VERIFICAR PERMISOS EN COMPONENTES:
----------------------------------
import { getUser, hasRoleAccess } from '@/service/api';

// Verificar rol específico
const user = getUser();
if (user && user.rol_nombre === 'ADMINISTRADOR') {
    // Mostrar botón de administración
}

// Verificar múltiples roles usando la función auxiliar
if (hasRoleAccess(['ADMINISTRADOR', 'SUP SISTEMAS'])) {
    // Usuario tiene uno de los roles requeridos
}

REDIRECCIÓN DESPUÉS DEL LOGIN:
------------------------------
En tu componente Login.vue, después de login exitoso:

const result = await login(credentials);
if (result.success) {
    const redirectPath = route.query.redirect || '/';
    router.push(redirectPath);
}

===============================================================================
*/
