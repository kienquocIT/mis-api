import django_filters
from django.db.models import Q
from django_filters.rest_framework import filters

from apps.masterdata.saledata.models import Account
from apps.shared import TypeCheck

__all__ = [
    'AccountListFilter',
]


class AccountListFilter(django_filters.FilterSet):
    manager__contains = filters.CharFilter(method='filter_manager__contains')

    class Meta:
        model = Account
        fields = (
            'account_types_mapped__account_type_order',
        )

    @classmethod
    def filter_manager__contains(cls, queryset, name, value):
        if value:
            ids = value.split(',')
            if TypeCheck.check_uuid_list(ids):
                filter_kwargs = Q()
                for idx in ids:
                    filter_kwargs |= Q(**{name: {'id': idx}})
                return queryset.filter(filter_kwargs)
        return queryset
