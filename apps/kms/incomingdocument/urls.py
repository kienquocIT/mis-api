from django.urls import path

from apps.kms.incomingdocument.views import KMSIncomingDocumentRequestList, KMSIncomingDocumentRequestDetail

urlpatterns = [  # config
    path('incoming-doc/list', KMSIncomingDocumentRequestList.as_view(), name='KMSIncomingDocumentRequestList'),
    path(
        'incoming-doc/detail/<str:pk>', KMSIncomingDocumentRequestDetail.as_view(),
        name='KMSIncomingDocumentRequestDetail')
]
