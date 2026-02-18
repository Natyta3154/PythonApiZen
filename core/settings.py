import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv
import mimetypes
import pymysql
import ssl

# 0. CONFIGURACIÓN INICIAL
pymysql.install_as_MySQLdb()
load_dotenv()

# Evita el error de certificado SSL en desarrollo local
if os.environ.get('DEVELOPMENT', 'False') == 'True':
    ssl._create_default_https_context = ssl._create_unverified_context

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-change-it')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# 1. SEGURIDAD Y HOSTS
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Reconocimiento de tipos de archivo
mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("text/javascript", ".js", True)

# 2. APLICACIONES
INSTALLED_APPS = [
    'jazzmin',

    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # terceros
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'cloudinary',
    'cloudinary_storage',

    # apps
    'users',
    'products',
    'blog',
]


# 3. MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise debe ir justo después de security
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # CORS debe ir ANTES de CommonMiddleware
    'corsheaders.middleware.CorsMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    # CSRF después de sessions
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# 4. CONFIGURACIÓN DE ALMACENAMIENTO (Cloudinary)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET')
}

# 5. ARCHIVOS ESTÁTICOS Y MULTIMEDIA
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.StaticFilesStorage",
    },
}

# --- AÑADIR ESTA LÍNEA PARA COMPATIBILIDAD CON CLOUDINARY ---
STATICFILES_STORAGE = "whitenoise.storage.StaticFilesStorage"

WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True

# 6. BASE DE DATOS (Lógica de prioridad)
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.mysql"),
            "NAME": os.getenv("DB_NAME", "sahum_db"),
            "USER": os.getenv("DB_USER", "root"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "OPTIONS": {
                "charset": os.getenv("DB_CHARSET", "utf8mb4"),
            },
        }
    }

# 7. TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# 8. SEGURIDAD, CORS Y COOKIES
CORS_ALLOW_CREDENTIALS = True

# Obtener orígenes del .env
cors_origins_env = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins_env if origin.strip()]

# Asegurar la URL de Vercel manualmente si no está en el .env
VERCEL_URL = "https://front-aroma-zen.vercel.app"
if VERCEL_URL not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(VERCEL_URL)

# IMPORTANTE: CSRF_TRUSTED_ORIGINS debe ser igual a los orígenes permitidos
CSRF_TRUSTED_ORIGINS = [origin for origin in CORS_ALLOWED_ORIGINS]

if not DEBUG:
    # PRODUCCIÓN (Railway + Vercel)
    SESSION_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
else:
    # DESARROLLO (Localhost)
    SESSION_COOKIE_SAMESITE = 'Lax' 
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False

CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600 # 2 semanas

# 9. CONFIGURACIÓN DE EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASS')
DEFAULT_FROM_EMAIL = f"Aroma Zen <{os.getenv('EMAIL_USER')}>"

# 10. OTROS
ROOT_URLCONF = 'core.urls'
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MP_ACCESS_TOKEN = os.getenv('MP_ACCESS_TOKEN')

# 11. JAZZMIN (Admin UI)
JAZZMIN_SETTINGS = {
    "site_title": "AromaZen Admin",
    "site_header": "AromaZen",
    "site_brand": "AromaZen Panel",
    "welcome_sign": "Bienvenido al Panel de Control de AromaZen",
    "copyright": "AromaZen Ltd",
    "search_model": ["auth.User", "products.Product"],
    "show_ui_builder": True,
}

# 12. REST FRAMEWORK (Movido al final y sin re-declarar CORS)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}
