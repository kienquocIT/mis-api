from django.urls import path

from apps.eoffice.leave.views import LeaveConfigDetail, LeaveTypeConfigCreate, LeaveTypeConfigUpdate

urlpatterns = [
    path('config', LeaveConfigDetail.as_view(), name='LeaveConfigDetail'),
    path('leave-type/create', LeaveTypeConfigCreate.as_view(), name='LeaveTypeConfigCreate'),
    path('leave-type/detail/<str:pk>', LeaveTypeConfigUpdate.as_view(), name='LeaveTypeConfigUpdate'),
]
