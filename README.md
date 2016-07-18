# Django secure redis
This library provides extra option for django-redis library, in which it provides a secure layer on the top of redis cache

# Installation
1. Use `pip install` to get this library
2. In `settings.py` in your project, go to `CACHE` settings and ensure you put the following:
 * Provide `REDIS_SECRET_KEY` to be used in the encreption
 * Let `CLIENT_CLASS` to use `secure-redis.client.SecureDjangoRedisClient`
 * If you already have existing data and you don't want to loose them (if you don't just skip this point), basiclly, when you need to add new cache configuration which is related to secure redis configuration, and keep the old configration (you MUST keep `KEY_PREFIX` as it is) so it can be used to read the old values - please note that you need to make sure that the two cache configuration point at the same redis db.
   * Add `DJANGO_REDIS_SECURE_CACHE_NAME` and let it equal to the new secure cache configuration. The default value for this is `default`
   * Add `DATA_RECOVERY` in which it holds
     * `OLD_KEY_PREFIX` which is the old cache prefix used in previous configutation
     * `OLD_CACHE_NAME` which is the old cache configuration
     * `CLEAR_OLD_ENTRIES` should delete old key/values.
3. Run `python manage.py migrate` to perform the data migration from old cache to new encrypted cache.

# Settings sample
```
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
                'OLD_KEY_PREFIX': 'app1',
                'OLD_CACHE_NAME': 'unsafe_redis',
                'CLEAR_OLD_ENTRIES': False,
            }

        },
        'KEY_PREFIX': 'app1:secure',
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
        'KEY_PREFIX': 'app1',
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
```
