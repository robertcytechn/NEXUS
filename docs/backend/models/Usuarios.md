# Usuarios — Modelo de Usuario Personalizado

**Archivo fuente:** `BackEnd/Usuarios/models.py`  
**Hereda de:** `AbstractBaseUser`, `ModeloBase`  
**Tabla BD:** `usuarios`  
**`AUTH_USER_MODEL`:** `'Usuarios.Usuarios'`  
**Propósito:** Usuario del sistema con autenticación por token propio (no JWT ni DRF TokenAuth estándar), control de sesiones, asociación a casino y sistema RPG de gamificación.

---

## Campos

| Campo | Tipo Django | Nulo | Único | Default | Descripción |
|---|---|---|---|---|---|
| `username` | `CharField(50)` | No | ✅ | — | Nombre de usuario. Es `USERNAME_FIELD` |
| `email` | `EmailField(150)` | No | ✅ | — | Correo institucional. También es único |
| `nombres` | `CharField(100)` | No | No | — | Nombre(s) del técnico |
| `apellido_paterno` | `CharField(100)` | No | No | — | Primer apellido |
| `apellido_materno` | `CharField(100)` | Sí | No | `None` | Segundo apellido (opcional) |
| `casino` | `ForeignKey(Casino)` | No | No | — | Sede a la que pertenece. `on_delete=PROTECT` |
| `rol` | `ForeignKey(Rol)` | No | No | — | Nivel de acceso. `on_delete=PROTECT` |
| `session_token` | `CharField(255)` | Sí | No | `None` | UUID de sesión activa. Generado al hacer login |
| `refresh_token` | `CharField(255)` | Sí | No | `None` | UUID para renovar sesión |
| `ultima_ip` | `GenericIPAddressField` | Sí | No | `None` | IP registrada en el último login |
| `user_agent` | `TextField` | Sí | No | `None` | Navegador/dispositivo del último acceso |
| `intentos_fallidos` | `PositiveSmallIntegerField` | No | No | `0` | Contador de contraseñas incorrectas. Al llegar a 3 la cuenta se bloquea |
| `requiere_cambio_password` | `BooleanField` | No | No | `False` | Fuerza cambio de contraseña en el próximo acceso |
| `EULAAceptada` | `BooleanField` | No | No | `False` | Acuerdo de licencia de usuario final aceptado |
| `puntos_gamificacion` | `PositiveIntegerField` | No | No | `0` | Puntos **disponibles** para canjear. Sube y baja |
| `puntos_gamificacion_historico` | `PositiveIntegerField` | No | No | `0` | Total **acumulado** de carrera. **Solo sube**, nunca baja. Determina el rango |
| `avatar` | `FileField` | Sí | No | `None` | Imagen de perfil. Ruta dinámica via `custom_upload_to` |
| *+ campos heredados de ModeloBase* | | | | | |

---

## Función `custom_upload_to`

```python
def custom_upload_to(instance, filename):
    base, ext = os.path.splitext(filename)
    user_id = instance.pk if instance.pk else 'new'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{user_id}_{instance.username}_{timestamp}{ext}"
    return os.path.join('usuarios/avatars', new_filename)
```

**Por qué:** Evita colisiones de nombre de archivo. El timestamp garantiza unicidad incluso si se sube el mismo archivo dos veces. La ruta final sería: `media/usuarios/avatars/42_rgarcia_20260224_143000.jpg`.

---

## `UsuarioManager`

Manager personalizado para `create_user`. Normaliza el email (`self.normalize_email`) antes de guardar.

---

## Sistema RPG — Gamificación

### Constante `RANGOS_GAMIFICACION`

Lista de tuplas `(puntos_min, nivel, titulo, insignia)` ordenada de mayor a menor. Se recorre de principio a fin hasta encontrar el primer umbral que el histórico supera:

```python
RANGOS_GAMIFICACION = [
    (4500, 10, 'Leyenda de NEXUS',        '⭐⭐⭐⭐⭐'),
    (3600, 9,  'Guardián del Casino',     '⭐⭐⭐⭐'),
    (2800, 8,  'Arquitecto de Sala',      '🔷🔷🔷🔷'),
    (2100, 7,  'Maestro Electrónico',     '🔷🔷🔷'),
    (1500, 6,  'Técnico Élite',           '🔷🔷'),
    (1000, 5,  'Especialista en Hardware','🔷'),
    (600,  4,  'Operador de Máquinas',    '🔶🔶🔶'),
    (300,  3,  'Técnico de Soporte',      '🔶🔶'),
    (100,  2,  'Aprendiz de Sala',        '🔶'),
    (0,    1,  'Novato de Mantenimiento', '🔩'),
]
```

### `@property rango_gamificacion`

Calcula el rango actual en tiempo de ejecución (no se almacena en BD). Retorna un `dict`:

```python
{
    'nivel': 3,
    'titulo': 'Técnico de Soporte',
    'insignia': '🔶🔶',
    'puntos_min': 300,
    'puntos_sig': 600,       # None si es nivel máximo
    'progreso_pct': 42.5,    # % dentro del nivel actual
}
```

**Fórmula de progreso:**

$$\text{progreso\_pct} = \frac{(\text{pts\_historico} - \text{puntos\_min})}{\text{puntos\_sig} - \text{puntos\_min}} \times 100$$

---

## `save()` — Sincronización de Histórico

```python
def save(self, *args, **kwargs):
    update_fields = kwargs.get('update_fields')
    if self.pk:
        previo = Usuarios.objects.get(pk=self.pk)
        if self.puntos_gamificacion > previo.puntos_gamificacion:
            diferencia = self.puntos_gamificacion - previo.puntos_gamificacion
            self.puntos_gamificacion_historico = (
                previo.puntos_gamificacion_historico + diferencia
            )
            # Asegura que update_fields incluya el histórico
            if update_fields is not None:
                campos = list(update_fields)
                if 'puntos_gamificacion_historico' not in campos:
                    campos.append('puntos_gamificacion_historico')
                kwargs['update_fields'] = campos
    else:
        # Usuario nuevo: histórico = puntos iniciales
        self.puntos_gamificacion_historico = self.puntos_gamificacion
    super().save(*args, **kwargs)
```

**Regla clave:** El histórico NUNCA se decrementa. Si un técnico canjea recompensas, sus `puntos_gamificacion` bajan, pero `puntos_gamificacion_historico` permanece igual y su rango no cambia.

> ⚠️ **Race condition evitada en signals:** Las signals de gamificación usan `F()` + `update()` directo en vez de llamar `save()`. El override de `save()` es un backstop para casos donde sí se use `save()` directo.

---

## Autenticación Personalizada

NEXUS **no usa JWT estándar**. Implementa tokens UUID:

| Flujo | Descripción |
|---|---|
| `POST /usuarios/login/` | Genera `session_token` y `refresh_token` (UUID v4), los guarda en BD |
| `POST /usuarios/refresh/` | Recibe `refresh_token`, genera nuevos tokens |
| Middleware `SessionTokenMiddleware` | Lee `Authorization: Bearer <token>` y autentica al usuario leyendo de BD |

---

## Bloqueo de Cuenta

```
intentos_fallidos >= 3  →  esta_activo = False  →  login retorna 403
```

El administrador reactiva la cuenta poniendo `esta_activo = True` y reseteando `intentos_fallidos = 0`.

---

## class Meta

```python
class Meta:
    db_table = 'usuarios'
    verbose_name = 'Usuario'
    verbose_name_plural = 'Usuarios'
```
