# -*- coding: utf-8 -*-
import os
from datetime import timedelta

from .assets import ASSETS


ASSETS_MANAGER_FILES = ASSETS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'from django.core.management.utils import get_random_secret_key; get_random_secret_key()'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
	# core
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	# vendor
	'compressor',
	'django_ajax_utils',
	'django_assets_manager',
	# apps
	'accounts',
	'feeds',
	'web',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django_ajax_utils.pjax.Middleware',
	'web.middlewares.ThreadLocalMiddleware',
	'template_dynamicloader.middleware.TemplateSwitchMiddleware',
]

ROOT_URLCONF = 'web.urls'

BUILTINS_EXTRA = [
	'django.contrib.staticfiles.templatetags.staticfiles',
	'django.templatetags.i18n',
	'django.templatetags.l10n',
	'compressor.templatetags.compress',
]

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, 'templates'),],
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
			'loaders': [
				'django_ajax_utils.pjax.Loader',
				'template_dynamicloader.loader.Loader',
				'django.template.loaders.filesystem.Loader',
				'django.template.loaders.app_directories.Loader',
			],
			'builtins': BUILTINS_EXTRA,
		},
	},
]

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'entry_list'
LOGOUT_REDIRECT_URL = 'accounts:login'

WSGI_APPLICATION = 'web.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
	}
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{ 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
	{ 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
	{ 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
	{ 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

PJAX_INCLUDE_URLPATTERNS = [r'.*']
PJAX_EXCLUDE_URLPATTERNS = [r'^admin:.*$']

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '..', 'static_assets', 'static')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	'compressor.finders.CompressorFinder',
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'static_assets', 'media')

COMPRESS_ENABLED = True
COMPRESS_PRECOMPILERS = (
	('text/x-scss', 'django_libsass.SassCompiler'),
)

LIBSASS_OUTPUT_STYLE = 'nested'
LIBSASS_SOURCE_COMMENTS = True

BROKER_URL = 'redis://localhost:6379/0'

CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'UTC'
CELERYBEAT_SCHEDULE = {
	'synchronize-feeds': {
		'task': 'feeds.tasks.synchronize',
		'schedule': timedelta(seconds=1800),
	},
	'clean-remember-tokens': {
		'task': 'accounts.tasks.clean_remember_tokens',
		'schedule': timedelta(seconds=1800),
	},
}

DYNAMIC_TEMPLATES = ('default', 'newspaper',)
