from drf_yasg.utils import swagger_auto_schema
from apps.accounting.accountingsettings.models.account_determination import (
    AccountDetermination, JEDocumentType
)
from apps.accounting.accountingsettings.serializers.account_determination import (
    AccountDeterminationListSerializer, AccountDeterminationDetailSerializer,
    AccountDeterminationUpdateSerializer, JEDocumentTypeListSerializer, JEDocumentTypeUpdateSerializer
)
from apps.shared import BaseListMixin, BaseUpdateMixin, mask_view


class JEDocumentTypeList(BaseListMixin):
    queryset = JEDocumentType.objects
    search_fields = ['title', 'code']
    serializer_list = JEDocumentTypeListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="JE Document Type List",
        operation_description="JE Document Type List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class JEDocumentTypeDetail(BaseUpdateMixin):
    queryset = JEDocumentType.objects
    serializer_update = JEDocumentTypeUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Update JE Document Type",
        request_body=JEDocumentTypeUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class AccountDeterminationList(BaseListMixin):
    queryset = AccountDetermination.objects
    search_fields = ['title',]
    serializer_list = AccountDeterminationListSerializer
    serializer_detail = AccountDeterminationDetailSerializer
    filterset_fields = {'account_determination_type': ['exact']}
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="Account Determination List",
        operation_description="Account Determination List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AccountDeterminationDetail(BaseUpdateMixin):
    queryset = AccountDetermination.objects
    serializer_update = AccountDeterminationUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

    @swagger_auto_schema(
        operation_summary="Update Account Determination",
        request_body=AccountDeterminationUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
