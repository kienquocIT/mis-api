from django.urls import path
from apps.accounting.journalentry.views import JournalEntryList, JournalEntryDetail, get_je_summarize

urlpatterns = [
    path('list', JournalEntryList.as_view(), name='JournalEntryList'),
    path('detail/<str:pk>', JournalEntryDetail.as_view(), name='JournalEntryDetail'),
    path('get-je-summarize', get_je_summarize, name='get_je_summarize'),
]
