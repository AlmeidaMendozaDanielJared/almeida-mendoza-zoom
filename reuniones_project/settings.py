
from pathlib import Path
from decouple import config 
import os, environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
config = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$1v2dvd^rz3y@=ew!x+$c$#4ni+)fm+%5gg(t++*8nkw$dl!g5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    config('ALLOWED_HOST'),
    'localhost'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reuniones'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'reuniones_project.urls'

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

WSGI_APPLICATION = 'reuniones_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Motor MySQL
        'NAME': config('DB_NAME'),              # Nombre de la base de datos
        'USER': config('DB_USER'),            # Usuario de MySQL
        'PASSWORD': config('DB_PASSWORD'),            # Contraseña del usuario
        'HOST': config('DB_HOST'),                 # Servidor (local)
        'PORT': config('DB_PORT'),                      # Puerto por defecto de MySQL
        'OPTIONS': {
            'charset': 'utf8mb4',           # Soporte para emojis y caracteres especiales
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


ZOOM_CLIENT_ID = config('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = config('ZOOM_CLIENT_SECRET')

ZOOM_OAUTH_AUTHORIZE_URL = config('ZOOM_OAUTH_AUTHORIZE_URL')  # URL autorización
ZOOM_OAUTH_TOKEN_URL = config('ZOOM_OAUTH_TOKEN_URL')  # URL obtener token
ZOOM_API_BASE_URL = config('ZOOM_API_BASE_URL')  # Endpoint base API v2

ZOOM_REDIRECT_URI = config('ZOOM_REDIRECT_URI')

LOGIN_URL='inicio'
LOGIN_REDIRECT_URL='lista_reuniones'
LOGOUT_REDIRECT_URL='inicio'

