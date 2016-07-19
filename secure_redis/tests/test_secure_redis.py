from __future__ import unicode_literals

import django.test
from django.core import cache

import mock

from .. import client


class SecureRedisTestCase(django.test.TestCase):
    def test_incr(self):
        redis_cache = cache.caches['default']
        with self.assertRaises(client.UnsupportedOperation):
            redis_cache.incr('num1')

    @mock.patch('redis.client.StrictRedis.set')
    @mock.patch('redis.client.StrictRedis.get')
    def test_enc(self, get_method, set_method):
        original_val = "123"
        set_method.return_value = True
        redis_cache = cache.caches['default']
        redis_cache.set('val', original_val)
        set_method.assert_called_once()

        encVal = set_method.call_args[0][1]
        self.assertNotEqual(encVal, original_val)

        get_method.return_value = encVal
        decrypted_value = redis_cache.get('val')
        self.assertEqual(original_val, decrypted_value)
