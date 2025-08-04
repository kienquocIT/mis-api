from django.urls import path

from apps.hrm.attendance.views import ShiftMasterDataList, ShiftMasterDataDetail, ShiftAssignmentList
from apps.hrm.attendance.views.attendance import AttendanceDataList

urlpatterns = [
    path('shift/list', ShiftMasterDataList.as_view(), name='ShiftMasterDataList'),
    path('shift/detail/<str:pk>', ShiftMasterDataDetail.as_view(), name='ShiftMasterDataDetail'),

    # shift assignment
    path('shift-assignment/list', ShiftAssignmentList.as_view(), name='ShiftAssignmentList'),

    # attendance
    path('attendance/list', AttendanceDataList.as_view(), name='AttendanceDataList'),
]
