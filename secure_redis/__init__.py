import settings

from .decorators import rq_job
from . import serializer


__version__ = '1.0.1'

_serializer = None


def get_serializer():
    global _serializer
    if not _serializer:
        _serializer = serializer.SecureSerializer(settings.get_secure_cache_opts())
    return _serializer

