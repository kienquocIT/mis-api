from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.sales.saleorder.models import SaleOrder
from apps.sales.saleorder.serializers import SaleOrderListSerializer, \
    SaleOrderCreateSerializer, SaleOrderDetailSerializer, SaleOrderUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class SaleOrderList(
    BaseListMixin,
    BaseCreateMixin
):
    permission_classes = [IsAuthenticated]
    queryset = SaleOrder.objects
    filterset_fields = []
    serializer_list = SaleOrderListSerializer
    serializer_create = SaleOrderCreateSerializer
    serializer_detail = SaleOrderListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "sale_person"
        )

    @swagger_auto_schema(
        operation_summary="Sale Order List",
        operation_description="Get Sale Order List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Sale Order",
        operation_description="Create new Sale Order",
        request_body=SaleOrderCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SaleOrderDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    permission_classes = [IsAuthenticated]
    queryset = SaleOrder.objects
    serializer_detail = SaleOrderDetailSerializer
    serializer_update = SaleOrderUpdateSerializer

    def get_queryset(self):
        return super().get_queryset().select_related(
            "opportunity",
            "customer",
            "contact",
            "sale_person",
            "payment_term"
        )

    @swagger_auto_schema(
        operation_summary="Sale Order detail",
        operation_description="Get Sale Order detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        self.serializer_class = SaleOrderDetailSerializer
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Sale Order",
        operation_description="Update Sale Order by ID",
        request_body=SaleOrderUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = SaleOrderUpdateSerializer
        return self.update(request, *args, **kwargs)
