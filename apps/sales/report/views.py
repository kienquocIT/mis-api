from drf_yasg.utils import swagger_auto_schema

from apps.sales.report.models import ReportRevenue, ReportProduct, ReportCustomer
from apps.sales.report.serializers.report_sales import ReportRevenueListSerializer, ReportProductListSerializer, \
    ReportCustomerListSerializer
from apps.shared import mask_view, BaseListMixin


# REPORT
class ReportRevenueList(BaseListMixin):
    queryset = ReportRevenue.objects
    search_fields = ['sale_order__title']
    filterset_fields = {
        'group_inherit_id': ['exact'],
        'employee_inherit_id': ['exact'],
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
        return self.list(request, *args, **kwargs)


class ReportProductList(BaseListMixin):
    queryset = ReportProduct.objects
    search_fields = ['product__title']
    filterset_fields = {
        'group_inherit_id': ['exact'],
        'employee_inherit_id': ['exact'],
        'date_approved': ['lte', 'gte'],
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
        login_require=True, auth_require=False,
        label_code='report', model_code='reportproduct', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ReportCustomerList(BaseListMixin):
    queryset = ReportCustomer.objects
    search_fields = ['customer__name']
    filterset_fields = {
        'group_inherit_id': ['exact'],
        'employee_inherit_id': ['exact'],
        'date_approved': ['lte', 'gte'],
    }
    serializer_list = ReportCustomerListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "customer__industry",
        )

    @swagger_auto_schema(
        operation_summary="Report customer List",
        operation_description="Get report customer List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='report', model_code='reportcustomer', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
