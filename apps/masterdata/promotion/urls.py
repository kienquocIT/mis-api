from django.urls import path

from apps.masterdata.promotion.views import PromotionList, PromotionDetail, PromotionCheckList

urlpatterns = [
    path('list', PromotionList.as_view(), name='PromotionList'),
    path('detail/<str:pk>', PromotionDetail.as_view(), name='PromotionDetail'),
    path('check-list', PromotionCheckList.as_view(), name='PromotionCheckList'),
]
