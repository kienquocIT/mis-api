from django.urls import path

from apps.core.workflow.views.config import WorkflowList, NodeSystemList

urlpatterns = [
    path('lists', WorkflowList.as_view(), name='WorkflowList'),
    path('nodes-system', NodeSystemList.as_view(), name='NodeSystemList'),
]