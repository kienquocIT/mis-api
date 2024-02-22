from django_filters.rest_framework import filters

from apps.shared import BastionFieldAbstractListFilter
from .models import ReportPipeline

__all__ = [
    'ReportPipelineListFilter',
]


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
