from drf_yasg.utils import swagger_auto_schema

from apps.sales.fixedasset.models import FixedAsset
from apps.sales.fixedasset.serializers import FixedAssetListSerializer, FixedAssetCreateSerializer, \
    FixedAssetDetailSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

class FixedAssetList(BaseListMixin, BaseCreateMixin):
    queryset = FixedAsset.objects
    search_fields = ['title', 'code']
    filterset_fields = {}
    serializer_list = FixedAssetListSerializer
    serializer_create = FixedAssetCreateSerializer
    serializer_detail = FixedAssetDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Fixed Asset List",
        operation_description="Get Fixed Asset List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Fixed Asset",
        operation_description="Create New Fixed Asset",
        request_body=FixedAssetCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)

class FixedAssetDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = FixedAsset.objects
    serializer_detail = FixedAssetDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Fixed Asset Detail",
        operation_description="Get Fixed Asset Detail",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)