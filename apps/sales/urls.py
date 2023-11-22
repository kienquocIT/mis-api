from django.urls import path, include

urlpatterns = [
    path('quotation/', include('apps.sales.quotation.urls')),
    path('opportunity/', include('apps.sales.opportunity.urls')),
    path('saleorder/', include('apps.sales.saleorder.urls')),
    path('cashoutflow/', include('apps.sales.cashoutflow.urls')),
    path('delivery/', include('apps.sales.delivery.urls')),
    path('task/', include('apps.sales.task.urls')),
    path('purchasing/', include('apps.sales.purchasing.urls')),
    path('inventory/', include('apps.sales.inventory.urls')),
    path('report/', include('apps.sales.report.urls')),
    path('acceptance/', include('apps.sales.acceptance.urls')),
]
