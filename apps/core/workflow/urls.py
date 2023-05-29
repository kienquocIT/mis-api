from django.urls import path

from apps.core.workflow.views import (
    WorkflowList, WorkflowDetail,
    RuntimeDataView, WorkflowRuntimeTest, RuntimeDiagramView, HistoryStage, RuntimeTask
)

urlpatterns = [
    path('history/stage/<str:pk>', HistoryStage.as_view(), name='HistoryStage'),
    path('lists', WorkflowList.as_view(), name='WorkflowList'),
    path('test', WorkflowRuntimeTest.as_view(), name='WorkflowRuntimeTest'),
    path('runtime', RuntimeDataView.as_view(), name='RuntimeDataView'),
    path('diagram', RuntimeDiagramView.as_view(), name='RuntimeDiagramView'),
    path('task/<str:pk>', RuntimeTask.as_view(), name='RuntimeTask'),
    path('<str:pk>', WorkflowDetail.as_view(), name='WorkflowDetail'),
]
