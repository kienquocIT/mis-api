from drf_yasg.utils import swagger_auto_schema

from apps.accounting.accountingsettings.models import Dimension, DimensionValue, DimensionSyncConfig, \
    AccountDimensionMap, ChartOfAccounts
from apps.accounting.accountingsettings.serializers import DimensionDefinitionListSerializer, \
    DimensionDefinitionCreateSerializer, DimensionDefinitionDetailSerializer, DimensionDefinitionUpdateSerializer, \
    DimensionDefinitionWithValuesSerializer, DimensionValueListSerializer, DimensionValueCreateSerializer, \
    DimensionValueDetailSerializer, DimensionValueUpdateSerializer, DimensionSyncConfigApplicationListSerializer, \
    DimensionSyncConfigListSerializer, DimensionSyncConfigCreateSerializer, DimensionSyncConfigDetailSerializer, \
    DimensionSyncConfigUpdateSerializer
from apps.accounting.accountingsettings.serializers.dimension_account_map import AccountDimensionMapCreateSerializer, \
    AccountDimensionMapDetailSerializer, DimensionListForAccountingAccountSerializer, \
    AccountDimensionMapUpdateSerializer
from apps.core.base.models import Application
from apps.shared import BaseListMixin, BaseCreateMixin, BaseUpdateMixin, mask_view, BaseRetrieveMixin


# Create your views here.
class DimensionDefinitionList(BaseListMixin, BaseCreateMixin):
    queryset = Dimension.objects
    serializer_list = DimensionDefinitionListSerializer
    serializer_create = DimensionDefinitionCreateSerializer
    serializer_detail = DimensionDefinitionDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Dimension Definition List",
        operation_description="Get Dimension Definition List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Dimension Definition Create",
        operation_description="Create new Dimension Definition",
        request_body=DimensionDefinitionCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DimensionDefinitionDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Dimension.objects
    serializer_update = DimensionDefinitionUpdateSerializer
    serializer_detail = DimensionDefinitionDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Dimension Definition Detail",
        operation_description="Get Dimension Definition Detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(request_body=DimensionDefinitionUpdateSerializer)
    @mask_view(login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class DimensionDefinitionWithValueList(BaseRetrieveMixin):
    queryset = Dimension.objects
    serializer_detail = DimensionDefinitionWithValuesSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Dimension Definition With Dimension Values",
        operation_description="Get Dimension Definition With Dimension Values",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)


class DimensionValueList(BaseListMixin, BaseCreateMixin):
    queryset = DimensionValue.objects
    serializer_list = DimensionValueListSerializer
    serializer_create = DimensionValueCreateSerializer
    serializer_detail = DimensionValueDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Dimension Value List",
        operation_description="Get Dimension Value List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Dimension Value Create",
        operation_description="Create new Value Definition",
        request_body=DimensionValueCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'tenant_current_id': request.user.tenant_current_id,
            'company_current_id': request.user.company_current_id,
        }
        return self.create(request, *args, **kwargs)


class DimensionValueDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = DimensionValue.objects
    serializer_update = DimensionValueUpdateSerializer
    serializer_detail = DimensionValueDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Dimension Value Detail",
        operation_description="Get Dimension Value Detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(request_body=DimensionValueUpdateSerializer)
    @mask_view(login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class DimensionSyncConfigApplicationList(BaseListMixin):
    queryset = Application.objects
    serializer_list = DimensionSyncConfigApplicationListSerializer

    # uuid of application
    list_app_id = [
        '4e48c863-861b-475a-aa5e-97a4ed26f294', # Account
        '3407d35d-27ce-407e-8260-264574a216e3', # payment term
        '7bc78f47-66f1-4104-a6fa-5ca07f3f2275', # unitofmeasure
        'a8badb2e-54ff-4654-b3fd-0d2d3c777538', # saledata.product
        '245e9f47-df59-4d4a-b355-7eff2859247f', # saledata.expenseitem
    ]
    def get_queryset(self):
        return Application.objects.filter(id__in=self.list_app_id)

    @swagger_auto_schema(
        operation_summary="Application List for Dimension",
        operation_description="Get Application List for Dimension",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DimensionSyncConfigList(BaseListMixin, BaseCreateMixin):
    queryset = DimensionSyncConfig.objects
    serializer_list = DimensionSyncConfigListSerializer
    serializer_create = DimensionSyncConfigCreateSerializer
    serializer_detail = DimensionSyncConfigDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Dimension Config List",
        operation_description="Get Dimension Config List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Dimension Config Create",
        operation_description="Create new dimension Config",
        request_body=DimensionSyncConfigCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DimensionSyncConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = DimensionSyncConfig.objects
    serializer_update = DimensionSyncConfigUpdateSerializer
    serializer_detail = DimensionSyncConfigDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Dimension Config Detail",
        operation_description="Get Dimension Config Detail",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Dimension Config Update",
        operation_description="Update Dimension Config",
        request_body=DimensionSyncConfigUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class DimensionAccountMapList(BaseCreateMixin):
    queryset = AccountDimensionMap.objects
    serializer_create = AccountDimensionMapCreateSerializer
    serializer_detail = AccountDimensionMapDetailSerializer
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Dimension Account Create",
        operation_description="Create new Dimension Account",
        request_body=AccountDimensionMapCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DimensionAccountMapDetail(BaseUpdateMixin):
    queryset = AccountDimensionMap.objects
    serializer_update = AccountDimensionMapUpdateSerializer
    serializer_detail = AccountDimensionMapDetailSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Dimension Account Update",
        operation_description="Update Dimension Account",
        request_body=AccountDimensionMapUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class DimensionListForAccountingAccount(BaseRetrieveMixin):
    queryset = ChartOfAccounts.objects
    serializer_detail = DimensionListForAccountingAccountSerializer
    retrieve_hidden_field =  BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="DimensionListForAccountingAccount",
        operation_description="Get DimensionListForAccountingAccount",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
