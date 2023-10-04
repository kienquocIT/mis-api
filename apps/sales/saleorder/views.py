from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.sales.saleorder.models import SaleOrder, SaleOrderExpense, SaleOrderAppConfig, SaleOrderIndicatorConfig, \
    SaleOrderProduct, SaleOrderCost
from apps.sales.saleorder.serializers import SaleOrderListSerializer, SaleOrderListSerializerForCashOutFlow, \
    SaleOrderCreateSerializer, SaleOrderDetailSerializer, SaleOrderUpdateSerializer, SaleOrderExpenseListSerializer, \
    SaleOrderProductListSerializer, SaleOrderPurchasingStaffListSerializer
from apps.sales.saleorder.serializers.sale_order_config import SaleOrderConfigUpdateSerializer, \
    SaleOrderConfigDetailSerializer
from apps.sales.saleorder.serializers.sale_order_indicator import SaleOrderIndicatorCompanyRestoreSerializer, \
    SaleOrderIndicatorListSerializer, SaleOrderIndicatorUpdateSerializer, SaleOrderIndicatorCreateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class SaleOrderList(BaseListMixin, BaseCreateMixin):
    queryset = SaleOrder.objects
    filterset_fields = ['delivery_call', 'system_status']
    serializer_list = SaleOrderListSerializer
    serializer_create = SaleOrderCreateSerializer
    serializer_detail = SaleOrderDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    # create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id',
        'company_id',
        'employee_created_id',
    ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "opportunity",
            "quotation",
            "employee_inherit",
        )

    @swagger_auto_schema(
        operation_summary="Sale Order List",
        operation_description="Get Sale Order List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saleorder', model_code='saleorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Sale Order",
        operation_description="Create new Sale Order",
        request_body=SaleOrderCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        employee_require=True,
        label_code='saleorder', model_code='saleorder', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SaleOrderDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = SaleOrder.objects
    serializer_detail = SaleOrderDetailSerializer
    serializer_update = SaleOrderUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "opportunity",
            "opportunity__customer",
            "customer",
            "contact",
            "payment_term",
            "quotation",
            "customer__payment_term_customer_mapped",
            "employee_inherit",
        ).prefetch_related(
            Prefetch(
                "sale_order_product_sale_order",
                queryset=SaleOrderProduct.objects.select_related(
                    "product",
                    'product__general_product_category',
                    'product__general_uom_group',
                    "product__sale_default_uom",
                    "product__sale_tax",
                    "product__sale_currency_using",
                    "unit_of_measure",
                    "tax",
                    "promotion",
                    "shipping",
                ),
            ),
            Prefetch(
                "sale_order_cost_sale_order",
                queryset=SaleOrderCost.objects.select_related(
                    "product",
                    'product__general_product_category',
                    'product__general_uom_group',
                    "product__sale_default_uom",
                    "product__sale_tax",
                    "product__sale_currency_using",
                    "unit_of_measure",
                    "tax",
                    "shipping",
                ),
            ),
        )

    @swagger_auto_schema(
        operation_summary="Sale Order detail",
        operation_description="Get Sale Order detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saleorder', model_code='saleorder', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Sale Order",
        operation_description="Update Sale Order by ID",
        request_body=SaleOrderUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saleorder', model_code='saleorder', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class SaleOrderExpenseList(BaseListMixin):
    queryset = SaleOrderExpense.objects
    serializer_list = SaleOrderExpenseListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("tax", "expense").filter(
            sale_order_id=self.request.query_params['filter_sale_order']
        )

    @swagger_auto_schema(
        operation_summary="SaleOrderExpense List",
        operation_description="Get SaleOrderExpense List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# Config
class SaleOrderConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = SaleOrderAppConfig.objects
    serializer_detail = SaleOrderConfigDetailSerializer
    serializer_update = SaleOrderConfigUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Sale Order Config Detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Sale Order Config Update",
        request_body=SaleOrderConfigUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)


# Indicator
class SaleOrderIndicatorList(
    BaseListMixin,
    BaseCreateMixin
):
    queryset = SaleOrderIndicatorConfig.objects
    filterset_fields = ['application_code']
    serializer_list = SaleOrderIndicatorListSerializer
    serializer_create = SaleOrderIndicatorCreateSerializer
    serializer_detail = SaleOrderIndicatorListSerializer
    list_hidden_field = ['company_id']
    create_hidden_field = ['company_id']

    @swagger_auto_schema(
        operation_summary="Sale Order Indicator List",
        operation_description="Get Sale Order Indicator List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Sale Order Indicator",
        operation_description="Create new Sale Order Indicator",
        request_body=SaleOrderIndicatorCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SaleOrderIndicatorDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = SaleOrderIndicatorConfig.objects
    serializer_detail = SaleOrderIndicatorListSerializer
    serializer_update = SaleOrderIndicatorUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Sale Order Indicator detail",
        operation_description="Get Sale Order Indicator detail by ID",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Sale Order Indicator",
        operation_description="Update Sale Order Indicator by ID",
        request_body=SaleOrderIndicatorUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class SaleOrderIndicatorCompanyRestore(
    BaseUpdateMixin,
):
    queryset = SaleOrderIndicatorConfig.objects
    serializer_detail = SaleOrderIndicatorListSerializer
    serializer_update = SaleOrderIndicatorCompanyRestoreSerializer

    @swagger_auto_schema(
        operation_summary="Restore Sale Order Indicator Of Company",
        operation_description="Restore Sale Order Indicator Of Company",
        request_body=SaleOrderIndicatorCompanyRestoreSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class SaleOrderListForCashOutFlow(BaseListMixin):
    queryset = SaleOrder.objects
    filterset_fields = []
    serializer_list = SaleOrderListSerializerForCashOutFlow
    list_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related("customer", "sale_person", "opportunity", "quotation")

    @swagger_auto_schema(
        operation_summary="Sale Order List For Cash Outflow",
        operation_description="Get Sale Order List For Cash Outflow",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        self.paginator.page_size = -1
        return self.list(request, *args, **kwargs)


class ProductListSaleOrder(BaseRetrieveMixin):
    queryset = SaleOrder.objects
    serializer_detail = SaleOrderProductListSerializer

    @swagger_auto_schema(
        operation_summary="SaleOrder Detail / Product List",
        operation_description="Get SaleOrder Detail / Product List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class SaleOrderPurchasingStaffList(BaseListMixin):
    queryset = SaleOrder.objects
    serializer_list = SaleOrderPurchasingStaffListSerializer
    filterset_fields = {
        'employee_inherit': ['exact', 'in'],
    }
    list_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Sale Order List For Purchasing Staff",
        operation_description="Get Sale Order List For Purchasing Staff"
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
