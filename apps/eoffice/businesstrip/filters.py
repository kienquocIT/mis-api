from datetime import datetime
from dateutil.relativedelta import relativedelta
from rest_framework import exceptions
from django_filters.rest_framework import filters

from django.db.models import Q
from .models import BusinessRequest

from apps.shared import BastionFieldAbstractListFilter

__all__ = ['BusinessTripListFilters']


class BusinessTripListFilters(BastionFieldAbstractListFilter):
    booking_date = filters.CharFilter(
        method='filter_meeting_date', field_name='booking_date'
    )

    class Meta:
        model = BusinessRequest
        fields = {
            'employee_inherit': ['exact'],
        }

    def filter_meeting_date(self, queryset, value):
        user_obj = getattr(self.request, 'user', None)
        if user_obj:
            filter_kwargs = None
            try:
                date_month = datetime.strptime(value, '%Y-%m-%d')
                first_month = date_month.replace(day=1)
                last_month = date_month + relativedelta(day=31)
                case_01 = {
                    'date_f__gte': first_month,
                    'date_t__lte': last_month
                }
                case_02 = {
                    'date_t__gte': first_month,
                    'date_t__lte': last_month
                }
                case_03 = {
                    'date_f__gte': first_month,
                    'date_f__lte': last_month
                }
                case_04 = {
                    'date_f__lte': first_month,
                    'date_t__gte': last_month
                }
                filter_kwargs |= Q(Q(**case_01) | Q(**case_02) | Q(**case_03) | Q(**case_04))
            except ValueError:
                pass
            if filter_kwargs is not None:
                return queryset.filter(filter_kwargs)
            return queryset
        raise exceptions.AuthenticationFailed
