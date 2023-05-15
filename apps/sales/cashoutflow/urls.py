from django.urls import path
from .views import AdvancePaymentList, AdvancePaymentDetail, ExpenseUnitPriceList

urlpatterns = [
    path('advances-payments', AdvancePaymentList.as_view(), name='AdvancePaymentList'),
    path('advances-payments/<str:pk>', AdvancePaymentDetail.as_view(), name='AdvancePaymentDetail'),
    path('get-expense-unit-price', ExpenseUnitPriceList.as_view(), name='ExpenseUnitPriceList'),
]
