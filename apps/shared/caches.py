import datetime
from typing import Union, Literal
from celery import shared_task

from django.conf import settings
from django.core.cache import caches
from django.utils import timezone

from .tasks import call_task_background

__all__ = ['CacheController']


class CacheController:
    """
    Support all action to relate cache.
    *** MUST USE THE CLASS FOR CACHE. DON'T ALLOW USE CACHE UTILS OUTSIDE THE CLASS. ***
    """

    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'  # datetime format
    KEY_CACHE_PREFIX = getattr(settings, 'CACHE_PREFIX_KEY', 'MiS')  # prefix all key cache
    EXPIRES_SECONDS_DEFAULT = 60 * 60  # seconds # 1 hours
    KEY_OF_MANAGEMENT_ALL_KEYS = f'{KEY_CACHE_PREFIX}___ALL_KEYS'  # [key1, key2, key3]
    KEY_OF_ALL_KEYS_WITH_TIMEOUTS = f'{KEY_CACHE_PREFIX}___ALL_KEYS__TIMEOUT'  # {key1: 'yyyy-mm-dd hh:mm:ss'}
    FLAG_CHECK_TIMEOUT = f'{KEY_CACHE_PREFIX}___ALL_KEYS__LAST_TIME_CHECKED'  # value='exist'
    FLAG_CHECK_TIMEOUT_CIRCLE = 60 * 60  # hourly

    def __init__(self, location='default'):
        self.sv = caches[location]  # pylint: disable=C0103

    @classmethod
    def append_prefix_key_cache(cls, key: str) -> str:
        """
        Auto append prefix key to key cache before force cache.
        """
        key = str(f'{cls.KEY_CACHE_PREFIX}_{key.lower()}')
        return key

    def get(self, key) -> Union[any, None]:
        """
        Get data cache by key | Key is not exist return None
        """
        if not key.startswith(self.KEY_CACHE_PREFIX):
            key = self.append_prefix_key_cache(key)
        self.make_decision_check_timeout()
        return self.sv.get(key)

    def set(self, key: str, value: Union[list, dict], expires: Union[int, None] = EXPIRES_SECONDS_DEFAULT) -> str:
        """
        Force set data cache to key | return key saved
        """
        if not key.startswith(self.KEY_CACHE_PREFIX):
            key = self.append_prefix_key_cache(key)
        self.sv.set(key, value, expires)
        self.management_key(key, action=1, expires=expires)
        return key

    def set_never_expires(self, key, value):
        """
        Force set data cache to key with being stored forever | call set(...) with expires=None
        """
        return self.set(key, value, None)

    def destroy(self, key):
        """
        Destroy cache data by key | return True(key is exist) or False (key isn't exist)
        """
        if not key.startswith(self.KEY_CACHE_PREFIX):
            key = self.append_prefix_key_cache(key)
        state_destroy = self.sv.delete(key)
        self.management_key(key, action=0)
        return state_destroy

    def clean(self):
        """
        Clear all key in all_keys and reset management all keys.
        """
        key_list = self.get_all_keys()
        if key_list and isinstance(key_list, list):
            for key in self.get_all_keys():
                self.destroy(key)
        self.destroy(self.KEY_OF_MANAGEMENT_ALL_KEYS)
        self.destroy(self.KEY_OF_ALL_KEYS_WITH_TIMEOUTS)
        return True

    # Management KEYS cache
    def make_decision_check_timeout(self, force_run: bool = False):
        """
        Get flag data was stored in cache.
        Active check cache task in background when flag data is not exists.
        Then set flag data to cache with expire is FLAG_CHECK_TIMEOUT_CIRCLE

        Args:
            force_run: True if check timeout now.
        """
        if force_run is True:  # auto call check timeout
            flag_checked = False
        else:
            flag_checked = self.sv.get(self.FLAG_CHECK_TIMEOUT)
        if not flag_checked:
            call_task_background(auto_check_timeout_all_keys, countdown=7)
            self.sv.set(
                self.FLAG_CHECK_TIMEOUT,
                'Check-Cache-At-The-Next-Time.',
                self.FLAG_CHECK_TIMEOUT_CIRCLE
            )
            return True
        return False

    def check_timeout_all_keys(self):
        """
        Refresh key by check timeout of keys.
        """
        list_key = self.sv.get(self.KEY_OF_MANAGEMENT_ALL_KEYS)
        map_timeout = self.sv.get(self.KEY_OF_ALL_KEYS_WITH_TIMEOUTS)

        time_now = timezone.now()
        if list_key and isinstance(list_key, list) and map_timeout and isinstance(map_timeout, dict):
            key_removed = {}
            for key, timeout in map_timeout.items():
                dt_timeout = datetime.datetime.strptime(timeout, self.DATETIME_FORMAT)
                if dt_timeout and dt_timeout < time_now:
                    key_removed[key] = timeout
                    self.management_key(key, action=0)  # remove key
            return True, key_removed
        return False, {'errors': "Don't have key data or timeout data. Or it's format is incorrect."}

    def get_all_keys(self):
        """
        Get all keys saved to cache.
        """
        return self.sv.get(self.KEY_OF_MANAGEMENT_ALL_KEYS)

    def get_timeout_all_keys(self):
        """
        Get all keys saved to cache.
        """
        return self.sv.get(self.KEY_OF_ALL_KEYS_WITH_TIMEOUTS)

    def management_key(
            self, key, action: Literal[0, 1], expires: int = None
    ):
        """
        Case 0: Remove key from all_keys, timeout_all_keys
        Case 1: Add key to all_keys and timeout_all_keys

        args:
            - key: Key data push/pop in all_keys
            - action: Action choice in push(1) or pop(0)
            - expires: Seconds delta time plus to now() for timeout of key
                required when action = 1
                another: default EXPIRES_SECONDS_DEFAULT
        """
        key = str(key)
        if not expires:
            expires = self.EXPIRES_SECONDS_DEFAULT

        match action:
            case 0:
                # remove key from all_keys
                data = self.sv.get(self.KEY_OF_MANAGEMENT_ALL_KEYS)
                if data and isinstance(data, list) and key in data:
                    data.remove(key)
                    self.sv.set(self.KEY_OF_MANAGEMENT_ALL_KEYS, data, None)

                # remove key from timeout_all_keys
                data_timeout = self.sv.get(self.KEY_OF_ALL_KEYS_WITH_TIMEOUTS)
                if data_timeout and isinstance(data_timeout, dict) and key in data_timeout:
                    data_timeout.pop(key, None)
                    self.sv.set(self.KEY_OF_ALL_KEYS_WITH_TIMEOUTS, data_timeout, None)
            case 1:
                # push key to all_keys
                data = self.sv.get(self.KEY_OF_MANAGEMENT_ALL_KEYS)
                if data and isinstance(data, list):
                    data.append(key)
                else:
                    data = [key]
                self.sv.set(self.KEY_OF_MANAGEMENT_ALL_KEYS, list(set(data)), None)

                # push timeout to timeout_all_keys
                data_timeout = self.sv.get(self.KEY_OF_ALL_KEYS_WITH_TIMEOUTS)
                timeout_time_str = (
                        timezone.now() + datetime.timedelta(seconds=expires)
                ).strftime(self.DATETIME_FORMAT)
                if data_timeout and isinstance(data_timeout, dict):
                    data_timeout[key] = timeout_time_str
                else:
                    data_timeout = {key: timeout_time_str}
                self.sv.set(self.KEY_OF_ALL_KEYS_WITH_TIMEOUTS, data_timeout, None)

        return True


@shared_task
def auto_check_timeout_all_keys():
    """
    Task was called when system receive signal to cache and true condition (hourly)
    """
    return CacheController().check_timeout_all_keys()
