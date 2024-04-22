from drf_yasg.utils import swagger_auto_schema
from apps.sales.inventory.models import GoodsReceiptProduct, GoodsReceipt
from apps.sales.inventory.serializers.goods_detail import GoodsDetailListSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin


class GoodsDetailList(BaseListMixin, BaseCreateMixin):
    queryset = GoodsReceipt.objects
    serializer_list = GoodsDetailListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related()

    @swagger_auto_schema(
        operation_summary="Goods detail List",
        operation_description="Get Goods detail List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsreceipt', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
