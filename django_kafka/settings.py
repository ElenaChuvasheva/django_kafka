import os
import sys
from pathlib import Path

from dotenv import load_dotenv

TEST_RUNNER = 'tests.runner.DjangoKafkaRunner'
TEST_MODE = 'test' in sys.argv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', default='very_$ecret!_key_@!!11')

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'web']
CSRF_TRUSTED_ORIGINS = ['http://*.127.0.0.1', 'http://localhost', 'http://localhost:81']

USE_DJANGO_JQUERY = True


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'django_extensions',

    'application',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'application.middlewares.kafka_save_response_middleware',
]

ROOT_URLCONF = 'django_kafka.urls'

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

WSGI_APPLICATION = 'django_kafka.wsgi.application'


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
        'default': {
            'ENGINE': os.getenv('DB_ENGINE', default='django.db.backends.postgresql_psycopg2'),
            'NAME': os.getenv('DB_NAME', default='postgres'),
            'USER': os.getenv('POSTGRES_USER', default='postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='abcd1234'),
            'HOST': os.getenv('DB_HOST', default='db'),
            'PORT': os.getenv('DB_PORT', default='5432')
        }
    }
print(DATABASES['default'])

KAFKA_HOST = os.getenv('KAFKA_HOST', default='host.docker.internal')
KAFKA_PORT = os.getenv('KAFKA_PORT', default='19092')

if not TEST_MODE:
    UPDATES_TOPIC = os.getenv('UPDATES_TOPIC', default='updates')
    DELETE_TOPIC = os.getenv('DELETE_TOPIC', default='deletions')
    OBJECTS_TO_KAFKA_TOPIC = os.getenv('OBJECTS_TO_KAFKA_TOPIC', default='some_model_objects')
    REST_LOG_TOPIC = os.getenv('REST_LOG_TOPIC', default='django-responses')
    UPCREATE_CONSUMER_GROUP_ID = 'pythonupcreate_consumer'
    DELETE_CONSUMER_GROUP_ID = 'pythondelete_consumer'
else:
    UPDATES_TOPIC = 'updates_tests'
    DELETE_TOPIC = 'deletions_tests'
    OBJECTS_TO_KAFKA_TOPIC = 'some_model_objects_tests'
    REST_LOG_TOPIC = 'django-responses_tests'
    UPCREATE_CONSUMER_GROUP_ID = 'pythonupcreate_consumer_tests'
    DELETE_CONSUMER_GROUP_ID = 'pythondelete_consumer_tests'


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


LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
