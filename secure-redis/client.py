from __future__ import unicode_literals

import django_redis.client.default


class UnsupportedOperation(Exception):
    pass


class SecureDjangoRedisClient(django_redis.client.default.DefaultClient):
    def __init__(self, server, params, backend):
        options = params.get("OPTIONS", {})
        options['SERIALIZER'] = 'secure-redis.serializer.SecureSerializer'
        params['OPTIONS'] = options
        super(SecureDjangoRedisClient, self).__init__(server, params, backend)

    def _incr(self, key, delta=1, version=None, client=None):
        # increment is atomic, since the value is encrypted, you can't increment it in an atomic way
        raise UnsupportedOperation()

