from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import Attribute
from apps.masterdata.saledata.serializers.attribute import AttributeListSerializer, AttributeCreateSerializer, \
    AttributeUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseUpdateMixin


class AttributeViewList(BaseListMixin, BaseCreateMixin):
    queryset = Attribute.objects
    search_fields = ["title"]
    filterset_fields = {
        'parent_n_id': ['exact', 'isnull'],
    }
    serializer_list = AttributeListSerializer
    serializer_detail = AttributeListSerializer
    serializer_create = AttributeCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id',
        'company_id',
        'employee_created_id',
    ]

    @swagger_auto_schema(
        operation_summary="Attribute List",
        operation_description="Get Attribute List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Attribute",
        operation_description="Create Attribute",
        request_body=AttributeCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AttributeViewDetail(BaseUpdateMixin):
    queryset = Attribute.objects
    serializer_detail = AttributeListSerializer
    serializer_update = AttributeUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Update Attribute",
        operation_description="Update Attribute by ID",
        request_body=AttributeUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
