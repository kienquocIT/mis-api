from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import Bank, BankAccount
from apps.masterdata.saledata.serializers import BankListSerializer, BankCreateSerializer, BankDetailSerializer, \
    BankUpdateSerializer, BankAccountListSerializer, BankAccountUpdateSerializer, BankAccountDetailSerializer, \
    BankAccountCreateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

__all__ = [
    'BankList',
    'BankDetail',
    'BankAccountList',
    'BankAccountDetail'
]

class BankList(BaseListMixin, BaseCreateMixin):
    queryset = Bank.objects
    serializer_list = BankListSerializer
    serializer_create = BankCreateSerializer
    serializer_detail = BankDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Bank list",
        operation_description="Bank list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Bank create",
        operation_description="Bank create",
        request_body=BankCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require = True, allow_admin_tenant=True, allow_admin_company=True
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BankDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Bank.objects
    search_fields = ['title']
    filterset_fields = {}
    serializer_update = BankUpdateSerializer
    serializer_detail = BankDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail Bank')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary="Update Bank",
                         request_body=BankUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class BankAccountList(BaseListMixin, BaseCreateMixin):
    queryset = BankAccount.objects
    serializer_list = BankAccountListSerializer
    serializer_create = BankAccountCreateSerializer
    serializer_detail = BankAccountDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="BankAccount list",
        operation_description="BankAccount list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="BankAccount create",
        operation_description="BankAccount create",
        request_body=BankAccountCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require = True, allow_admin_tenant=True, allow_admin_company=True
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BankAccountDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = BankAccount.objects
    search_fields = ['title']
    filterset_fields = {}
    serializer_update = BankAccountUpdateSerializer
    serializer_detail = BankAccountDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail BankAccount')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary="Update BankAccount",
                         request_body=BankAccountUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
