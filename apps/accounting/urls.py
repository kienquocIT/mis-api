from django.urls import path, include

urlpatterns = [
    path('accountchart/', include('apps.accounting.accountchart.urls')),
]
