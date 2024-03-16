from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import WareHouse
from apps.sales.opportunity.models import OpportunityStage
from apps.sales.report.models import ReportRevenue, ReportProduct, ReportCustomer, ReportPipeline, ReportCashflow, \
    ReportInventory, ReportInventoryProductWarehouse
from apps.sales.report.serializers import (
    ReportInventoryDetailListSerializer, BalanceInitializationListSerializer, ReportInventoryListSerializer
)
from apps.sales.report.serializers.report_sales import ReportRevenueListSerializer, ReportProductListSerializer, \
    ReportCustomerListSerializer, ReportPipelineListSerializer, ReportCashflowListSerializer, \
    ReportGeneralListSerializer
from apps.sales.revenue_plan.models import RevenuePlanGroupEmployee
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin


# REPORT REVENUE
class ReportRevenueList(BaseListMixin):
    queryset = ReportRevenue.objects
    search_fields = ['sale_order__title']
    filterset_fields = {
        'group_inherit_id': ['exact', 'in'],
        'employee_inherit_id': ['exact', 'in'],
        'date_approved': ['lte', 'gte'],
        'sale_order_id': ['exact', 'in'],
        'sale_order__customer_id': ['exact', 'in'],
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
            Prefetch(
                'opportunity__opportunity_stage_opportunity',
                queryset=OpportunityStage.objects.select_related('stage'),
            ),
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
class ReportInventoryDetailList(BaseListMixin):
    queryset = ReportInventory.objects
    serializer_list = ReportInventoryDetailListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        try:
            if self.request.query_params['product_id_list'] != '':
                return super().get_queryset().select_related(
                    "product", "period_mapped"
                ).prefetch_related(
                    'report_inventory_by_month',
                    'product__report_inventory_product_warehouse_product__period_mapped',
                ).filter(
                    sub_period_order=self.request.query_params['sub_period_order'],
                    period_mapped_id=self.request.query_params['period_mapped'],
                    product_id__in=self.request.query_params['product_id_list'].split(',')
                )
            return super().get_queryset().select_related(
                "product", "period_mapped"
            ).prefetch_related(
                'report_inventory_by_month',
                'product__report_inventory_product_warehouse_product__period_mapped',
            ).filter(
                sub_period_order=self.request.query_params['sub_period_order'],
                period_mapped_id=self.request.query_params['period_mapped'],
            )
        except KeyError:
            return super().get_queryset().select_related(
                "product", "period_mapped",
            ).prefetch_related(
                'report_inventory_by_month',
                'product__report_inventory_product_warehouse_product__period_mapped',
            )

    @swagger_auto_schema(
        operation_summary="Report inventory Detail",
        operation_description="Get report inventory Detail",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='report', model_code='reportinventory', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        self.ser_context = {
            'wh_list': set(WareHouse.objects.all().values_list('id', 'code', 'title'))
        }
        return self.list(request, *args, **kwargs)


class BalanceInitializationList(BaseListMixin, BaseCreateMixin):
    queryset = ReportInventoryProductWarehouse.objects
    serializer_list = BalanceInitializationListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related(
            'product',
            'warehouse',
            'period_mapped'
        ).prefetch_related().filter(for_balance=True).order_by('warehouse')

    @swagger_auto_schema(
        operation_summary="Balance Initialization list",
        operation_description="Balance Initialization list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ReportInventoryList(BaseListMixin):
    queryset = ReportInventoryProductWarehouse.objects
    serializer_list = ReportInventoryListSerializer

    def get_queryset(self):
        try:
            if self.request.query_params['product_id_list'] != '':
                return super().get_queryset().select_related(
                    "product__inventory_uom", "warehouse", "period_mapped"
                ).prefetch_related(
                    'product__report_inventory_product_warehouse_product',
                    'product__report_inventory_by_month_product'
                ).filter(
                    sub_period_order=self.request.query_params['sub_period_order'],
                    period_mapped_id=self.request.query_params['period_mapped'],
                    product_id__in=self.request.query_params['product_id_list'].split(',')
                )
            return super().get_queryset().select_related(
                "product__inventory_uom", "warehouse", "period_mapped"
            ).prefetch_related(
                'product__report_inventory_product_warehouse_product',
                'product__report_inventory_by_month_product'
            ).filter(
                sub_period_order=self.request.query_params['sub_period_order'],
                period_mapped_id=self.request.query_params['period_mapped'],
            )
        except KeyError:
            return super().get_queryset().select_related(
                "product__inventory_uom", "warehouse", "period_mapped"
            ).prefetch_related(
                'product__report_inventory_product_warehouse_product',
                'product__report_inventory_by_month_product__report_inventory'
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
        if 'date_range' in request.query_params:
            self.ser_context = {
                'date_range': [int(num) for num in request.query_params['date_range'].split('-')],
            }
        return self.list(request, *args, **kwargs)


# REPORT REVENUE
class ReportGeneralList(BaseListMixin):
    queryset = ReportRevenue.objects
    search_fields = ['group_inherit__title', 'employee_inherit__search_content']
    filterset_fields = {
        'group_inherit_id': ['exact', 'in'],
        'employee_inherit_id': ['exact', 'in'],
        'date_approved': ['lte', 'gte'],
    }
    serializer_list = ReportGeneralListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "employee_inherit",
            "group_inherit",
        ).prefetch_related(
            Prefetch(
                'employee_inherit__rp_group_employee_employee',
                queryset=RevenuePlanGroupEmployee.objects.select_related(
                    'revenue_plan_mapped',
                    'revenue_plan_mapped__period_mapped',
                ),
            ),
        )

    @swagger_auto_schema(
        operation_summary="Report general List",
        operation_description="Get report general List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='report', model_code='reportrevenue', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
