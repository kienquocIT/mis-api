from django.urls import path

from apps.core.hr.views.employee import EmployeeList, EmployeeDetail
from apps.core.hr.views.group import GroupLevelList, GroupLevelDetail, GroupList, GroupDetail, GroupParentList
from apps.core.hr.views.role import RoleList, RoleDetail

urlpatterns = [
    path('employees', EmployeeList.as_view(), name='EmployeeList'),
    path("employee/<str:pk>", EmployeeDetail.as_view(), name="EmployeeDetail"),

    path("roles", RoleList.as_view(), name="RoleList"),
    path("role/<str:pk>", RoleDetail.as_view(), name="RoleDetail"),

    path('levels', GroupLevelList.as_view(), name='GroupLevelList'),
    path("level/<str:pk>", GroupLevelDetail.as_view(), name="GroupLevelDetail"),
    path('groups', GroupList.as_view(), name='GroupList'),
    path("group/<str:pk>", GroupDetail.as_view(), name="GroupDetail"),

    path("group/parent/<str:level>", GroupParentList.as_view(), name="GroupParentList"),
]
