from drf_yasg.utils import swagger_auto_schema # noqa
from rest_framework.permissions import IsAuthenticated
from apps.masterdata.saledata.models.shipping import Shipping
from apps.masterdata.saledata.serializers.shipping import ShippingListSerializer, ShippingCreateSerializer, \
    ShippingDetailSerializer
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class ShippingList(BaseListMixin, BaseCreateMixin):
    queryset = Shipping.objects
    serializer_list = ShippingListSerializer
    serializer_create = ShippingCreateSerializer
    serializer_detail = ShippingDetailSerializer

    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Expense list",
        operation_description="Expense list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Expense",
        operation_description="Create new Expense",
        request_body=ShippingCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
