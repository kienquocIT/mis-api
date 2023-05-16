from django.urls import path

from apps.masterdata.promotion.views import PromotionList
from apps.masterdata.promotion.views.promotion import PromotionDetail

urlpatterns = [
    path('list', PromotionList.as_view(), name='PromotionList'),
    path('detail/<str:pk>', PromotionDetail.as_view(), name='PromotionDetail'),
]
