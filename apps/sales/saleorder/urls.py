from django.urls import path

from .views import (
    SaleOrderList, SaleOrderDetail, SaleOrderExpenseList, SaleOrderConfigDetail, SaleOrderIndicatorList,
    SaleOrderIndicatorDetail, SaleOrderIndicatorCompanyRestore, ProductListSaleOrder, SaleOrderPurchasingStaffList
)

urlpatterns = [
    path('config', SaleOrderConfigDetail.as_view(), name='SaleOrderConfigDetail'),
    path('indicators', SaleOrderIndicatorList.as_view(), name='SaleOrderIndicatorList'),
    path('indicator/<str:pk>', SaleOrderIndicatorDetail.as_view(), name='SaleOrderIndicatorDetail'),
    path('indicator-restore/<str:pk>', SaleOrderIndicatorCompanyRestore.as_view(),
         name='SaleOrderIndicatorCompanyRestore'),

    path('list', SaleOrderList.as_view(), name='SaleOrderList'),
    path('<str:pk>', SaleOrderDetail.as_view(), name='SaleOrderDetail'),
    path('saleorder-expense-list/lists', SaleOrderExpenseList.as_view(), name='SaleOrderExpenseList'),
    path('product/list/<str:pk>', ProductListSaleOrder.as_view(), name='ProductListSaleOrder'),
    path('purchasing-staff/list', SaleOrderPurchasingStaffList.as_view(), name='SaleOrderPurchasingStaffList'),
]
