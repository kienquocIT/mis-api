import django_filters
from django.db.models import Q
from django_filters.rest_framework import filters
from rest_framework import exceptions

from apps.masterdata.saledata.models import Account
from apps.shared import TypeCheck, PermissionChecking

__all__ = [
    'AccountListFilter',
]


class AccountListFilter(django_filters.FilterSet):
    manager__contains = filters.CharFilter(method='filter_manager__contains', field_name='manager__contains')
    has_manager_custom = filters.CharFilter(method='filter_has_manager_custom', field_name='manager__contains')

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

    def filter_has_manager_custom(self, queryset, name, value):
        user_obj = getattr(self.request, 'user', None)
        if user_obj:
            if value and value != 'all':
                employee_current = getattr(self.request.user, 'employee_current', None)
                if employee_current:
                    if value == 'me':
                        return queryset.filter(**{name: {'id': str(employee_current.id)}})

                    filter_q = Q()
                    if value == 'same':
                        employee_ids = PermissionChecking.get_employee_same_group(
                            employee_obj=employee_current,
                            is_append_me=True,
                        )
                        for employee_id in employee_ids:
                            filter_q |= Q(**{name: {'id': employee_id}})
                    elif value == 'staff':
                        employee_ids = PermissionChecking.get_employee_my_staff(
                            employee_obj=employee_current,
                            is_append_me=True,
                        )
                        for employee_id in employee_ids:
                            filter_q |= Q(**{name: {'id': employee_id}})

                    if filter_q:
                        return queryset.filter(filter_q)
                return queryset.none()
            return queryset
        raise exceptions.AuthenticationFailed
