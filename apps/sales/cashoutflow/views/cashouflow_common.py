from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import Account
from apps.sales.cashoutflow.serializers.cashoutflow_common import (
    CashOutflowQuotationListSerializer, CashOutflowSaleOrderListSerializer, CashOutflowSupplierListSerializer
)
from apps.sales.quotation.models import Quotation
from apps.sales.saleorder.models import SaleOrder
from apps.shared import BaseListMixin, mask_view


class CashOutflowQuotationList(BaseListMixin):
    queryset = Quotation.objects
    search_fields = ['title', 'code', 'customer__name']
    filterset_fields = {
        'opportunity': ['exact', 'isnull'],
        'employee_inherit': ['exact'],
        'opportunity__sale_order': ['exact', 'isnull'],
        'opportunity__is_close_lost': ['exact'],
        'opportunity__is_deal_close': ['exact'],
        'system_status': ['exact', 'in'],
        'id': ['exact'],
    }
    serializer_list = CashOutflowQuotationListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(
            system_status=3,
            opportunity=None
        ).select_related().prefetch_related('sale_order_quotation')

    @swagger_auto_schema(
        operation_summary="Quotation List for Cash Outflow",
        operation_description="Get Quotation List for Cash Outflow",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='quotation', model_code='quotation', perm_code='view',
        opp_enabled=True, prj_enabled=True,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CashOutflowSaleOrderList(BaseListMixin):
    queryset = SaleOrder.objects
    search_fields = ['title', 'code', 'customer__name']
    filterset_fields = {
        'delivery_call': ['exact'],
        'system_status': ['exact', 'in'],
        'quotation_id': ['exact'],
        'customer_id': ['exact'],
        'employee_inherit_id': ['exact', 'in'],
        'employee_inherit__group_id': ['exact', 'in'],
        'opportunity_id': ['exact', 'in'],
        'has_regis': ['exact'],
    }
    serializer_list = CashOutflowSaleOrderListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(
            system_status=3,
            opportunity=None
        ).select_related("quotation")

    @swagger_auto_schema(
        operation_summary="Sale Order List for Cash Outflow",
        operation_description="Get Sale Order List for Cash Outflow",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saleorder', model_code='saleorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CashOutflowSupplierList(BaseListMixin):  # noqa
    queryset = Account.objects
    serializer_list = CashOutflowSupplierListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    search_fields = ['name', 'code', 'tax_code']

    def get_queryset(self):
        return super().get_queryset().filter(is_supplier_account=True).select_related().prefetch_related(
            'account_banks_mapped'
        )

    @swagger_auto_schema(
        operation_summary="Supplier list",
        operation_description="Supplier list",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='saledata', model_code='account', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
