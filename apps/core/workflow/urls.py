from django.urls import path

from apps.core.workflow.views import (
    WorkflowOfAppList, WorkflowOfAppDetail, WorkflowList, WorkflowDetail,
    RuntimeDataView, WorkflowRuntimeTest, RuntimeDiagramView, HistoryStage, RuntimeTask, RuntimeListView,
)

urlpatterns = [
    # runtime
    path('history/stage/<str:pk>', HistoryStage.as_view(), name='HistoryStage'),
    path('test', WorkflowRuntimeTest.as_view(), name='WorkflowRuntimeTest'),
    path('runtime/list', RuntimeListView.as_view(), name='RuntimeListView'),
    path('runtime', RuntimeDataView.as_view(), name='RuntimeDataView'),
    path('diagram', RuntimeDiagramView.as_view(), name='RuntimeDiagramView'),
    path('task/<str:pk>', RuntimeTask.as_view(), name='RuntimeTask'),

    # config
    path('apps', WorkflowOfAppList.as_view(), name='WorkflowOfAppList'),
    path('app/<str:pk>', WorkflowOfAppDetail.as_view(), name='WorkflowOfAppDetail'),
    path('lists', WorkflowList.as_view(), name='WorkflowList'),
    path('<str:pk>', WorkflowDetail.as_view(), name='WorkflowDetail'),
]
