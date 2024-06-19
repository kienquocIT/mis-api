from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser

from apps.shared import BaseCreateMixin, mask_view, BaseListMixin, BaseRetrieveMixin, BaseUpdateMixin

from apps.core.attachments.models import Files, PublicFiles, Folder
from apps.core.attachments.serializers import (
    FilesUploadSerializer, FilesDetailSerializer, FilesListSerializer,
    DetailImageWebBuilderInPublicFileListSerializer, CreateImageWebBuilderInPublicFileListSerializer,
    FolderListSerializer, FolderCreateSerializer, FolderDetailSerializer, FolderUpdateSerializer,
    FolderUploadFileSerializer,
)


class FilesUpload(BaseCreateMixin):
    parser_classes = [MultiPartParser]
    queryset = Files.objects
    serializer_create = FilesUploadSerializer
    serializer_detail = FilesDetailSerializer

    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    def write_log(self, *args, **kwargs):
        doc_obj = kwargs['doc_obj']
        change_partial: bool = kwargs.get('change_partial', False)
        task_id = kwargs.get('task_id', None)

        request_data = {
            'id': str(doc_obj.id),
            'file_name': doc_obj.file_name,
            'file_type': doc_obj.file_type,
            'file_size': doc_obj.file_size,
        }
        return super().write_log(
            doc_obj=doc_obj, request_data=request_data, change_partial=change_partial, task_id=task_id
        )

    @swagger_auto_schema(request_body=FilesUploadSerializer)
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user_obj': self.request.user
        }
        return self.create(request, *args, **kwargs)


class FilesUnused(BaseListMixin):
    queryset = Files.objects
    serializer_list = FilesListSerializer
    search_fields = ('file_name',)
    list_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        self.kwargs['relate_doc_id__isnull'] = True
        return self.list(request, *args, **kwargs)


class ImageWebBuilderUpload(BaseCreateMixin):
    queryset = PublicFiles.objects
    serializer_create = CreateImageWebBuilderInPublicFileListSerializer
    serializer_detail = DetailImageWebBuilderInPublicFileListSerializer
    parser_classes = [MultiPartParser]

    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    def write_log(self, *args, **kwargs):
        doc_obj = kwargs['doc_obj']
        change_partial: bool = kwargs.get('change_partial', False)
        task_id = kwargs.get('task_id', None)

        request_data = {
            'id': str(doc_obj.id),
            'file_name': doc_obj.file_name,
            'file_type': doc_obj.file_type,
            'file_size': doc_obj.file_size,
        }
        return super().write_log(
            doc_obj=doc_obj, request_data=request_data, change_partial=change_partial, task_id=task_id
        )

    @swagger_auto_schema(request_body=FilesUploadSerializer)
    @mask_view(login_require=True, auth_require=False, employee_require=True, allow_admin_company=True)
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user_obj': self.request.user
        }
        return self.create(request, *args, **kwargs)


class ImageWebBuilderList(BaseListMixin):
    queryset = PublicFiles.objects
    serializer_list = DetailImageWebBuilderInPublicFileListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(relate_app_code=settings.FILE_WEB_BUILDER_RELATE_APP).order_by('file_name')

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False, allow_admin_company=True)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# BEGIN FOLDER
class FolderList(BaseListMixin, BaseCreateMixin):
    queryset = Folder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'parent_n_id': ['exact', 'isnull'],
        'id': ['exact', 'isnull'],
    }
    serializer_list = FolderListSerializer
    serializer_create = FolderCreateSerializer
    serializer_detail = FolderDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Folder List",
        operation_description="Get Folder List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Folder",
        operation_description="Create New Folder",
        request_body=FolderCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class FolderDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = Folder.objects
    serializer_detail = FolderDetailSerializer
    serializer_update = FolderUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related("parent_n").prefetch_related('files_folder', 'folder_parent_n')

    @swagger_auto_schema(
        operation_summary="Folder Detail",
        operation_description="Get Folder Detail By ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Folder",
        operation_description="Update Folder By ID",
        request_body=FolderUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class FolderUploadFileList(BaseCreateMixin):
    parser_classes = [MultiPartParser]
    queryset = Files.objects
    serializer_create = FolderUploadFileSerializer
    serializer_detail = FilesDetailSerializer
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    def write_log(self, *args, **kwargs):
        doc_obj = kwargs['doc_obj']
        change_partial: bool = kwargs.get('change_partial', False)
        task_id = kwargs.get('task_id', None)
        request_data = {
            'id': str(doc_obj.id),
            'file_name': doc_obj.file_name,
            'file_type': doc_obj.file_type,
            'file_size': doc_obj.file_size,
        }
        return super().write_log(
            doc_obj=doc_obj, request_data=request_data, change_partial=change_partial, task_id=task_id
        )

    @swagger_auto_schema(request_body=FilesUploadSerializer)
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user_obj': self.request.user
        }
        return self.create(request, *args, **kwargs)
