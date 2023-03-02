from django.urls import path, include

urlpatterns = [
    path('saledata/', include('apps.sale.saledata.urls')),
]
