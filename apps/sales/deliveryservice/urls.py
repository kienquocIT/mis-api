from django.urls import path
from apps.sales.deliveryservice.views import DeliveryServiceList, DeliveryServiceDetail

urlpatterns = [
    path('list', DeliveryServiceList.as_view(), name='DeliveryServiceList'),
    path('detail/<str:pk>', DeliveryServiceDetail.as_view(), name='DeliveryServiceDetail'),
]
