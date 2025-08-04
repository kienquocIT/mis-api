from drf_yasg.utils import swagger_auto_schema

from apps.sales.apinvoice.models import APInvoice
from apps.sales.arinvoice.models import ARInvoice
from apps.sales.financialcashflow.models import CashInflow, CashOutflow
from apps.sales.reconciliation.models import Reconciliation
from apps.sales.reconciliation.serializers import (
    ReconListSerializer, ReconDetailSerializer, ReconCreateSerializer, ARInvoiceListForReconSerializer,
    CashInflowListForReconSerializer, APInvoiceListForReconSerializer, CashOutflowListForReconSerializer,
    ReconUpdateSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin


__all__ = [
    'ReconList',
    'ReconDetail',
    'APInvoiceListForRecon',
    'CashOutflowListForRecon',
    'ARInvoiceListForRecon',
    'CashInflowListForRecon'
]

# main views
class ReconList(BaseListMixin, BaseCreateMixin):
    queryset = Reconciliation.objects
    search_fields = ['title', 'business_partner__name']
    serializer_list = ReconListSerializer
    serializer_create = ReconCreateSerializer
    serializer_detail = ReconDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Recon list",
        operation_description="Recon list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='reconciliation', model_code='reconciliation', perm_code='view',
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
        label_code='reconciliation', model_code='reconciliation', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'tenant_id': request.user.tenant_current_id,
            'company_id': request.user.company_current_id,
        }
        return self.create(request, *args, **kwargs)


class ReconDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Reconciliation.objects  # noqa
    serializer_list = ReconListSerializer
    serializer_update = ReconUpdateSerializer
    serializer_detail = ReconDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

    @swagger_auto_schema(operation_summary='Detail Recon')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='reconciliation', model_code='reconciliation', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Recon", request_body=ReconUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        label_code='reconciliation', model_code='reconciliation', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {
            'tenant_id': request.user.tenant_current_id,
            'company_id': request.user.company_current_id,
        }
        return self.update(request, *args, **kwargs)


# related views
class APInvoiceListForRecon(BaseListMixin):
    queryset = APInvoice.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {'supplier_mapped_id': ['exact']}
    serializer_list = APInvoiceListForReconSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(system_status=3).prefetch_related(
            'ap_invoice_items',
        ).select_related(
            'supplier_mapped',
        ).order_by('date_created')

    @swagger_auto_schema(
        operation_summary="APInvoice list",
        operation_description="APInvoice list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CashOutflowListForRecon(BaseListMixin):
    queryset = CashOutflow.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {
        'customer_id': ['exact'],
        'supplier_id': ['exact'],
    }
    serializer_list = CashOutflowListForReconSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(
            no_ap_invoice_value__gt=0
        ).prefetch_related().select_related().order_by('date_created')

    @swagger_auto_schema(
        operation_summary="Cash Outflow list",
        operation_description="Cash Outflow list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


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
        ).prefetch_related().select_related().order_by('date_created')

    @swagger_auto_schema(
        operation_summary="Cash Inflow list",
        operation_description="Cash Inflow list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
