from drf_yasg.utils import swagger_auto_schema
from apps.sales.deliveryservice.models import DeliveryService
from apps.sales.deliveryservice.serializers import (
    DeliveryServiceListSerializer, DeliveryServiceDetailSerializer,
    DeliveryServiceCreateSerializer, DeliveryServiceUpdateSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin


__all__ = [
    'DeliveryServiceList',
    'DeliveryServiceDetail',
]


class DeliveryServiceList(BaseListMixin, BaseCreateMixin):
    queryset = DeliveryService.objects
    search_fields = [
        'title', 'code',
    ]
    serializer_list = DeliveryServiceListSerializer
    serializer_create = DeliveryServiceCreateSerializer
    serializer_detail = DeliveryServiceDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="DeliveryService list",
        operation_description="DeliveryService list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='deliveryservice', model_code='deliveryservice', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create DeliveryService",
        operation_description="Create new DeliveryService",
        request_body=DeliveryServiceCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='deliveryservice', model_code='deliveryservice', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class DeliveryServiceDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = DeliveryService.objects  # noqa
    serializer_list = DeliveryServiceListSerializer
    serializer_detail = DeliveryServiceDetailSerializer
    serializer_update = DeliveryServiceUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(operation_summary='Detail DeliveryService')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='deliveryservice', model_code='deliveryservice', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update DeliveryService", request_body=DeliveryServiceUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        label_code='deliveryservice', model_code='deliveryservice', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)
