from django.urls import path

from apps.core.hr.views.fimport import GroupLevelImport, GroupImport

urlpatterns = [
    path('hr/group-level', GroupLevelImport.as_view(), name='GroupLevelImport'),
    path('hr/group', GroupImport.as_view(), name='GroupImport'),
]
