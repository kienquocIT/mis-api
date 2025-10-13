from django.urls import path

from apps.hrm.payroll.views import PayrollConfigList

urlpatterns = [
    path('payrollconfig/list', PayrollConfigList.as_view(), name='PayrollConfigList'),
]
