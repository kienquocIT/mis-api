from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Q
from rest_framework import exceptions
from django_filters.rest_framework import filters

from apps.shared import BastionFieldAbstractListFilter
from .models import Opportunity, OpportunityMeeting

__all__ = ['OpportunityListFilters', 'OpportunityMeetingFilters']


class OpportunityListFilters(BastionFieldAbstractListFilter):
    class Meta:
        model = Opportunity
        fields = {
            'employee_inherit': ['exact'],
            'quotation': ['exact', 'isnull'],
            'sale_order': ['exact', 'isnull'],
            'is_close_lost': ['exact'],
            'is_deal_close': ['exact'],
            'id': ['in'],
        }


class OpportunityMeetingFilters(BastionFieldAbstractListFilter):
    meeting_date = filters.CharFilter(
        method='filter_meeting_date', field_name='meeting_date'
    )

    class Meta:
        model = OpportunityMeeting
        fields = {
            'employee_attended_list': ['exact'],
        }

    def filter_meeting_date(self, queryset, name, value): # pylint: disable=W0613  # noqa
        user_obj = getattr(self.request, 'user', None)
        params = self.request.query_params.dict()
        if user_obj:
            filter_kwargs = Q()
            if 'employee_in_list' in params:
                filter_kwargs &= Q(**{'employee_attended_list__in': params['employee_in_list'].split(',')})
            if 'employee_inherit__group' in params:
                filter_kwargs &= Q(**{'opportunity__employee_inherit__group': params['employee_inherit__group']})
            try:
                date_month = datetime.strptime(value, '%Y-%m-%d')
                first_month = date_month.replace(day=1)
                last_month = date_month + relativedelta(day=31)
                case_01 = {
                    'meeting_date__gte': first_month,
                    'meeting_date__lte': last_month
                }
                case_02 = {
                    'meeting_date__gte': first_month,
                    'meeting_date__lte': last_month
                }
                case_03 = {
                    'meeting_date__gte': first_month,
                    'meeting_date__lte': last_month
                }
                case_04 = {
                    'meeting_date__lte': first_month,
                    'meeting_date__gte': last_month
                }
                filter_kwargs &= Q(Q(**case_01) | Q(**case_02) | Q(**case_03) | Q(**case_04))
            except ValueError:
                pass
            if filter_kwargs is not None:
                return queryset.filter(filter_kwargs)
            return queryset
        raise exceptions.AuthenticationFailed
