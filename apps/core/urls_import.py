from django.urls import path

from apps.core.account.views_import import CoreAccountUserImport
from apps.core.hr.views.fimport import (
    GroupLevelImport, GroupImport, RoleImport, EmployeeImport,
)

urlpatterns = [
    # core
    path('core/account/user', CoreAccountUserImport.as_view(), name='CoreAccountUserImport'),
    # hr
    path('hr/group-level', GroupLevelImport.as_view(), name='GroupLevelImport'),
    path('hr/group', GroupImport.as_view(), name='GroupImport'),
    path('hr/role', RoleImport.as_view(), name='RoleImport'),
    path('hr/employee', EmployeeImport.as_view(), name='EmployeeImport'),
]
