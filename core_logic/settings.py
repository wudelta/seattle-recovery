# ======================================================================
# FILE: core_logic/settings.py (PATCH 1 OF 3 ALTERATION)
# START: ENVIRONMENT INITIALIZATION & APP MANIFEST REGISTER
# ======================================================================
import environ
from pathlib import Path
import os
from neomodel import config as neomodel_config

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()

env_file_path = os.path.join(BASE_DIR, '.env')
if not os.path.exists(env_file_path):
    env_file_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_file_path):
    environ.Env.read_env(env_file_path)

SECRET_KEY = env('DJANGO_SECRET_KEY', default="django-insecure-fallback-key-token")
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', 'django_app', '*'])

# Baseline system components
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_neomodel',
    'core_logic',
    'users',
]

# Structural Split Invariant: Only load the domain app relevant to this running node container
CURRENT_CONTAINER_TARGET = os.getenv('DB_NAME')

if CURRENT_CONTAINER_TARGET == 'hopehub_db':
    INSTALLED_APPS.append('hopehub')
elif CURRENT_CONTAINER_TARGET == 'aurora_db':
    INSTALLED_APPS.append('aurora')
else:
    # Local fallback/management command environment catch
    INSTALLED_APPS.extend(['aurora', 'hopehub'])
# ======================================================================
# END: ENVIRONMENT INITIALIZATION & APP MANIFEST REGISTER (PATCH 1 OF 3)
# ======================================================================

# ====================================================================== #
# FILE: core_logic/settings.py (PATCH 2 OF 3)                            #
# START: MIDDLEWARE PIPELINES, CRISPY UI CONFS, & TEMPLATE LOOPS         #
# ====================================================================== #
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core_logic.urls'

# ==============================================================================
# CRISPY FORMS FOR BOOTSTRAP 5 LAYOUT DESIGN
# ==============================================================================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_CONFIG = {
    "template_pack": "bootstrap5",
}

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

WSGI_APPLICATION = 'core_logic.wsgi.application'
ASGI_APPLICATION = 'core_logic.asgi.application'
# ====================================================================== #
# END: MIDDLEWARE PIPELINES, CRISPY UI CONFS, & TEMPLATE LOOPS (PATCH 2 OF 3) #
# ====================================================================== #


# ======================================================================
# FILE: core_logic/settings.py (PATCH 3 OF 3)
# START: DATA STORES, NEO4J LOOPBACK, COOKIE & STATIC PATH PARAMS
# ======================================================================
# Databases
DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='seattle_postgres'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# ==============================================================================
# GRAPH DATABASE CONFIGURATION (NEO4J TANDEM LAYER)
# ==============================================================================
# Dynamically builds the production-ready connection URI string using your auth parameters
NEO4J_SCHEME = "bolt"
NEO4J_USER = env('NEO4J_USER', default='neo4j')
NEO4J_PASSWORD = env('NEO4J_PASSWORD')
NEO4J_HOST = env('NEO4J_HOST', default='seattle_neo4j')
NEO4J_PORT = env('NEO4J_PORT', default='7687')

# REVERTED: Locked in the standard v5 uppercase string connection mapping variable
neomodel_config.DATABASE_URL = f"{NEO4J_SCHEME}://{NEO4J_USER}:{NEO4J_PASSWORD}@{NEO4J_HOST}:{NEO4J_PORT}"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = 'media/'

# Secure Cookie Infrastructure Parameters
CSRF_COOKIE_PATH = '/'
SESSION_COOKIE_PATH = '/'
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:9000",
    "http://127.0.0.1:9000",
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [{
                "address": "redis://seattle_redis:6379/0",
                "socket_timeout": 15, # Generous timeout for 2-core systems
                "socket_connect_timeout": 15,
            }],
        },
    },
}

GEMINI_API_KEY = env("GEMINI_API_KEY", default="")

# Register the custom UUID user model globally across the monorepo
AUTH_USER_MODEL = 'users.CustomUser'
# ======================================================================
# END: DATA STORES, NEO4J LOOPBACK, COOKIE & STATIC PATH PARAMS (PATCH 3 OF 3)
# ======================================================================
