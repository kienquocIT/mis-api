import datetime
from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import WareHouse, Periods, SubPeriods, ProductWareHouse
from apps.sales.opportunity.models import OpportunityStage
from apps.sales.purchasing.models import PurchaseOrder
from apps.sales.report.models import (
    ReportRevenue, ReportProduct, ReportCustomer, ReportPipeline, ReportCashflow,
    ReportStock, ReportInventoryCost, ReportStockLog,
    ReportInventorySubFunction, ReportInventoryCostWH
)
from apps.sales.report.serializers import (
    ReportStockListSerializer, BalanceInitializationListSerializer,
    ReportInventoryCostListSerializer, ProductWarehouseViewListSerializer
)
from apps.sales.report.serializers.report_purchasing import PurchaseOrderListReportSerializer
from apps.sales.report.serializers.report_sales import (
    ReportRevenueListSerializer, ReportProductListSerializer, ReportCustomerListSerializer,
    ReportPipelineListSerializer, ReportCashflowListSerializer, ReportGeneralListSerializer
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
            "sale_order__customer",
            "sale_order__employee_inherit",
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
class ReportStockDetailList(BaseListMixin):
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
                ReportInventorySubFunction.calculate_ending_balance_for_periodic(
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
            ).order_by('product__code', 'lot_mapped__lot_number')
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
        self.ser_context['config_inventory_management'] = ReportStockLog.get_config_inventory_management(
            company_config
        )
        return self.list(request, *args, **kwargs)


class BalanceInitializationList(BaseListMixin, BaseCreateMixin):
    queryset = ReportInventoryCost.objects
    serializer_list = BalanceInitializationListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'product__inventory_uom',
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


class ReportStockList(BaseListMixin):
    queryset = ReportInventoryCost.objects
    serializer_list = ReportInventoryCostListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @classmethod
    def for_perpetual(
            cls, last_item, tenant, company, employee_current, period_mapped, sub_period_order, sub,
            bulk_info, bulk_info_wh
    ):
        quantity = last_item.ending_balance_quantity
        cost = last_item.ending_balance_cost
        value = last_item.ending_balance_value
        rp_prd_wh = ReportInventoryCost(
            tenant=tenant,
            company=company,
            employee_created=employee_current,
            employee_inherit=employee_current,
            product_id=last_item.product_id,
            lot_mapped_id=last_item.lot_mapped_id,
            warehouse_id=last_item.warehouse_id,
            sale_order_id=last_item.sale_order_id,
            period_mapped=period_mapped,
            sub_period_order=sub_period_order,
            sub_period=sub,
            opening_balance_quantity=quantity,
            opening_balance_cost=cost,
            opening_balance_value=value,
            ending_balance_quantity=quantity,
            ending_balance_cost=cost,
            ending_balance_value=value
        )
        bulk_info.append(rp_prd_wh)
        for report_inventory_cost in last_item.report_inventory_cost_wh.all():
            bulk_info_wh.append(
                ReportInventoryCostWH(
                    report_inventory_cost=rp_prd_wh,
                    warehouse=report_inventory_cost.warehouse,
                    opening_quantity=report_inventory_cost.ending_quantity,
                    ending_quantity=report_inventory_cost.ending_quantity
                )
            )
        return bulk_info, bulk_info_wh

    @classmethod
    def for_periodic(
            cls, last_item, tenant, company, employee_current, period_mapped, sub_period_order, sub,
            bulk_info, bulk_info_wh
    ):
        quantity = last_item.periodic_ending_balance_quantity
        cost = last_item.periodic_ending_balance_cost
        value = last_item.periodic_ending_balance_value
        rp_prd_wh = ReportInventoryCost(
            tenant=tenant,
            company=company,
            employee_created=employee_current,
            employee_inherit=employee_current,
            product_id=last_item.product_id,
            lot_mapped_id=last_item.lot_mapped_id,
            warehouse_id=last_item.warehouse_id,
            period_mapped=period_mapped,
            sub_period_order=sub_period_order,
            sub_period=sub,
            opening_balance_quantity=quantity,
            opening_balance_cost=cost,
            opening_balance_value=value,
            periodic_ending_balance_quantity=quantity,
            periodic_ending_balance_cost=cost,
            periodic_ending_balance_value=value
        )
        bulk_info.append(rp_prd_wh)
        for report_inventory_cost in last_item.report_inventory_cost_wh.all():
            bulk_info_wh.append(
                ReportInventoryCostWH(
                    report_inventory_cost=rp_prd_wh,
                    warehouse=report_inventory_cost.warehouse,
                    opening_quantity=report_inventory_cost.ending_quantity,
                    ending_quantity=report_inventory_cost.ending_quantity
                )
            )
        return bulk_info, bulk_info_wh

    @classmethod
    def create_this_sub_record(cls, tenant, company, employee_current, period_mapped, sub_period_order):
        sub_period = SubPeriods.objects.filter(period_mapped=period_mapped, order=sub_period_order).first()
        if all([
            not sub_period.run_report_inventory or sub_period.report_inventory_cost_sub_period.count() == 0,
            int(sub_period_order) > company.software_start_using_time.month - period_mapped.space_month
        ]):
            if sub_period_order == 12:
                last_sub_period_order = 1
                last_period_mapped = Periods.objects.filter(fiscal_year=period_mapped.fiscal_year - 1).first()
            else:
                last_sub_period_order = int(sub_period_order) - 1
                last_period_mapped = period_mapped

            all_subs = {
                'last': ReportInventoryCost.objects.filter(
                    tenant=tenant, company=company,
                    period_mapped=last_period_mapped, sub_period_order=last_sub_period_order
                ),
                'this': ReportInventoryCost.objects.filter(
                    tenant=tenant, company=company,
                    period_mapped=period_mapped, sub_period_order=sub_period_order
                )
            }

            bulk_info = []
            bulk_info_wh = []  # For project
            for last_item in all_subs['last']:
                if not all_subs['this'].filter(
                    product_id=last_item.product_id,
                    warehouse_id=last_item.warehouse_id,
                    lot_mapped_id=last_item.lot_mapped_id,
                    sale_order_id=last_item.sale_order_id,
                ).exists():
                    if company.company_config.definition_inventory_valuation == 0:
                        bulk_info, bulk_info_wh = cls.for_perpetual(
                            last_item, tenant, company, employee_current, period_mapped, sub_period_order, sub_period,
                            bulk_info, bulk_info_wh
                        )
                    if company.company_config.definition_inventory_valuation == 1:
                        bulk_info, bulk_info_wh = cls.for_periodic(
                            last_item, tenant, company, employee_current, period_mapped, sub_period_order, sub_period,
                            bulk_info, bulk_info_wh
                        )

            if len(bulk_info) > 0:
                ReportInventoryCost.objects.bulk_create(bulk_info)
                ReportInventoryCostWH.objects.bulk_create(bulk_info_wh)
                sub_period.run_report_inventory = True
                sub_period.save(update_fields=['run_report_inventory'])
        return True

    def get_queryset(self):
        filter_fields = {}
        try:
            period_mapped = Periods.objects.filter(id=self.request.query_params['period_mapped']).first()
            sub_period_order = self.request.query_params['sub_period_order']
            if 'sale_order' in self.request.query_params:
                filter_fields['sale_order_id'] = self.request.query_params['sale_order']

            self.create_this_sub_record(
                self.request.user.tenant_current,
                self.request.user.company_current,
                self.request.user.employee_current,
                period_mapped,
                sub_period_order
            )

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
                if self.request.user.company_current.company_config.cost_per_project:
                    return return_query.order_by(
                        "warehouse__code", 'sale_order__code', '-product__code', 'lot_mapped__lot_number'
                    )
                return return_query.order_by('warehouse__code', '-product__code', 'lot_mapped__lot_number')

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
            if self.request.user.company_current.company_config.cost_per_project:
                return return_query.order_by(
                    'warehouse__code', 'sale_order__code', '-product__code', 'lot_mapped__lot_number'
                )
            return return_query.order_by('warehouse__code', '-product__code', 'lot_mapped__lot_number')
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
        self.ser_context['config_inventory_management'] = ReportStockLog.get_config_inventory_management(
            company_config
        )
        return self.list(request, *args, **kwargs)


class ProductWarehouseViewList(BaseListMixin):
    queryset = ProductWareHouse.objects
    serializer_list = ProductWarehouseViewListSerializer
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

    @swagger_auto_schema(operation_summary='Product WareHouse View')
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
