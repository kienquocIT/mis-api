from drf_yasg.utils import swagger_auto_schema

from apps.sales.apinvoice.models import APInvoice
from apps.sales.financialcashflow.models.cof_models import CashOutflow
from apps.sales.financialcashflow.serializers.cof_serializers import (
    CashOutflowListSerializer, CashOutflowCreateSerializer,
    CashOutflowUpdateSerializer, CashOutflowDetailSerializer,
    AdvanceForSupplierForCashOutflowSerializer, APInvoiceListForCashOutflowSerializer
)
from apps.sales.purchasing.models import PurchaseOrderPaymentStage
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

__all__ = [
    'CashOutflowList',
    'CashOutflowDetail',
    'AdvanceForSupplierListForCashOutflow',
    'APInvoiceListForCashOutflow',
]


# main views
class CashOutflowList(BaseListMixin, BaseCreateMixin):
    queryset = CashOutflow.objects
    search_fields = ['title', 'code']
    serializer_list = CashOutflowListSerializer
    serializer_create = CashOutflowCreateSerializer
    serializer_detail = CashOutflowDetailSerializer
    filterset_fields = {}
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="CashOutflow list",
        operation_description="CashOutflow list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialcashflow', model_code='cashoutflow', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Cash Outflow",
        operation_description="Create new Cash Outflow",
        request_body=CashOutflowCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialcashflow', model_code='cashoutflow', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CashOutflowDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = CashOutflow.objects
    serializer_detail = CashOutflowDetailSerializer
    serializer_update = CashOutflowUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(operation_summary='Detail CashOutflow')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialcashflow', model_code='cashoutflow', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update CashOutflow", request_body=CashOutflowUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialcashflow', model_code='cashoutflow', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


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
            'ap_invoice_items',
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
