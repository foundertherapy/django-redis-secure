from __future__ import unicode_literals

import django.test
from django.core import cache

import mock


class SecureRedisTestCase(django.test.TestCase):
    @mock.patch('redis.client.StrictRedis.set')
    @mock.patch('cryptography.fernet.Fernet.encrypt')
    def test_encryption_called(self, encrypt_method, set_method):
        set_method.return_value = True
        original_val = "123"
        redis_cache = cache.caches['default']
        redis_cache.set('val', original_val)
        encrypt_method.assert_called_once()
        set_method.assert_called_once()

    @mock.patch('redis.client.StrictRedis.set')
    @mock.patch('redis.client.StrictRedis.get')
    def test_encryption_flow(self, get_method, set_method):
        original_val = "123"
        set_method.return_value = True
        redis_cache = cache.caches['default']
        redis_cache.set('val', original_val)
        set_method.assert_called_once()

        enc_val = set_method.call_args[0][1]
        self.assertNotEqual(enc_val, original_val)

        get_method.return_value = enc_val
        decrypted_value = redis_cache.get('val')
        self.assertEqual(original_val, decrypted_value)
