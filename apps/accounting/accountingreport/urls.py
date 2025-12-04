from django.urls import path

from apps.accounting.accountingreport.views.journalentry_report import JournalEntryLineList

urlpatterns = [
    path('line/list', JournalEntryLineList.as_view(), name='JournalEntryLineList'),
]
