

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'yilhuf8!02%k(wqj%qmqxwk8xrv2vsvq026lp%n1b+sfyhk^=c'

DEBUG = False

ALLOWED_HOSTS = ["*"]


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
    'autofixture',
    'wkhtmltopdf',
    'reversion',
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
    'common_data.middleware.users.UserTestMiddleware'
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


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '..','database', 'db.sqlite3'),
    }
}

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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True

DATE_FORMAT = "d/m/Y"

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

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': '/',
        'STATS_FILE': os.path.join(BASE_DIR, 'assets', 'webpack-stats.json'),
    }
}

WKHTMLTOPDF_CMD_OPTIONS = {
    'quiet': True,
}


try:
    config_file = open('global_config.json', 'r')
    email_config = json.load(config_file)
except json.JSONDecodeError:
    email_config = {
        'email_host': '',
        'email_port': '',
        'email_user': '',
        'email_password': ''
    }


EMAIL_HOST = email_config['email_host']
EMAIL_PORT =email_config['email_port']
EMAIL_HOST_USER = email_config['email_user']
EMAIL_HOST_PASSWORD = email_config['email_password']
EMAIL_USE_TLS = True
