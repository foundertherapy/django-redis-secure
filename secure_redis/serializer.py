from __future__ import unicode_literals

from cryptography.fernet import Fernet

import django_redis.serializers.pickle

from . import settings


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


default_secure_serializer = SecureSerializer(settings.get_secure_cache_opts())
