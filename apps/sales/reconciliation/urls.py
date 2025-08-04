from django.urls import path
from apps.sales.reconciliation.views import (
    ReconList, ReconDetail,
    APInvoiceListForRecon, CashOutflowListForRecon,
    ARInvoiceListForRecon, CashInflowListForRecon,
)

urlpatterns = [
    path('list', ReconList.as_view(), name='ReconList'),
    path('detail/<str:pk>', ReconDetail.as_view(), name='ReconDetail'),
    path('ap-invoice-for-recon/list', APInvoiceListForRecon.as_view(), name='APInvoiceListForRecon'),
    path('cash-outflow-for-recon/list', CashOutflowListForRecon.as_view(), name='CashOutflowListForRecon'),
    path('ar-invoice-for-recon/list', ARInvoiceListForRecon.as_view(), name='ARInvoiceListForRecon'),
    path('cash-inflow-for-recon/list', CashInflowListForRecon.as_view(), name='CashInflowListForRecon'),
]
