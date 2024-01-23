from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import RevenuePlanConfig
from apps.masterdata.saledata.serializers import (
    RevenuePlanConfigListSerializer, RevenuePlanConfigDetailSerializer, RevenuePlanConfigCreateSerializer
)
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


# Create your views here.
class RevenuePlanConfigList(BaseListMixin, BaseCreateMixin):
    queryset = RevenuePlanConfig.objects
    search_fields = ['title']
    serializer_list = RevenuePlanConfigListSerializer
    serializer_create = RevenuePlanConfigCreateSerializer
    serializer_detail = RevenuePlanConfigDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="RevenuePlanConfig list",
        operation_description="RevenuePlanConfig list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create RevenuePlanConfig",
        operation_description="Create new RevenuePlanConfig",
        request_body=RevenuePlanConfigCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RevenuePlanConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = RevenuePlanConfig.objects
    serializer_list = RevenuePlanConfigListSerializer
    serializer_create = RevenuePlanConfigCreateSerializer
    serializer_detail = RevenuePlanConfigDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail RevenuePlanConfig')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)
