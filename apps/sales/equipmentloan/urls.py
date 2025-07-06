from django.urls import path
from apps.sales.equipmentloan.views import (
    ELProductList, ELWarehouseListByProduct, ELProductLotList, ELProductSerialList,
    EquipmentLoanList, EquipmentLoanDetail
)

urlpatterns = [
    path('list', EquipmentLoanList.as_view(), name='EquipmentLoanList'),
    path('detail/<str:pk>', EquipmentLoanDetail.as_view(), name='EquipmentLoanDetail'),
    path('el-product-list', ELProductList.as_view(), name='ELProductList'),
    path('el-warehouse-list-by-product', ELWarehouseListByProduct.as_view(), name='ELWarehouseListByProduct'),
    path('el-product-lot-list', ELProductLotList.as_view(), name='ELProductLotList'),
    path('el-product-serial-list', ELProductSerialList.as_view(), name='ELProductSerialList'),
]
