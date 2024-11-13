from django.contrib.auth.models import AnonymousUser
from django.db import models
from crum import get_current_user

__all__ = ['NormalManager']


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

    def table_key_cache(self, **kwargs) -> str or None:
        if kwargs:
            generate_key_cache = getattr(self.model, 'generate_key_cache', None)
            if callable(generate_key_cache) is True:
                return generate_key_cache(**kwargs)  # pylint: disable=E1102
        return None

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

    # def get(self, *args, **kwargs):
    #     # force_cache = kwargs.pop('force_cache', False)
    #     # if force_cache and not args and kwargs:
    #     #     key = self.table_key_cache(**kwargs)
    #     #     if key:
    #     #         cache_timeout = kwargs.pop('cache_timeout', 60 * 60)
    #     #         data = Caching().get(key)
    #     #         if data and isinstance(data, models.Model):
    #     #             return data
    #     #         data = super().get(*args, **kwargs)
    #     #         Caching().set(key, data, cache_timeout)
    #     #         return data
    #     return super().get(*args, **kwargs)


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
