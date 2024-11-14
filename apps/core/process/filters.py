from django.db.models import Q
from django_filters.rest_framework import filters, FilterSet

from apps.core.process.models import Process, ProcessMembers
from apps.shared import TypeCheck


class ProcessRuntimeListFilter(FilterSet):
    belong_to_me = filters.BooleanFilter(
        method='filter_belong_to_me', field_name='employee_id', label='Accept value in: true, 1'
    )

    def filter_belong_to_me(self, queryset, name, value):  # pylint: disable=W0613
        if value in ['true', True, '1']:
            user_obj = getattr(self.request, 'user', None)
            if user_obj and user_obj.employee_current_id:
                process_ids = ProcessMembers.objects.filter(**{name: user_obj.employee_current_id}).values_list(
                    'process_id', flat=True
                )
                return queryset.filter(Q(id__in=process_ids) | Q(employee_created_id=user_obj.employee_current_id))
            return queryset.none()
        return queryset

    members__contains = filters.CharFilter(
        method='filter_members__contains', field_name='members', label='Check employee ID in members'
    )

    @classmethod
    def filter_members__contains(cls, queryset, name, value):
        if value:
            if TypeCheck.check_uuid(value):
                kw_filter = {
                    name + '__contains': value
                }
                return queryset.filter(**kw_filter)
            return queryset.none()
        return queryset

    class Meta:
        model = Process
        fields = {
            'is_ready': ['exact'],
            'config_id': ['exact'],
            'employee_created_id': ['exact'],
            'was_done': ['exact'],
        }
