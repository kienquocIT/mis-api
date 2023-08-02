import hashlib

from django.conf import settings
from django.utils.cache import caches

from .utils import StringHandler

__all__ = ['Caching', 'CacheManagement', 'make_key_global']

TABLE_REF = {  # clean cache reference when system clean cache of model. Bad performance but real data.
    'account_user': (
        'tenant_tenant', 'company_company', 'hr_employee', 'company_companyuseremployee',
    ),
    'company_companyuseremployee': (
        'account_user', 'hr_employee', 'company_company',
    ),
    'tenant_tenant': (
        'company_company', 'account_user', 'account_user', 'hr_employee', 'company_companyuseremployee'
    ),
    'hr_employee': (
        'hr_group',
    ),
    'hr_group': (
        'hr_employee',
    )
}


def make_key_global(key, key_prefix, version):
    return ":".join([key_prefix, str(version), key])


class CacheManagement:
    KEY_SAVE_ALL = f'{settings.CACHE_KEY_PREFIX}.all_keys'

    def __init__(self, server=None):
        self.sv_cache = caches[server] if server else caches['default']

    @property
    def all_keys(self) -> list[str]:
        """
        Get all keys in storage caches.
        Returns:

        """
        data = self.sv_cache.get(self.KEY_SAVE_ALL)
        if data and isinstance(data, list):
            return data
        return []

    def clean(self):
        """
        Delete all value of key in all_keys
        Returns:

        """
        return self.sv_cache.delete_many(self.all_keys)

    def add_to_all(self, keys: list[str]):
        """
        Add keys (list key) to field all_keys (management keys)
        Args:
            keys:

        Returns:

        """
        all_keys = self.sv_cache.get(self.KEY_SAVE_ALL)
        if all_keys and isinstance(all_keys, list):
            all_keys += keys
        else:
            all_keys = keys
        self.sv_cache.set(self.KEY_SAVE_ALL, list(set(all_keys)), None)
        return True

    def remove(self, key):
        """
        Remove key from field all_keys (management keys)
        Args:
            key:

        Returns:

        """
        all_keys = self.sv_cache.get(self.KEY_SAVE_ALL)
        if all_keys:
            all_keys = list(set(all_keys))
            if key in all_keys:
                all_keys.remove(str(key))
                self.sv_cache.set(self.KEY_SAVE_ALL, all_keys, None)
        return True

    def remove_from_all(self, keys: list[str]):
        """
        Remove keys (list key) to field all_keys (management keys)
        Args:
            keys:

        Returns:

        """
        for key in keys:
            self.remove(key)
        return True


class Caching:
    def __init__(self, server=None):
        self.server = server
        self.sv_cache = caches[server] if server else caches['default']

    @staticmethod
    def key_cache_table(table_name, string_key, hash_key=True, replace_pk_to_id=True):
        """
        Generate key from table_name, query_sql / filter.
        Auto replace pk => id
        Auto hash key. If hash_key = False, length key must be less than 200 character.
        Args:
            table_name:
            string_key:
            hash_key:
            replace_pk_to_id:

        Returns:

        """

        if replace_pk_to_id is True:
            string_key = string_key.replace('pk', 'id')
        key = StringHandler.remove_special_characters_translate(string_key)
        # [SHA256] hash: 30M/s, collision: 1/2^128 (10^-38)
        # [MD5] [FAST, NOT SECURE] hash: 120M/s, collision 1/70M
        # ==> TOTAL KEY CACHE: 0 ~ 1M ==> USE MD5 ==> OK
        key_hashed = hashlib.md5(key.encode('utf-8')).hexdigest() if hash_key is True else key
        return f'{table_name}-{key_hashed}'

    @staticmethod
    def parse_key(key: str) -> str:
        """
        Generate new key by system rule. (Append constant data to key)
        """
        if key.startswith(settings.CACHE_KEY_PREFIX):
            return key
        return f'{settings.CACHE_KEY_PREFIX}.{key}'

    def set(self, key, value, timeout=None) -> str:
        """
        Set key=value to cache storage.
        Args:
            key:
            value:
            timeout:

        Returns:

        """
        if not timeout:
            timeout = 60 * 60  # timeout = 1 hours
        key_parsed = self.parse_key(key)
        self.sv_cache.set(key_parsed, value, timeout)
        CacheManagement(self.server).add_to_all([key_parsed])
        return key_parsed

    def get(self, key: str) -> any:
        """
        Get value by key name from cache storage.
        Args:
            key:

        Returns:

        """
        key_parsed = self.parse_key(key)
        return self.sv_cache.get(key_parsed)

    def get_many(self, keys: list[str]) -> dict:
        """
        Get value by many keys name from cache storage.
        Args:
            keys:

        Returns:

        """
        return self.sv_cache.get_many([self.parse_key(k) for k in keys])

    def delete(self, key: str) -> str:
        """
        Delete key in cache storage.
        Args:
            key:

        Returns:

        """
        key_parsed = self.parse_key(key)
        self.sv_cache.delete(key_parsed)
        CacheManagement(self.server).remove_from_all([key_parsed])
        return key_parsed

    def delete_many(self, keys: list[str]) -> list[str]:
        """
        Delete many keys in cache storage.
        Args:
            keys:

        Returns:

        """
        keys_parsed = [self.parse_key(k) for k in keys]
        self.sv_cache.delete_many(keys_parsed)
        CacheManagement(self.server).remove_from_all(keys_parsed)
        return keys_parsed

    @classmethod
    def __key_cache_relate(cls, all_keys, table_name_parsed, table_ref_parsed_list):
        """
        Append all keys need destroy include key of main table and key of reference table.
        Args:
            all_keys:
            table_name_parsed:
            table_ref_parsed_list:

        Returns:

        """
        key_mapped = []
        for key in all_keys:
            if key.startswith(table_name_parsed):
                key_mapped.append(key)
            else:
                for k in table_ref_parsed_list:
                    if key.startswith(k):
                        key_mapped.append(key)
        return key_mapped

    def clean_by_prefix(self, table_name):
        """
        Clean many keys from table name... Make sure cache don't have fake data.
        Args:
            table_name:

        Returns:

        """
        all_keys = CacheManagement(self.server).all_keys
        key_mapped = self.__key_cache_relate(
            all_keys=all_keys if all_keys and isinstance(all_keys, list) else [],
            table_name_parsed=self.parse_key(table_name),
            table_ref_parsed_list=[self.parse_key(x) for x in TABLE_REF.get(table_name, [])],
        )
        self.delete_many(key_mapped)
        return True
