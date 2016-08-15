from __future__ import unicode_literals
import os


BASE_DIR = os.path.dirname(__file__)
APPSERVER = os.uname()[1]

SITE_ID = 1
INTERNAL_IPS = ('127.0.0.1', )
ALLOWED_HOSTS = ['localhost', '127.0.0.1', ]
APPEND_SLASH = True
TIME_ZONE = 'UTC'
USE_TZ = True
SECRET_KEY = 'abc'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.sessions',
    'secure_redis',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}

ROOT_URLCONF = 'urls'


REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
REDIS_DB = 0

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            # "SOCKET_CONNECT_TIMEOUT": 5,  # in seconds
            'DB': REDIS_DB,
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SERIALIZER': 'secure_redis.serializer.SecureSerializer',
            'REDIS_SECRET_KEY': 'kPEDO_pSrPh3qGJVfGAflLZXKAh4AuHU64tTlP-f_PY=',
        },
        'KEY_PREFIX': 'register:secure',
        'TIMEOUT': 60 * 60 * 24,  # 1 day
    },
    'insecure': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            # "SOCKET_CONNECT_TIMEOUT": 5,  # in seconds
            'DB': REDIS_DB,
            'PARSER_CLASS': 'redis.connection.HiredisParser',
        },
        'KEY_PREFIX': 'register',
        'TIMEOUT': 60 * 60 * 24,  # 1 day
    },
}


RQ_QUEUES = {
    'default': {
        'USE_REDIS_CACHE': 'default',
        'DEFAULT_TIMEOUT': 600,
    },
    'automation': {
        'USE_REDIS_CACHE': 'default',
        'DEFAULT_TIMEOUT': 600,
    },
}

RQ_SCHEDULER_ENABLED = False
for q in RQ_QUEUES.itervalues():
    q['ASYNC'] = False
