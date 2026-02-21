from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-2r7uo@@oxv*x-cw)#e3%6e-9-(^23*)6z*(3h)w*=sov7c6z1%'
DEBUG = True
ALLOWED_HOSTS = ['*']  # Permite todas las IPs - en producción especifica las IPs permitidas
OWN_APPS = [
    'ModelBase',
    'Roles',
    'Casinos',
    'Usuarios',
    'Proveedores',
    'ModelosMaquinas',
    'Denominaciones',
    'Maquinas',
    'Tickets',
    'BitacoraTecnica',
    'MantenimientosPreventivos',
    'TareasEspeciales',
    'InventarioSala',
    'IncidenciasInfraestructura',
    'RelevosTurnos',
    'Wiki',
    'AuditoriasExternas',
    'Notificaciones',
    'EvolucionNexus',
    'Menus',
    'AuditoriaGlobal',
]

AUTH_USER_MODEL = 'Usuarios.Usuarios'


THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_filters',
]

INIT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

INSTALLED_APPS = INIT_APPS + THIRD_PARTY_APPS + OWN_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'Usuarios.middleware.SessionTokenMiddleware',  # Middleware personalizado para session_token
    'AuditoriaGlobal.middleware.AuditMiddleware',  # <--- Middleware de captura ThreadLocal
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BackEnd.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'BackEnd.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ot',
        'USER': 'robert',
        'PASSWORD': 'Chido1993$',
        # usar ip en local en lugar de localhost para usar bd del servidor
        #'HOST': '192.168.1.69',
        #usar liga http cuando se trabaja furea de oficina y se tiene acceso a la base de datos a través de un dominio con puerto específico
        'HOST': 'cytechn.ddns.net',
        'PORT': '3306'
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# CONFIGURACIÓN DE CORS Y CSRF
# ============================================================================

# Permitir peticiones desde el frontend Vue (localhost:5173)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Orígenes confiables para CSRF (necesario para PATCH/POST/DELETE desde frontend)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    # Ip de fromacion local
    'http://192.168.1.69:5173',
    'http://192.168.1.69:8000',
    # Dominio No-IP con puertos específicos
    'http://cytechn.ddns.net:',
    'http://cytechn.ddns.net:8000',
    'https://cytechn.ddns.ne',  # Si usas HTTPS
    'https://cytechn.ddns.net:8000',
]

# Como usamos autenticación basada en tokens (Bearer), 
# podemos excluir las APIs REST de verificación CSRF
# El token ya provee la seguridad necesaria
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False  # True en producción con HTTPS

# ============================================================================
# CONFIGURACIÓN DE REST FRAMEWORK
# ============================================================================

REST_FRAMEWORK = {
    # Autenticación personalizada basada en session_token (Bearer token desde localStorage)
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'Usuarios.authentication.SessionTokenAuthentication',
    ],
    # Sin permisos por defecto, cada vista define sus propios permisos
    'DEFAULT_PERMISSION_CLASSES': [],
    # Usuario no autenticado se trata como AnonymousUser
    'UNAUTHENTICATED_USER': 'django.contrib.auth.models.AnonymousUser',
    # Manejador global de excepciones para estandarizar las respuestas JSON
    'EXCEPTION_HANDLER': 'BackEnd.exceptions.custom_exception_handler',
}
