from django.urls import path

from apps.core.workflow.views.config import WorkflowList

urlpatterns = [
    path('lists', WorkflowList.as_view(), name='WorkflowList'),
]