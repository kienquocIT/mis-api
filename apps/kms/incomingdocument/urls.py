from django.urls import path

from apps.kms.incomingdocument.views import KMSIncomingDocumentRequestList

urlpatterns = [  # config
    path('incoming-doc/list', KMSIncomingDocumentRequestList.as_view(), name='KMSIncomingDocumentRequestList')
]
