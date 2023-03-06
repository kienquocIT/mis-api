from typing import Union

from django.core.cache import caches


class CacheController:
    EXPIRES_SECONDS_DEFAULT = 60 * 60

    def __init__(self, location='default'):
        self.sv = caches[location]  # pylint: disable=C0103

    def get(self, key):
        return self.sv.get(key)

    def set(self, key: str, value: Union[list, dict], expires: Union[int, None] = EXPIRES_SECONDS_DEFAULT) -> str:
        self.sv.set(key, value, expires)
        return key

    def set_never_expires(self, key, value):
        return self.set(key, value, None)

    def destroy(self, key):
        return self.sv.delete(key)
