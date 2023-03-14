from django.conf import settings
from django.utils.cache import caches

__all__ = ['Caching', 'CacheManagement']


class CacheManagement:
    KEY_SAVE_ALL = f'{settings.CACHE_KEY_PREFIX}.all_keys'

    def __init__(self, server=None):
        self.sv_cache = caches[server] if server else caches['default']

    @property
    def all_keys(self) -> list[str]:
        data = self.sv_cache.get(self.KEY_SAVE_ALL)
        if data and isinstance(data, list):
            return data
        return []

    def clean(self):
        return self.sv_cache.delete_many(self.all_keys)

    def add_to_all(self, keys: list[str]):
        all_keys = self.sv_cache.get(self.KEY_SAVE_ALL)
        if all_keys and isinstance(all_keys, list):
            all_keys += keys
        else:
            all_keys = keys
        self.sv_cache.set(self.KEY_SAVE_ALL, list(set(all_keys)), None)
        return True

    def remove(self, key):
        all_keys = self.sv_cache.get(self.KEY_SAVE_ALL)
        all_keys = list(set(all_keys))
        if key in all_keys:
            all_keys.remove(str(key))
            self.sv_cache.set(self.KEY_SAVE_ALL, all_keys, None)
        return True

    def remove_from_all(self, keys: list[str]):
        for key in keys:
            self.remove(key)
        return True


class Caching:
    def __init__(self, server=None):
        self.server = server
        self.sv_cache = caches[server] if server else caches['default']

    @staticmethod
    def parse_key(key: str) -> str:
        """
        Append constant data to key.
        """
        if key.startswith(settings.CACHE_KEY_PREFIX):
            return key
        return f'{settings.CACHE_KEY_PREFIX}.{key}'

    def set(self, key, value, timeout=None) -> str:
        if not timeout:
            timeout = 60 * 60  # timeout = 1 hours
        key_parsed = self.parse_key(key)
        self.sv_cache.set(key_parsed, value, timeout)
        CacheManagement(self.server).add_to_all([key_parsed])
        return key_parsed

    def get(self, key: str) -> any:
        key_parsed = self.parse_key(key)
        print('CACHING GET: ', key_parsed)
        return self.sv_cache.get(key_parsed)

    def get_many(self, keys: list[str]) -> dict:
        return self.sv_cache.get_many([self.parse_key(k) for k in keys])

    def delete(self, key: str) -> str:
        key_parsed = self.parse_key(key)
        self.sv_cache.delete(key_parsed)
        CacheManagement(self.server).remove_from_all([key_parsed])
        return key_parsed

    def delete_many(self, keys: list[str]) -> list[str]:
        keys_parsed = [self.parse_key(k) for k in keys]
        self.sv_cache.delete_many(keys_parsed)
        CacheManagement(self.server).remove_from_all(keys_parsed)
        return keys_parsed

    def clean_by_prefix(self, prefix):
        prefix = self.parse_key(prefix)
        all_keys = CacheManagement(self.server).all_keys
        if all_keys and isinstance(all_keys, list):
            keys_mapped = [x for x in all_keys if x.startswith(prefix)]
            self.delete_many(keys_mapped)
        return True
