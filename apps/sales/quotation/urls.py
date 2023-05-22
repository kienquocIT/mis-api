from django.urls import path

from .views import QuotationList, QuotationDetail, QuotationExpenseList

urlpatterns = [
    path('lists', QuotationList.as_view(), name='QuotationList'),
    path('<str:pk>', QuotationDetail.as_view(), name='QuotationDetail'),
    path('quotation-expense-list/lists', QuotationExpenseList.as_view(), name='QuotationExpenseList'),
]
