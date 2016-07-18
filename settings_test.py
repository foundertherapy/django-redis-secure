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
    'secure-redis',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}

ROOT_URLCONF = 'urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'accounts.middleware.TimezoneMiddleware',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_AGE = 60 * 30  # 30 minute session length

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
            'REDIS_SECRET_KEY': 'kPEDO_pSrPh3qGJVfGAflLZXKAh4AuHU64tTlP-f_PY=',
            'CLIENT_CLASS': 'secure-redis.client.SecureDjangoRedisClient',
            'DATA_RECOVERY': {
                'OLD_KEY_PREFIX': 'register',
                'OLD_CACHE_NAME': 'unsafe_redis',
                'CLEAR_OLD_ENTRIES': False,
            }

        },
        'KEY_PREFIX': 'register:secure',
        'TIMEOUT': 60 * 60 * 24,  # 1 day
    },
    'unsafe_redis': {
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
    'staticfiles': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            # "SOCKET_CONNECT_TIMEOUT": 5,  # in seconds
            'DB': REDIS_DB,
            'PARSER_CLASS': 'redis.connection.HiredisParser',
        },
        'KEY_PREFIX': 'sf',
        'TIMEOUT': 60 * 60 * 24 * 180,  # 180 days
    },
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'test_templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'accounts.context_processors.masquerade_info',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.request',
            ],
            'debug': True,
        }
    },
]
