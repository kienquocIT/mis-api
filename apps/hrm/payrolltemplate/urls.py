from django.urls import path

from apps.hrm.payrolltemplate.views import PayrollTemplateList, PayrollTemplateDetail
from apps.hrm.payrolltemplate.views.views import PayrollComponentList, PayrollComponentDetail

urlpatterns = [
    path('request/list', PayrollTemplateList.as_view(), name='PayrollTemplateList'),
    path('request/detail/<str:pk>', PayrollTemplateDetail.as_view(), name='PayrollTemplateDetail'),
    path('component/list', PayrollComponentList.as_view(), name='PayrollComponentList'),
    path('component/detail/<str:pk>', PayrollComponentDetail.as_view(), name='PayrollComponentDetail'),
]
