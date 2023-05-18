from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.masterdata.promotion.models import Promotion
from apps.masterdata.promotion.serializers.promotion import PromotionListSerializer, PromotionCreateSerializer, \
    PromotionDetailSerializer, PromotionUpdateSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin

__all__ = ['PromotionList', 'PromotionDetail']


class PromotionList(BaseListMixin, BaseCreateMixin):
    queryset = Promotion.objects.all()
    serializer_list = PromotionListSerializer
    serializer_create = PromotionCreateSerializer
    serializer_detail = PromotionListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

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


class PromotionDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    permission_classes = [IsAuthenticated]
    queryset = Promotion.objects
    serializer_detail = PromotionDetailSerializer
    serializer_update = PromotionUpdateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']
    @swagger_auto_schema(
        operation_summary="Promotion detail",
        operation_description="get detail, update and delete promotion by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @mask_view(login_require=True, auth_require=True, code_perm='')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
