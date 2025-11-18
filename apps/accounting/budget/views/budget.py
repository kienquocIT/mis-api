from drf_yasg.utils import swagger_auto_schema

from apps.accounting.budget.models import BudgetLine, Budget
from apps.accounting.budget.serializers import BudgetLineListSerializer, BudgetListSerializer
from apps.shared import BaseListMixin, mask_view


class BudgetList(BaseListMixin):
    queryset = Budget.objects
    search_fields = ["app_code"]
    filterset_fields = {
        'doc_id': ['exact', 'in'],
    }
    serializer_list = BudgetListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Budget List",
        operation_description="Get Budget List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='budget', model_code='budget', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BudgetLineList(BaseListMixin):
    queryset = BudgetLine.objects
    search_fields = ["remark"]
    # filterset_fields = {
    #     'dimension_values__id': ['exact', 'in'],
    # }
    serializer_list = BudgetLineListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        request_qs = self.request.query_params.dict()
        if 'dimension_values' in request_qs:
            dimension_values = request_qs.pop('dimension_values')
            qs_m2m_dv = super().get_queryset()
            for dimension_value in dimension_values.split(','):
                qs_m2m_dv = qs_m2m_dv.filter(dimension_values__id=dimension_value)
            return qs_m2m_dv

        return super().get_queryset()

    @swagger_auto_schema(
        operation_summary="Budget Line List",
        operation_description="Get Budget Line List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='budget', model_code='budget', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
