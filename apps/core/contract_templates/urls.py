from django.urls import path

from .views import ContractTemplateList, ContractTemplateDetail

urlpatterns = [
    path('list', ContractTemplateList.as_view(), name='ContractTemplateList'),
    path('detail/<str:pk>', ContractTemplateDetail.as_view(), name='ContractTemplateDetail'),
]
