from django.urls import path

from apps.eoffice.businesstrip.views import BusinessTripRequestList
from apps.eoffice.businesstrip.views.views import BusinessTripRequestDetail

urlpatterns = [
    path('list', BusinessTripRequestList.as_view(), name='BusinessTripRequestList'),
    path('detail/<str:pk>', BusinessTripRequestDetail.as_view(), name='BusinessTripRequestDetail'),
]
