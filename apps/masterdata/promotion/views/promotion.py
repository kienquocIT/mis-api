from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.promotion.models import Promotion
from apps.masterdata.promotion.serializers.promotion import PromotionListSerializer, PromotionCreateSerializer, \
    PromotionDetailSerializer, PromotionUpdateSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin,\
    BaseDestroyMixin

__all__ = ['PromotionList', 'PromotionDetail', 'PromotionCheckList']


class PromotionList(BaseListMixin, BaseCreateMixin):
    queryset = Promotion.objects
    serializer_list = PromotionListSerializer
    serializer_create = PromotionCreateSerializer
    serializer_detail = PromotionListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Promotion list",
        operation_description="Master data promotion list, all about setup discount, coupons, gift",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Promotion",
        operation_description="Create new Promotion",
        request_body=PromotionCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PromotionDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = Promotion.objects
    serializer_detail = PromotionDetailSerializer
    serializer_update = PromotionUpdateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Promotion detail",
        operation_description="get detail, update and delete promotion by ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class PromotionCheckList(BaseListMixin):
    queryset = Promotion.objects
    search_fields = ['title', 'code', 'customer__name']
    filterset_fields = {
        'customer_type': ['exact'],
        'customers_map_promotion__id': ['exact'],
    }
    serializer_list = PromotionDetailSerializer
    serializer_detail = PromotionDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related("currency").prefetch_related('sale_order_product_promotion')

    @swagger_auto_schema(
        operation_summary="Promotion list",
        operation_description="Master data promotion list use for check sale's app: quotation, sale-order,...",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
