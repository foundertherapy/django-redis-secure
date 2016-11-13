from __future__ import unicode_literals

from cryptography.fernet import Fernet
import logging

import django.conf
import django_redis.serializers.pickle

import settings


logger = logging.getLogger(__name__)


class SecureSerializer(django_redis.serializers.pickle.PickleSerializer):
    def __init__(self, options):
        super(SecureSerializer, self).__init__(options)
        param_key = options.get("REDIS_SECRET_KEY")
        key = param_key.encode("utf-8")
        self.crypter = Fernet(key)

    def dumps(self, value):
        val = super(SecureSerializer, self).dumps(value)
        return self.crypter.encrypt(val)

    def loads(self, value):
        val = self.crypter.decrypt(value)
        return super(SecureSerializer, self).loads(val)


opts = settings.secure_cache_options_settings
if not opts and django.conf.settings.DEBUG:
    default_secure_serializer = django_redis.serializers.pickle.PickleSerializer({})
    logger.warn("Secure redis OPTIONS not defined, using pickle serializer for local")
else:
    default_secure_serializer = SecureSerializer(opts)
