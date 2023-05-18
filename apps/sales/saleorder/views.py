from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.sales.saleorder.models import SaleOrder, SaleOrderExpense
from apps.sales.saleorder.serializers import SaleOrderListSerializer, \
    SaleOrderCreateSerializer, SaleOrderDetailSerializer, SaleOrderUpdateSerializer, SaleOrderExpenseListSerializer
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
            "sale_person",
            "opportunity"
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
            "payment_term",
            "quotation"
        )

    @swagger_auto_schema(
        operation_summary="Sale Order detail",
        operation_description="Get Sale Order detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Sale Order",
        operation_description="Update Sale Order by ID",
        request_body=SaleOrderUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class SaleOrderExpenseList(BaseListMixin):
    permission_classes = [IsAuthenticated]
    queryset = SaleOrderExpense.objects
    serializer_list = SaleOrderExpenseListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related(
            "tax"
        )

    @swagger_auto_schema(
        operation_summary="SaleOrderExpense List",
        operation_description="Get SaleOrderExpense List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        kwargs.update({'sale_order_id': request.query_params['filter_sale_order']})
        return self.list(request, *args, **kwargs)
