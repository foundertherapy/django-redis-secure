from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_secure_cache_name():
    """
    Return the cache name to use for django-rq functionality
    """
    if not hasattr(settings, 'DJANGO_REDIS_SECURE_CACHE_NAME'):
        cache_name = 'default'
    else:
        cache_name = settings.DJANGO_REDIS_SECURE_CACHE_NAME
    return cache_name


def get_secure_cache_opts():
    """
    Return the options dict for the Django cache specified in the
    `DJANGO_REDIS_SECURE_CACHE_NAME` setting
    """
    cache_name = get_secure_cache_name()

    # If `DJANGO_REDIS_SECURE_CACHE_NAME` is explicitly set to `None`, don't
    # return the options dict, django-rq functionality has been turned off
    if cache_name is not None:
        secure_cache_opts = settings.CACHES[cache_name].get('OPTIONS')
        if not secure_cache_opts:
            raise ImproperlyConfigured(
                'OPTIONS must be defined in settings in secure cache settings!')

        if secure_cache_opts['SERIALIZER'] == 'secure_redis.serializer.SecureSerializer':
            return secure_cache_opts


secure_cache_options_settings = get_secure_cache_opts()
if secure_cache_options_settings:
    if not secure_cache_options_settings.get('REDIS_SECRET_KEY'):
        raise ImproperlyConfigured(
            'REDIS_SECRET_KEY must be defined in settings in secure cache OPTIONS')

