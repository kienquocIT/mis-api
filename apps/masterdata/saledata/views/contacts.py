from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin
from apps.masterdata.saledata.models.contacts import (
    Salutation, Interest, Contact
)
from apps.masterdata.saledata.serializers.contacts import (
    SalutationListSerializer, SalutationCreateSerializer, SalutationDetailSerializer, SalutationUpdateSerializer,
    InterestsListSerializer, InterestsCreateSerializer, InterestsDetailsSerializer, InterestsUpdateSerializer,

    ContactListSerializer, ContactCreateSerializer, ContactDetailSerializer,
    ContactUpdateSerializer, ContactListNotMapAccountSerializer,
)


# Create your views here.
class SalutationList(BaseListMixin, BaseCreateMixin):
    queryset = Salutation.objects
    serializer_list = SalutationListSerializer
    serializer_create = SalutationCreateSerializer

    serializer_detail = SalutationDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Salutation list",
        operation_description="Salutation list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Salutation",
        operation_description="Create new Salutation",
        request_body=SalutationCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SalutationDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Salutation.objects
    serializer_list = SalutationListSerializer
    serializer_create = SalutationCreateSerializer
    serializer_detail = SalutationDetailSerializer
    serializer_update = SalutationUpdateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail Salutation')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Salutation", request_body=SalutationUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class InterestsList(BaseListMixin, BaseCreateMixin):
    queryset = Interest.objects
    serializer_list = InterestsListSerializer
    serializer_create = InterestsCreateSerializer
    serializer_detail = InterestsDetailsSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Interests list",
        operation_description="Interests list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Interests",
        operation_description="Create new Interests",
        request_body=InterestsCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class InterestsDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Interest.objects
    serializer_list = InterestsListSerializer
    serializer_create = InterestsCreateSerializer
    serializer_detail = InterestsDetailsSerializer
    serializer_update = InterestsUpdateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail Interest')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Interest", request_body=InterestsUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# Contact
class ContactList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects
    filterset_fields = ['account_name_id']
    serializer_list = ContactListSerializer
    serializer_create = ContactCreateSerializer
    serializer_detail = ContactDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id', 'employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related('salutation', 'account_name', 'owner', 'report_to')

    @swagger_auto_schema(
        operation_summary="Contact list",
        operation_description="Contact list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='contact', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Contact",
        operation_description="Create new Contact",
        request_body=ContactCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='contact', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ContactDetail(BaseRetrieveMixin, BaseUpdateMixin):
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects
    serializer_detail = ContactDetailSerializer
    serializer_update = ContactUpdateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related('salutation', 'account_name', 'owner', 'report_to')

    @swagger_auto_schema(operation_summary='Detail Contact')
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='contact', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Contact", request_body=ContactUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='contact', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        print('UPDATE BODY: ', request.data)
        return self.update(request, *args, **kwargs)


class ContactListNotMapAccount(BaseListMixin):
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects
    serializer_list = ContactListNotMapAccountSerializer
    serializer_detail = ContactDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Contact list not map account",
        operation_description="Contact list not map account",
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='sale', app_code='contact', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        kwargs.update({'account_name': None})
        return self.list(request, *args, **kwargs)
