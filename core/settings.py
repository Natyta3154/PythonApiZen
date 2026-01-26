import os
from pathlib import Path
from dotenv import load_dotenv

# 1. RUTAS Y VARIABLES DE ENTORNO
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'clave-segura-desarrollo')
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = ['*']

# 2. APLICACIONES (El orden es importante)
INSTALLED_APPS = [
    'jazzmin',                    # Panel admin (debe ir antes que admin)
    'cloudinary_storage',         # Almacenamiento nube (debe ir antes que staticfiles)
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Librerías de terceros
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'cloudinary',

    # Aplicaciones locales
    'users',
    'products',
    'blog',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# 3. AUTENTICACIÓN Y SEGURIDAD
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication', # Sube esto al primer lugar
        'users.authentication.CookieTokenAuthentication', 
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# Configuración de CORS y Cookies para Frontend (React)
CORS_ALLOW_CREDENTIALS = True  # Permite envío de cookies
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",   # Puerto por defecto de Vite/React
]

# VITAL: Sin esto, el POST de comprar/ siempre dará 403 aunque el token sea válido
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# 3. Permite que el header CSRF pase a través de CORS
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken", # <--- Agrégalo explícitamente si usas una lista personalizada
    "x-requested-with",
    "withcredentials",
]

# Configuración de Cookies para desarrollo local
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # False porque usas http y no http



CSRF_COOKIE_HTTPONLY = False   # El frontend necesita leerla para seguridad CSRF
SESSION_COOKIE_HTTPONLY = True # Protege la sesión contra ataques XSS

# 4. MIDDLEWARE
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Siempre al principio
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# 5. BASE DE DATOS (MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# 6. ALMACENAMIENTO (Cloudinary)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET')
}

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# 7. INTERNACIONALIZACIÓN Y TEMPLATES
ROOT_URLCONF = 'core.urls'
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 8. CONFIGURACIONES EXTRA (Mercado Pago, Jazzmin)
MP_ACCESS_TOKEN = os.getenv('MP_ACCESS_TOKEN')

JAZZMIN_SETTINGS = {
    "site_title": "Admin Catalogo",
    "dashboard_url": None, 
    "show_sidebar": True,
    "navigation_expanded": True,
}

# La sesión expira cuando se cierra el navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Tiempo de vida de la sesión (ejemplo: 30 minutos de inactividad)
SESSION_COOKIE_AGE = 1800  # 30 minutos en segundos
STATIC_ROOT = BASE_DIR / "staticfiles"
