from django.urls import path

from apps.hrm.attendance.views import ShiftMasterDataList, ShiftMasterDataDetail, ShiftAssignmentList, \
    DeviceIntegrateEmployeeList, DeviceIntegrateEmployeeDetail, AttendanceDeviceList, AttendanceDeviceDetail, \
    ShiftMasterDataImport, ShiftAssignmentConfigDetail
from apps.hrm.attendance.views.attendance import AttendanceDataList

urlpatterns = [
    path('shift/list', ShiftMasterDataList.as_view(), name='ShiftMasterDataList'),
    path('shift/detail/<str:pk>', ShiftMasterDataDetail.as_view(), name='ShiftMasterDataDetail'),
    path('shift/import', ShiftMasterDataImport.as_view(), name='ShiftMasterDataImport'),

    # shift assignment
    path('shift-assignment-config', ShiftAssignmentConfigDetail.as_view(), name='ShiftAssignmentConfigDetail'),
    path('shift-assignment/list', ShiftAssignmentList.as_view(), name='ShiftAssignmentList'),

    # attendance
    path('attendance/list', AttendanceDataList.as_view(), name='AttendanceDataList'),

    # device integrate
    path('attendance-device/list', AttendanceDeviceList.as_view(), name='AttendanceDeviceList'),
    path(
        'attendance-device/<str:pk>',
        AttendanceDeviceDetail.as_view(),
        name='AttendanceDeviceDetail'
    ),
    path('device-integrate-employee/list', DeviceIntegrateEmployeeList.as_view(), name='DeviceIntegrateEmployeeList'),
    path(
        'device-integrate-employee/<str:pk>',
        DeviceIntegrateEmployeeDetail.as_view(),
        name='DeviceIntegrateEmployeeDetail'
    ),
]
