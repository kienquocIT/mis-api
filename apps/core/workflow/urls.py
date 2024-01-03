from django.urls import path

from apps.core.workflow.views import (
    WorkflowOfAppList, WorkflowOfAppDetail, WorkflowList, WorkflowDetail,
    RuntimeDiagramDetail,
    RuntimeListView, RuntimeMeListView, RuntimeDetail,
    RuntimeAssigneeList, RuntimeAssigneeDetail, WorkflowCurrentOfAppList,
)

urlpatterns = [
    # runtime
    path('runtimes', RuntimeListView.as_view(), name='RuntimeListView'),
    path('runtimes/me', RuntimeMeListView.as_view(), name='RuntimeMeListView'),
    path('diagram/<str:runtime_id>', RuntimeDiagramDetail.as_view(), name='RuntimeDiagramDetail'),
    path('runtime/<str:pk>', RuntimeDetail.as_view(), name='RuntimeDetail'),
    path('tasks', RuntimeAssigneeList.as_view(), name='RuntimeAssigneeList'),
    path('task/<str:pk>', RuntimeAssigneeDetail.as_view(), name='RuntimeAssigneeDetail'),

    # config
    path('apps', WorkflowOfAppList.as_view(), name='WorkflowOfAppList'),
    path('app/<str:pk>', WorkflowOfAppDetail.as_view(), name='WorkflowOfAppDetail'),
    path('currents', WorkflowCurrentOfAppList.as_view(), name='WorkflowCurrentOfAppList'),
    path('lists', WorkflowList.as_view(), name='WorkflowList'),
    path('<str:pk>', WorkflowDetail.as_view(), name='WorkflowDetail'),
]
