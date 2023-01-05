from django.urls import path

from apps.core.hr.views.employee import EmployeeList, EmployeeDetail
from apps.core.hr.views.role import RoleList, RoleDetail

urlpatterns = [
    path('employees', EmployeeList.as_view(), name='EmployeeList'),
    path("employee/<str:pk>", EmployeeDetail.as_view(), name="EmployeeDetail"),

    path("roles", RoleList.as_view(), name="RoleList"),
    path("role/<str:pk>", RoleDetail.as_view(), name="RoleDetail"),
]
