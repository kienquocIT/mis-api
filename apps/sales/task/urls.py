from django.urls import path

from apps.sales.task.views import TaskConfigDetail, OpportunityTaskSwitchSTT, OpportunityTaskLogWork
from apps.sales.task.views import OpportunityTaskList, OpportunityTaskDetail

urlpatterns = [
    path('config', TaskConfigDetail.as_view(), name='TaskConfigDetail'),
    path('list', OpportunityTaskList.as_view(), name='OpportunityTaskList'),
    path('log-work', OpportunityTaskLogWork.as_view(), name='OpportunityTaskLogWork'),
    path('detail/<str:pk>', OpportunityTaskDetail.as_view(), name='OpportunityTaskDetail'),
    path('update-status/<str:pk>', OpportunityTaskSwitchSTT.as_view(), name='OpportunityTaskSwitchSTT'),
]
