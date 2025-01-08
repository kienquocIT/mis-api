from django.urls import path
from apps.sales.reconciliation.views import ReconList, ReconDetail, ARInvoiceListForRecon, CashInflowListForRecon

urlpatterns = [
    path('list', ReconList.as_view(), name='ReconList'),
    path('detail/<str:pk>', ReconDetail.as_view(), name='ReconDetail'),
    path('ar-invoice-for-recon/list', ARInvoiceListForRecon.as_view(), name='ARInvoiceListForRecon'),
    path('cash-inflow-for-recon/list', CashInflowListForRecon.as_view(), name='CashInflowListForRecon'),
]
