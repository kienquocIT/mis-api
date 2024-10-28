from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.filters import AccountListFilter
from apps.masterdata.saledata.models import Account, DocumentType
from apps.sales.bidding.models import Bidding
from apps.sales.bidding.serializers.bidding import BiddingListSerializer, \
    DocumentMasterDataBiddingListSerializer, AccountForBiddingListSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

class BiddingList(BaseListMixin, BaseCreateMixin):
    queryset = Bidding.objects
    serializer_list = BiddingListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id',
        'company_id',
        'employee_created_id',
    ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "opportunity",
            "account",
            "employee_inherit",
        )

    @swagger_auto_schema(
        operation_summary="Bidding List",
        operation_description="Get Bidding List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='bidding', model_code='bidding', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class AccountForBiddingList(BaseListMixin):
    queryset = Account.objects
    serializer_list = AccountForBiddingListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT
    filterset_fields = {
        'is_partner_account': ['exact'],
        'is_customer_account': ['exact'],
    }
    search_fields = ['name', 'code', 'tax_code']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'owner', 'payment_term_customer_mapped', 'payment_term_supplier_mapped'
        ).prefetch_related(
            'contact_account_name', 'account_banks_mapped',
            'company__saledata_periods_belong_to_company',
            'report_customer_customer',
            'account_mapped_billing_address'
        )

    @swagger_auto_schema(
        operation_summary="Account For Bidding list",
        operation_description="Account List for Bidding",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='bidding', model_code='bidding', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DocumentMasterDataBiddingList(BaseListMixin):
    queryset = DocumentType.objects
    serializer_list = DocumentMasterDataBiddingListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT
    filterset_fields = {}
    search_fields = ['title']

    @swagger_auto_schema(
        operation_summary="Document Masterdata Bidding list",
        operation_description="Document Masterdata for Bidding Document list",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='bidding', model_code='bidding', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
