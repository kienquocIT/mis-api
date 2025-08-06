from django.urls import path, include

urlpatterns = [
    path('', include('apps.hrm.employeeinfo.urls')),
    path('attendance/', include('apps.hrm.attendance.urls')),
    path('absenceexplanation/', include('apps.hrm.absenceexplanation.urls')),
]
