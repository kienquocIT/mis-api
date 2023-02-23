from django.urls import path

from apps.core.workflow.views.config import WorkflowList, NodeSystemList, WorkflowDetail

urlpatterns = [
    path('lists', WorkflowList.as_view(), name='WorkflowList'),
    path('nodes-system', NodeSystemList.as_view(), name='NodeSystemList'),
    path('<str:pk>', WorkflowDetail.as_view(), name='WorkflowDetail'),
]