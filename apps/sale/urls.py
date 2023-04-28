from django.urls import path, include

urlpatterns = [
    path('saledata/', include('apps.sale.saledata.urls')),
    path('promotion/', include('apps.sale.promotion.urls')),
]
