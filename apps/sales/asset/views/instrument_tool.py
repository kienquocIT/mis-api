from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.sales.asset.models import InstrumentTool
from apps.sales.asset.serializers import InstrumentToolUpdateSerializer, InstrumentToolDetailSerializer, \
    InstrumentToolCreateSerializer, InstrumentToolListSerializer, ToolForLeaseListSerializer, \
    ToolStatusLeaseListSerializer
from apps.sales.delivery.models import OrderDeliveryProductTool
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

__all__ =[
    'InstrumentToolList',
    'InstrumentToolDetail',
    'ToolForLeaseList',
    'ToolStatusLeaseList',
    'InstrumentToolNoPermList'
]


class InstrumentToolList(BaseListMixin, BaseCreateMixin):
    queryset = InstrumentTool.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'product': ['exact', 'in'],
        'status': ['exact', 'in'],
        'manage_department': ['exact', 'in'],
        'source_type': ['exact', 'in'],
    }
    serializer_list = InstrumentToolListSerializer
    serializer_create = InstrumentToolCreateSerializer
    serializer_detail =InstrumentToolDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        queryset = (super().get_queryset().select_related('product', 'manage_department', 'use_customer')
                                          .prefetch_related('write_off_quantities', 'use_departments'))
        return queryset

    @swagger_auto_schema(
        operation_summary="Instrument Tool List",
        operation_description="Get InstrumentTool List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='instrumenttool', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Instrument Tool",
        operation_description="Create New Instrument Tool",
        request_body=InstrumentToolCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='instrumenttool', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class InstrumentToolDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = InstrumentTool.objects
    serializer_detail = InstrumentToolDetailSerializer
    serializer_update = InstrumentToolUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        queryset = (super().get_queryset().select_related('classification', 'product', 'manage_department')
                                          .prefetch_related('write_off_quantities', 'use_departments',
                                                            'ap_invoice_items', 'asset_sources'))
        return queryset

    @swagger_auto_schema(
        operation_summary="Instrument Tool Detail",
        operation_description="Get Instrument Tool Detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='instrumenttool', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Instrument Tool Update",
        operation_description="Instrument Tool Update",
        request_body=InstrumentToolUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='instrumenttool', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, pk, **kwargs)


class ToolForLeaseList(BaseListMixin, BaseCreateMixin):
    queryset = InstrumentTool.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        "status": ["exact"],
    }
    serializer_list = ToolForLeaseListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "product",
            "product__sale_default_uom",
        )

    @swagger_auto_schema(
        operation_summary="Instrument Tool For Lease List",
        operation_description="Get Instrument Tool For Lease List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='asset', model_code='instrumenttool', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ToolStatusLeaseList(BaseListMixin, BaseCreateMixin):
    queryset = InstrumentTool.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        "status": ["exact"],
        "delivery_pt_tool__delivery_sub__order_delivery__lease_order_id": ["exact", "in"],
    }
    serializer_list = ToolStatusLeaseListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            Prefetch(
                'delivery_pt_tool',
                queryset=OrderDeliveryProductTool.objects.select_related(
                    'delivery_sub',
                    'delivery_sub__order_delivery',
                    'delivery_sub__order_delivery__lease_order',
                    'delivery_sub__order_delivery__lease_order__customer',
                ),
            ),
        )

    @swagger_auto_schema(
        operation_summary="Instrument Tool Status Lease List",
        operation_description="Get Instrument Tool Status Lease List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='asset', model_code='instrumenttool', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class InstrumentToolNoPermList(BaseListMixin):
    queryset = InstrumentTool.objects
    search_fields = ['title', 'code']
    serializer_list = InstrumentToolListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    filterset_fields = {
        'product': ['exact', 'in'],
        'status': ['exact'],
        'manage_department': ['exact', 'in'],
        'source_type': ['exact', 'in'],
    }

    def get_queryset(self):
        queryset = (super().get_queryset().select_related('product', 'manage_department', 'use_customer')
                                          .prefetch_related('write_off_quantities', 'use_departments'))
        return queryset

    @swagger_auto_schema(
        operation_summary="Instrument Tool List",
        operation_description="Get InstrumentTool List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='asset', model_code='instrumenttool', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
