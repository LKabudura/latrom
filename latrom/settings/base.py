"""
Django settings for latrom project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import json

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yilhuf8!02%k(wqj%qmqxwk8xrv2vsvq026lp%n1b+sfyhk^=c'

# SECURITY WARNING: don't run with debug turned on in production!



# Application definition
USER_APPS = [
    'common_data',
    'invoicing',
    'inventory',
    'employees',
    'accounting',
    'services',
    'planner',
    'messaging',
    'manufacturing'
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'webpack_loader',
    'django_filters',
    'crispy_forms',
    'wkhtmltopdf',
    'reversion',
    'background_task',
    'dbbackup',
    'formtools'
    
] + USER_APPS

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

LOGIN_REQUIRED_FOR_CRUD = True
PROJECT_NAME = 'Smart business solutions'

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY =True
SESSION_COOKIE_AGE = 600 #10 minutes
SESSION_SAVE_EVERY_REQUEST = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'common_data.middleware.license.LicenseMiddleware',
    'common_data.middleware.users.UserTestMiddleware',
    'common_data.middleware.events.EventReminderMiddleware',
]

ROOT_URLCONF = 'latrom.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'latrom.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Harare'

USE_I18N = True

USE_L10N = False

USE_TZ = False

DATE_FORMAT = "d/m/Y"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets', 'bundles'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'common_data', 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'

CRISPY_TEMPLATE_PACK = 'bootstrap4'
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/base/workflow'



#change for each installation
#WKHTMLTOPDF_CMD = os.path.join(BASE_DIR, 'wkhtmltopdf', 'bin')

'''WKHTMLTOPDF_CMD_OPTIONS = {
    'quiet': True,
}'''

#EMAIL
try:
    config_file = open(os.path.join(BASE_DIR, 'global_config.json'), 'r')
    email_config = json.load(config_file)
except json.JSONDecodeError:
    email_config = {
        'email_host': '',
        'email_port': '',
        'email_user': '',
        'email_password': ''
    }


DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'

CACHES = {
    'default': {
		'BACKEND': \
			'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'djangoq-localmem',
    }
}

MAX_ATTEMPTS = 1

