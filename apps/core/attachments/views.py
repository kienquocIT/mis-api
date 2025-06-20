import os
from wsgiref.util import FileWrapper
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser

from django.conf import settings
from django.http import StreamingHttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.shared import (
    BaseCreateMixin, mask_view, BaseListMixin, BaseRetrieveMixin, BaseUpdateMixin, TypeCheck,
    ResponseController, BaseDestroyMixin, AttMsg, HttpMsg,
)

from .models import Files, PublicFiles, Folder, FolderPermission
from .serializers import (
    FilesUploadSerializer, FilesDetailSerializer, FilesListSerializer,
    DetailImageWebBuilderInPublicFileListSerializer, CreateImageWebBuilderInPublicFileListSerializer,
    FolderListSerializer, FolderCreateSerializer, FolderDetailSerializer, FolderUpdateSerializer,
    FolderUploadFileSerializer, PublicFilesUploadSerializer, PublicFilesDetailSerializer, PublicFilesListSerializer,
    FileDeleteAllSerializer, FolderDeleteAllSerializer
)
from .utils import check_folder_perm, check_file_perm


class FilesUpload(BaseListMixin, BaseCreateMixin):
    parser_classes = [MultiPartParser]
    queryset = Files.objects
    serializer_list = FilesListSerializer
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


class FilesEdit(BaseDestroyMixin):
    queryset = Files.objects
    serializer_delete_all = FileDeleteAllSerializer

    @swagger_auto_schema(
        operation_summary="Delete file list",
        operation_description="Delete file list",
        request_body=FileDeleteAllSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def delete(self, request, *args, **kwargs):
        if check_file_perm(request.data.get('id_list', None), 'my_space', request.user.employee_current) is False:
            return Response(
                data={
                    "status": status.HTTP_403_FORBIDDEN,
                    "detail": HttpMsg.FORBIDDEN,
                }, status=status.HTTP_403_FORBIDDEN, content_type="application/json"
            )
        kwargs['is_purge'] = True
        kwargs['remove_file'] = True
        return self.destroy_list(request, *args, **kwargs)


class PublicFilesUpload(BaseListMixin, BaseCreateMixin):
    parser_classes = [MultiPartParser]
    queryset = PublicFiles.objects
    serializer_list = PublicFilesListSerializer
    serializer_create = PublicFilesUploadSerializer
    serializer_detail = PublicFilesDetailSerializer

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

    @swagger_auto_schema(request_body=PublicFilesUploadSerializer)
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user_obj': self.request.user
        }
        return self.create(request, *args, **kwargs)


class FilesDownload(APIView):
    def get_object(self) -> Files:
        try:
            return Files.objects.get_current(
                fill__tenant=True, fill__company=True, pk=self.kwargs['pk']
            )
        except Files.DoesNotExist:
            pass
        raise exceptions.NotFound

    @swagger_auto_schema(operation_summary='Download file')
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            obj = self.get_object()

            if obj and os.path.isfile(obj.file.path):
                f_path = obj.file.path
                chunk_size = 8192
                response = StreamingHttpResponse(
                    FileWrapper(
                        open(f_path, "rb"),  # pylint: disable=R1732
                        chunk_size,
                    ),
                    # content_type=mimetypes.guess_type(f_path)[0],
                    content_type=obj.file_type,
                )
                response["Content-Length"] = os.path.getsize(f_path)
                response["Content-Disposition"] = f"attachment; filename={obj.file_name}"
                return response
        return ResponseController.notfound_404()


class FilesInformation(APIView):
    def get_object(self) -> Files:
        try:
            return Files.objects.select_related('employee_created', 'folder', 'relate_app').get_current(
                fill__tenant=True, fill__company=True, pk=self.kwargs['pk']
            )
        except Files.DoesNotExist:
            pass
        raise exceptions.NotFound

    @classmethod
    def get_file_metadata(cls, obj: Files):
        return {
            'file_name': obj.file_name,
            'file_type': obj.file_type,
            'file_size': obj.file_size,
            'remarks': obj.remarks,
            'relate_app': {
                'title': obj.relate_app.title,
                'plan': obj.relate_app.app_label,
                'app': obj.relate_app.model_code,
            } if obj.relate_app else {},
            'relate_doc': obj.relate_doc_id,
            'employee_created': {
                'id': obj.employee_created.id,
                'full_name': obj.employee_created.get_full_name(),
            } if obj.employee_created else {},
            'folder': {
                'id': obj.folder.id,
                'title': obj.folder.title,
            } if obj.folder else {},
            'date_created': obj.date_created,
        }

    @swagger_auto_schema(operation_summary='Download file')
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            obj = self.get_object()

            if obj:
                return ResponseController.success_200(data=self.get_file_metadata(obj=obj))
        return ResponseController.notfound_404()


class FilesUnused(BaseListMixin):
    queryset = Files.objects
    serializer_list = FilesListSerializer
    search_fields = ('file_name',)
    filterset_fields = {'id': ['in']}
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
        'employee_inherit_id': ['exact', 'isnull'],
    }
    serializer_list = FolderListSerializer
    serializer_create = FolderCreateSerializer
    serializer_detail = FolderDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        user = self.request.user
        employee_id = str(user.employee_current_id)
        # group_id = str(user.employee_current.group.id) if hasattr(user.employee_current, 'group') else None
        # filter by parent and employee

        qs = super().get_queryset()
        # if self.request.query_params.get('parent_n_id', None) is None and self.request.query_params.get(
        #         'parent_n_id__isnull', None
        # ) is None:
        #     qs = qs.filter(parent_n_id__isnull=True)
        if self.request.query_params.get('employee_inherit_id', None) is None and self.request.query_params.get(
                'employee_inherit_id__isnull', None
        ) is None:
            qs = qs.filter(employee_inherit_id=employee_id)
        return qs.select_related('employee_inherit', 'parent_n')

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


class FolderMySpaceList(BaseListMixin, BaseDestroyMixin):
    queryset = Folder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'parent_n_id': ['exact', 'isnull'],
        'employee_inherit_id': ['exact', 'isnull'],
    }
    serializer_list = FolderListSerializer
    serializer_delete_all = FolderDeleteAllSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        if not isinstance(self.request.user, AnonymousUser):
            emp_crt = self.request.user.employee_current
            qs = super().get_queryset()
            if self.request.query_params.get('parent_n_id', None) is None and self.request.query_params.get(
                    'parent_n_id__isnull', None
            ) is None:
                qs = qs.filter(parent_n_id__isnull=True)
            return qs.filter(is_owner=True, employee_inherit=emp_crt)
        return Folder.objects.none()

    @swagger_auto_schema(
        operation_summary="Folder List my space",
        operation_description="Get Folder List my space",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete folder list my space",
        operation_description="Delete folder list my space",
        request_body=FolderDeleteAllSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def delete(self, request, *args, **kwargs):
        if check_folder_perm(request.data.get('id_list', None), 'my_space', request.user.employee_current) is False:
            return Response(
                data={
                    "status": status.HTTP_403_FORBIDDEN,
                    "detail": HttpMsg.FORBIDDEN,
                }, status=status.HTTP_403_FORBIDDEN, content_type="application/json"
            )
        kwargs['is_purge'] = True
        return self.destroy_list(request, *args, **kwargs)


class FolderListSharedToMe(BaseListMixin):
    queryset = Folder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'parent_n_id': ['exact', 'isnull'],
        'employee_inherit_id': ['exact', 'isnull'],
    }
    serializer_list = FolderListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        # query default filter by employee and group of user requests
        # and permission has view
        user = self.request.user
        employee_id = str(user.employee_current_id)
        group_id = str(user.employee_current.group.id) if hasattr(user.employee_current, 'group') else None

        # Base queryset
        queryset = super().get_queryset()

        # filter employee/group has shared
        employee_filter = Q(employee_list__icontains=f'"{employee_id}"') & Q(folder_perm_list__contains=[1])
        group_filter = Q(group_list__icontains=f'"{group_id}"') & Q(
            file_in_perm_list__contains=[1]
        ) if group_id else Q()

        accessible_folder_ids = FolderPermission.objects.filter(
            employee_filter | group_filter
        ).values_list('folder_id', flat=True).distinct()

        accessible_folder_ids = list(accessible_folder_ids)

        return queryset.filter(Q(id__in=accessible_folder_ids))

    @swagger_auto_schema(
        operation_summary="Folder List shared to me",
        operation_description="Get Folder List shared to me",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class FolderDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin
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

    @swagger_auto_schema(
        operation_summary="Delete folder",
        operation_description="Delete Folder By ID",
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_system:
            raise ValueError(AttMsg.FOLDER_SYSTEM_ERROR)
        folder_perm = instance.folder_permission_folder.all().first()
        employee = request.user.employee_current
        group = employee.group if hasattr(employee, 'group') else None
        has_perm = False
        if instance.employee_inherit_id == employee.id:
            has_perm = True

        if has_perm is False and folder_perm:
            # nếu không phải user owner và có permission
            has_permission = 5 in folder_perm.folder_perm_list
            is_employee_allowed = str(employee.id) in folder_perm.employee_list
            is_group_allowed = group and str(group.id) in folder_perm.group_list

            if has_permission and (is_employee_allowed or is_group_allowed):
                has_perm = True
        if has_perm:
            instance.delete()
            return ResponseController.no_content_204()
        return ResponseController.notfound_404(AttMsg.FOLDER_DELETE_ERROR)


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
