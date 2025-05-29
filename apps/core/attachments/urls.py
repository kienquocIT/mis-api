from django.urls import path
from apps.core.attachments.views import (
    FilesUpload, FilesUnused,
    ImageWebBuilderUpload, ImageWebBuilderList, FolderList, FolderDetail, FolderUploadFileList, FilesDownload,
    FilesInformation, PublicFilesUpload,
)

urlpatterns = [
    path('unused', FilesUnused.as_view(), name='FilesUnused'),
    path('upload', FilesUpload.as_view(), name='FilesUpload'),
    path('public-upload', PublicFilesUpload.as_view(), name='PublicFilesUpload'),
    path('download/<str:pk>', FilesDownload.as_view(), name='FilesDownload'),
    path('info/<str:pk>', FilesInformation.as_view(), name='FilesInformation'),
    path('web-builder/upload', ImageWebBuilderUpload.as_view(), name='ImageWebBuilderUpload'),
    path('web-builder/list', ImageWebBuilderList.as_view(), name='ImageWebBuilderList'),
    path('folder/list', FolderList.as_view(), name='FolderList'),
    path('folder/<str:pk>', FolderDetail.as_view(), name='FolderDetail'),
    path('folder-upload-file/list', FolderUploadFileList.as_view(), name='FolderUploadFileList'),
]
