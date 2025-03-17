from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import Bank, BankAccount
from apps.masterdata.saledata.serializers import (
    BankListSerializer, BankCreateSerializer, BankDetailSerializer,
    BankAccountListSerializer, BankAccountDetailSerializer, BankAccountCreateSerializer
)
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseDestroyMixin


__all__ = [
    'BankList',
    'BankDetail',
    'BankAccountList',
    'BankAccountDetail'
]


# Bank
class BankList(BaseListMixin, BaseCreateMixin):
    queryset = Bank.objects
    serializer_list = BankListSerializer
    serializer_create = BankCreateSerializer
    serializer_detail = BankDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="Bank list", operation_description="Bank list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Bank create", operation_description="Bank create",
    )
    @mask_view(
        login_require=True, auth_require = True,
        allow_admin_tenant=True, allow_admin_company=True
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BankDetail(BaseRetrieveMixin, BaseDestroyMixin):
    queryset = Bank.objects
    filterset_fields = {}
    serializer_detail = BankDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary='Detail Bank', operation_description="Detail Bank",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Bank", operation_description="Delete Bank",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)


# Bank Account
class BankAccountList(BaseListMixin, BaseCreateMixin):
    queryset = BankAccount.objects
    serializer_list = BankAccountListSerializer
    serializer_create = BankAccountCreateSerializer
    serializer_detail = BankAccountDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

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


class BankAccountDetail(BaseRetrieveMixin, BaseDestroyMixin):
    queryset = BankAccount.objects
    search_fields = ['title']
    filterset_fields = {}
    serializer_detail = BankAccountDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail BankAccount')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Bank Account", operation_description="Delete Bank Account",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)
