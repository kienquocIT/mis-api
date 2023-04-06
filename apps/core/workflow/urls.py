from django.urls import path

from .views import WorkflowList, NodeSystemList, WorkflowDetail # pylint: disable-msg=E0611

urlpatterns = [
    path('lists', WorkflowList.as_view(), name='WorkflowList'),
    path('nodes-system', NodeSystemList.as_view(), name='NodeSystemList'),
    path('<str:pk>', WorkflowDetail.as_view(), name='WorkflowDetail'),
]
