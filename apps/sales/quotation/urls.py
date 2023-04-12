from django.urls import path

from .views.quotation import QuotationList, QuotationDetail

urlpatterns = [
    path('lists', QuotationList.as_view(), name='QuotationList'),
    path('<str:pk>', QuotationDetail.as_view(), name='QuotationDetail'),
]
