from django.urls import path

from .views import (
    QuotationList, QuotationDetail, QuotationExpenseList, QuotationConfigDetail,
    QuotationIndicatorList, QuotationIndicatorDetail, QuotationIndicatorCompanyRestore
)

urlpatterns = [
    path('config', QuotationConfigDetail.as_view(), name='QuotationConfigDetail'),
    path('indicators', QuotationIndicatorList.as_view(), name='QuotationIndicatorList'),
    path('indicator/<str:pk>', QuotationIndicatorDetail.as_view(), name='ssssQuotationIndicatorDetail'),
    path('indicator-restore/<str:pk>', QuotationIndicatorCompanyRestore.as_view(),
         name='QuotationIndicatorCompanyRestore'),

    path('list', QuotationList.as_view(), name='QuotationList'),
    path('<str:pk>', QuotationDetail.as_view(), name='QuotationDetail'),
    path('quotation-expense-list/lists', QuotationExpenseList.as_view(), name='QuotationExpenseList'),
]
