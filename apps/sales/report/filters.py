from django.apps import apps
from django.db.models import Q, F
from django.db.models.functions import Round
from django_filters.rest_framework import filters

from apps.shared import BastionFieldAbstractListFilter
from .models import ReportPipeline, ReportRevenue

__all__ = [
    'ReportPipelineListFilter',
    'filter_by_advance_filter'
]

from ..partnercenter.models import List


class ReportPipelineListFilter(BastionFieldAbstractListFilter):
    opportunity__close_date_month = filters.CharFilter(
        method='filter_opportunity__close_date_month', field_name='opportunity__close_date_month'
    )

    class Meta:
        model = ReportPipeline
        fields = (
            'employee_inherit__group_id',
            'employee_inherit_id',
            'opportunity__close_date_month',
        )

def filter_by_advance_filter(query_set, filter_item_id): # pylint: disable=R0914
    if not filter_item_id:
        return query_set

    filter_item_obj = List.objects.filter(id=filter_item_id).first()
    if not filter_item_obj:
        raise List.DoesNotExist()
    filter_condition = filter_item_obj.filter_condition
    application = filter_item_obj.application
    model_code = application.model_code
    app_label = application.app_label
    model_class = apps.get_model(app_label=app_label, model_name=model_code)

    programmatic_handlers = {
        'gross_margin': filter_gross_margin,
    }

    operator_handlers = {
        'notexact': lambda field, value: ~Q(**{field: value}),
        'exactnull': lambda field, _: Q(**{f"{field}__exact": None}),
        'notexactnull': lambda field, _: ~Q(**{f"{field}__exact": None}),
        'noticontains': lambda field, value: ~Q(**{f"{field}__icontains": value}),
    }
    overall_results = set()
    for group in filter_condition:
        group_results = None
        for condition in group:
            left = condition.get('left')
            left_field = left.get('code')
            operator = condition.get('operator', 'exact')

            if int(condition.get('type')) == 5 and (operator not in ('exactnull', 'notexactnull')):
                right_obj = condition.get('right')
                right = str(right_obj.get('id')).replace('-', '')
            else:
                right = condition.get('right')

            if left_field in programmatic_handlers:
                handler = programmatic_handlers[left_field]
                queryset = set(handler(filter_item_obj, operator, right))
            else:
                filter_func = operator_handlers.get(operator, None)
                if filter_func:
                    group_query = filter_func(left_field, right)
                else:
                    group_query = Q(**{f"{left_field}__{operator}": right})
                queryset = set(model_class.objects.
                               filter_current(fill__company=True).
                               filter(group_query).
                               values_list('id', flat=True))

            if group_results is None:
                group_results = queryset
            else:
                group_results.intersection_update(queryset)
        if group_results:
            overall_results.update(group_results)

    return query_set.filter(id__in=overall_results)

def filter_gross_margin(obj, operator, right):
    application = obj.application
    model_code = application.model_code
    app_label = application.app_label
    model_class = apps.get_model(app_label=app_label, model_name=model_code)

    right_ratio = round(int(right) / 100, 2)

    annotated_report = model_class.objects.annotate(
        gross_margin = Round(F('gross_profit') / F('revenue'), 2)
    )
    filter_kwargs = {f"gross_margin__{operator}": right_ratio}
    return annotated_report.filter(**filter_kwargs).values_list('id', flat=True)

