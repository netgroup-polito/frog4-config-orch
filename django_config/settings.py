"""
Django settings for api project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import datetime
from configparser import SafeConfigParser #ConfigParser  in python 2
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

SECRET_KEY = "abc123"
DEBUG = True
from corsheaders.defaults import default_headers
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'rest_framework',
    'configuration_service_core',
	'rest_framework_swagger',
    'corsheaders',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'django_config.urls'

WSGI_APPLICATION = 'django_config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
 
        'ENGINE': 'django.db.backends.mysql', 
        'NAME':'frog4_datastore',
        'USER': 'datastore',
        'PASSWORD': 'datastorePWD',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

"""
REST_FRAMEWORK = {
	'DEFAULT_PARSER_CLASSES': (
		'rest_framework.parsers.JSONParser',
		'rest_framework.parsers.FileUploadParser',
		'rest_framework.parsers.MultiPartParser',
	)
}
"""		

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.abspath('.'), 'static')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

parser = SafeConfigParser()
parser.read(os.environ["CONFIGURATION_SERVICE_CONFIG_FILE"])
repository = parser.get('repository', 'repository')
expiration = int(parser.get('repository', 'upload_expiration_hrs'))

#MEDIA_ROOT = parser.get('General', 'IMAGE_DIR') if repository == "LOCAL_FILES" else ''

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = default_headers + (
    'content-range',
    'content-disposition',
)
