from django.urls import path
from apps.sales.equipmentloan.views import (
    LoanProductList, WarehouseListByProduct, ProductLotList, ProductSerialList, EquipmentLoanList, EquipmentLoanDetail
)

urlpatterns = [
    path('list', EquipmentLoanList.as_view(), name='EquipmentLoanList'),
    path('detail/<str:pk>', EquipmentLoanDetail.as_view(), name='EquipmentLoanDetail'),
    path('loan-product-list', LoanProductList.as_view(), name='LoanProductList'),
    path('warehouse-list-by-product', WarehouseListByProduct.as_view(), name='WarehouseListByProduct'),
    path('product-lot-list', ProductLotList.as_view(), name='ProductLotList'),
    path('product-serial-list', ProductSerialList.as_view(), name='ProductSerialList'),
]
