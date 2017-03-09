"""
Django settings for deploy_ec2 project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""
import json
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('MODE') == 'DEBUG'
STORAGE_S3 = os.environ.get('STORAGE') == 'S3' or DEBUG is False
DB_RDS = os.environ.get('DB') == 'RDS'
print('DEBUG: {}'.format(DEBUG))
print('STORAGE_S3: {}'.format(STORAGE_S3))
# DEBUG = True
# 그냥 런서버: DEBUG = False
# MODE='DEBUG' ./manage.py runserver : DEBUG = True

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/
CONFIG_FILE_COMMON = os.path.join(os.path.join(os.path.dirname(BASE_DIR), '.conf-secret'), 'settings_common.json')
config_common = json.loads(open(CONFIG_FILE_COMMON).read())
CONFIG_FILE = os.path.join(os.path.join(os.path.dirname(BASE_DIR), '.conf-secret'), 'settings_local.json')
CONFIG_DEPLOY = os.path.join(os.path.join(os.path.dirname(BASE_DIR), '.conf-secret'), 'settings_deploy.json')

if DEBUG:
    config = json.loads(open(CONFIG_FILE).read())
else:
    config = json.loads(open(CONFIG_DEPLOY).read())

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config_common['django']['secret_key']

for key, key_dict in config_common.items():
    if not config.get(key):
        config[key] = {}
    for inner_key, inner_key_dict in key_dict.items():
        config[key][inner_key] = inner_key_dict

ALLOWED_HOSTS = config['django']['allowed_hosts']

# AWS
AWS_ACCESS_KEY_ID = config['aws']['access_key_id']
AWS_SECRET_ACCESS_KEY = config['aws']['secret_access_key']
AWS_STORAGE_BUCKET_NAME = config['aws']['s3_storage_bucket_name']
AWS_S3_SIGNATURE_VERSION = config['aws']['s3_signature_version']
AWS_S3_HOST = 's3.{}.amazonaws.com/'.format(config['aws']['s3_region'])
AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)

STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (
    STATIC_DIR,
)

# STORAGE_S3 사용할때
if STORAGE_S3:
    DEFAULT_FILE_STORAGE = 'deploy_ec2.storages.MediaStorage'
    STATICFILES_STORAGE = 'deploy_ec2.storages.StaticStorage'
    STATICFILES_LOCATION = 'static'
    MEDIAFILES_LOCATION = 'media'
    STATIC_URL = 'https://{custom_domain}/{staticfiles_location}/'.format(
        custom_domain=AWS_S3_CUSTOM_DOMAIN,
        staticfiles_location=STATICFILES_LOCATION
    )
    MEDIA_URL = 'https://{custom_domain}/{mediafiles_location}/'.format(
        custom_domain=AWS_S3_CUSTOM_DOMAIN,
        mediafiles_location=MEDIAFILES_LOCATION
    )
    # STATIC_URL = 's3.{region}.amazonaws.com/{bucket_name}/static'.format(region=config['aws']['s3_region'],
    #                                                                bucket_name=AWS_STORAGE_BUCKET_NAME)
    # MEDIR_URL = 's3.{region}.amazonaws.com/{bucket_name}/'.format(region=config['aws']['s3_region'],
    #                                                               bucket_name=AWS_STORAGE_BUCKET_NAME)
    # MEDIA_URL = 'https://{bucket_name}.s3.amazonaws.com/'.format(bucket_name=AWS_STORAGE_BUCKET_NAME )

else:
    STATIC_ROOT = os.path.join(ROOT_DIR, 'static_root')
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(ROOT_DIR, 'media')

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# Application definition

AUTH_USER_MODEL = 'member.MyUser'
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'storages',

    'member',
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

ROOT_URLCONF = 'deploy_ec2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            TEMPLATES_DIR,
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'deploy_ec2.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
if DEBUG and DB_RDS:
    config_db = config['db_rds']
else:
    config_db = config['db']
DATABASES = {
    'default': {
        'ENGINE': config_db['engine'],
        'NAME': config_db['name'],
        'USER': config_db['user'],
        'PASSWORD': config_db['password'],
        'HOST': config_db['host'],
        'PORT': config_db['port'],
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
