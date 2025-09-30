from drf_yasg.utils import swagger_auto_schema

from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin
from ..models import KMSDocumentType, KMSContentGroup
from ..serializers import KMSDocumentTypeSerializer, KMSContentGroupSerializer, \
    KMSDocumentTypeUpdateSerializer, KMSDocumentTypeCreateSerializer


class KSMDocumentTypeList(BaseListMixin, BaseCreateMixin):
    queryset = KMSDocumentType.objects
    filterset_fields = {
        'applications__id': ['exact', 'in'],
    }
    serializer_list = KMSDocumentTypeSerializer
    serializer_detail = KMSDocumentTypeSerializer
    serializer_create = KMSDocumentTypeCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    search_fields = ('code', 'title')

    def get_queryset(self):
        return super().get_queryset().select_related('folder').filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="List of KMS document type",
        operation_description="get KMS document type list",
    )
    @mask_view(
        login_require=True, auth_require=False, skip_filter_employee=True
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create KMS document type",
        operation_description="Create master data KMS document type"
    )
    @mask_view(
        login_require=True, auth_require=False, allow_admin_company=True
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class KMSDocumentTypeDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = KMSDocumentType.objects
    serializer_detail = KMSDocumentTypeSerializer
    serializer_update = KMSDocumentTypeUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="KMS document type detail",
        operation_description="Get detail KMS document type by ID",
    )
    @mask_view(
        login_require=True, auth_require=False, allow_admin_company=True
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update KMS document type",
        operation_description="Update KMS document type by ID"
    )
    @mask_view(
        login_require=True, auth_require=False, allow_admin_company=True
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete KMS document type",
        operation_description="Delete KMS document type by ID",
    )
    @mask_view(
        login_require=True, auth_require=False, allow_admin_company=True
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, is_purge=True, **kwargs)


class KSMContentGroupList(BaseListMixin, BaseCreateMixin):
    queryset = KMSContentGroup.objects
    serializer_list = KMSContentGroupSerializer
    serializer_detail = KMSContentGroupSerializer
    serializer_create = KMSContentGroupSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    search_fields = ('code', 'title')

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="List of KMS Content group",
        operation_description="get KMS Content group ",
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create KMS Content group",
        operation_description="Create master data KMS Content group"
    )
    @mask_view(
        login_require=True, auth_require=False, allow_admin_company=True
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class KMSContentGroupDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = KMSContentGroup.objects
    serializer_detail = KMSContentGroupSerializer
    serializer_update = KMSContentGroupSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="KMS Content group detail",
        operation_description="Get detail KMS Content group by ID",
    )
    @mask_view(
        login_require=True, auth_require=False, allow_admin_company=True
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update KMS Content group",
        operation_description="Update KMS Content group by ID"
    )
    @mask_view(
        login_require=True, auth_require=False, allow_admin_company=True
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete KMS Content group",
        operation_description="Delete KMS Content group by ID",
    )
    @mask_view(
        login_require=True, auth_require=False, allow_admin_company=True
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, is_purge=True, **kwargs)
