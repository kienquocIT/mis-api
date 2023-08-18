from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.views import APIView

from apps.shared import (
    BaseRetrieveMixin, BaseUpdateMixin,
    mask_view, DisperseModel, ResponseController, TypeCheck,
    call_task_background,
)
from apps.sales.delivery.models import (
    DeliveryConfig,
)
from apps.sales.delivery.serializers import (
    DeliveryConfigDetailSerializer, DeliveryConfigUpdateSerializer,
)
from apps.sales.delivery.tasks import (
    task_active_delivery_from_sale_order,
)

__all__ = [
    'DeliveryConfigDetail',
    'SaleOrderActiveDelivery',
]


class DeliveryConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = DeliveryConfig.objects
    serializer_detail = DeliveryConfigDetailSerializer
    serializer_update = DeliveryConfigUpdateSerializer
    list_hidden_field = ['company_id']
    create_hidden_field = ['company_id']

    @swagger_auto_schema(
        operation_summary="Delivery Config Detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delivery Config Update",
        request_body=DeliveryConfigUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)


class SaleOrderActiveDelivery(APIView):
    @swagger_auto_schema(
        operation_summary='Call delivery at SaleOrder Detail',
        operation_description='"id" is Sale Order ID - Start delivery process of this'
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='delivery', model_code='orderpickingsub', perm_code='create',
    )
    def post(self, request, *args, pk, **kwargs):
        cls_model = DisperseModel(app_model='saleorder.SaleOrder').get_model()
        cls_m2m_product_model = DisperseModel(app_model='saleorder.SaleOrderProduct').get_model()
        if cls_model and cls_m2m_product_model and TypeCheck.check_uuid(pk):
            try:
                obj = cls_model.objects.get_current(pk=pk, fill__company=True)
                is_not_picking = False
                if cls_m2m_product_model.objects.filter(sale_order=obj).count() > 0:
                    prod_so = cls_m2m_product_model.objects.filter(sale_order=obj, product__isnull=False)
                    count_prod = prod_so.count()
                    is_services = 0
                    for item in prod_so:
                        if 1 not in item.product.product_choice:
                            is_services += 1
                    if count_prod == is_services:
                        is_not_picking = True

                else:
                    raise serializers.ValidationError(
                        {
                            'detail': 'Need at least once product for delivery process run'
                        }
                    )

                call_task_background(
                    my_task=task_active_delivery_from_sale_order,
                    **{'sale_order_id': str(obj.id)}
                )
                config = DeliveryConfig.objects.get(company_id=str(obj.company_id))
                serializer = DeliveryConfigDetailSerializer(config)
                return ResponseController.success_200(
                    data={'state': 'Successfully', 'config': serializer.data, 'is_not_picking': is_not_picking},
                    key_data='result'
                )
            except cls_model.DoesNotExist:
                pass
            except DeliveryConfig.DoesNotExist:
                pass
        return ResponseController.notfound_404()
