import AppLayout from '@/layout/AppLayout.vue';
import { createRouter, createWebHistory } from 'vue-router';
import { getAuthToken, getUser, hasRoleAccess } from '@/service/api';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            component: AppLayout,
            children: [
                {
                    path: '/',
                    component: () => import('@/views/Dashboard.vue'),
                    meta: {
                        title: 'Escritorio',
                        requiresAuth: true,
                        roles: ['all']
                    }
                },
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
                },
                {
                    path: '/admin/roles',
                    component: () => import('@/views/MandoCentral/Roles.vue'),
                    meta: {
                        title: 'Gestión de Roles',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR']
                    }
                },
                {
                    path: '/admin/casinos',
                    component: () => import('@/views/MandoCentral/Casinos.vue'),
                    meta: {
                        title: 'Casinos y Salas',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR']
                    }
                },
                {
                    path: '/admin/usuarios',
                    component: () => import('@/views/MandoCentral/Usuarios.vue'),
                    meta: {
                        title: 'Usuarios',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR']
                    }
                },
                {
                    path: '/admin/proveedores',
                    component: () => import('@/views/MandoCentral/Proveedores.vue'),
                    meta: {
                        title: 'Proveedores',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR']
                    }
                },
                {
                    path: '/admin/modelos',
                    component: () => import('@/views/MandoCentral/ModelosMaquinas.vue'),
                    meta: {
                        title: 'Modelos',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR']
                    }
                },
                {
                    path: '/admin/maquinas',
                    component: () => import('@/views/MandoCentral/Maquinas.vue'),
                    meta: {
                        title: 'Máquinas',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR']
                    }

                },
                {
                    path: '/admin/tickets',
                    component: () => import('@/views/MandoCentral/Tickets.vue'),
                    meta: {
                        title: 'Tickets',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR']
                    }

                },
                {
                    path: '/admin/bitacora-tecnica',
                    component: () => import('@/views/MandoCentral/BitacoraTecnica.vue'),
                    meta: {
                        title: 'Bitácora Técnica',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR']
                    }
                },
                {
                    path: '/admin/mantenimientos-preventivos',
                    component: () => import('@/views/MandoCentral/MantenimientosPreventivos.vue'),
                    meta: {
                        title: 'Mantenimientos Preventivos',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO', 'GERENCIA', 'SUPERVISOR SALA']
                    }
                },
                {
                    path: '/admin/incidentes-infraestructura',
                    component: () => import('@/views/MandoCentral/IncidentesInfraestructura.vue'),
                    meta: {
                        title: 'Incidentes de Infraestructura',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR']
                    }
                },
                {
                    path: '/centro-servicios/usuarios',
                    component: () => import('@/views/CentroServicios/Usuarios.vue'),
                    meta: {
                        title: 'Usuarios',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'GERENCIA', 'SUPERVISOR SALA']
                    }
                },
                {
                    path: '/centro-servicios/proveedores',
                    component: () => import('@/views/CentroServicios/Proveedores.vue'),
                    meta: {
                        title: 'Proveedores',
                        requiresAuth: true,
                        roles: ['SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ADMINISTRADOR']
                    }
                },
                {
                    path: '/centro-servicios/modelos',
                    component: () => import('@/views/CentroServicios/ModelosMaquinas.vue'),
                    meta: {
                        title: 'Modelos de Máquinas',
                        requiresAuth: true,
                        roles: ['SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ADMINISTRADOR']
                    }
                },
                {
                    path: '/centro-servicios/maquinas',
                    component: () => import('@/views/CentroServicios/Maquinas.vue'),
                    meta: {
                        title: 'Maquinas',
                        requiresAuth: true,
                        roles: ['SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ADMINISTRADOR']
                    }
                },
                {
                    path: '/centro-servicios/tickets',
                    component: () => import('@/views/CentroServicios/Tickets.vue'),
                    meta: {
                        title: 'Tickets',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA']
                    }
                },
                {
                    path: '/centro-servicios/mapa-sala',
                    component: () => import('@/views/CentroServicios/MapaSala.vue'),
                    meta: {
                        title: 'Mapa de Sala',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'GERENCIA', 'SUPERVISOR SALA', 'TECNICO']
                    }
                },
                {
                    path: '/centro-servicios/inventario',
                    component: () => import('@/views/CentroServicios/InventarioSala.vue'),
                    meta: {
                        title: 'Inventario de Sala',
                        requiresAuth: true,
                        roles: ['SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ADMINISTRADOR']
                    }
                },
                {
                    path: '/centro-servicios/mantenimientos-preventivos',
                    component: () => import('@/views/CentroServicios/MantenimientosPreventivos.vue'),
                    meta: {
                        title: 'Mantenimientos Preventivos',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO', 'GERENCIA', 'SUPERVISOR SALA']
                    }
                },
                {
                    path: '/centro-servicios/incidentes-infraestructura',
                    component: () => import('@/views/CentroServicios/IncidenciasInfraestructura.vue'),
                    meta: {
                        title: 'Incidentes de Infraestructura',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA', 'ENCARGADO AREA']
                    }
                },
                {
                    path: '/operatividad/auditorias-externas',
                    component: () => import('@/views/Operatividad/AuditoriasExternas.vue'),
                    meta: {
                        title: 'Auditorías Externas',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO', 'GERENCIA', 'SUPERVISOR SALA']
                    }
                },
                {
                    path: '/operatividad/relevo-turno',
                    component: () => import('@/views/Operatividad/RelevosTurnos.vue'),
                    meta: {
                        title: 'Relevo de Turno',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR', 'DB ADMIN', 'SUP SISTEMAS', 'TECNICO', 'GERENCIA', 'SUPERVISOR SALA']
                    }
                },
                {
                    path: '/evolucion-nexus',
                    component: () => import('@/views/pages/EvolucionNexus.vue'),
                    meta: {
                        title: 'Evolución NEXUS',
                        requiresAuth: true,
                        roles: ['ADMINISTRADOR', 'DB ADMIN', 'GERENCIA', 'SUP SISTEMAS', 'TECNICO', 'SUPERVISOR SALA']
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
