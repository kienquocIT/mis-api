from django.urls import path

from apps.sales.task.views import TaskConfigDetail, OpportunityTaskSwitchSTT, OpportunityTaskLogWork, \
    OpportunityTaskStatusList, OpportunityTaskList, OpportunityTaskDetail, GroupAssigneeList, \
    OpportunityTaskWithGroupList
from apps.sales.task.views_report import MyTaskReportView, MyTaskSummaryReportView

urlpatterns = [
    path('config', TaskConfigDetail.as_view(), name='TaskConfigDetail'),
    path('status', OpportunityTaskStatusList.as_view(), name='OpportunityTaskStatusList'),
    path('list', OpportunityTaskList.as_view(), name='OpportunityTaskList'),
    path('log-work', OpportunityTaskLogWork.as_view(), name='OpportunityTaskLogWork'),
    path('detail/<str:pk>', OpportunityTaskDetail.as_view(), name='OpportunityTaskDetail'),
    path('update-status/<str:pk>', OpportunityTaskSwitchSTT.as_view(), name='OpportunityTaskSwitchSTT'),

    path('my-report', MyTaskReportView.as_view(), name='MyTaskReportView'),
    path('my-summary-report', MyTaskSummaryReportView.as_view(), name='MyTaskSummaryReportView'),

    path(
        'assignee-group/list', GroupAssigneeList.as_view(),
        name='GroupAssigneeList'
    ),
    path(
        'list-has-group-assign', OpportunityTaskWithGroupList.as_view(),
        name='OpportunityTaskWithGroupList'
    ),

]
