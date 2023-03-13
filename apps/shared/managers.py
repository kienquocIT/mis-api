from django.db import models
from django.conf import settings
from .utils import StringHandler

__all__ = [
    'NormalManager'
]

APP_LABEL_CACHE = [x.split(".")[0] for x in settings.CACHE_DATA_CONFIG.keys()]
MODEL_NAME_CACHE = [x.split(".")[1] for x in settings.CACHE_DATA_CONFIG.keys()]
print(APP_LABEL_CACHE, MODEL_NAME_CACHE)


class EntryQuerySet(models.query.QuerySet):
    def table_name(self):
        return str(self.model._meta.db_table)  # pylint: disable=protected-access / W0212

    @staticmethod
    def is_enable_cache(db_table_name) -> (bool, int):
        if db_table_name:
            config = settings.CACHE_DATA_CONFIG

            timeout = 60 * 60  # 1 hours
            is_enable = False
            app_code, model_code = db_table_name.split('_')

            if f'{app_code}.*' in config:
                is_enable, timeout = True, config[f'{app_code}.*'].get('timeout', timeout)
            elif f'{app_code}.{model_code}' in config:
                is_enable, timeout = True, config[f'{app_code}.*'].get('timeout', timeout)
            elif '*.*' in config:
                is_enable, timout = True, config['*.*'].get('timeout', timeout)

            return is_enable, timeout
        return False, 0

    def filter(self, *args, **kwargs):
        # is_enable, timeout = self.is_enable_cache(self.table_name())
        data = super().filter(*args, **kwargs)
        return data


class NormalManager(models.Manager):
    def get_queryset(self):  # pylint: disable=W0246
        return EntryQuerySet(self.model).filter()
