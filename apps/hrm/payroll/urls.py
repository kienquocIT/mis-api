from django.urls import path

from apps.hrm.payroll.views import PayrollConfigDetail

urlpatterns = [
    path('payrollconfig/config', PayrollConfigDetail.as_view(), name='PayrollConfigDetail'),
]
