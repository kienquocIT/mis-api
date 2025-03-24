from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import Product, ProductPriceList
from apps.sales.grouporder.serializers import GroupOrderProductListSerializer, GroupOrderProductPriceListListSerializer
from apps.shared import (
    mask_view, ResponseController,
    BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin,
)

# Create your views here.
class GroupOrderProductList(BaseListMixin, BaseCreateMixin):
    queryset = Product.objects
    serializer_list = GroupOrderProductListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    search_fields = [
        'title',
    ]

    def get_queryset(self):
        return super().get_queryset().prefetch_related('bom_product', 'product_price_product')

    @swagger_auto_schema(
        operation_summary="GroupOrder Product list",
        operation_description="GroupOrder Product list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class GroupOrderProductPriceListList(BaseListMixin, BaseCreateMixin):
    queryset = ProductPriceList.objects
    serializer_list = GroupOrderProductPriceListListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    search_fields = [
        'title',
    ]
    filterset_fields = {
        'product__id': ['exact'],
    }

    def get_queryset(self):
        return super().get_queryset()

    @swagger_auto_schema(
        operation_summary="GroupOrder ProductPriceList list",
        operation_description="GroupOrder ProductPriceList list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
