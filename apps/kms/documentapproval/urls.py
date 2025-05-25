from django.urls import path

from .views import KSMDocumentTypeList, KMSDocumentTypeDetail, KSMContentGroupList, \
    KMSContentGroupDetail, KMSDocumentApprovalRequestList, KMSDocumentApprovalRequestDetail

urlpatterns = [  # config
    path('doc-approval/doc-type-list', KSMDocumentTypeList.as_view(), name='KSMDocumentTypeList'),
    path('doc-approval/doc-type-detail/<str:pk>', KMSDocumentTypeDetail.as_view(), name='KMSDocumentTypeDetail'),
    path('doc-approval/content-group-list', KSMContentGroupList.as_view(), name='KSMContentGroupList'),
    path('doc-approval/content-group-detail/<str:pk>', KMSContentGroupDetail.as_view(), name='KMSContentGroupDetail'),
    # document approval

    path('doc-approval/list', KMSDocumentApprovalRequestList.as_view(), name='KMSDocumentApprovalRequestList'),
    path(
        'doc-approval/detail/<str:pk>', KMSDocumentApprovalRequestDetail.as_view(),
        name='KMSDocumentApprovalRequestDetail'
    ),
]
