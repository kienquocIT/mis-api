from django.urls import path
from apps.accounting.journalentry.views import (
    JournalEntryList, JournalEntryDetail, get_je_summarize,
    AllowedAppAutoJEList, AllowedAppAutoJEDetail
)

urlpatterns = [
    path('allow-app-auto-je/list', AllowedAppAutoJEList.as_view(), name='AllowedAppAutoJEList'),
    path('allow-app-auto-je/detail/<str:pk>', AllowedAppAutoJEDetail.as_view(), name='AllowedAppAutoJEDetail'),
    path('list', JournalEntryList.as_view(), name='JournalEntryList'),
    path('detail/<str:pk>', JournalEntryDetail.as_view(), name='JournalEntryDetail'),
    path('get-je-summarize', get_je_summarize, name='get_je_summarize'),
]
