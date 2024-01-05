from datetime import datetime
from dateutil.relativedelta import relativedelta
from rest_framework import exceptions
from django_filters.rest_framework import filters

from django.db.models import Q
from apps.shared import BastionFieldAbstractListFilter
from .models import LeaveRequestDateListRegister

__all__ = ['LeaveRequestListFilters']


class LeaveRequestListFilters(BastionFieldAbstractListFilter):
    leave_date = filters.CharFilter(
        method='filter_leave_date', field_name='leave_date'
    )

    class Meta:
        model = LeaveRequestDateListRegister
        fields = {}

    def filter_leave_date(self, queryset, name, value):  # pylint: disable=W0613  # noqa
        user_obj = getattr(self.request, 'user', None)
        request_params = self.request.query_params.dict()
        if user_obj:
            filter_kwargs = Q(**{'leave__system_status__gte': 2})
            if 'leave_employee_list' in request_params:
                filter_kwargs &= Q(
                    **{'leave__employee_inherit__in': request_params['leave_employee_list'].split(",")}
                )
            if 'leave__employee_inherit__group' in request_params:
                filter_kwargs &= Q(
                    **{'leave__employee_inherit__group': request_params['leave__employee_inherit__group']}
                )
            try:
                date_month = datetime.strptime(value, '%Y-%m-%d')
                first_month = date_month.replace(day=1)
                last_month = date_month + relativedelta(day=31)
                case_01 = {
                    'date_from__gte': first_month,
                    'date_to__lte': last_month
                }
                case_02 = {
                    'date_to__gte': first_month,
                    'date_to__lte': last_month
                }
                case_03 = {
                    'date_from__gte': first_month,
                    'date_from__lte': last_month
                }
                case_04 = {
                    'date_from__lte': first_month,
                    'date_to__gte': last_month
                }
                filter_kwargs &= Q(Q(**case_01) | Q(**case_02) | Q(**case_03) | Q(**case_04))
            except ValueError:
                pass
            if filter_kwargs is not None:
                return queryset.filter(filter_kwargs)
            return queryset
        raise exceptions.AuthenticationFailed
