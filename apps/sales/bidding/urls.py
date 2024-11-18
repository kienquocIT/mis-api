from django.urls import path

from .views import (
    BiddingList, DocumentMasterDataBiddingList, AccountForBiddingList, BiddingDetail, BiddingResult,
    BiddingResultConfigList
)

urlpatterns = [
    path('list', BiddingList.as_view(), name='BiddingList'),
    path('detail/<str:pk>', BiddingDetail.as_view(), name='BiddingDetail'),
    path('result', BiddingResult.as_view(), name='BiddingResult'),
    path('account-list', AccountForBiddingList.as_view(), name='AccountForBiddingList'),
    path('document-list', DocumentMasterDataBiddingList.as_view(), name='DocumentMasterDataBiddingList'),
    path('bidding-result-config', BiddingResultConfigList.as_view(), name='BiddingResultConfigList'),
]
