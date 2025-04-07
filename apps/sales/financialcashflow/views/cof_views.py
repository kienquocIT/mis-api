from drf_yasg.utils import swagger_auto_schema

from apps.sales.apinvoice.models import APInvoice
from apps.sales.financialcashflow.models.cif_models import CashInflow
from apps.sales.financialcashflow.serializers import (
    AdvanceForSupplierForCashOutflowSerializer,
    APInvoiceListForCashOutflowSerializer
)
from apps.sales.purchasing.models import PurchaseOrderPaymentStage
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

__all__ = [
    'AdvanceForSupplierListForCashOutflow',
    'APInvoiceListForCashOutflow',
]


# main views


# related views
class AdvanceForSupplierListForCashOutflow(BaseListMixin):
    queryset = PurchaseOrderPaymentStage.objects
    filterset_fields = {
        'id': ['in'],
        'purchase_order__supplier_id': ['exact'],
        'cash_outflow_done': ['exact']
    }
    serializer_list = AdvanceForSupplierForCashOutflowSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(
            purchase_order__system_status=3,
            is_ap_invoice=False
        ).prefetch_related(
            'purchase_order__supplier',
        ).select_related('purchase_order').order_by('due_date')

    @swagger_auto_schema(
        operation_summary="Advance For Supplier list",
        operation_description="Advance For Supplier list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class APInvoiceListForCashOutflow(BaseListMixin):
    queryset = APInvoice.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {
        'id': ['in'],
        'supplier_mapped_id': ['exact'],
        'cash_outflow_done': ['exact']
    }
    serializer_list = APInvoiceListForCashOutflowSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(
            system_status=3
        ).prefetch_related(
            'ar_invoice_items',
            'purchase_order_mapped__purchase_order_payment_stage_po'
        ).select_related(
            'supplier_mapped',
            'purchase_order_mapped',
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
