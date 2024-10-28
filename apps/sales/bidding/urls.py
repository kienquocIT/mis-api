from django.urls import path

from .serializers.bidding import AccountForBiddingListSerializer
from .views import (
    BiddingList, DocumentMasterDataBiddingList, AccountForBiddingList
)

urlpatterns = [
    path('list', BiddingList.as_view(), name='BiddingList'),
    path('account-list', AccountForBiddingList.as_view(), name='AccountForBiddingList'),
    path('document-list', DocumentMasterDataBiddingList.as_view(), name='DocumentMasterDataBiddingList'),
]
