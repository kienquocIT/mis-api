from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import Account, DocumentType
from apps.sales.bidding.models import Bidding, BiddingResultConfig
from apps.sales.bidding.serializers.bidding import (
    BiddingListSerializer, DocumentMasterDataBiddingListSerializer, AccountForBiddingListSerializer,
    BiddingCreateSerializer, BiddingDetailSerializer, BiddingUpdateSerializer, BiddingUpdateResultSerializer,
    BiddingResultConfigListSerializer, BiddingResultConfigCreateSerializer, BiddingResultConfigDetailSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class BiddingResultConfigList(BaseListMixin, BaseCreateMixin):
    queryset = BiddingResultConfig.objects
    serializer_list = BiddingResultConfigListSerializer
    serializer_create = BiddingResultConfigCreateSerializer
    serializer_detail = BiddingResultConfigDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Bidding Result Config list",
        operation_description="Bidding Result Config list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Bidding Result Config",
        operation_description="Create new Bidding Result Config",
        request_body=BiddingResultConfigCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BiddingList(BaseListMixin, BaseCreateMixin):
    queryset = Bidding.objects
    serializer_list = BiddingListSerializer
    serializer_detail = BiddingDetailSerializer
    serializer_create = BiddingCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id',
        'company_id',
        'employee_created_id',
    ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
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

    @swagger_auto_schema(
        operation_summary="Create Bidding",
        operation_description="Create New Bidding",
        request_body=BiddingCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        employee_require=True,
        label_code='bidding', model_code='bidding', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class BiddingDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Bidding.objects
    serializer_detail = BiddingDetailSerializer
    serializer_update = BiddingUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "opportunity",
            "customer",
            "employee_inherit",
        ).prefetch_related(
            "other_bidder",
            "venture_partner",
            "attachment_m2m"
        )

    @swagger_auto_schema(
        operation_summary="Bidding List",
        operation_description="Get Bidding List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='bidding', model_code='bidding', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Bidding List",
        operation_description="Get Bidding List",
        request_body=BiddingUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='bidding', model_code='bidding', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, pk, **kwargs)


class BiddingResult(BaseRetrieveMixin, BaseCreateMixin):
    queryset = Bidding.objects
    serializer_list = BiddingListSerializer
    serializer_detail = BiddingDetailSerializer
    serializer_create = BiddingUpdateResultSerializer
    create_hidden_field = [
        'tenant_id',
        'company_id',
        'employee_created_id',
    ]
    @swagger_auto_schema(
        operation_summary="Update Bidding Result",
        operation_description="Create Bidding Result",
        request_body=BiddingUpdateResultSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        employee_require=True,
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)

class AccountForBiddingList(BaseListMixin):
    queryset = Account.objects
    serializer_list = AccountForBiddingListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    filterset_fields = {
        'is_partner_account': ['exact'],
        'is_competitor_account': ['exact']
    }
    search_fields = []

    @swagger_auto_schema(
        operation_summary="Account For Bidding list",
        operation_description="Account List for Bidding",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='bidding', model_code='bidding', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DocumentMasterDataBiddingList(BaseListMixin):
    queryset = DocumentType.objects
    serializer_list = DocumentMasterDataBiddingListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    filterset_fields = {}
    search_fields = ['title']

    @swagger_auto_schema(
        operation_summary="Document Masterdata Bidding list",
        operation_description="Document Masterdata for Bidding Document list",
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
