from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import DocumentType
from apps.masterdata.saledata.serializers import (
    DocumentTypeListSerializer, DocumentTypeCreateSerializer, DocumentTypeDetailSerializer
)
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin

class DocumentTypeList(BaseListMixin, BaseCreateMixin):
    queryset = DocumentType.objects
    search_fields = ['title']
    filterset_fields = { }
    serializer_list = DocumentTypeListSerializer
    serializer_create = DocumentTypeCreateSerializer
    serializer_detail = DocumentTypeDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="DocumentType list",
        operation_description="DocumentType list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create DocumentType",
        operation_description="Create new DocumentType",
        request_body=DocumentTypeCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
