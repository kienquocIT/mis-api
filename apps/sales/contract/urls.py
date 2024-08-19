from django.urls import path

from .views import (
    ContractList, ContractDetail
)

urlpatterns = [
    path('list', ContractList.as_view(), name='ContractList'),
    path('<str:pk>', ContractDetail.as_view(), name='ContractDetail'),
]
