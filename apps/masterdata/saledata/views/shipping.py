from drf_yasg.utils import swagger_auto_schema # noqa
from rest_framework.permissions import IsAuthenticated
from apps.masterdata.saledata.models import Shipping
from apps.masterdata.saledata.serializers import ShippingListSerializer, ShippingCreateSerializer, \
    ShippingDetailSerializer, ShippingUpdateSerializer, ShippingCheckListSerializer
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class ShippingList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated]
    queryset = Shipping.objects
    serializer_list = ShippingListSerializer
    serializer_create = ShippingCreateSerializer
    serializer_detail = ShippingDetailSerializer

    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Shipping list",
        operation_description="Shipping list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Shipping",
        operation_description="Create new Shipping",
        request_body=ShippingCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ShippingDetail(BaseRetrieveMixin, BaseUpdateMixin):
    permission_classes = [IsAuthenticated] # noqa
    queryset = Shipping.objects
    serializer_detail = ShippingDetailSerializer
    serializer_update = ShippingUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Shipping detail",
        operation_description="Get Expense detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Shipping",
        operation_description="Update Shipping by ID",
        request_body=ShippingUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ShippingCheckList(BaseListMixin):
    permission_classes = [IsAuthenticated]
    queryset = Shipping.objects
    serializer_list = ShippingCheckListSerializer
    serializer_detail = ShippingDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Shipping check list",
        operation_description="Shipping check list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
