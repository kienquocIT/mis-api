from django.urls import path, include

urlpatterns = [
    path('quotation/', include('apps.sales.quotation.urls')),
    path('opportunity/', include('apps.sales.opportunity.urls')),
    path('saleorder/', include('apps.sales.saleorder.urls')),
    path('cashoutflow/', include('apps.sales.cashoutflow.urls')),
    path('delivery/', include('apps.sales.delivery.urls')),
    path('task/', include('apps.sales.task.urls')),
]
