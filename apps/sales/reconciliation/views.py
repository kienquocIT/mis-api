from drf_yasg.utils import swagger_auto_schema

from apps.sales.arinvoice.models import ARInvoice
from apps.sales.financialcashflow.models import CashInflow
from apps.sales.reconciliation.models import Reconciliation
from apps.sales.reconciliation.serializers import (
    ReconListSerializer, ReconDetailSerializer, ReconCreateSerializer, ARInvoiceListForReconSerializer,
    CashInflowListForReconSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin


__all__ = [
    'ReconList',
    'ReconDetail',
    'ARInvoiceListForRecon',
    'CashInflowListForRecon'
]


# main views
class ReconList(BaseListMixin, BaseCreateMixin):
    queryset = Reconciliation.objects
    search_fields = ['title', 'customer__name']
    serializer_list = ReconListSerializer
    serializer_create = ReconCreateSerializer
    serializer_detail = ReconDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

    @swagger_auto_schema(
        operation_summary="Recon list",
        operation_description="Recon list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialrecon', model_code='reconciliation', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Recon",
        operation_description="Create new Recon",
        request_body=ReconCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialrecon', model_code='reconciliation', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ReconDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Reconciliation.objects  # noqa
    serializer_list = ReconListSerializer
    serializer_create = ReconCreateSerializer
    serializer_detail = ReconDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

    @swagger_auto_schema(operation_summary='Detail Recon')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialrecon', model_code='reconciliation', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


# related views
class ARInvoiceListForRecon(BaseListMixin):
    queryset = ARInvoice.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {'customer_mapped_id': ['exact']}
    serializer_list = ARInvoiceListForReconSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(system_status=3).prefetch_related(
            'ar_invoice_items',
            'recon_item_ar_invoice',
            'customer_mapped__cash_inflow_customer',
            'customer_mapped__cash_inflow_customer__recon_item_cash_inflow',
        ).select_related(
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


class CashInflowListForRecon(BaseListMixin):
    queryset = CashInflow.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {'customer_id': ['exact']}
    serializer_list = CashInflowListForReconSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(
            no_ar_invoice_value__gt=0
        ).prefetch_related('recon_item_cash_inflow').select_related().order_by('date_created')

    @swagger_auto_schema(
        operation_summary="Cash Inflow list",
        operation_description="Cash Inflow list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
