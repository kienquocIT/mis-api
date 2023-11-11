import django_filters
from django.db.models import Q
from django_filters.rest_framework import filters
from rest_framework import exceptions

from apps.shared import BastionFieldAbstractListFilter
from apps.shared import TypeCheck
from .models import Employee, DistributionApplication

__all__ = [
    'EmployeeListFilter',
    'EmployeeStorageAppAllListFilter',
]


class EmployeeListFilter(BastionFieldAbstractListFilter):
    group__first_manager__id = filters.CharFilter(
        method='filter_group__first_manager', field_name='group__first_manager__id'
    )
    list_from_leave = filters.CharFilter(method='filter_list_from_leave')

    class Meta:
        model = Employee
        fields = (
            'group__id', 'id',
            'group_id'
        )

    def filter_group__first_manager(self, queryset, name, value):
        user_obj = getattr(self.request, 'user', None)
        if user_obj:
            filter_kwargs = Q()
            if TypeCheck.check_uuid(value):
                filter_kwargs |= Q(**{name: value})
            elif user_obj.employee_current and user_obj.employee_current.group and str(
                    user_obj.id) == str(user_obj.employee_current.group.first_manager_id):
                manager = str(user_obj.employee_current.group.first_manager_id)
                filter_kwargs |= Q(**{name: manager})
            return queryset.filter(filter_kwargs)
        raise exceptions.AuthenticationFailed

    @classmethod
    def filter_list_from_leave(cls, queryset, *args, **kwargs):
        return queryset


class EmployeeStorageAppAllListFilter(django_filters.FilterSet):
    opportunity = filters.UUIDFilter(method='filter_opportunity')
    project = filters.UUIDFilter(method='filter_project')

    @classmethod
    def filter_get_from(cls, queryset, *args, **kwargs):
        return queryset

    @classmethod
    def filter_opportunity(cls, queryset, *args, **kwargs):
        return queryset

    @classmethod
    def filter_project(cls, queryset, *args, **kwargs):
        return queryset

    class Meta:
        model = DistributionApplication
        fields = ()
