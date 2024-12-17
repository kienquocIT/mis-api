from django.urls import path

from apps.sales.consulting.serializers.consulting import ConsultingDocumentMasterDataListSerializer
from apps.sales.consulting.views import ConsultingList, ConsultingDetail, ConsultingAccountList, \
    ConsultingProductCategoryList, ConsultingDocumentMasterDataList

urlpatterns = [
    path('list', ConsultingList.as_view(), name='ConsultingList'),
    path('detail/<str:pk>', ConsultingDetail.as_view(), name='ConsultingDetail'),
    path('account/list', ConsultingAccountList.as_view(), name='ConsultingAccountList'),
    path('product-category/list', ConsultingProductCategoryList.as_view(), name='ConsultingProductCategoryList'),
    path('masterdata-doc/list', ConsultingDocumentMasterDataList.as_view(), name='ConsultingDocumentMasterDataList'),
]
