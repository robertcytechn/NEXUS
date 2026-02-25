# Rol — Catálogo de Roles del Sistema

**Archivo fuente:** `BackEnd/Roles/models.py`  
**Hereda de:** `ModeloBase`  
**Tabla BD:** `roles`  
**Propósito:** Catálogo maestro de los niveles de acceso. Cada `Usuario` apunta a un `Rol`, y el sistema usa el campo `rol.nombre` como llave discriminante para aplicar permisos en vistas y filtros.

---

## Campos

| Campo | Tipo Django | Nulo | Único | Default | Descripción |
|---|---|---|---|---|---|
| `nombre` | `CharField(50)` | No | ✅ | — | Identificador del rol. Usado directamente en lógica de permisos |
| `descripcion` | `TextField` | Sí | No | `None` | Descripción libre de las responsabilidades del rol |
| *+ campos heredados de ModeloBase* | | | | | |

---

## Roles predefinidos del sistema

> Estas cadenas son los valores exactos que deben existir en la tabla `roles`. El sistema compara `rol.nombre` contra ellos en lógica de negocio:

| `nombre` | Propósito |
|---|---|
| `ADMINISTRADOR` | Acceso total. Puede configurar casinos, usuarios y parámetros del sistema |
| `SUP SISTEMAS` | Supervisor técnico. Recibe notificaciones críticas de infraestructura y tickets |
| `TECNICO` | Usuario operativo. Agenda en gamificación; gestiona tickets y mantenimientos |
| `GERENCIA` | Acceso a reportes. Puede crear y entregar recompensas de gamificación |
| `PROVEEDOR` | Acceso restringido. Solo visualización relacionada con sus máquinas |
| `OBSERVADOR` | Solo lectura. Sin permisos de modificación |

---

## Uso en lógica de negocio

El `nombre` del rol se consulta directamente en múltiples puntos:

```python
# En signals de gamificación (quién gana puntos)
ROLES_GAMIFICACION = {'TECNICO', 'SUP SISTEMAS'}
if rol_nombre not in ROLES_GAMIFICACION:
    return None  # No acumula puntos

# En vistas de usuarios (exclusión de admin)
queryset.exclude(rol__nombre='ADMINISTRADOR')

# En signals de infraestructura (quién recibe notificaciones)
nombres_rol = ['SUP SISTEMAS', 'GERENCIA'] if es_critica else ['SUP SISTEMAS']
```

---

## class Meta

```python
class Meta:
    db_table = 'roles'
    verbose_name = "Rol"
    verbose_name_plural = "Roles"
    ordering = ['nombre']
```
