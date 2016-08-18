from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_secure_cache_opts():
    if hasattr(settings, 'DJANGO_REDIS_SECURE_CACHE_NAME'):
        cache_name = settings.DJANGO_REDIS_SECURE_CACHE_NAME
    else:
        cache_name = 'default'

    secure_cache_options_settings = settings.CACHES[cache_name].get('OPTIONS')
    if not secure_cache_options_settings:
            raise ImproperlyConfigured(
                'OPTIONS must be defined in settings in secure cache settings!')
    if secure_cache_options_settings['SERIALIZER'] == 'secure_redis.serializer.SecureSerializer':
        return secure_cache_options_settings


secure_cache_options_settings = get_secure_cache_opts()
if secure_cache_options_settings:
    if not secure_cache_options_settings.get('REDIS_SECRET_KEY'):
        raise ImproperlyConfigured(
            'REDIS_SECRET_KEY must be defined in settings in secure cache OPTIONS')

