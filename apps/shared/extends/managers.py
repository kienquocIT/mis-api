import hashlib

from django.db import models
from crum import get_current_user

from .utils import StringHandler

__all__ = ['NormalManager']

from .caching import Caching


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
    def append_filter_currently(sql_query, filter_kwargs):
        """
        Put key=value to filter or get for auto append currently data user to filter.
        Args:
            sql_query:
            filter_kwargs:

        Returns:
            Dictionary from filter_kwargs
        """
        is__tenant = filter_kwargs.pop('is__tenant', False)
        is__company = filter_kwargs.pop('is__company', False)
        is__space = filter_kwargs.pop('is__space', False)
        sql_query = str(sql_query)
        user_obj = get_current_user()
        if user_obj:
            # append tenant_id if not exist in query
            if (
                    is__tenant and
                    user_obj.tenant_current_id and
                    f'tenant_id` = {user_obj.tenant_current_id.hex}' not in sql_query
            ):
                filter_kwargs['tenant_id'] = user_obj.tenant_current_id

            # append company_id if not exist in query
            if (
                    is__company and
                    user_obj.company_current_id and
                    f'company_id` = {user_obj.company_current_id.hex}' not in sql_query
            ):
                filter_kwargs['company_id'] = user_obj.company_current_id

            # append space_id if not exist in query
            if (
                    is__space and
                    user_obj.space_current_id and
                    f'space_id` = {user_obj.space_current_id.hex}' not in sql_query
            ):
                filter_kwargs['space_id'] = user_obj.space_current_id.pop('is__tenant', False)
        return filter_kwargs

    def filter_current(self, *args, **kwargs):
        """
        Support call append currently user data from QuerySet then call self.filter()
        Args:
            *args:
            **kwargs:

        Returns:
            return self.filter()
        """
        kwargs_converted = self.append_filter_currently(self.query, kwargs)
        return self.filter(*args, **kwargs_converted)

    def cache(self, timeout=None):
        """
        Call cache() from QuerySet for get cache value else get data then force save cache.
        Returns:
            QuerySet()

        Notes:
            *** DON'T SHOULD use it for QUERYSET have SELECT_RELATED or PREFETCH_RELATED ***
        """
        sql_split = str(self.query).rsplit('FROM', maxsplit=1)[-1]
        key = StringHandler.remove_special_characters_translate(sql_split)
        # [SHA256] hash: 30M/s, collision: 1/2^128 (10^-38)
        # [MD5] [FAST, NOT SECURE] hash: 120M/s, collision 1/70M
        # ==> TOTAL KEY CACHE: 0 ~ 1M ==> USE MD5 ==> OK
        key = self.table_name + '-' + hashlib.md5(key.encode('utf-8')).hexdigest()

        data = Caching().get(key)
        if data:
            return data

        data = self
        Caching().set(key, data, timeout=timeout)
        return data

    def get_current(self, *args, **kwargs):
        """
        Support call append currently user data from QuerySet then call self.get()
        Args:
            *args:
            **kwargs:

        Returns:
            self.get()
        """
        kwargs_converted = self.append_filter_currently(self.query, kwargs)
        return super().get(*args, **kwargs_converted)


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
