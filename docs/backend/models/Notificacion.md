# Notificacion / NotificacionUsuario — Sistema de Alertas

**Archivo fuente:** `BackEnd/Notificaciones/models.py`  
**Hereda de:** `ModeloBase`  
**Tablas BD:** `sys_notificaciones`, `sys_notificaciones_usuarios`  
**Propósito:** Motor de notificaciones en tiempo pseudo-real (polling REST cada 45 s). El sistema dirige alertas a audiencias específicas usando una combinación de tres dimensiones: usuario individual, casino y rol.

---

## Modelo: `Notificacion`

### Campos

| Campo | Tipo Django | Nulo | Default | Descripción |
|---|---|---|---|---|
| `titulo` | `CharField(150)` | No | — | Encabezado de la alerta |
| `contenido` | `TextField` | No | — | Mensaje completo |
| `nivel` | `CharField(20)` | No | `'informativa'` | Prioridad visual (choices) |
| `tipo` | `CharField(20)` | No | — | Origen del evento (choices) |
| `usuario_destino` | `ForeignKey(Usuarios)` | Sí | `None` | Si se define: solo este usuario la ve |
| `casino_destino` | `ForeignKey(Casino)` | Sí | `None` | Si se define: usuarios de este casino |
| `rol_destino` | `ForeignKey(Rol)` | Sí | `None` | Si se define junto con `casino_destino`: solo ese rol |
| `es_global` | `BooleanField` | No | `False` | Si `True`: todos los usuarios la ven sin importar casino/rol |
| `es_del_director` | `BooleanField` | No | `False` | Prolonga vida de la notificación a 7 días |
| *+ campos heredados de ModeloBase* | | | | |

### Choices

**`NIVEL_CHOICES`**
| Valor | Etiqueta |
|---|---|
| `urgente` | Urgente (Acción Inmediata) |
| `alerta` | Alerta (Atención Requerida) |
| `informativa` | Informativa (Solo lectura) |

**`TIPO_CHOICES`**
| Valor | Etiqueta |
|---|---|
| `ticket` | Gestión de Tickets |
| `infraestructura` | Incidencia de Infraestructura |
| `wiki` | Nueva Guía en Wiki |
| `sistema` | Aviso del Sistema |
| `DIRECTOR` | Mensaje de Dirección |

### class Meta

```python
db_table = 'sys_notificaciones'
indexes = [models.Index(fields=['creado_en', 'es_del_director'])]
```

---

## Modelo: `NotificacionUsuario`

Tabla de unión que registra si un usuario específico ya leyó una notificación. Permite lectura independiente por usuario.

### Campos

| Campo | Tipo Django | Nulo | Descripción |
|---|---|---|---|
| `notificacion` | `ForeignKey(Notificacion)` | No | Notificación leída |
| `usuario` | `ForeignKey(Usuarios)` | No | Usuario que la leyó |
| `fecha_visto` | `DateTimeField(auto_now_add)` | No | Timestamp de lectura |
| *+ campos heredados de ModeloBase* | | | |

### class Meta

```python
db_table = 'sys_notificaciones_usuarios'
unique_together = [['notificacion', 'usuario']]
indexes = [
    models.Index(fields=['usuario', 'fecha_visto']),
    models.Index(fields=['notificacion', 'usuario']),
]
```

El `unique_together` evita duplicados de lectura (un usuario no puede marcar la misma notificación dos veces).

---

## Lógica de Segmentación

La audiencia de una notificación se determina por combinación de campos:

```
es_global = True                          → Todos los usuarios
usuario_destino = X                       → Solo usuario X
casino_destino = C + rol_destino = R      → Todos con rol R en casino C  
casino_destino = C + rol_destino = null   → Todos en casino C (cualquier rol)
```

El `get_queryset` de `NotificacionViewSet` traduce esto a una query con `Q()`:

```python
Q(es_global=True) |
Q(usuario_destino=user) |
Q(casino_destino=user.casino, rol_destino=user.rol) |
Q(casino_destino=user.casino, rol_destino__isnull=True, usuario_destino__isnull=True)
```

---

## Limpieza Automática

Las notificaciones obsoletas **no** se eliminan en el QuerySet de la vista (eso sería ineficiente). Se delegan a un comando de management programado a medianoche:

```
python manage.py limpiar_notificaciones
```

Las notificaciones con `es_del_director=True` tienen vida de 7 días.
