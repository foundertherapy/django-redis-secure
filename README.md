# Django secure redis
Django caching plugin for django-redis that adds a Serializer class and configuration to support transparent,
symmetrical encryption of cached values using the python cryptography library.
This pluging also provide encryption for `django-rq` jobs by simply using `@secure_redis.rq_job` decorator on top of the job instead of `@django_rq.job`

# Important
Before using this library, make sure that you really need it. By using it, put in mind:
- You are loosing atomic functionalities like `incr()`
- The values stored to redis are now bigger
- Will take more time to set and retrieve data from redis

# Installation
1. Use `pip install` to get this library
2. In `settings.py` in your project, go to `CACHE` settings and ensure you put the following:
 * Add `secure_redis` to `INSTALLED_APPS`
 * Provide `REDIS_SECRET_KEY` to be used in the encryption
 * Configure the `SERIALIZER` setting to use `secure_redis.serializer.SecureSerializer`

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
            'SERIALIZER': 'secure_redis.serializer.SecureSerializer',
        },
        'KEY_PREFIX': 'app1:secure',
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
        'KEY_PREFIX': 'app1',
        'TIMEOUT': 60 * 60 * 24,  # 1 day
    },
}
```
# Data migration
If you already have an existing data in your redis, you might need to consider data migration for un-encrypted values,
you are free to handle this case as you want, we would suggest to use django management command to handle this case:

1. Keep old redis cache settings and add your new secure django redis cache configuration
2. Make sure your new secure django redis cache settings has different `KEY_PREFIX`
3. Make sure old configutation still point at the correct `REDIS_URL` and `REDIS_DB`
4. You can see an example configuration in the previous section of `Settings sample`
5. Make sure either to delete old keys or make sure your redis can holds the new values
6. Code sinppet for sample command is shown below:
```
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.core import cache


class Command(BaseCommand):
    def handle(self, *args, **options):
        new_cache_name = 'default'
        old_cache_name = 'insecure'
        old_key_prefix = 'app1'
        new_prefix = 'app1:secure'
        delete_old_keys = False

        old_cache = cache.caches[old_cache_name]
        new_cache = cache.caches[new_cache_name]

        # Use low level api to access full key name
        existing_keys = old_cache.client.get_client().keys('{}*'.format(old_key_prefix))
        for key in existing_keys:
            if new_prefix not in key:
                actual_key = old_cache.client.reverse_key(key)
                unencrypted_val = old_cache.get(actual_key)
                if new_cache.set(actual_key, unencrypted_val):
                    if delete_old_keys:
                        old_cache.delete(actual_key)

```

# Scheduler related usage
You can use some extra functionality provided by this plugin, if secure cache settings are not added in the `default` settings, please make sure that you specify your secure cache settings name by setting `DJANGO_REDIS_SECURE_CACHE_NAME` settings. To enable these feature, this simply by adding `@secure_redis.rq_job` decorator on top of your task. By doing this you can get use of:

1. `delay` method, so you can use it like `my_job.delay()`. This method is same as `django_rq.job.delay`
2. `enqueue_at` method, called as `my_job.enqueue_at()`. This is an exposed method of `django_rq.Scheduler.enqueue_at`
3. `schedule_once` method, called as `my_job.schedule_once()`. Same as `django_rq.Scheduler.schedule` but will check if method already exists so it will not added twice.

## Important:
When using `secure_redis.rq_job` decorator, this will direct your method to a proxy method which will result in changing method name in admin page, so if you want to see the actual method name, you can use `secure_redis.urls` instead of `django_rq.urls`, this will take care of displaying actual method name.
