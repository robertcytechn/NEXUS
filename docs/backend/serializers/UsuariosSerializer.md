# UsuariosSerializer — Serialización Completa del Usuario

**Archivo fuente:** `BackEnd/Usuarios/serializers.py`  
**Modelos:** `Usuarios`  
**Propósito:** Serializer principal del sistema. Expone los datos del usuario incluyendo información calculada de relaciones y el sistema de gamificación RPG.

---

## Serializers Disponibles

| Clase | Propósito |
|---|---|
| `UsuariosSerializer` | CRUD completo + gamificación |
| `UsuarioLoginSerializer` | Solo recibe `username` + `password` |
| `UsuarioRefreshSerializer` | Solo recibe `refresh_token` |

---

## `UsuariosSerializer`

### Campos Expuestos

| Campo | Origen | Acceso | Descripción |
|---|---|---|---|
| `id` | Modelo | R/W | PK del usuario |
| `username` | Modelo | R/W | Nombre de usuario |
| `email` | Modelo | R/W | Correo electrónico |
| `nombres` | Modelo | R/W | Nombres del técnico |
| `apellido_paterno` | Modelo | R/W | Primer apellido |
| `apellido_materno` | Modelo | R/W | Segundo apellido |
| `nombre_completo` | `SerializerMethodField` | Solo lectura | Concatenación calculada |
| `casino` | Modelo | R/W | FK (ID del casino) |
| `casino_nombre` | `source='casino.nombre'` | Solo lectura | Nombre del casino |
| `rol` | Modelo | R/W | FK (ID del rol) |
| `rol_nombre` | `source='rol.nombre'` | Solo lectura | Nombre del rol |
| `esta_activo` | Modelo | R/W | Bandera de activación |
| `creado_en` | Modelo | Solo lectura | Timestamp de creación |
| `modificado_en` | Modelo | Solo lectura | Timestamp de modificación |
| `creado_por` | Modelo | Solo lectura | Username del creador |
| `modificado_por` | Modelo | Solo lectura | Username del modificador |
| `ultima_ip` | Modelo | Solo lectura | Última IP de acceso |
| `user_agent` | Modelo | Solo lectura | Navegador del último acceso |
| `requiere_cambio_password` | Modelo | R/W | Flag de cambio de contraseña |
| `password` | Modelo | **Solo escritura** | Contraseña (hasheada en `create`/`update`) |
| `session_token` | Modelo | Solo lectura | Token de sesión activa |
| `refresh_token` | Modelo | Solo lectura | Token de renovación |
| `intentos_fallidos` | Modelo | Solo lectura | Contador de errores de login |
| `EULAAceptada` | Modelo | Solo lectura | Flag de EULA |
| `avatar` | `SerializerMethodField` | R/W | URL absoluta del avatar |
| `puntos_gamificacion` | Modelo | R/W | Puntos disponibles |
| `puntos_gamificacion_historico` | Modelo | Solo lectura | Histórico acumulado |
| `rango_gamificacion` | `SerializerMethodField` | Solo lectura | Dict con nivel, título, emblema, progreso |

---

## Métodos Personalizados

### `get_nombre_completo`
```python
def get_nombre_completo(self, obj):
    return f"{obj.nombres} {obj.apellido_paterno} {obj.apellido_materno or ''}".strip()
```
Concatena los tres campos de nombre en un string limpio. El `.strip()` elimina el espacio extra si no hay apellido materno.

### `get_avatar`
```python
def get_avatar(self, obj):
    if not obj.avatar:
        return None
    request = self.context.get('request')
    if request:
        return request.build_absolute_uri(obj.avatar.url)
    # Fallback sin request (ej. en el login)
    return f"{settings.MEDIA_URL}{obj.avatar.name}"
```

**Por qué el fallback:** El endpoint de login no siempre pasa `context={'request': request}`. En esos casos, se construye la URL manualmente usando `MEDIA_URL`. Esto garantiza que el frontend siempre reciba una URL funcional.

### `get_rango_gamificacion`
```python
def get_rango_gamificacion(self, obj):
    return obj.rango_gamificacion  # Delega a @property del modelo
```

---

## Métodos `create` y `update`

```python
def create(self, validated_data):
    password = validated_data.pop('password', None)
    instance = self.Meta.model(**validated_data)
    if password:
        instance.set_password(password)   # Hashea con bcrypt/PBKDF2
    instance.save()
    return instance

def update(self, instance, validated_data):
    password = validated_data.pop('password', None)
    for attr, value in validated_data.items():
        setattr(instance, attr, value)
    if password:
        instance.set_password(password)
    instance.save()
    return instance
```

**Por qué se hace manualmente en vez de usar `super()`:** Se necesita interceptar el campo `password` antes de asignarlo, porque `set_password()` hashe la contraseña correctamente usando el sistema de Django. Si se asignara directamente (`instance.password = "1234"`), se guardaría en texto plano.

---

## `UsuarioLoginSerializer`

```python
class UsuarioLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
```

Serializer simple de input. No usa `ModelSerializer`. El `write_only=True` en password evita que se incluya en la respuesta.

---

## `UsuarioRefreshSerializer`

```python
class UsuarioRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)
```

Solo valida que el campo esté presente. La lógica de verificar si el token es válido la hace la vista.
