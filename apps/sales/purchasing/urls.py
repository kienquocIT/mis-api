from django.urls import path

from apps.sales.purchasing.views import PurchaseRequestList, PurchaseRequestDetail
from apps.sales.purchasing.views.purchase_order import PurchaseOrderDetail, PurchaseOrderList

urlpatterns = [
    # purchase request
    path('purchase-request/list', PurchaseRequestList.as_view(), name='PurchaseRequestList'),
    path('purchase-request/<str:pk>', PurchaseRequestDetail.as_view(), name='PurchaseRequestDetail'),
    # purchase quotation request
    # purchase quotation
    # purchase order
    path('purchase-order/list', PurchaseOrderList.as_view(), name='PurchaseOrderList'),
    path('purchase-order/<str:pk>', PurchaseOrderDetail.as_view(), name='PurchaseOrderDetail'),
]
