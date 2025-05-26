from drf_yasg.utils import swagger_auto_schema

from apps.kms.documentapproval.models import KMSDocumentApproval
from apps.kms.documentapproval.serializers.serializers import KMSDocumentApprovalListSerializer, \
    KMSDocumentApprovalCreateSerializer, KMSDocumentApprovalDetailSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin


class KMSDocumentApprovalRequestList(BaseListMixin, BaseCreateMixin):
    queryset = KMSDocumentApproval.objects
    serializer_list = KMSDocumentApprovalListSerializer
    serializer_detail = KMSDocumentApprovalListSerializer
    serializer_create = KMSDocumentApprovalCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT
    search_fields = ('code', 'title')

    @swagger_auto_schema(
        operation_summary="KMS Document approval request list",
        operation_description="get document approval request list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='documentapproval', model_code='kmsdocumentapproval', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create document approval request",
        operation_description="Create business trip request",
        request_body=KMSDocumentApprovalCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='documentapproval', model_code='kmsdocumentapproval', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user,
        }
        return self.create(request, *args, **kwargs)


class KMSDocumentApprovalRequestDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = KMSDocumentApproval.objects
    serializer_detail = KMSDocumentApprovalDetailSerializer
    serializer_update = KMSDocumentApprovalDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('employee_inherit')

    @swagger_auto_schema(
        operation_summary="Document approval request detail",
        operation_description="get document approval request detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='documentapproval', model_code='kmsdocumentapproval', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Document approval request update",
        operation_description="Document approval request update by ID",
        request_body=KMSDocumentApprovalDetailSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='documentapproval', model_code='kmsdocumentapproval', perm_code="edit",
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)
