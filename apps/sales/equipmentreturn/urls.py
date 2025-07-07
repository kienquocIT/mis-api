from django.urls import path
from apps.sales.equipmentreturn.views import (
    EquipmentReturnList, EquipmentReturnDetail, EREquipmentLoanListByAccount
)

urlpatterns = [
    path('list', EquipmentReturnList.as_view(), name='EquipmentReturnList'),
    path('detail/<str:pk>', EquipmentReturnDetail.as_view(), name='EquipmentReturnDetail'),
    path('er-el-list-by-account', EREquipmentLoanListByAccount.as_view(), name='EREquipmentLoanListByAccount'),
]
