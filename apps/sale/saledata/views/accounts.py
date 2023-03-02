from drf_yasg.utils import swagger_auto_schema

from apps.core.hr.models import Employee
from apps.sale.saledata.models.accounts import (Salutation, Interest, AccountType, Industry, Contact, Account)
from apps.sale.saledata.serializers.accounts import (
    SalutationListSerializer, SalutationCreateSerializer, SalutationDetailSerializer,
    InterestsListSerializer, InterestsCreateSerializer, InterestsDetailsSerializer,
    AccountTypeListSerializer, AccountTypeCreateSerializer, AccountTypeDetailsSerializer,
    IndustryListSerializer, IndustryCreateSerializer, IndustryDetailsSerializer,

    ContactListSerializer, ContactCreateSerializer, ContactDetailSerializer,
    ContactUpdateSerializer, ContactListNotMapAccountSerializer,

    AccountListSerializer, AccountCreateSerializer, AccountDetailSerializer,
    AccountUpdateSerializer, EmployeeMapAccountListSerializer,
)
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class SalutationList(BaseListMixin, BaseCreateMixin):
    queryset = Salutation.object_normal
    serializer_list = SalutationListSerializer
    serializer_create = SalutationCreateSerializer
    serializer_detail = SalutationDetailSerializer

    @swagger_auto_schema(
        operation_summary="Salutation list",
        operation_description="Salutation list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Salutation",
        operation_description="Create new Salutation",
        request_body=SalutationCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class InterestsList(BaseListMixin, BaseCreateMixin):
    queryset = Interest.object_normal
    serializer_list = InterestsListSerializer
    serializer_create = InterestsCreateSerializer
    serializer_detail = InterestsDetailsSerializer

    @swagger_auto_schema(
        operation_summary="Interests list",
        operation_description="Interests list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Interests",
        operation_description="Create new Interests",
        request_body=InterestsCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AccountTypeList(BaseListMixin, BaseCreateMixin):
    queryset = AccountType.object_normal
    serializer_list = AccountTypeListSerializer
    serializer_create = AccountTypeCreateSerializer
    serializer_detail = AccountTypeDetailsSerializer

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


class IndustryList(BaseListMixin, BaseCreateMixin):
    queryset = Industry.object_normal
    serializer_list = IndustryListSerializer
    serializer_create = IndustryCreateSerializer
    serializer_detail = IndustryDetailsSerializer

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


# Contact
class ContactList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated]
    queryset = Contact.object_normal
    serializer_list = ContactListSerializer
    serializer_create = ContactCreateSerializer
    serializer_detail = ContactDetailSerializer

    @swagger_auto_schema(
        operation_summary="Contact list",
        operation_description="Contact list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Contact",
        operation_description="Create new Contact",
        request_body=ContactCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ContactDetail(BaseRetrieveMixin, BaseUpdateMixin):
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects
    serializer_detail = ContactDetailSerializer

    @swagger_auto_schema(operation_summary='Detail Contact')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Contact", request_body=ContactUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = ContactUpdateSerializer
        return self.update(request, *args, **kwargs)


class ContactListNotMapAccount(BaseListMixin):
    permission_classes = [IsAuthenticated]
    queryset = Contact.object_normal
    serializer_list = ContactListNotMapAccountSerializer
    serializer_detail = ContactDetailSerializer

    @swagger_auto_schema(
        operation_summary="Contact list not map account",
        operation_description="Contact list not map account",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        kwargs.update({'account_name': None})
        return self.list(request, *args, **kwargs)


# Account
class AccountList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated]
    queryset = Account.object_normal
    serializer_list = AccountListSerializer
    serializer_create = AccountCreateSerializer
    serializer_detail = AccountDetailSerializer

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

    @swagger_auto_schema(operation_summary='Detail Account')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Account", request_body=AccountUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = AccountUpdateSerializer
        return self.update(request, *args, **kwargs)


class EmployeeMapAccountList(BaseListMixin):
    permission_classes = [IsAuthenticated]
    queryset = Employee.object_global
    search_fields = ["search_content"]

    serializer_list = EmployeeMapAccountListSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super(EmployeeMapAccountList, self).get_queryset().select_related(
            'group',
            'user'
        )

    @swagger_auto_schema(
        operation_summary="Account Map Employee list",
        operation_description="Account Map Employee list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
