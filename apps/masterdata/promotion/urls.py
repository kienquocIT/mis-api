from django.urls import path

from apps.masterdata.promotion.views import PromotionList

urlpatterns = [
    path('list', PromotionList.as_view(), name='PromotionList'),
]
