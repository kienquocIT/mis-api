from django.urls import path

from apps.core.hr.views.employee import EmployeeList, EmployeeDetail

urlpatterns = [
    path('employees', EmployeeList.as_view(), name='EmployeeList'),
    path("employee/<str:pk>", EmployeeDetail.as_view(), name="EmployeeDetail"),
]
