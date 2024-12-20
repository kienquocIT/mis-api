from drf_yasg.utils import swagger_auto_schema

from apps.sales.saleorder.models import SaleOrder
from apps.shared import BaseListMixin, mask_view
from apps.sales.arinvoice.models import ARInvoice
from apps.sales.financialcashflow.serializers import (
    ARInvoiceListForCashInflowSerializer
)

__all__ = [
    'ARInvoiceListForCashInflow',
]


class ARInvoiceListForCashInflow(BaseListMixin):
    queryset = ARInvoice.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {'customer_mapped_id': ['exact']}
    serializer_list = ARInvoiceListForCashInflowSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related(
            'customer_mapped',
        ).order_by('date_created')

    @swagger_auto_schema(
        operation_summary="ARInvoice list",
        operation_description="ARInvoice list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
