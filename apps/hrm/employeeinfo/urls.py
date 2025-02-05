from django.urls import path

from .views import EmployeeInfoList, EmployeeInfoDetail, EmployeeNotMapHRMList, \
    EmployeeContractList, EmployeeContractDetail, EmployeeInfoSignatureList, AttachmentSignatureUpdate

urlpatterns = [
    path('employee-not-map/list', EmployeeNotMapHRMList.as_view(), name='EmployeeNotMapHRMList'),
    path('employee-info/list', EmployeeInfoList.as_view(), name='EmployeeInfoList'),
    path('employee-info/detail/<str:pk>', EmployeeInfoDetail.as_view(), name='EmployeeInfoDetail'),
    # contract
    path('employee-info/contract/list', EmployeeContractList.as_view(), name='EmployeeContractList'),
    path('employee-info/contract/detail/<str:pk>', EmployeeContractDetail.as_view(), name='EmployeeContractDetail'),
    # signature
    path('employee-info/signature/list', EmployeeInfoSignatureList.as_view(), name='EmployeeInfoSignatureList'),
    path(
        'employee-info/signature/update/<str:pk>', AttachmentSignatureUpdate.as_view(), name='AttachmentSignatureUpdate'
    ),
]
