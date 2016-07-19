# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings
from django.core import cache


class Migration(migrations.Migration):

    dependencies = [
    ]

    def recover(apps, schema):
        if hasattr(settings, 'DJANGO_REDIS_SECURE_CACHE_NAME'):
            cache_name = settings.DJANGO_REDIS_SECURE_CACHE_NAME
        else:
            cache_name = 'default'
        new_cache_settings = settings.CACHES.get(cache_name, {})
        recovery_settings = new_cache_settings.get('OPTIONS', {}).get('DATA_RECOVERY')
        if not recovery_settings:
            return

        old_key_prefix = recovery_settings.get('OLD_KEY_PREFIX')
        old_cache_name = recovery_settings.get('OLD_CACHE_NAME')

        old_cache = cache.caches[old_cache_name]
        new_cache = cache.caches[cache_name]

        new_prefix = new_cache_settings['KEY_PREFIX']
        delete_old_keys = recovery_settings.get('CLEAR_OLD_ENTRIES')
        # Use low level api to access full key name
        existing_keys = old_cache.client.get_client().keys('{}*'.format(old_key_prefix))
        for key in existing_keys:
            if new_prefix not in key:
                actual_key = old_cache.client.reverse_key(key)
                unencrypted_val = old_cache.get(actual_key)
                if new_cache.set(actual_key, unencrypted_val):
                    if delete_old_keys:
                        old_cache.delete(actual_key)

    def recover_backward(apps, schema):
        pass

    operations = [
        migrations.RunPython(recover, reverse_code=recover_backward),
    ]
