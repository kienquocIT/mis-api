from django.urls import path

from apps.sales.purchasing.views import PurchaseRequestList, PurchaseRequestDetail

# purchase request
urlpatterns = [
    path('purchase-request', PurchaseRequestList.as_view(), name='PurchaseRequestList'),
    path('purchase-request/<str:pk>', PurchaseRequestDetail.as_view(), name='PurchaseRequestDetail'),
]
