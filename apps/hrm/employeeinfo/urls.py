from django.urls import path

from apps.hrm.employeeinfo.views import EmployeeInfoList, EmployeeInfoDetail, EmployeeNotMapHRMList

urlpatterns = [
    path('employee-not-map/list', EmployeeNotMapHRMList.as_view(), name='EmployeeNotMapHRMList'),
    path('employee-info/list', EmployeeInfoList.as_view(), name='EmployeeInfoList'),
    path('employee-info/detail/<str:pk>', EmployeeInfoDetail.as_view(), name='EmployeeInfoDetail'),
]
