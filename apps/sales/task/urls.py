from django.urls import path

urlpatterns = [
    path('config', QuotationConfigDetail.as_view(), name='QuotationConfigDetail'),

]
