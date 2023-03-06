from typing import Union

from django.conf import settings
from django.core.cache import caches

__all__ = ['CacheController']


class CacheController:
    KEY_CACHE_PREFIX = getattr(settings, 'CACHE_PREFIX_KEY', 'MiS')
    EXPIRES_SECONDS_DEFAULT = 60 * 60

    def __init__(self, location='default'):
        self.sv = caches[location]

    @classmethod
    def append_prefix_key_cache(cls, key: str) -> str:
        key = str(f'{cls.KEY_CACHE_PREFIX}_{key.lower()}')
        return key

    def get(self, key):
        if not key.startswith(self.KEY_CACHE_PREFIX):
            key = self.append_prefix_key_cache(key)
        return self.sv.get(key)

    def set(self, key: str, value: Union[list, dict], expires: Union[int, None] = EXPIRES_SECONDS_DEFAULT) -> str:
        if not key.startswith(self.KEY_CACHE_PREFIX):
            key = self.append_prefix_key_cache(key)
        self.sv.set(key, value, expires)
        return key

    def set_never_expires(self, key, value):
        if not key.startswith(self.KEY_CACHE_PREFIX):
            key = self.append_prefix_key_cache(key)
        return self.set(key, value, None)

    def destroy(self, key):
        if not key.startswith(self.KEY_CACHE_PREFIX):
            key = self.append_prefix_key_cache(key)
        return self.sv.delete(key)
