from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


if hasattr(settings, 'DJANGO_REDIS_SECURE_CACHE_NAME'):
    cache_name = settings.DJANGO_REDIS_SECURE_CACHE_NAME
else:
    cache_name = 'default'

secure_cache_options_settings = settings.CACHES[cache_name]['OPTIONS']
if secure_cache_options_settings['CLIENT_CLASS'] == 'secure_redis.client.SecureDjangoRedisClient':
    if not secure_cache_options_settings.get('REDIS_SECRET_KEY'):
        raise ImproperlyConfigured(
            'REDIS_SECRET_KEY must be defined in settings in secure cache OPTIONS')

    if secure_cache_options_settings.get('DATA_RECOVERY'):
        data_recovery = secure_cache_options_settings['DATA_RECOVERY']
        if not data_recovery.get('OLD_KEY_PREFIX'):
            raise ImproperlyConfigured(
                'OLD_KEY_PREFIX must be defined in DATA_RECOVERY in settings')
        if not data_recovery.get('OLD_CACHE_NAME'):
            raise ImproperlyConfigured(
                'OLD_CACHE_NAME must be defined in DATA_RECOVERY in settings')
        if not data_recovery.get('CLEAR_OLD_ENTRIES'):
            raise ImproperlyConfigured(
                'CLEAR_OLD_ENTRIES must be defined in DATA_RECOVERY in settings')
