from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin
from apps.masterdata.saledata.models.accounts import (
    AccountType, Industry, Account, AccountEmployee, AccountGroup
)
from apps.masterdata.saledata.serializers.accounts import (
    AccountTypeListSerializer, AccountTypeCreateSerializer, AccountTypeDetailsSerializer, AccountTypeUpdateSerializer,
    IndustryListSerializer, IndustryCreateSerializer, IndustryDetailsSerializer, IndustryUpdateSerializer,

    AccountListSerializer, AccountCreateSerializer, AccountDetailSerializer, AccountUpdateSerializer,

    AccountGroupListSerializer, AccountGroupCreateSerializer,
    AccountGroupDetailsSerializer, AccountGroupUpdateSerializer,

    AccountsMapEmployeesListSerializer
)


# Create your views here.
class AccountTypeList(BaseListMixin, BaseCreateMixin): # noqa
    queryset = AccountType.objects
    serializer_list = AccountTypeListSerializer
    serializer_create = AccountTypeCreateSerializer
    serializer_detail = AccountTypeDetailsSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="AccountType list",
        operation_description="AccountType list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create AccountType",
        operation_description="Create new AccountType",
        request_body=AccountTypeCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AccountTypeDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = AccountType.objects
    serializer_list = AccountTypeListSerializer
    serializer_create = AccountTypeCreateSerializer
    serializer_detail = AccountTypeDetailsSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail AccountType')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update AccountType", request_body=AccountTypeUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = AccountTypeUpdateSerializer
        return self.update(request, *args, **kwargs)


class AccountGroupList(BaseListMixin, BaseCreateMixin):
    queryset = AccountGroup.objects
    serializer_list = AccountGroupListSerializer
    serializer_create = AccountGroupCreateSerializer
    serializer_detail = AccountGroupDetailsSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="AccountGroup list",
        operation_description="AccountGroup list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create AccountGroup",
        operation_description="Create new AccountGroup",
        request_body=AccountGroupCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AccountGroupDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = AccountGroup.objects
    serializer_list = AccountGroupListSerializer
    serializer_create = AccountGroupCreateSerializer
    serializer_detail = AccountGroupDetailsSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail AccountGroup')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update AccountGroup", request_body=AccountGroupUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = AccountGroupUpdateSerializer
        return self.update(request, *args, **kwargs)


class IndustryList(BaseListMixin, BaseCreateMixin):
    queryset = Industry.objects
    serializer_list = IndustryListSerializer
    serializer_create = IndustryCreateSerializer
    serializer_detail = IndustryDetailsSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Industry list",
        operation_description="Industry list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Industry",
        operation_description="Create new Industry",
        request_body=IndustryCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class IndustryDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Industry.objects
    serializer_list = IndustryListSerializer
    serializer_create = IndustryCreateSerializer
    serializer_detail = IndustryDetailsSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail Industry')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Industry", request_body=IndustryUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = IndustryUpdateSerializer
        return self.update(request, *args, **kwargs)


# Account
class AccountList(BaseListMixin, BaseCreateMixin): # noqa
    permission_classes = [IsAuthenticated]
    queryset = Account.objects
    serializer_list = AccountListSerializer
    serializer_create = AccountCreateSerializer
    serializer_detail = AccountDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related('industry', 'owner')

    @swagger_auto_schema(
        operation_summary="Account list",
        operation_description="Account list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Account",
        operation_description="Create new Account",
        request_body=AccountCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AccountDetail(BaseRetrieveMixin, BaseUpdateMixin):
    permission_classes = [IsAuthenticated]
    queryset = Account.objects
    serializer_detail = AccountDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related('industry', 'owner')

    @swagger_auto_schema(operation_summary='Detail Account')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Account", request_body=AccountUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = AccountUpdateSerializer
        return self.update(request, *args, **kwargs)


class AccountsMapEmployeesList(BaseListMixin):
    permission_classes = [IsAuthenticated]
    queryset = AccountEmployee.objects
    serializer_list = AccountsMapEmployeesListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related('account', 'employee')

    @swagger_auto_schema(
        operation_summary="Accounts map Employees list",
        operation_description="Accounts map Employees list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
