from django.urls import path

from .views import (
    SaleOrderList, SaleOrderDetail, SaleOrderExpenseList, SaleOrderConfigDetail, SaleOrderIndicatorList,
    SaleOrderIndicatorDetail, SaleOrderIndicatorCompanyRestore, ProductListSaleOrder, SaleOrderPurchasingStaffList,
    SOProductWOList, SORecurrenceList, SaleOrderDDList, SaleOrderDetailPrint
)

urlpatterns = [
    path('config', SaleOrderConfigDetail.as_view(), name='SaleOrderConfigDetail'),
    path('indicators', SaleOrderIndicatorList.as_view(), name='SaleOrderIndicatorList'),
    path('indicator/<str:pk>', SaleOrderIndicatorDetail.as_view(), name='SaleOrderIndicatorDetail'),
    path('indicator-restore/<str:pk>', SaleOrderIndicatorCompanyRestore.as_view(),
         name='SaleOrderIndicatorCompanyRestore'),

    path('list', SaleOrderList.as_view(), name='SaleOrderList'),
    path('<str:pk>', SaleOrderDetail.as_view(), name='SaleOrderDetail'),
    path('print/<str:pk>', SaleOrderDetailPrint.as_view(), name='SaleOrderDetailPrint'),
    path('saleorder-expense-list/lists', SaleOrderExpenseList.as_view(), name='SaleOrderExpenseList'),
    path('product/list/<str:pk>', ProductListSaleOrder.as_view(), name='ProductListSaleOrder'),
    path('purchasing-staff/list', SaleOrderPurchasingStaffList.as_view(), name='SaleOrderPurchasingStaffList'),
    path('sale-order-product-wo/list', SOProductWOList.as_view(), name='SOProductWOList'),
    path('sale-order-recurrence/list', SORecurrenceList.as_view(), name='SORecurrenceList'),
    path('dropdown/list', SaleOrderDDList.as_view(), name='SaleOrderDDList'),
]
