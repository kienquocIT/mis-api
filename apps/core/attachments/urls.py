from django.urls import path
from apps.core.attachments.views import (
    FilesUpload, FilesUnused,
    ImageWebBuilderUpload, ImageWebBuilderList,
)

urlpatterns = [
    path('unused', FilesUnused.as_view(), name='FilesUnused'),
    path('upload', FilesUpload.as_view(), name='FilesUpload'),
    path('web-builder/upload', ImageWebBuilderUpload.as_view(), name='ImageWebBuilderUpload'),
    path('web-builder/list', ImageWebBuilderList.as_view(), name='ImageWebBuilderList'),
]
