from drf_yasg.utils import swagger_auto_schema

from apps.sales.report.models import ReportRevenue, ReportProduct, ReportCustomer, ReportPipeline, ReportCashflow, \
    ReportInventory
from apps.sales.report.serializers import ReportInventoryListSerializer
from apps.sales.report.serializers.report_sales import ReportRevenueListSerializer, ReportProductListSerializer, \
    ReportCustomerListSerializer, ReportPipelineListSerializer, ReportCashflowListSerializer
from apps.shared import mask_view, BaseListMixin


# REPORT REVENUE
class ReportRevenueList(BaseListMixin):
    queryset = ReportRevenue.objects
    search_fields = ['sale_order__title']
    filterset_fields = {
        'group_inherit_id': ['exact', 'in'],
        'employee_inherit_id': ['exact', 'in'],
        'date_approved': ['lte', 'gte'],
    }
    serializer_list = ReportRevenueListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "sale_order",
            "sale_order__customer",
            "sale_order__employee_inherit",
        )

    @swagger_auto_schema(
        operation_summary="Report revenue List",
        operation_description="Get report revenue List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='report', model_code='reportrevenue', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)


# REPORT PRODUCT
class ReportProductList(BaseListMixin):
    queryset = ReportProduct.objects
    search_fields = ['product__title']
    filterset_fields = {
        'group_inherit_id': ['exact', 'in'],
        'employee_inherit_id': ['exact', 'in'],
        'date_approved': ['lte', 'gte'],
        'product_id': ['exact', 'in'],
    }
    serializer_list = ReportProductListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "product",
            "product__general_product_category",
        )

    @swagger_auto_schema(
        operation_summary="Report product List",
        operation_description="Get report product List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='report', model_code='reportproduct', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)


# REPORT CUSTOMER
class ReportCustomerList(BaseListMixin):
    queryset = ReportCustomer.objects
    search_fields = ['customer__name']
    filterset_fields = {
        'group_inherit_id': ['exact', 'in'],
        'employee_inherit_id': ['exact', 'in'],
        'date_approved': ['lte', 'gte'],
        'customer_id': ['exact', 'in'],
    }
    serializer_list = ReportCustomerListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "customer__industry",
            "employee_inherit"
        )

    @swagger_auto_schema(
        operation_summary="Report customer List",
        operation_description="Get report customer List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='report', model_code='reportcustomer', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)


# REPORT PIPELINE
class ReportPipelineList(BaseListMixin):
    queryset = ReportPipeline.objects
    search_fields = ['opportunity__title', 'opportunity__code', 'employee_inherit__search_content']
    filterset_fields = {
        'employee_inherit__group_id': ['exact', 'in'],
        'employee_inherit_id': ['exact', 'in'],
        'opportunity__close_date': ['exact', 'gte', 'lte'],
    }
    serializer_list = ReportPipelineListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "opportunity",
            "employee_inherit",
            "employee_inherit__group",
            "opportunity__customer",
        ).prefetch_related(
            'opportunity__opportunity_calllog',
            'opportunity__opportunity_send_email',
            'opportunity__opportunity_meeting',
            'opportunity__opportunity_document',
            'opportunity__opportunity_stage_opportunity',
        )

    @swagger_auto_schema(
        operation_summary="Report pipeline list",
        operation_description="Get report pipeline list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='report', model_code='reportpipeline', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)


# REPORT CASHFLOW
class ReportCashflowList(BaseListMixin):
    queryset = ReportCashflow.objects
    search_fields = ['sale_order__title']
    filterset_fields = {
        'group_inherit_id': ['exact', 'in'],
        'employee_inherit_id': ['exact', 'in'],
        'sale_order_id': ['exact', 'in'],
        'due_date': ['exact', 'gte', 'lte'],
    }
    serializer_list = ReportCashflowListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    # def get_queryset(self):
    #     return super().get_queryset().select_related(
    #         "employee_inherit",
    #     )

    @swagger_auto_schema(
        operation_summary="Report cashflow list",
        operation_description="Get report cashflow list",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='report', model_code='reportcashflow', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# REPORT INVENTORY
class ReportInventoryList(BaseListMixin):
    queryset = ReportInventory.objects
    serializer_list = ReportInventoryListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        print(self.request.query_params)
        try:
            order_param = self.request.query_params['order']
            return super().get_queryset().select_related(
                "product"
            ).filter(order=order_param)
        except KeyError:
            return super().get_queryset().select_related(
                "product"
            )

    @swagger_auto_schema(
        operation_summary="Report inventory List",
        operation_description="Get report inventory List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='report', model_code='reportinventory', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)
