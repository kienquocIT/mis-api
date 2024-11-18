from django.urls import path

from apps.core.recurrence.views import RecurrenceList, RecurrenceDetail

urlpatterns = [
    path('list', RecurrenceList.as_view(), name='RecurrenceList'),
    path('<str:pk>', RecurrenceDetail.as_view(), name='RecurrenceDetail'),
]
