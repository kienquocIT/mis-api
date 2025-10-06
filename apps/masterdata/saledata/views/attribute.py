from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import Attribute, Product
from apps.masterdata.saledata.serializers.attribute import AttributeListSerializer, AttributeCreateSerializer, \
    AttributeUpdateSerializer, ProductAttributeDetailSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseUpdateMixin, BaseRetrieveMixin


class AttributeViewList(BaseListMixin, BaseCreateMixin):
    queryset = Attribute.objects
    search_fields = ["title"]
    filterset_fields = {
        'parent_n_id': ['exact', 'isnull'],
        'is_category': ['exact'],
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

    def get_queryset(self):
        request_qs = self.request.query_params.dict()
        if 'exclude_id' in request_qs:
            exclude_id = request_qs.pop('exclude_id')
            return super().get_queryset().select_related('parent_n').exclude(id=exclude_id)

        return super().get_queryset().select_related('parent_n')

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


class ProductAttributeDetail(BaseRetrieveMixin):
    queryset = Product.objects
    serializer_detail = ProductAttributeDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(operation_summary='Product Attribute List')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saledata', model_code='product', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)
