from django.urls import path
from apps.accounting.journalentry.views import JournalEntryList, JournalEntryDetail

urlpatterns = [
    path('list', JournalEntryList.as_view(), name='JournalEntryList'),
    path('detail/<str:pk>', JournalEntryDetail.as_view(), name='JournalEntryDetail'),
]
