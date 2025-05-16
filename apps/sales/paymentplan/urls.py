from django.urls import path

from apps.sales.paymentplan.views import PaymentPlanList

urlpatterns = [
    path('list', PaymentPlanList.as_view(), name='PaymentPlanList'),
]
