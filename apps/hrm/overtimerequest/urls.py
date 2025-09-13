from django.urls import path

from apps.hrm.overtimerequest.views import OvertimeRequestList, OvertimeRequestDetail

urlpatterns = [
    path('request/list', OvertimeRequestList.as_view(), name='OvertimeRequestList'),
    path('request/detail/<str:pk>', OvertimeRequestDetail.as_view(), name='OvertimeRequestDetail'),
]
