from drf_yasg.utils import swagger_auto_schema

from apps.core.hr.filters import EmployeeListFilter
from apps.core.hr.models import Employee
from apps.masterdata.saledata.models import Contact, Industry, Account
from apps.sales.opportunity.models import OpportunityConfigStage
from apps.sales.partnercenter.models import DataObject, List
from apps.sales.partnercenter.serializers import ListDataObjectListSerializer, ListCreateSerializer, \
    ListDetailSerializer, ListResultListSerializer, ListListSerializer, ListEmployeeListSerializer, \
    ListContactListSerializer, ListUpdateSerializer, ListIndustryListSerializer, \
    ListOpportunityConfigStageListSerializer, ListAccountListSerializer
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, \
    ResponseController, HttpMsg


class ListDataObjectList(BaseListMixin):
    queryset = DataObject.objects
    serializer_list = ListDataObjectListSerializer
    list_hidden_field = []

    @swagger_auto_schema(
        operation_summary="Data Object List",
        operation_description="Get Data Object List",
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListList(BaseListMixin, BaseCreateMixin):
    queryset = List.objects
    serializer_list = ListListSerializer
    serializer_create = ListCreateSerializer
    serializer_detail = ListDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(application=None)

    @swagger_auto_schema(
        operation_summary="list",
        operation_description="list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='partnercenter', model_code='list', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create ParnterCenter List",
        operation_description="Create ParnterCenter List",
        request_body=ListCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='partnercenter', model_code='list', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = List.objects
    serializer_detail = ListDetailSerializer
    serializer_update = ListUpdateSerializer

    @swagger_auto_schema(
        operation_summary="PartnerCenter List Detail",
        operation_description="Get PartnerCenter List Detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='partnercenter', model_code='list', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update List List",
        operation_description="Update List List",
        request_body=ListUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='partnercenter', model_code='list', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete List'
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='partnercenter', model_code='list', perm_code='delete',
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return ResponseController.success_200(data={'detail': HttpMsg.SUCCESSFULLY}, key_data='result')

class ListResultList(BaseRetrieveMixin):
    queryset = List.objects
    serializer_detail = ListResultListSerializer

    @swagger_auto_schema(
        operation_summary="PartnerCenter List Result List",
        operation_description="Get PartnerCenter List Result List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='partnercenter', model_code='list', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)


class ListEmployeeList(BaseListMixin):
    queryset = Employee.objects
    filterset_class = EmployeeListFilter
    serializer_list = ListEmployeeListSerializer

    list_hidden_field = ('tenant_id', 'company_id')

    @swagger_auto_schema(
        operation_summary="Employee list",
        operation_description="Get employee list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListContactList(BaseListMixin):
    queryset = Contact.objects
    serializer_list = ListContactListSerializer

    list_hidden_field = ('tenant_id', 'company_id')

    @swagger_auto_schema(
        operation_summary="Contact list",
        operation_description="Get Contact list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListIndustryList(BaseListMixin):
    queryset = Industry.objects
    serializer_list = ListIndustryListSerializer

    list_hidden_field = ('tenant_id', 'company_id')

    @swagger_auto_schema(
        operation_summary="Industry list",
        operation_description="Get Industry list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListOpportunityConfigStageList(BaseListMixin):
    queryset = OpportunityConfigStage.objects
    serializer_list = ListOpportunityConfigStageListSerializer

    list_hidden_field = ('company_id',)

    @swagger_auto_schema(
        operation_summary="Opportunity Config Stage list",
        operation_description="Get Opportunity Config Stage list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListAccountList(BaseListMixin):
    queryset = Account.objects
    serializer_list = ListAccountListSerializer

    list_hidden_field = ('tenant_id', 'company_id')

    @swagger_auto_schema(
        operation_summary="Account list",
        operation_description="Get Account list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
