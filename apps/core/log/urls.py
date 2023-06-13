from django.urls import path

from apps.core.log.views import ActivityLogList

urlpatterns = [
    path('activities', ActivityLogList.as_view(), name='ActivityLogList'),
]
