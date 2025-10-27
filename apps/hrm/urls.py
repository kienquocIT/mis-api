from django.urls import path, include

urlpatterns = [
    path('', include('apps.hrm.employeeinfo.urls')),
    path('attendance/', include('apps.hrm.attendance.urls')),
    path('absenceexplanation/', include('apps.hrm.absenceexplanation.urls')),
    path('overtime/', include('apps.hrm.overtimerequest.urls')),
    path('payroll/', include('apps.hrm.payroll.urls')),
    path('payroll/template/', include('apps.hrm.payrolltemplate.urls')),
]
