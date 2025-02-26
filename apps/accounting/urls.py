from django.urls import path, include

urlpatterns = [
    path('accounting-setting/', include('apps.accounting.accountingsettings.urls')),
    path('journal-entry/', include('apps.accounting.journalentry.urls')),
]
