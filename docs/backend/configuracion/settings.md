# Configuración de Django — settings.py

**Archivo fuente:** `BackEnd/BackEnd/settings.py`

---

## Variables de Entorno y Seguridad

```python
SECRET_KEY = 'django-insecure-...'   # ⚠️ Cambiar en producción
DEBUG = True                          # ⚠️ False en producción
ALLOWED_HOSTS = ['*']                 # ⚠️ Restringir en producción
```

> **Pendiente para producción:** `SECRET_KEY` desde variable de entorno, `DEBUG=False`, `ALLOWED_HOSTS` con IPs/dominios específicos.

---

## Aplicaciones Instaladas

### `OWN_APPS` — Aplicaciones propias del proyecto

```python
OWN_APPS = [
    'ModelBase',        # Modelo abstracto base
    'Roles',            # Catálogo de roles
    'Casinos',          # Sucursales/casinos
    'Usuarios',         # Usuarios con RPG
    'Proveedores',      # Catálogo de proveedores
    'ModelosMaquinas',  # Modelos de máquinas
    'Denominaciones',   # Denominaciones monetarias
    'Maquinas',         # Máquinas de casino
    'Tickets',          # Sistema de tickets
    'BitacoraTecnica',  # Registro de intervenciones
    'MantenimientosPreventivos',
    'TareasEspeciales',
    'InventarioSala',
    'IncidenciasInfraestructura',
    'RelevosTurnos',
    'Wiki',             # Wiki técnica
    'AuditoriasExternas',
    'Notificaciones',
    'EvolucionNexus',   # Cambios de versión del sistema
    'Menus',            # Menús dinámicos por rol
    'AuditoriaGlobal',  # Logs de auditoría
    'Gamificacion',     # Sistema RPG de recompensas
]
```

### `THIRD_PARTY_APPS`

| Paquete | Uso |
|---|---|
| `rest_framework` | API REST |
| `corsheaders` | CORS para el frontend Vue |
| `django_filters` | Filtros en ViewSets |

---

## Modelo de Usuario Personalizado

```python
AUTH_USER_MODEL = 'Usuarios.Usuarios'
```

Django usa `Usuarios.Usuarios` (que extiende `AbstractBaseUser`) en lugar del `User` por defecto. Esto afecta todas las referencias FK con `settings.AUTH_USER_MODEL`.

---

## Orden del Middleware (crítico)

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',           # CORS antes de common
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'Usuarios.middleware.SessionTokenMiddleware',      # ← Lee Bearer token
    'AuditoriaGlobal.middleware.AuditMiddleware',      # ← Captura usuario en ThreadLocal
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

**Orden crítico:**
1. `CorsMiddleware` debe ir **antes** de `CommonMiddleware`
2. `SessionTokenMiddleware` debe ir **después** de `AuthenticationMiddleware` para poder sobreescribir `request.user`
3. `AuditMiddleware` debe ir **después** de `SessionTokenMiddleware` para que `request.user` ya esté correctamente asignado

---

## Base de Datos

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ot',
        'USER': 'robert',
        'HOST': 'cytechn.ddns.net',
        'PORT': '3306'
    }
}
```

**MySQL** en servidor remoto `cytechn.ddns.net:3306`, base de datos `ot`. Se requiere el driver `mysqlclient` instalado.

### Conexión local alternativa (comentada)

```python
# 'HOST': '192.168.1.69',  # IP local para trabajo en oficina
```

---

## Configuración de REST Framework

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'Usuarios.authentication.SessionTokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [],          # Sin permisos globales — cada vista define los suyos
    'UNAUTHENTICATED_USER': 'django.contrib.auth.models.AnonymousUser',
    'EXCEPTION_HANDLER': 'BackEnd.exceptions.custom_exception_handler',
}
```

| Configuración | Valor | Razón |
|---|---|---|
| Auth class | `SessionTokenAuthentication` | Token UUID en header `Authorization: Bearer` |
| Permission classes | `[]` vacío | Cada ViewSet declara `permission_classes` individualmente |
| Exception handler | `custom_exception_handler` | Normalizar todos los errores a `{"error": "..."}` |

---

## CORS y CSRF

```python
CORS_ALLOW_ALL_ORIGINS = True           # ⚠️ Restringir en producción
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_HTTPONLY = False            # Necesario para Vue con localStorage
CSRF_COOKIE_SECURE = False             # True en producción con HTTPS
```

`CSRF_TRUSTED_ORIGINS` incluye:
- `http://localhost:5173` — Vite dev server
- `http://localhost:8000` — Django local
- `http://192.168.1.69:5173/8000` — Red local de oficina
- `http://cytechn.ddns.net:8000` — Servidor remoto

> Los endpoints REST usan autenticación Bearer, por lo que CSRF es secundario. Aun así se configura por las vistas que puedan usarlo.

---

## Internacionalización

```python
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True
```

**`USE_TZ = True`:** Todos los `DateTimeField` usan timezone-aware datetimes. Se almacenan en UTC en la DB y se muestran en `America/Mexico_City`.

---

## Archivos Media

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

Los archivos de imagen (avatares, PDFs de Wiki) se sirven desde `/media/` en desarrollo. En producción se configurará Nginx para servir archivos estáticos.
