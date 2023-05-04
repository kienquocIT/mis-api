from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.promotion.models import Promotion
from apps.masterdata.promotion.serializers.promotion import PromotionListSerializer, PromotionCreateSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view

__all__ = ['PromotionList']


class PromotionList(BaseListMixin, BaseCreateMixin):
    queryset = Promotion.objects.all()
    serializer_list = PromotionListSerializer
    serializer_create = PromotionCreateSerializer
    serializer_detail = PromotionListSerializer
    list_hidden_field = ['tenant_id', 'company_id', 'json_method']
    create_hidden_field = ['tenant_id', 'company_id', 'json_method']

    @swagger_auto_schema(
        operation_summary="Promotion list",
        operation_description="Master data promotion list, all about setup discount, coupons, gift",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Promotion",
        operation_description="Create new Promotion",
        request_body=PromotionCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
