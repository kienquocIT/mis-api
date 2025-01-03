from django.urls import path
from .views import (
    ReportRevenueList, ReportProductList, ReportCustomerList, ReportPipelineList, ReportCashflowList,
    ReportStockList, BalanceInitializationList, ReportInventoryCostList, ReportGeneralList,
    PurchaseOrderListReport, ReportInventoryCostWarehouseDetail, BudgetReportCompanyList, PaymentListForBudgetReport,
    BudgetReportGroupList, BalanceInitializationListImportDB, ReportProductListForDashBoard
)

urlpatterns = [
    path('revenue/list', ReportRevenueList.as_view(), name='ReportRevenueList'),
    path('product/list', ReportProductList.as_view(), name='ReportProductList'),
    path(
        'product-for-dashboard/list',
        ReportProductListForDashBoard.as_view(),
        name='ReportProductListForDashBoard'
    ),
    path('customer/list', ReportCustomerList.as_view(), name='ReportCustomerList'),
    path('pipeline/list', ReportPipelineList.as_view(), name='ReportPipelineList'),
    path('cashflow/list', ReportCashflowList.as_view(), name='ReportCashflowList'),

    path('general/list', ReportGeneralList.as_view(), name='ReportGeneralList'),

    # Report inventory
    path('balance-init/list', BalanceInitializationList.as_view(), name='BalanceInitializationList'),
    path(
        'balance-init-import-db/list',
        BalanceInitializationListImportDB.as_view(),
        name='BalanceInitializationListImportDB'
    ),
    path('inventory-cost-report/list', ReportInventoryCostList.as_view(), name='ReportInventoryCostList'),
    path('inventory-stock-report/list', ReportStockList.as_view(), name='ReportStockList'),
    path(
        'inventory-cost-warehouse-detail',
        ReportInventoryCostWarehouseDetail.as_view(),
        name='ReportInventoryCostWarehouseDetail'
    ),

    # Report purchasing
    path('po-report/list', PurchaseOrderListReport.as_view(), name='PurchaseOrderListReport'),

    # Report budget
    path('budget-report-company/list', BudgetReportCompanyList.as_view(), name='BudgetReportCompanyList'),
    path('budget-report-group/list', BudgetReportGroupList.as_view(), name='BudgetReportGroupList'),
    path('budget-report-payment/list', PaymentListForBudgetReport.as_view(), name='PaymentListForBudgetReport'),
]
