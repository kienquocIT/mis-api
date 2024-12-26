from django.urls import path

from .views import ContractTemplateList, ContractTemplateDetail, ContractTemplateDDList

urlpatterns = [
    path('list', ContractTemplateList.as_view(), name='ContractTemplateList'),
    path('dd-list', ContractTemplateDDList.as_view(), name='ContractTemplateDDList'),
    path('detail/<str:pk>', ContractTemplateDetail.as_view(), name='ContractTemplateDetail'),
]
