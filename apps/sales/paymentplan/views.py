from drf_yasg.utils import swagger_auto_schema

from apps.sales.paymentplan.models import PaymentPlan
from apps.sales.paymentplan.serializers.payment_plan_serializers import PaymentPlanListSerializer
from apps.shared import BaseListMixin, mask_view


class PaymentPlanList(BaseListMixin):
    queryset = PaymentPlan.objects
    search_fields = []
    filterset_fields = {
        'sale_order_id': ['exact', 'in'],
        'purchase_order_id': ['exact', 'in'],
        'customer_id': ['exact', 'in'],
        'supplier_id': ['exact', 'in'],
        'value_balance': ['exact', 'gt', 'gte', 'lt', 'lte'],
        'due_date': ['exact', 'lte', 'gte'],
        'date_approved': ['exact', 'lte', 'gte'],
    }
    serializer_list = PaymentPlanListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Payment Plan List",
        operation_description="Get Payment Plan List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='paymentplan', model_code='paymentplan', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
