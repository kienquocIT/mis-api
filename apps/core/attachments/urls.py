from django.urls import path
from .views import (
    FilesUpload, FilesUnused,
    ImageWebBuilderUpload, ImageWebBuilderList, FolderList, FolderDetail, FolderUploadFileList, FilesDownload,
    FilesInformation, PublicFilesUpload, FolderListSharedToMe, FolderMySpaceList, FilesEdit
)

urlpatterns = [
    path('unused', FilesUnused.as_view(), name='FilesUnused'),
    path('upload', FilesUpload.as_view(), name='FilesUpload'),
    path('edit', FilesEdit.as_view(), name='FilesEdit'),
    path('public-upload', PublicFilesUpload.as_view(), name='PublicFilesUpload'),
    path('download/<str:pk>', FilesDownload.as_view(), name='FilesDownload'),
    path('info/<str:pk>', FilesInformation.as_view(), name='FilesInformation'),
    path('web-builder/upload', ImageWebBuilderUpload.as_view(), name='ImageWebBuilderUpload'),
    path('web-builder/list', ImageWebBuilderList.as_view(), name='ImageWebBuilderList'),

    # KMS file and folder
    path('folder/list', FolderList.as_view(), name='FolderList'),
    path('folder/list-my-space', FolderMySpaceList.as_view(), name='FolderMySpaceList'),
    path('folder/list-share-to-me', FolderListSharedToMe.as_view(), name='FolderListSharedToMe'),
    path('folder/<str:pk>', FolderDetail.as_view(), name='FolderDetail'),
    path('folder-upload-file/list', FolderUploadFileList.as_view(), name='FolderUploadFileList'),
]
