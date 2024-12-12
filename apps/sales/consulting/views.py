from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import Account, ProductCategory
from apps.sales.consulting.models import Consulting
from apps.sales.consulting.serializers.consulting import ConsultingListSerializer, ConsultingDetailSerializer, \
    ConsultingCreateSerializer, ConsultingAccountListSerializer, ConsultingProductCategoryListSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin


class ConsultingList(BaseListMixin, BaseCreateMixin):
    queryset = Consulting.objects
    serializer_list = ConsultingListSerializer
    serializer_detail = ConsultingDetailSerializer
    serializer_create = ConsultingCreateSerializer
    search_fields = ['title', 'customer__name']
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
        operation_summary="Consulting List",
        operation_description="Get Consulting List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='consulting', model_code='consulting', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Consulting",
        operation_description="Create New Consulting",
        request_body=ConsultingCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        employee_require=True,
        label_code='consulting', model_code='consulting', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class ConsultingDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Consulting.objects
    serializer_detail = ConsultingDetailSerializer
    # serializer_update = BiddingUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "opportunity",
            "customer",
            "employee_inherit",
        ).prefetch_related(
            "product_categories",
            "attachment_data"
        )

    @swagger_auto_schema(
        operation_summary="Consulting Detail",
        operation_description="Get Consulting Detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='consulting', model_code='consulting', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    # @swagger_auto_schema(
    #     operation_summary="Bidding List",
    #     operation_description="Get Bidding List",
    #     request_body=BiddingUpdateSerializer,
    # )
    # @mask_view(
    #     login_require=True, auth_require=True,
    #     label_code='bidding', model_code='bidding', perm_code='edit',
    # )
    # def put(self, request, *args, pk, **kwargs):
    #     self.ser_context = {'user': request.user}
    #     return self.update(request, *args, pk, **kwargs)


class ConsultingAccountList(BaseListMixin):
    queryset = Account.objects
    serializer_list = ConsultingAccountListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_customer_account=True)

    @swagger_auto_schema(
        operation_summary="Account For Consulting",
        operation_description="Account List for consulting",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class ConsultingProductCategoryList(BaseListMixin):
    queryset = ProductCategory.objects
    serializer_list = ConsultingProductCategoryListSerializer

    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Prod Category For Consulting",
        operation_description="Prod Category List for consulting",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)