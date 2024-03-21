from django.db.models import Q
from django_filters.rest_framework import filters
from apps.shared import BastionFieldAbstractListFilter

from apps.core.base.models import ApplicationProperty


class ApplicationPropertiesListFilter(BastionFieldAbstractListFilter):
    system_code__is_null_or_value = filters.CharFilter(
        method='filter_system_code__is_null_or_value', field_name='system_code'
    )

    class Meta:
        model = ApplicationProperty
        fields = {
            'application': ['exact', 'in'],
            'system_code': ['exact', 'isnull'],
        }

    @classmethod
    def filter_system_code__is_null_or_value(cls, queryset, name, value):  # pylint: disable=W0613
        arr = [item.strip() for item in value.split(',')]
        return queryset.filter(
            Q(system_code__isnull=True) | Q(system_code__in=arr)
        )
