from django.urls import path

from .views import (
    ReportRevenueList, ReportProductList, ReportCustomerList, ReportPipelineList, ReportCashflowList,
    ReportInventoryDetailList, BalanceInitializationList, ReportInventoryList
)

urlpatterns = [
    path('revenue/list', ReportRevenueList.as_view(), name='ReportRevenueList'),
    path('product/list', ReportProductList.as_view(), name='ReportProductList'),
    path('customer/list', ReportCustomerList.as_view(), name='ReportCustomerList'),
    path('pipeline/list', ReportPipelineList.as_view(), name='ReportPipelineList'),
    path('cashflow/list', ReportCashflowList.as_view(), name='ReportCashflowList'),
    path('inventory-detail/list', ReportInventoryDetailList.as_view(), name='ReportInventoryDetailList'),
    path('balance-init/list', BalanceInitializationList.as_view(), name='BalanceInitializationList'),
    path('inventory/list', ReportInventoryList.as_view(), name='ReportInventoryList'),
]
