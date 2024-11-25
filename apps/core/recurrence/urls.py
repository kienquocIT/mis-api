from django.urls import path

from apps.core.recurrence.views import RecurrenceList, RecurrenceDetail, RecurrenceActionList, RecurrenceActionDetail

urlpatterns = [
    path('list', RecurrenceList.as_view(), name='RecurrenceList'),
    path('<str:pk>', RecurrenceDetail.as_view(), name='RecurrenceDetail'),
    path('action/list', RecurrenceActionList.as_view(), name='RecurrenceActionList'),
    path('action/<str:pk>', RecurrenceActionDetail.as_view(), name='RecurrenceActionDetail'),
]
