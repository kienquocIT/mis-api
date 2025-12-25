from django.db.models import Q, Prefetch
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.masterdata.saledata.models import ProductWareHouse
from apps.sales.asset.models import FixedAsset
from apps.sales.asset.serializers import FixedAssetListSerializer, FixedAssetCreateSerializer, \
    FixedAssetDetailSerializer, FixedAssetUpdateSerializer, AssetForLeaseListSerializer, \
    AssetStatusLeaseListSerializer, ProductWarehouseListSerializerForFixedAsset, \
    FixedAssetListWithDepreciationSerializer, RunFixedAssetDepreciationSerializer
from apps.sales.delivery.models import OrderDeliveryProductAsset
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, \
    ResponseController, HttpMsg

__all__ =[
    'FixedAssetList',
    'FixedAssetDetail',
    'AssetForLeaseList',
    'AssetStatusLeaseList',
    'AssetListNoPerm',
    'ProductWarehouseListForFixedAsset',
    'FixedAssetListWithDepreciationList',
    'RunDepreciationAPIView'
]

class FixedAssetList(BaseListMixin, BaseCreateMixin):
    queryset = FixedAsset.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'status': ['exact'],
        'manage_department': ['exact', 'in'],
        'source_type': ['exact', 'in'],
    }
    serializer_list = FixedAssetListSerializer
    serializer_create = FixedAssetCreateSerializer
    serializer_detail = FixedAssetDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        query_set = (super().get_queryset().select_related('manage_department', 'use_customer')
                                           .prefetch_related('use_departments'))
        # get fixed assets that haven't been written off
        return query_set.filter(
                        Q(fixed_asset_write_off__isnull=True) |
                        Q(fixed_asset_write_off__isnull=False, fixed_asset_write_off__system_status=0))

    @swagger_auto_schema(
        operation_summary="Fixed Asset List",
        operation_description="Get Fixed Asset List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='fixedasset', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Fixed Asset",
        operation_description="Create New Fixed Asset",
        request_body=FixedAssetCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        employee_require=True,
        label_code='asset', model_code='fixedasset', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class FixedAssetDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = FixedAsset.objects
    serializer_detail = FixedAssetDetailSerializer
    serializer_update = FixedAssetUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        query_set = (super().get_queryset().select_related('manage_department')
                                           .prefetch_related('use_departments'))
        return query_set

    @swagger_auto_schema(
        operation_summary="Fixed Asset Detail",
        operation_description="Get Fixed Asset Detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='fixedasset', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Fixed Asset Update",
        operation_description="Fixed Asset Update",
        request_body=FixedAssetUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='fixedasset', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, pk, **kwargs)


class AssetForLeaseList(BaseListMixin, BaseCreateMixin):
    queryset = FixedAsset.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        "status": ["exact"],
    }
    serializer_list = AssetForLeaseListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT


    @swagger_auto_schema(
        operation_summary="Fixed Asset For Lease List",
        operation_description="Get Fixed Asset For Lease List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='asset', model_code='fixedasset', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AssetStatusLeaseList(BaseListMixin, BaseCreateMixin):
    queryset = FixedAsset.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        "status": ["exact"],
        "delivery_pa_asset__delivery_sub__order_delivery__lease_order_id": ["exact", "in"],
    }
    serializer_list = AssetStatusLeaseListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            Prefetch(
                'delivery_pa_asset',
                queryset=OrderDeliveryProductAsset.objects.select_related(
                    'delivery_sub',
                    'delivery_sub__order_delivery',
                    'delivery_sub__order_delivery__lease_order',
                    'delivery_sub__order_delivery__lease_order__customer',
                ),
            ),
        )

    @swagger_auto_schema(
        operation_summary="Fixed Asset Status Lease List",
        operation_description="Get Fixed Asset Status Lease List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='asset', model_code='fixedasset', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AssetListNoPerm(BaseListMixin):
    queryset = FixedAsset.objects
    search_fields = ['title', 'code']
    serializer_list = FixedAssetListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    filterset_fields = {
        'status': ['exact'],
        'manage_department': ['exact', 'in'],
        'source_type': ['exact', 'in'],
    }

    def get_queryset(self):
        query_set = (super().get_queryset().select_related('product', 'manage_department', 'use_customer')
                     .prefetch_related('use_departments'))
        # get fixed assets that haven't been written off
        return query_set.filter(
            Q(fixed_asset_write_off__isnull=True) |
            Q(fixed_asset_write_off__isnull=False, fixed_asset_write_off__system_status=0))

    @swagger_auto_schema(
        operation_summary="Fixed Asset List No Perm",
        operation_description="Get Fixed Asset List No Perm",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='asset', model_code='fixedasset', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductWarehouseListForFixedAsset(BaseListMixin):
    queryset = ProductWareHouse.objects
    serializer_list = ProductWarehouseListSerializerForFixedAsset
    filterset_fields = {
        "id": ["exact"],
        "product_id": ["exact"],
        "warehouse_id": ["exact"],
    }

    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('warehouse').prefetch_related()

    @swagger_auto_schema(operation_summary='Product WareHouse')
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class FixedAssetListWithDepreciationList(BaseListMixin):
    queryset = FixedAsset.objects
    serializer_list = FixedAssetListWithDepreciationSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        query_set = (super().get_queryset().select_related('manage_department', 'use_customer')
                     .prefetch_related('use_departments'))
        # get only workflow finished
        return query_set.filter(system_status=3)

    @swagger_auto_schema(
        operation_summary="Fixed Asset List With Depreciation",
        operation_description="Fixed Asset List With Depreciation",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='fixedasset', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RunDepreciationAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="Fixed Asset Run Depreciation",
        operation_description="Fixed Asset Run Depreciation",
        request_body=RunFixedAssetDepreciationSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='fixedasset', perm_code='edit',
    )
    def post(self, request, *args, **kwargs):
        serializer = RunFixedAssetDepreciationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ResponseController.success_200(data={'detail': HttpMsg.SUCCESSFULLY}, key_data='result')
