from django.urls import path
from apps.sales.reconciliation.views import ReconList, ReconDetail

urlpatterns = [
    path('list', ReconList.as_view(), name='ReconList'),
    path('detail/<str:pk>', ReconDetail.as_view(), name='ReconDetail'),
]
