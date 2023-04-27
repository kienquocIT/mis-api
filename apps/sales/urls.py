from django.urls import path, include

urlpatterns = [
    path('quotation/', include('apps.sales.quotation.urls')),
    path('opportunity/', include('apps.sales.opportunity.urls')),
]
