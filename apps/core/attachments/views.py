from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser

from apps.shared import BaseCreateMixin, mask_view, BaseListMixin

from apps.core.attachments.models import Files
from apps.core.attachments.serializers import FilesUploadSerializer, FilesDetailSerializer, FilesListSerializer


class FilesUpload(BaseCreateMixin):
    parser_classes = [MultiPartParser]
    queryset = Files.objects
    serializer_create = FilesUploadSerializer
    serializer_detail = FilesDetailSerializer

    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    def write_log(self, doc_obj, request_data: dict = None, change_partial: bool = False, task_id=None):
        request_data = {
            'id': str(doc_obj.id),
            'file_name': doc_obj.file_name,
            'file_type': doc_obj.file_type,
            'file_size': doc_obj.file_size,
            'belong_to': doc_obj.belong_to,
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
