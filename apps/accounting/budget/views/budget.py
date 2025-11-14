from drf_yasg.utils import swagger_auto_schema

from apps.accounting.budget.models import BudgetLine
from apps.accounting.budget.serializers import BudgetLineListSerializer
from apps.shared import BaseListMixin, mask_view


class BudgetLineList(BaseListMixin):
    queryset = BudgetLine.objects
    search_fields = ["remark"]
    filterset_fields = {
        'dimension_values__id': ['exact', 'in'],
    }
    serializer_list = BudgetLineListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

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
