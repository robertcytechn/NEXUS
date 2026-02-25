# Proveedor — Catálogo de Empresas de Servicios

**Archivo fuente:** `BackEnd/Proveedores/models.py`  
**Hereda de:** `ModeloBase`  
**Tabla BD:** `proveedores`  
**Propósito:** Registra las empresas externas que prestan servicios al casino (internet, UPS, seguridad, etc.) y sus credenciales de acceso a sus propios sistemas. Vinculado por casino —cada sede mantiene su propio directorio de proveedores.

---

## Campos

| Campo | Tipo Django | Nulo | Descripción |
|---|---|---|---|
| `casino` | `ForeignKey(Casino)` | No | Sede a la que pertenece. `CASCADE` |
| `nombre` | `CharField(150)` | No | Razón social o nombre comercial |
| `rfc` | `CharField(13)` | No | Registro Federal de Contribuyentes |
| `email_corporativo` | `EmailField` | No | Email de contacto principal |
| `telefono_soporte` | `CharField(20)` | Sí | Línea directa de soporte técnico |
| `email_soporte` | `EmailField` | Sí | Email del departamento de soporte |
| `nombre_contacto_tecnico` | `CharField(150)` | Sí | Nombre del técnico asignado por el proveedor |
| `username` | `CharField(50)` | No | Usuario de acceso al sistema del proveedor |
| `password` | `CharField(100)` | No | Contraseña de acceso (⚠️ sin cifrado) |
| *+ campos heredados de ModeloBase* | | | |

---

## Restricciones

```python
unique_together = [
    ('casino', 'nombre'),     # No dos proveedores con el mismo nombre en un casino
    ('casino', 'username'),   # No dos usuarios iguales de proveedor en un casino
]
```

---

## ⚠️ Nota de Seguridad

El campo `password` almacena la contraseña **en texto plano**. Esto es deliberado: el objetivo es guardar las credenciales de acceso al portal del proveedor externo (no del sistema NEXUS), para que el técnico pueda consultarlas directamente desde la plataforma. En un entorno de producción seria recomendable encriptar este campo con algo como `django-encrypted-model-fields`.

---

## class Meta

```python
class Meta:
    db_table = 'proveedores'
    verbose_name = "Proveedor"
    verbose_name_plural = "Proveedores"
```
