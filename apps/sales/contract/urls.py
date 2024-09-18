from django.urls import path

from .views import (
    ContractApprovalList, ContractApprovalDetail
)

urlpatterns = [
    path('list', ContractApprovalList.as_view(), name='ContractApprovalList'),
    path('<str:pk>', ContractApprovalDetail.as_view(), name='ContractApprovalDetail'),
]
