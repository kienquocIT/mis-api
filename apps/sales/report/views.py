import json
import datetime
from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import WareHouse, Periods, ProductWareHouse
from apps.sales.budgetplan.models import BudgetPlanCompanyExpense, BudgetPlanGroupExpense
from apps.sales.cashoutflow.models import Payment
from apps.sales.opportunity.models import OpportunityStage
from apps.sales.purchasing.models import PurchaseOrder
from apps.sales.report.inventory_log import ReportInvCommonFunc
from apps.sales.report.models import (
    ReportRevenue, ReportProduct, ReportCustomer, ReportPipeline, ReportCashflow,
    ReportStock, ReportInventoryCost, ReportStockLog, ReportInventorySubFunction, BalanceInitialization
)
from apps.sales.report.serializers import (
    ReportStockListSerializer, ReportInventoryCostListSerializer, ReportInventoryCostWarehouseDetailSerializer,
    BalanceInitializationListSerializer, BalanceInitializationDetailSerializer,
    BalanceInitializationCreateSerializer, BalanceInitializationCreateSerializerImportDB
)
from apps.sales.report.serializers.report_budget import (
    BudgetReportCompanyListSerializer,
    BudgetReportGroupListSerializer,
    PaymentListSerializerForBudgetPlan
)
from apps.sales.report.serializers.report_purchasing import PurchaseOrderListReportSerializer
from apps.sales.report.serializers.report_sales import (
    ReportRevenueListSerializer, ReportProductListSerializer, ReportCustomerListSerializer,
    ReportPipelineListSerializer, ReportCashflowListSerializer, ReportGeneralListSerializer,
    ReportProductListSerializerForDashBoard
)
from apps.sales.revenue_plan.models import RevenuePlanGroupEmployee
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin


# REPORT REVENUE
class ReportRevenueList(BaseListMixin):
    queryset = ReportRevenue.objects
    search_fields = ['sale_order__title']
    filterset_fields = {
        'group_inherit_id': ['exact', 'in'],
        'employee_inherit_id': ['exact', 'in'],
        'employee_inherit__group_id': ['exact', 'in'],
        'date_approved': ['lte', 'gte'],
        'sale_order_id': ['exact', 'in'],
        'sale_order__customer_id': ['exact', 'in'],
        'is_initial': ['exact'],
        'sale_order__system_status': ['exact'],
        'group_inherit__is_delete': ['exact'],
    }
    serializer_list = ReportRevenueListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "sale_order",
            "quotation",
            "opportunity",
            "customer",
            "employee_inherit",
        ).filter(group_inherit__is_delete=False, sale_order__system_status=3)

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
        'employee_inherit__group_id': ['exact', 'in'],
        'date_approved': ['lte', 'gte'],
        'product_id': ['exact', 'in'],
        'product__general_product_category_id': ['exact', 'in'],
        'sale_order__system_status': ['exact'],
        'group_inherit__is_delete': ['exact'],
    }
    serializer_list = ReportProductListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "sale_order",
            "sale_order__customer",
            "product",
            "product__general_product_category",
            "product__sale_default_uom",
        ).filter(group_inherit__is_delete=False, sale_order__system_status=3)

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


class ReportProductListForDashBoard(BaseListMixin):
    queryset = ReportProduct.objects
    search_fields = ['product__title']
    filterset_fields = {
        'group_inherit_id': ['exact', 'in'],
        'employee_inherit_id': ['exact', 'in'],
        'employee_inherit__group_id': ['exact', 'in'],
        'date_approved': ['lte', 'gte'],
        'product_id': ['exact', 'in'],
        'product__general_product_category_id': ['exact', 'in'],
        'sale_order__system_status': ['exact'],
        'group_inherit__is_delete': ['exact'],
    }
    serializer_list = ReportProductListSerializerForDashBoard
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "product",
            "product__general_product_category",
        ).filter(group_inherit__is_delete=False, sale_order__system_status=3)

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
        'employee_inherit__group_id': ['exact', 'in'],
        'date_approved': ['lte', 'gte'],
        'customer_id': ['exact', 'in'],
        'sale_order__system_status': ['exact'],
        'group_inherit__is_delete': ['exact'],
    }
    serializer_list = ReportCustomerListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "customer__industry",
            "employee_inherit"
        ).filter(group_inherit__is_delete=False, sale_order__system_status=3)

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
        'employee_inherit__group_id': ['exact', 'in'],
        'sale_order_id': ['exact', 'in'],
        'due_date': ['exact', 'gte', 'lte'],
        'sale_order__system_status': ['exact'],
        'purchase_order__system_status': ['exact'],
    }
    serializer_list = ReportCashflowListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "sale_order",
            "purchase_order",
        ).filter(group_inherit__is_delete=False)

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
class ReportInventoryCostList(BaseListMixin):
    queryset = ReportInventoryCost.objects
    serializer_list = ReportInventoryCostListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        filter_fields = {}
        try:
            period_mapped = Periods.objects.filter(id=self.request.query_params['period_mapped']).first()
            sub_period_order = self.request.query_params['sub_period_order']
            if 'sale_order' in self.request.query_params:
                filter_fields['sale_order_id'] = self.request.query_params['sale_order']

            for order in range(1, int(sub_period_order) + 1):
                run_state = ReportInvCommonFunc.check_and_push_to_this_sub(
                    self.request.user.tenant_current,
                    self.request.user.company_current,
                    self.request.user.employee_current,
                    period_mapped,
                    order
                )
                if run_state is False:
                    break

            if self.request.query_params['product_id_list'] != '':
                prd_id_list = self.request.query_params['product_id_list'].split(',')
                return_query = super().get_queryset().select_related(
                    "product__inventory_uom", "warehouse", "period_mapped"
                ).prefetch_related(
                    'product__report_inventory_cost_product',
                    'product__report_stock_log_product'
                ).filter(
                    period_mapped=period_mapped,
                    sub_period_order=sub_period_order,
                    product_id__in=prd_id_list,
                    **filter_fields
                )
                return return_query.order_by(
                    "warehouse__code", 'sale_order__code', '-product__code', 'lot_mapped__lot_number'
                )

            return_query = super().get_queryset().select_related(
                "product__inventory_uom", "warehouse", "period_mapped"
            ).prefetch_related(
                'product__report_inventory_cost_product',
                'product__report_stock_log_product'
            ).filter(
                period_mapped=period_mapped,
                sub_period_order=sub_period_order,
                **filter_fields
            )
            return return_query.order_by(
                'warehouse__code', 'sale_order__code', '-product__code', 'lot_mapped__lot_number'
            )
        except KeyError:
            return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Report inventory List",
        operation_description="Get report inventory List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='report', model_code='reportinventory', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        company_config = self.request.user.company_current.company_config
        if 'date_range' in request.query_params:
            self.ser_context = {
                'date_range': [int(num) for num in request.query_params['date_range'].split('-')]
            }
        self.ser_context['definition_inventory_valuation'] = company_config.definition_inventory_valuation
        self.ser_context['cost_cfg'] = ReportInvCommonFunc.get_cost_config(self.request.user.company_current)
        return self.list(request, *args, **kwargs)


class ReportStockList(BaseListMixin):
    queryset = ReportStock.objects
    serializer_list = ReportStockListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        try:
            period_mapped = Periods.objects.filter(id=self.request.query_params['period_mapped']).first()
            sub_period_order = int(self.request.query_params['sub_period_order'])

            tenant_obj = self.request.user.tenant_current
            company_obj = self.request.user.company_current
            div = self.request.user.company_current.company_config.definition_inventory_valuation
            if 'is_calculate' in self.request.query_params and div == 1:
                ReportInventorySubFunction.calculate_cost_dict_for_periodic(
                    period_mapped, sub_period_order, tenant_obj, company_obj
                )

            if self.request.query_params['product_id_list'] != '':
                prd_id_list = self.request.query_params['product_id_list'].split(',')
                return super().get_queryset().select_related(
                    "product", "period_mapped"
                ).prefetch_related(
                    'report_stock_log',
                    'product__report_inventory_cost_product__period_mapped',
                ).filter(
                    period_mapped=period_mapped, sub_period_order=sub_period_order, product_id__in=prd_id_list
                ).order_by('product__code', 'lot_mapped__lot_number')
            return super().get_queryset().select_related(
                "product", "period_mapped"
            ).prefetch_related(
                'report_stock_log',
                'product__report_inventory_cost_product__period_mapped',
            ).filter(
                period_mapped=period_mapped, sub_period_order=sub_period_order
            ).order_by('product__code', 'sale_order__code', 'lot_mapped__lot_number')
        except KeyError:
            return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Report inventory Detail",
        operation_description="Get report inventory Detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='report', model_code='reportinventory', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        tenant_id = self.request.user.tenant_current_id
        company_id = self.request.user.company_current_id
        company_config = self.request.user.company_current.company_config
        self.ser_context = {
            'wh_list': set(WareHouse.objects.filter(
                tenant_id=tenant_id, company_id=company_id
            ).values_list('id', 'code', 'title')),
        }
        if all([
            'period_mapped' in self.request.query_params,
            'sub_period_order' in self.request.query_params
        ]):
            self.ser_context['all_logs_by_month'] = ReportStockLog.objects.filter(
                tenant_id=tenant_id, company_id=company_id,
                report_stock__period_mapped_id=self.request.query_params['period_mapped'],
                report_stock__sub_period_order=self.request.query_params['sub_period_order']
            ).select_related('warehouse')
        else:
            self.ser_context['all_logs_by_month'] = ReportStockLog.objects.filter(
                tenant_id=tenant_id, company_id=company_id,
            ).select_related('warehouse')
        self.ser_context['definition_inventory_valuation'] = company_config.definition_inventory_valuation
        self.ser_context['cost_cfg'] = ReportInvCommonFunc.get_cost_config(self.request.user.company_current)
        return self.list(request, *args, **kwargs)


class BalanceInitializationList(BaseListMixin, BaseCreateMixin):
    queryset = BalanceInitialization.objects
    serializer_list = BalanceInitializationListSerializer
    serializer_create = BalanceInitializationCreateSerializer
    serializer_detail = BalanceInitializationDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('product', 'uom', 'warehouse').prefetch_related()

    @swagger_auto_schema(
        operation_summary="Balance Initialization list",
        operation_description="Balance Initialization list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Balance Initialization",
        operation_description="Create new Balance Initialization",
        request_body=BalanceInitializationCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        self.ser_context['employee_current'] = self.request.user.employee_current
        self.ser_context['company_current'] = self.request.user.company_current
        self.ser_context['tenant_current'] = self.request.user.tenant_current
        return self.create(request, *args, **kwargs)


class BalanceInitializationListImportDB(BaseCreateMixin):
    queryset = ReportInventoryCost.objects
    serializer_create = BalanceInitializationCreateSerializerImportDB
    serializer_detail = BalanceInitializationDetailSerializer

    @swagger_auto_schema(
        operation_summary="Create Balance Initialization Import BD",
        operation_description="Create new Balance Initialization Import BD",
        request_body=BalanceInitializationCreateSerializerImportDB,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        self.ser_context['employee_current'] = self.request.user.employee_current
        self.ser_context['company_current'] = self.request.user.company_current
        self.ser_context['tenant_current'] = self.request.user.tenant_current
        return self.create(request, *args, **kwargs)


class ReportInventoryCostWarehouseDetail(BaseListMixin):
    queryset = ProductWareHouse.objects
    serializer_list = ReportInventoryCostWarehouseDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        try:
            warehouse_id = self.request.query_params['warehouse_id']
            return super().get_queryset().select_related(
                'product__inventory_uom'
            ).prefetch_related(
                'product_warehouse_lot_product_warehouse',
                'product_warehouse_serial_product_warehouse'
            ).filter(
                warehouse_id=warehouse_id, stock_amount__gt=0
            ).order_by('product__code')
        except KeyError:
            return super().get_queryset().none()

    @swagger_auto_schema(operation_summary='Report Inventory Cost Warehouse Detail')
    @mask_view(
        login_require=True, auth_require=False
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# REPORT GENERAL
class ReportGeneralList(BaseListMixin):
    queryset = ReportRevenue.objects
    search_fields = ['group_inherit__title', 'employee_inherit__search_content']
    filterset_fields = {
        'group_inherit_id': ['exact', 'in'],
        'employee_inherit_id': ['exact', 'in'],
        'employee_inherit__group_id': ['exact', 'in'],
        'date_approved': ['lte', 'gte'],
        'is_initial': ['exact'],
        'group_inherit__is_delete': ['exact'],
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
        ).filter(group_inherit__is_delete=False, sale_order__system_status=3)

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


# REPORT PURCHASING
class PurchaseOrderListReport(BaseListMixin):
    queryset = PurchaseOrder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'supplier_id': ['exact'],
        'contact_id': ['exact'],
    }
    serializer_list = PurchaseOrderListReportSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        try:
            period_mapped_id = self.request.query_params.get('period_mapped')
            sub_period_order = self.request.query_params.get('sub_period_order')
            start_day = int(self.request.query_params.get('start_day'))
            end_day = int(self.request.query_params.get('end_day'))
            period_mapped = Periods.objects.filter(id=period_mapped_id).first()
            if period_mapped and sub_period_order and start_day and end_day:
                sub_period_order = int(sub_period_order) + period_mapped.space_month
                start_date = datetime.date(period_mapped.fiscal_year, sub_period_order, start_day)
                end_date = datetime.date(period_mapped.fiscal_year, sub_period_order, end_day)
                return super().get_queryset().select_related(
                    "supplier", "employee_inherit"
                ).prefetch_related(
                    "purchase_order_product_order__product",
                    "purchase_order_product_order__uom_order_actual",
                ).filter(
                    system_status=3,
                    delivered_date__date__range=[start_date, end_date]
                )
            return (super().get_queryset().select_related(
                "supplier", "employee_inherit"
            ).prefetch_related(
                "purchase_order_product_order__product",
                "purchase_order_product_order__uom_order_actual",
            ).filter(
                system_status=3,
                delivered_date__year=period_mapped.fiscal_year
            ))
        except KeyError:
            return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Purchase order List",
        operation_description="Get Purchase order List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='report', model_code='reportpurchasing', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)


# REPORT BUDGET
class BudgetReportCompanyList(BaseListMixin):
    queryset = BudgetPlanCompanyExpense.objects
    filterset_fields = {
        'budget_plan__period_mapped_id': ['exact'],
    }
    serializer_list = BudgetReportCompanyListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related().order_by('order')

    @swagger_auto_schema(
        operation_summary="Budget report list",
        operation_description="Budget report list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='report', model_code='reportbudget', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)


class BudgetReportGroupList(BaseListMixin):
    queryset = BudgetPlanGroupExpense.objects
    filterset_fields = {
        'budget_plan__period_mapped_id': ['exact'],
        'budget_plan_group__group_mapped_id': ['exact'],
    }
    serializer_list = BudgetReportGroupListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related().order_by('order')

    @swagger_auto_schema(
        operation_summary="Budget report list",
        operation_description="Budget report list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='report', model_code='reportbudget', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)


class PaymentListForBudgetReport(BaseListMixin):
    queryset = Payment.objects
    serializer_list = PaymentListSerializerForBudgetPlan
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        data_filter = {'system_status': 3}
        if 'period_id' in self.request.query_params:
            period_obj = Periods.objects.filter(id=self.request.query_params.get('period_id')).first()
            if period_obj:
                data_filter['date_approved__year__in'] = [period_obj.start_date.year, period_obj.end_date.year]
                if 'month_list' in self.request.query_params:
                    data_filter['date_approved__month__in'] = json.loads(self.request.query_params.get('month_list'))
                if 'group_id' in self.request.query_params:
                    data_filter['employee_inherit__group_id'] = self.request.query_params.get('group_id')
        if len(data_filter) > 0:
            return super().get_queryset().filter(**data_filter).prefetch_related('payment').select_related()
        return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Payment list for budget plan",
        operation_description="Payment list budget plan",
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
