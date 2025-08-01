from django.urls import path

from apps.hrm.attendance.views import ShiftMasterDataList, ShiftMasterDataDetail, ShiftAssignmentList, \
    DeviceIntegrateEmployeeList, DeviceIntegrateEmployeeDetail

urlpatterns = [
    path('shift/list', ShiftMasterDataList.as_view(), name='ShiftMasterDataList'),
    path('shift/detail/<str:pk>', ShiftMasterDataDetail.as_view(), name='ShiftMasterDataDetail'),

    # shift assignment
    path('shift-assignment/list', ShiftAssignmentList.as_view(), name='ShiftAssignmentList'),

    # device integrate
    path('device-integrate-employee/list', DeviceIntegrateEmployeeList.as_view(), name='DeviceIntegrateEmployeeList'),
    path(
        'device-integrate-employee/<str:pk>',
        DeviceIntegrateEmployeeDetail.as_view(),
        name='DeviceIntegrateEmployeeDetail'
    ),
]
