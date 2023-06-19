from django.urls import path

from apps.core.log.views import (
    ActivityLogList,
    MyNotifyNoDoneCount,
    MyNotifySeenAll,
    MyNotifyList,
    MyNotifyDetail,
    MyNotifyCleanAll,
)

urlpatterns = [
    path('activities', ActivityLogList.as_view(), name='ActivityLogList'),
    path('notifies/me', MyNotifyList.as_view(), name='MyNotifyList'),
    path('notifies/me/count', MyNotifyNoDoneCount.as_view(), name='MyNotifyNoDoneCount'),
    path('notifies/me/seen-all', MyNotifySeenAll.as_view(), name='MyNotifySeenAll'),
    path('notifies/me/clean-all', MyNotifyCleanAll.as_view(), name='MyNotifyCleanAll'),
    path('notify/<str:pk>', MyNotifyDetail.as_view(), name='MyNotifyDetail'),
]
