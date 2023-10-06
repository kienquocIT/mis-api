from django.urls import path

from apps.eoffice.leave.views import LeaveConfigDetail, LeaveTypeConfigCreate, LeaveTypeConfigUpdate, \
    WorkingCalendarConfigDetail, WorkingYearCreate, WorkingYearDetail, WorkingHolidayCreate, WorkingHolidayAPI, \
    LeaveRequestList, LeaveRequestDetail

urlpatterns = [
    path('config', LeaveConfigDetail.as_view(), name='LeaveConfigDetail'),
    path('leave-type/create', LeaveTypeConfigCreate.as_view(), name='LeaveTypeConfigCreate'),
    path('leave-type/detail/<str:pk>', LeaveTypeConfigUpdate.as_view(), name='LeaveTypeConfigUpdate'),
    # working calendar
    path('working-calendar/config', WorkingCalendarConfigDetail.as_view(), name='WorkingCalendarConfigDetail'),
    path('working-calendar/year', WorkingYearCreate.as_view(), name='WorkingYearCreate'),
    path('working-calendar/year/<str:pk>', WorkingYearDetail.as_view(), name='WorkingYearDetail'),
    path('working-calendar/holiday', WorkingHolidayCreate.as_view(), name='WorkingHolidayCreate'),
    path('working-calendar/holiday/<str:pk>', WorkingHolidayAPI.as_view(), name='WorkingHolidayDetail'),
    # request
    path('request', LeaveRequestList.as_view(), name='LeaveRequestList'),
    path('request/detail/<str:pk>', LeaveRequestDetail.as_view(), name='LeaveRequestDetail'),
]
