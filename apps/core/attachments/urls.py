from django.urls import path
from apps.core.attachments.views import FilesUpload, FilesUnused


urlpatterns = [
    path('unused', FilesUnused.as_view(), name='FilesUnused'),
    path('upload', FilesUpload.as_view(), name='FilesUpload'),
]
