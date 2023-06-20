from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.sales.saleorder.models import SaleOrder, SaleOrderExpense, SaleOrderAppConfig
from apps.sales.saleorder.serializers import SaleOrderListSerializer, \
    SaleOrderCreateSerializer, SaleOrderDetailSerializer, SaleOrderUpdateSerializer, SaleOrderExpenseListSerializer
from apps.sales.saleorder.serializers.sale_order_config import SaleOrderConfigUpdateSerializer, \
    SaleOrderConfigDetailSerializer
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
            "opportunity",
            "quotation"
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
            "quotation",
            "customer__payment_term_mapped",
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
            "tax",
            "expense"
        )

    @swagger_auto_schema(
        operation_summary="SaleOrderExpense List",
        operation_description="Get SaleOrderExpense List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        kwargs.update({
            'sale_order_id': request.query_params['filter_sale_order'],
        })
        return self.list(request, *args, **kwargs)


# Config
class SaleOrderConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = SaleOrderAppConfig.objects
    serializer_detail = SaleOrderConfigDetailSerializer
    serializer_update = SaleOrderConfigUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Sale Order Config Detail",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Sale Order Config Update",
        request_body=SaleOrderConfigUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)
