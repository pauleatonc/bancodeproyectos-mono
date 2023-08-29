import environ
import os
from .base import *

# we load the variables from the .env file to the environment
env = environ.Env()
environ.Env.read_env()

# SECURITY WARNING: keep the secret key used in production secret!
# Your secret key
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = [ 'qabancodeproyectos.subdere.gob.cl', 'www.qabancodeproyectos.subdere.gob.cl', ]

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    # Base de datos de aplicación
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env("DB_NAME"),
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': 'banco_db',
        'PORT': env("DB_PORT"),
    },
        # Base de datos externa
    'externaldb': {
        'ENGINE': 'django.db.backends.mysql', # Necesita instalación de mysqlclient (en reqirements.txt)
        'NAME': env("SEL_DB_NAME"),
        'USER': env("SEL_DB_USER"),
        'PASSWORD': env("SEL_DB_PASSWORD"),
        'HOST': env("SEL_DB_HOST"),
        'PORT': env("SEL_DB_PORT"),
    }

}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static', 'banco_proyectos')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/banco_proyectos')
MEDIA_URL = '/media/'

RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY")
RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY")

# Sendgrid
SENDGRID_API_KEY = env("SENDGRID_API_KEY")
ADMIN_EMAIL = env("ADMIN_EMAIL")
NOREPLY_EMAIL = env("NOREPLY_EMAIL")


# Trusted origins for the CSRF validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# If we are behind proxy with https we trust the header defined here.
# https://docs.djangoproject.com/en/4.2/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = env.tuple('SECURE_PROXY_SSL_HEADER', default=None)
