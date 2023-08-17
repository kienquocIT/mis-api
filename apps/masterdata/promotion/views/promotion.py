from django.db.models import Q
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.promotion.models import Promotion
from apps.masterdata.promotion.serializers.promotion import PromotionListSerializer, PromotionCreateSerializer, \
    PromotionDetailSerializer, PromotionUpdateSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin,\
    BaseDestroyMixin, TypeCheck

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
    serializer_list = PromotionDetailSerializer
    serializer_detail = PromotionDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        # filter expires date
        current_date = timezone.now()
        filter_expires = {
            'valid_date_start__lte': current_date,
            'valid_date_end__gte': current_date
        }
        # setup where OR
        data_filter = self.request.query_params.dict()
        filter_q = Q()
        for key in data_filter:
            match key:
                case 'customer_type':
                    val_of_key = data_filter[key]
                    if isinstance(val_of_key, int) or val_of_key.isdigit():
                        filter_q |= Q(customer_type=int(val_of_key))
                case 'customers_map_promotion__id':
                    val_of_key = data_filter[key]
                    if TypeCheck.check_uuid(val_of_key):
                        filter_q |= Q(customers_map_promotion__id=val_of_key)
        # return query filter
        if len(filter_q) > 0:
            return super().get_queryset().filter(**filter_expires).filter(filter_q)
        return super().get_queryset().filter(**filter_expires)

    @swagger_auto_schema(
        operation_summary="Promotion list",
        operation_description="Master data promotion list use for check sale's app: quotation, sale-order,...",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
