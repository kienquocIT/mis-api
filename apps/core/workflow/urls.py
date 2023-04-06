from django.urls import path

from .views import WorkflowList, WorkflowDetail # pylint: disable-msg=E0611

urlpatterns = [
    path('lists', WorkflowList.as_view(), name='WorkflowList'),
    path('<str:pk>', WorkflowDetail.as_view(), name='WorkflowDetail'),
]
