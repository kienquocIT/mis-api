from django.urls import path

from apps.core.hr.views.app_of_employee import (
    EmployeeStorageAppAllList, EmployeeStorageAppSummaryList,
    EmployeeStoragePlanSummaryList, EmployeeStoragePermissionSummaryList,
)
from apps.core.hr.views.employee import (
    EmployeeList, EmployeeDetail, EmployeeCompanyList, EmployeeTenantList,
    EmployeeMediaToken, EmployeeUploadAvatar, EmployeeAppList, EmployeeListAll,
)
from apps.core.hr.views.group import (
    GroupLevelList, GroupLevelDetail, GroupList, GroupDetail, GroupParentList,
)
from apps.core.hr.views.role import (
    RoleList, RoleDetail, RoleAppList,
)

urlpatterns = [

    path("employee/media-token", EmployeeMediaToken.as_view(), name="EmployeeMediaToken"),
    path("employee/tenant", EmployeeTenantList.as_view(), name="EmployeeTenantList"),
    # path("employee/company/<str:company_id>", EmployeeCompanyList.as_view(), name="EmployeeCompanyList"),
    path('employees', EmployeeList.as_view(), name='EmployeeList'),
    path('employees/all', EmployeeListAll.as_view(), name='EmployeeListAll'),
    path("employee/<str:pk>", EmployeeDetail.as_view(), name="EmployeeDetail"),
    path('employee/<str:pk>/upload-avatar', EmployeeUploadAvatar.as_view(), name='EmployeeUploadAvatar'),
    path("employee/<str:pk>/app", EmployeeAppList.as_view(), name="EmployeeAppList"),
    path("employee/<str:pk>/app/all", EmployeeStorageAppAllList.as_view(), name='EmployeeStorageAppAllList'),
    path(
        "employee/<str:pk>/app/summary", EmployeeStorageAppSummaryList.as_view(),
        name='EmployeeStorageAppSummaryList'
    ),
    path(
        "employee/<str:pk>/plan/summary", EmployeeStoragePlanSummaryList.as_view(),
        name='EmployeeStoragePlanSummaryList'
    ),
    path(
        "employee/<str:pk>/permissions/summary", EmployeeStoragePermissionSummaryList.as_view(),
        name='EmployeeStoragePermissionSummaryList'
    ),
    path('employees-company', EmployeeCompanyList.as_view(), name="EmployeeCompanyList"),

    path("roles", RoleList.as_view(), name="RoleList"),
    path("role/<str:pk>", RoleDetail.as_view(), name="RoleDetail"),
    path("role/<str:pk>/app", RoleAppList.as_view(), name="RoleAppList"),

    path('levels', GroupLevelList.as_view(), name='GroupLevelList'),
    path("level/<str:pk>", GroupLevelDetail.as_view(), name="GroupLevelDetail"),
    path('groups', GroupList.as_view(), name='GroupList'),
    path("group/<str:pk>", GroupDetail.as_view(), name="GroupDetail"),
    path("group/parent/<str:level>", GroupParentList.as_view(), name="GroupParentList"),
]
