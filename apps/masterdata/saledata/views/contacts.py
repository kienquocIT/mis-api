from drf_yasg.utils import swagger_auto_schema
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
from apps.sales.lead.models import Lead


# Create your views here.
class SalutationList(BaseListMixin, BaseCreateMixin):
    queryset = Salutation.objects
    serializer_list = SalutationListSerializer
    serializer_create = SalutationCreateSerializer

    serializer_detail = SalutationDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Salutation list",
        operation_description="Salutation list",
    )
    @mask_view(
        login_require=True, auth_require=False
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
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail Salutation')
    @mask_view(
        login_require=True, auth_require=False
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
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Interests list",
        operation_description="Interests list",
    )
    @mask_view(
        login_require=True, auth_require=False
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
        allow_admin_tenant=True, allow_admin_company=True
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class InterestsDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Interest.objects
    serializer_list = InterestsListSerializer
    serializer_create = InterestsCreateSerializer
    serializer_detail = InterestsDetailsSerializer
    serializer_update = InterestsUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail Interest')
    @mask_view(
        login_require=True, auth_require=False
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Interest", request_body=InterestsUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# Contact
class ContactList(BaseListMixin, BaseCreateMixin):
    queryset = Contact.objects
    search_fields = ['title', 'code', 'fullname', 'mobile', 'email', 'account_name__name']
    filterset_fields = ['account_name_id']
    serializer_list = ContactListSerializer
    serializer_create = ContactCreateSerializer
    serializer_detail = ContactDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('salutation', 'account_name', 'owner', 'report_to')

    @swagger_auto_schema(
        operation_summary="Contact list",
        operation_description="Contact list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saledata', model_code='contact', perm_code='view',
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
        label_code='saledata', model_code='contact', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        if all(['convert_contact' in request.data, 'lead_id' in request.data]):
            lead = Lead.objects.filter(id=request.data['lead_id']).first()
            if lead:
                request.data['email'] = lead.email
                request.data['mobile'] = lead.mobile
                request.data['fullname'] = lead.contact_name
                request.data['job_title'] = lead.job_title
                request.data['owner'] = str(self.request.user.employee_current_id)

                self.ser_context = {'lead': lead}
        return self.create(request, *args, **kwargs)


class ContactDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Contact.objects
    serializer_detail = ContactDetailSerializer
    serializer_update = ContactUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'salutation', 'account_name', 'owner', 'report_to',
            'work_country', 'work_city', 'work_district', 'work_ward',
            'home_country', 'home_city', 'home_district', 'home_ward',
        )

    @swagger_auto_schema(operation_summary='Detail Contact')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saledata', model_code='contact', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Contact", request_body=ContactUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saledata', model_code='contact', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ContactListNotMapAccount(BaseListMixin):
    queryset = Contact.objects
    serializer_list = ContactListNotMapAccountSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(account_name=None)

    @swagger_auto_schema(
        operation_summary="Contact list not map account",
        operation_description="Contact list not map account",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saledata', model_code='contact', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
