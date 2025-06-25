from drf_yasg.utils import swagger_auto_schema

from apps.kms.incomingdocument.models import KMSIncomingDocument
from apps.kms.incomingdocument.serializers.serializers import KMSIncomingDocumentCreateSerializer, \
    KMSIncomingDocumentListSerializer, KMSIncomingDocumentDetailSerializer, KMSIncomingDocumentUpdateSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin


class KMSIncomingDocumentRequestList(BaseListMixin, BaseCreateMixin):
    queryset = KMSIncomingDocument.objects
    serializer_list = KMSIncomingDocumentListSerializer
    serializer_detail = KMSIncomingDocumentDetailSerializer
    serializer_create = KMSIncomingDocumentCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="KMS Incoming Document request list",
        operation_description="get incoming document request list"
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='incomingdocument', model_code='kmsincomingdocument', perm_code='view'
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create incoming document request",
        operation_description="Create new incoming document request",
        request_body=KMSIncomingDocumentCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='incomingdocument', model_code='kmsincomingdocument', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user,
        }
        return self.create(request, *args, **kwargs)


class KMSIncomingDocumentRequestDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = KMSIncomingDocument.objects
    serializer_detail = KMSIncomingDocumentDetailSerializer
    serializer_update = KMSIncomingDocumentUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('employee_inherit')

    @swagger_auto_schema(
        operation_summary="Incoming document request detail",
        operation_description="Get Incoming document request detail"
    )
    @mask_view(
        login_require=True,
        auth_require=False,
        label_code="incomingdocument",
        model_code='kmsincomingdocument',
        perm_code='view'
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @mask_view(
        login_require=True,
        auth_require=False,
        label_code='incomingdocument',
        model_code='kmsincomingdocument',
        perm_code='edit'
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)

