from django.urls import path, include

urlpatterns = [
    path('saledata/', include('apps.masterdata.saledata.urls')),
    path('promotion/', include('apps.masterdata.promotion.urls')),
]
