from django.urls import path

from apps.core.log.views import (
    ActivityLogList,
    MyNotifyNoDoneCount,
    MyNotifySeenAll,
    MyNotifyList,
    MyNotifyDetail,
    MyNotifyCleanAll,
    BookMarkList,
    BookMarkDetail,
    DocPinedList,
    DocPinedDetail,
)

urlpatterns = [
    # activities
    path('activities', ActivityLogList.as_view(), name='ActivityLogList'),

    # notifies
    path('notifies/me', MyNotifyList.as_view(), name='MyNotifyList'),
    path('notifies/me/count', MyNotifyNoDoneCount.as_view(), name='MyNotifyNoDoneCount'),
    path('notifies/me/seen-all', MyNotifySeenAll.as_view(), name='MyNotifySeenAll'),
    path('notifies/me/clean-all', MyNotifyCleanAll.as_view(), name='MyNotifyCleanAll'),
    path('notify/<str:pk>', MyNotifyDetail.as_view(), name='MyNotifyDetail'),

    # Bookmarks
    path('bookmarks', BookMarkList.as_view(), name='BookMarkList'),
    path('bookmark/<str:pk>', BookMarkDetail.as_view(), name='BookMarkDetail'),

    # Bookmarks
    path('pin-docs', DocPinedList.as_view(), name='DocPinedList'),
    path('pin-doc/<str:pk>', DocPinedDetail.as_view(), name='DocPinedDetail'),
]
