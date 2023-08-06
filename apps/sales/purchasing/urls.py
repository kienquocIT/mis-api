from django.urls import path

from apps.sales.purchasing.views import PurchaseRequestList, PurchaseRequestDetail, PurchaseRequestProductList
from apps.sales.purchasing.views.purchase_order import PurchaseOrderDetail, PurchaseOrderList

urlpatterns = [
    # purchase request
    path('purchase-request/list', PurchaseRequestList.as_view(), name='PurchaseRequestList'),
    path('purchase-request/<str:pk>', PurchaseRequestDetail.as_view(), name='PurchaseRequestDetail'),
    path('purchase-request-product/list', PurchaseRequestProductList.as_view(), name='PurchaseRequestProductList'),
    # purchase quotation request
    # purchase quotation
    # purchase order
    path('purchase-order/list', PurchaseOrderList.as_view(), name='PurchaseOrderList'),
    path('purchase-order/<str:pk>', PurchaseOrderDetail.as_view(), name='PurchaseOrderDetail'),
]
