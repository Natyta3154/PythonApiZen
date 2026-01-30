import os
from pathlib import Path
from dotenv import load_dotenv

# 1. RUTAS Y VARIABLES DE ENTORNO
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-2-&=d=k!(hxe-=+8mrzjsw4!ou=hc)9liihg32bp#ci&z6eu7&')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 2. APLICACIONES
INSTALLED_APPS = [
    'cloudinary_storage',         # Debe ir antes de staticfiles
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

# 3. MIDDLEWARE
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Agregado para servir CSS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 4. CONFIGURACIÓN DE ALMACENAMIENTO (ESTO ES LO IMPORTANTE)
# Separamos Media (Cloudinary) de Static (Local)
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
        # Usamos el básico de Django para evitar errores de archivos faltantes
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# 5. AUTENTICACIÓN Y API
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'users.authentication.CookieTokenAuthentication', 
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# 6. BASE DE DATOS
#DATABASES = {
 #   'default': {
  #      'ENGINE': 'django.db.backends.mysql',
   #     'NAME': os.getenv('DB_NAME'),
    #    'USER': os.getenv('DB_USER'),
     #   'PASSWORD': os.getenv('DB_PASSWORD'),
      #  'HOST': os.getenv('DB_HOST'),
       # 'PORT': os.getenv('DB_PORT'),
    #}
#}
import dj_database_url

# 6. BASE DE DATOS
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Si por alguna razón no hay DATABASE_URL, usamos la configuración manual de MySQL (como respaldo local)
if not DATABASES['default']:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
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

# 8. SEGURIDAD Y COOKIES
CORS_ALLOW_CREDENTIALS = True

# Permitir orígenes desde variables de entorno
cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins if origin.strip()]

csrf_origins = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins if origin.strip()]

CORS_ALLOW_HEADERS = ["accept", "authorization", "content-type", "user-agent", "x-csrftoken", "x-requested-with", "withcredentials"]

SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# 9. OTROS
ROOT_URLCONF = 'core.urls'
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MP_ACCESS_TOKEN = os.getenv('MP_ACCESS_TOKEN')