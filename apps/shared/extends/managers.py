from typing import Union

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import EmptyResultSet
from django.db import models
from crum import get_current_user

__all__ = ['NormalManager']

from .caching import Caching

DEFAULT__FILL__MAP_KEY = {
    'fill__tenant': 'tenant_id',
    'fill__company': 'company_id',
    'fill__space': 'space_id',
    'fill__allow_use': 'system_status__in',
}


class EntryQuerySet(models.query.QuerySet):
    """
    The class is custom QuerySet that support new method call
    """

    @property
    def table_name(self):
        """
        Get table name of Queryset call.
        Returns:
            String
        """
        return str(self.model._meta.db_table)  # pylint: disable=protected-access / W0212

    @staticmethod
    def parsed_fill__map_key(fill__map_key) -> dict:
        if fill__map_key and isinstance(fill__map_key, dict):
            default__fill__map_key = DEFAULT__FILL__MAP_KEY.copy()
            default__fill__map_key.update(fill__map_key)
            return default__fill__map_key
        return DEFAULT__FILL__MAP_KEY

    @classmethod
    def append_filter_currently(
            cls, sql_query, fill__tenant, fill__company, fill__space, filter_kwargs,
            fill__allow_use,
            default__fill__map_key: dict,
    ):
        """
        Put key=value to filter or get for auto append currently data user to filter.
        Args:
            default__fill__map_key:
            fill__space:
            fill__company:
            fill__tenant:
            sql_query:
            filter_kwargs:
            fill__allow_use:

        Returns:
            Dictionary from filter_kwargs
        """
        # handle with SQL
        sql_query = str(sql_query)
        user_obj = get_current_user()
        if user_obj and not isinstance(user_obj, AnonymousUser):
            # append tenant_id if not exist in query
            if (
                    fill__tenant and
                    user_obj.tenant_current_id and
                    f'{default__fill__map_key["fill__tenant"]}` = {user_obj.tenant_current_id.hex}' not in
                    sql_query
            ):
                filter_kwargs[default__fill__map_key["fill__tenant"]] = user_obj.tenant_current_id

            # append company_id if not exist in query
            if (
                    fill__company and
                    user_obj.company_current_id and
                    f'{default__fill__map_key["fill__company"]}` = {user_obj.company_current_id.hex}' not in
                    sql_query
            ):
                filter_kwargs[default__fill__map_key["fill__company"]] = user_obj.company_current_id

            # append space_id if not exist in query
            if (
                    fill__space and
                    user_obj.space_current_id and
                    f'{default__fill__map_key["fill__space"]}` = {user_obj.space_current_id.hex}' not in sql_query
            ):
                filter_kwargs[default__fill__map_key["fill__space"]] = user_obj.space_current_id

            # append system_status__in if not exist in query
            if (
                    fill__allow_use and
                    f'{default__fill__map_key["fill__allow_use"]}` = ' not in sql_query
            ):
                filter_kwargs[default__fill__map_key["fill__allow_use"]] = [2, 3]
        return filter_kwargs

    def filter_current(
            self, *args,
            fill__tenant: bool = False, fill__company: bool = False, fill__space: bool = False,
            fill__map_key: dict[str, str] = None,
            fill__allow_use: bool = False,
            **kwargs
    ):
        """
        Support call append currently user data from QuerySet then call self.filter()
        Args:
            fill__space:
            fill__company:
            fill__tenant:
            fill__map_key:
            fill__allow_use:
            *args:
            **kwargs:

        Returns:
            return self.filter()
        """
        # convert kwargs before force db
        kwargs_converted = self.append_filter_currently(
            self.query,
            fill__tenant=fill__tenant, fill__company=fill__company, fill__space=fill__space,
            filter_kwargs=kwargs,
            fill__allow_use=fill__allow_use,
            default__fill__map_key=self.parsed_fill__map_key(fill__map_key),
        )
        return self.filter(*args, **kwargs_converted)

    def cache(self, timeout: Union[None, int] = None):
        """
        Call cache() from QuerySet for get cache value else get data then force save cache.
        timout:
            None: use default
            0: forever
            > 0: expires seconds
        Returns:
            QuerySet()

        Notes:
            *** DON'T SHOULD use it for QUERYSET have SELECT_RELATED or PREFETCH_RELATED ***
        """
        try:
            sql_split = str(self.query).rsplit('FROM', maxsplit=1)[-1]
            key = Caching.key_cache_table(self.table_name, sql_split)
            data = Caching().get(key)
            if data:
                if settings.DEBUG and settings.CACHE_ENABLED:
                    print('Data from CACHE: key=', key, ', length=', len(data))
                return data

            data = self
            if timeout is None:
                timeout = settings.CACHE_EXPIRES_DEFAULT
            elif timeout == 0:
                timeout = None
            else:
                timeout = timeout * 60
            Caching().set(key, data, timeout=timeout)
            return data
        except EmptyResultSet:
            ...
        return self

    def get_current(
            self, *args,
            fill__tenant: bool = False, fill__company: bool = False, fill__space: bool = False,
            fill__map_key: dict[str, str] = None,
            fill__allow_use: bool = False,
            **kwargs
    ):
        """
        Support call append currently user data from QuerySet then call self.get()
        Args:
            fill__space:
            fill__company:
            fill__tenant:
            fill__map_key:
            fill__allow_use:
            *args:
            **kwargs:

        Returns:
            self.get()
        """
        # convert kwargs before force db
        kwargs_converted = self.append_filter_currently(
            self.query,
            fill__tenant=fill__tenant, fill__company=fill__company, fill__space=fill__space,
            filter_kwargs=kwargs,
            fill__allow_use=fill__allow_use,
            default__fill__map_key=self.parsed_fill__map_key(fill__map_key)
        )
        return super().get(*args, **kwargs_converted)

    def get(self, *args, **kwargs):
        force_cache = kwargs.pop('force_cache', False)
        cache_timeout = kwargs.pop('cache_timeout', None)
        if force_cache and not args and kwargs:
            key = Caching.key_cache_table(
                self.table_name, "".join([f"{k}{v}" for k, v in kwargs.items()]),
                hash_key=False,
                replace_pk_to_id=True,
            )
            data = Caching().get(key)
            if data and isinstance(data, models.Model):
                return data
            data = super().get(*args, **kwargs)
            Caching().set(key, data, cache_timeout)
            return data
        return super().get(*args, **kwargs)


class NormalManager(models.Manager):
    """
    The class is custom manager that support maintain system
    """

    def get_queryset(self):
        """
        Override default is models.query.QuerySet to EntryQuery.
        It supports some method such as: cache, filter_current
        Returns:
            Customize Queryset
        """
        return EntryQuerySet(self.model, using=self._db)

    def filter_current(self, *args, **kwargs):
        fill__map_key = kwargs.pop('fill__map_key', None)
        fill__tenant = kwargs.pop('fill__tenant', False)
        fill__company = kwargs.pop('fill__company', False)
        fill__space = kwargs.pop('fill__space', False)
        return EntryQuerySet(self.model, using=self._db).filter_current(
            *args,
            fill__tenant=fill__tenant, fill__company=fill__company, fill__space=fill__space,
            fill__map_key=fill__map_key,
            **kwargs
        )

    def get_current(self, *args, **kwargs):
        """
        Support call append currently user data from QuerySet then call self.get()
        Args:
            *args:
            **kwargs:

        Returns:
            self.get()
        """
        fill__map_key = kwargs.pop('fill__map_key', None)
        fill__tenant = kwargs.pop('fill__tenant', False)
        fill__company = kwargs.pop('fill__company', False)
        fill__space = kwargs.pop('fill__space', False)
        return EntryQuerySet(self.model, using=self._db).get_current(
            *args,
            fill__tenant=fill__tenant, fill__company=fill__company, fill__space=fill__space,
            fill__map_key=fill__map_key,
            **kwargs
        )
