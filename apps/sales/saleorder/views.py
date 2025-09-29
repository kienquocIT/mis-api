from drf_yasg.utils import swagger_auto_schema
from apps.sales.saleorder.models import (
    SaleOrder, SaleOrderExpense, SaleOrderAppConfig, SaleOrderIndicatorConfig, SaleOrderProduct
)
from apps.sales.saleorder.serializers import (
    SaleOrderListSerializer, SaleOrderCreateSerializer, SaleOrderDetailSerializer, SaleOrderUpdateSerializer,
    SaleOrderExpenseListSerializer, SaleOrderProductListSerializer,
    SOProductWOListSerializer, SaleOrderMinimalListSerializer, SORecurrenceListSerializer,
    SaleOrderDetailPrintSerializer
)
from apps.sales.saleorder.serializers.sale_order_config import (
    SaleOrderConfigUpdateSerializer, SaleOrderConfigDetailSerializer
)
from apps.sales.saleorder.serializers.sale_order_indicator import (
    SaleOrderIndicatorCompanyRestoreSerializer,SaleOrderIndicatorListSerializer, SaleOrderIndicatorUpdateSerializer,
    SaleOrderIndicatorCreateSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class SaleOrderList(BaseListMixin, BaseCreateMixin):
    queryset = SaleOrder.objects
    search_fields = ['title', 'code', 'customer__name']
    filterset_fields = {
        'id': ['exact', 'in'],
        'delivery_call': ['exact'],
        'system_status': ['exact', 'in'],
        'quotation_id': ['exact'],
        'employee_inherit_id': ['exact', 'in'],
        'employee_inherit__group_id': ['exact', 'in'],
        'opportunity_id': ['exact', 'in'],
        'opportunity__is_deal_close': ['exact'],
        'customer_id': ['exact', 'in'],
        'indicator_revenue': ['exact', 'gt', 'lt', 'gte', 'lte'],
        'date_approved': ['lte', 'gte'],
        'has_regis': ['exact'],
        'is_recurring': ['exact'],
        'document_root_id': ['exact'],
    }
    serializer_list = SaleOrderListSerializer
    serializer_list_minimal = SaleOrderMinimalListSerializer
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
        is_minimal = self.get_param(key='is_minimal')
        if is_minimal:
            return super().get_queryset()

        return super().get_queryset().select_related(
            "customer",
            "opportunity",
            "quotation",
            "employee_inherit",
        )
        # return self.get_queryset_custom_direct_page(main_queryset)

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
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class SaleOrderDDList(BaseListMixin):
    queryset = SaleOrder.objects
    search_fields = ['title', 'code', 'customer__name']
    filterset_fields = {
        'delivery_call': ['exact'],
        'system_status': ['exact', 'in'],
        'quotation_id': ['exact'],
        'customer_id': ['exact'],
        'employee_inherit_id': ['exact', 'in'],
        'employee_inherit__group_id': ['exact', 'in'],
        'opportunity_id': ['exact', 'in'],
        'opportunity__is_deal_close': ['exact'],
        'has_regis': ['exact'],
        'is_recurring': ['exact'],
    }
    serializer_list = SaleOrderMinimalListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Sale Order DD List",
        operation_description="Get Sale Order DD List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


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
            "employee_inherit",
            "process",
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
        self.ser_context = {'user': request.user}
        return self.update(request, *args, pk, **kwargs)


# PRINT VIEW
class SaleOrderDetailPrint(BaseRetrieveMixin):
    queryset = SaleOrder.objects
    serializer_detail = SaleOrderDetailPrintSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "opportunity",
            "opportunity__customer",
            "employee_inherit",
        )

    @swagger_auto_schema(
        operation_summary="Sale Order Detail Print",
        operation_description="Get Sale Order Detail Print By ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saleorder', model_code='saleorder', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)


class SaleOrderExpenseList(BaseListMixin):
    queryset = SaleOrderExpense.objects
    filterset_fields = {
        'sale_order_id': ['exact'],
    }
    serializer_list = SaleOrderExpenseListSerializer

    def get_queryset(self):
        return super().get_queryset().filter(sale_order__system_status=3).select_related("tax", "expense_item")

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
    @mask_view(
        login_require=True, auth_require=False,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Sale Order Config Update",
        request_body=SaleOrderConfigUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
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
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id', ]

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
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

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


class SOProductWOList(BaseListMixin, BaseCreateMixin):
    queryset = SaleOrderProduct.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'sale_order_id': ['exact', 'in'],
        'product__bom_product': ['isnull'],
        'product_id': ['exact', 'isnull'],
        'sale_order__opportunity_id': ['exact', 'isnull'],
        'sale_order__system_status': ['exact', 'in'],
    }
    serializer_list = SOProductWOListSerializer

    @swagger_auto_schema(
        operation_summary="SO Product Work Order List",
        operation_description="Get SO Product Work Order List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class SORecurrenceList(BaseListMixin, BaseCreateMixin):
    queryset = SaleOrder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'is_recurrence_template': ['exact'],
        'employee_inherit_id': ['exact'],
    }
    serializer_list = SORecurrenceListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related(
            "employee_inherit",
        )

    @swagger_auto_schema(
        operation_summary="SO Recurrence List",
        operation_description="Get SO Recurrence List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
