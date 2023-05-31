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

    @swagger_auto_schema(
        operation_summary="Delivery Config Detail",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delivery Config Update",
        request_body=DeliveryConfigUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)


class SaleOrderActiveDelivery(APIView):
    @swagger_auto_schema(
        operation_summary='Call delivery at SaleOrder Detail',
        operation_description='"id" is Sale Order ID - Start delivery process of this'
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, pk, **kwargs):
        cls_model = DisperseModel(app_model='saleorder.SaleOrder').get_model()
        cls_m2m_product_model = DisperseModel(app_model='saleorder.SaleOrderProduct').get_model()
        if cls_model and cls_m2m_product_model and TypeCheck.check_uuid(pk):
            try:
                obj = cls_model.objects.get_current(pk=pk, fill__company=True)
                if cls_m2m_product_model.objects.filter(sale_order=obj).count() <= 0:
                    raise serializers.ValidationError(
                        {
                            'detail': 'Need at least once product for delivery process run'
                        }
                    )
                call_task_background(
                    my_task=task_active_delivery_from_sale_order,
                    **{'sale_order_id': str(obj.id)}
                )
                return ResponseController.success_200(data={'state': 'Successfully'}, key_data='result')
            except cls_model.DoesNotExist:
                pass
            except DeliveryConfig.DoesNotExist:
                pass
        return ResponseController.notfound_404()
