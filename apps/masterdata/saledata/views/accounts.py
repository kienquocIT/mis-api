from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin
from apps.masterdata.saledata.models.accounts import (
    AccountType, Industry, Account, AccountEmployee, AccountGroup,
)
from apps.masterdata.saledata.serializers.accounts import (
    AccountTypeListSerializer, AccountTypeCreateSerializer, AccountTypeDetailsSerializer, AccountTypeUpdateSerializer,
    IndustryListSerializer, IndustryCreateSerializer, IndustryDetailsSerializer, IndustryUpdateSerializer,

    AccountListSerializer, AccountCreateSerializer, AccountDetailSerializer, AccountUpdateSerializer,

    AccountGroupListSerializer, AccountGroupCreateSerializer,
    AccountGroupDetailsSerializer, AccountGroupUpdateSerializer,

    AccountsMapEmployeesListSerializer, AccountForSaleListSerializer,
)


# Create your views here.
class AccountTypeList(BaseListMixin, BaseCreateMixin):  # noqa
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
    @mask_view(
        login_require=True, auth_require=False
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create AccountType",
        operation_description="Create new AccountType",
        request_body=AccountTypeCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='account', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AccountTypeDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = AccountType.objects
    serializer_list = AccountTypeListSerializer
    serializer_create = AccountTypeCreateSerializer
    serializer_detail = AccountTypeDetailsSerializer
    serializer_update = AccountTypeUpdateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail AccountType')
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update AccountType", request_body=AccountTypeUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='account', perm_code='edit'
    )
    def put(self, request, *args, **kwargs):
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
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create AccountGroup",
        operation_description="Create new AccountGroup",
        request_body=AccountGroupCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='account', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AccountGroupDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = AccountGroup.objects
    serializer_list = AccountGroupListSerializer
    serializer_create = AccountGroupCreateSerializer
    serializer_detail = AccountGroupDetailsSerializer
    serializer_update = AccountGroupUpdateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail AccountGroup')
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update AccountGroup", request_body=AccountGroupUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='account', perm_code='edit'
    )
    def put(self, request, *args, **kwargs):
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
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Industry",
        operation_description="Create new Industry",
        request_body=IndustryCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='account', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class IndustryDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Industry.objects
    serializer_list = IndustryListSerializer
    serializer_create = IndustryCreateSerializer
    serializer_detail = IndustryDetailsSerializer
    serializer_update = IndustryUpdateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail Industry')
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Industry", request_body=IndustryUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='account', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# Account
class AccountList(BaseListMixin, BaseCreateMixin):  # noqa
    permission_classes = [IsAuthenticated]
    queryset = Account.objects
    serializer_list = AccountListSerializer
    serializer_create = AccountCreateSerializer
    serializer_detail = AccountDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id', 'employee_modified_id']
    filterset_fields = {'account_types_mapped__account_type_order': ['exact']}

    def get_queryset(self):
        return super().get_queryset().select_related(
            'industry', 'owner', 'payment_term_mapped'
        ).prefetch_related(
            'contact_account_name'
        )

    @swagger_auto_schema(
        operation_summary="Account list",
        operation_description="Account list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='account', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Account",
        operation_description="Create new Account",
        request_body=AccountCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        employee_require=True,
        plan_code='sale', app_code='account', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AccountDetail(BaseRetrieveMixin, BaseUpdateMixin):
    permission_classes = [IsAuthenticated]
    queryset = Account.objects
    serializer_detail = AccountDetailSerializer
    serializer_update = AccountUpdateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related('industry', 'owner')

    @swagger_auto_schema(operation_summary='Detail Account')
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='account', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Account", request_body=AccountUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='account', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
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
    @mask_view(login_require=True, auth_require=False)  # true: using opportunity
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# Account List use for Sale Apps
class AccountForSaleList(BaseListMixin):
    permission_classes = [IsAuthenticated]
    queryset = Account.objects
    serializer_list = AccountForSaleListSerializer
    serializer_detail = AccountDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    filterset_fields = {
        'account_types_mapped__account_type_order': ['exact'],
        'employee__id': ['exact']
    }

    def get_queryset(self):
        return super().get_queryset().select_related(
            'industry',
            'owner',
            'payment_term_mapped',
            'price_list_mapped'
        )

    @swagger_auto_schema(
        operation_summary="Account list use for Sales",
        operation_description="Account list use for Sales Apps",
    )
    @mask_view(login_require=True, auth_require=False)  # true: using purchase, quotation,...
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
