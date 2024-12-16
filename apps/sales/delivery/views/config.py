from datetime import datetime

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.views import APIView

from apps.core.process.msg import ProcessMsg
from apps.core.process.utils import ProcessRuntimeControl
from apps.masterdata.saledata.models import SubPeriods
from apps.shared import (
    BaseRetrieveMixin, BaseUpdateMixin,
    mask_view, DisperseModel, ResponseController, TypeCheck,
    call_task_background,
)
from apps.sales.delivery.models import (
    DeliveryConfig, OrderDeliverySub,
)
from apps.sales.delivery.serializers import (
    DeliveryConfigDetailSerializer, DeliveryConfigUpdateSerializer,
)
from apps.sales.delivery.tasks import (
    task_active_delivery_from_sale_order, task_active_delivery_from_lease_order,
)

__all__ = [
    'DeliveryConfigDetail',
    'SaleOrderActiveDelivery',
    'LeaseOrderActiveDelivery',
]

from apps.shared.translations.sales import DeliverMsg


class DeliveryConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = DeliveryConfig.objects
    serializer_detail = DeliveryConfigDetailSerializer
    serializer_update = DeliveryConfigUpdateSerializer
    list_hidden_field = ['company_id']
    create_hidden_field = ['company_id']

    def get_queryset(self):
        return super().get_queryset().select_related("lead_picking", "lead_delivery")

    @swagger_auto_schema(
        operation_summary="Delivery Config Detail",
    )
    @mask_view(
        login_require=True, auth_require=False,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delivery Config Update",
        request_body=DeliveryConfigUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)


class SaleOrderActiveDelivery(APIView):

    @classmethod
    def check_config(cls, config):
        if not config.lead_picking and config.is_picking or not config.lead_delivery:
            # case 1: có setup picking mà ko chọn leader
            # case 2: ko setup lead cho delivery
            return False
        return True

    @swagger_auto_schema(
        operation_summary='Call delivery at SaleOrder Detail',
        operation_description='"id" is Sale Order ID - Start delivery process of this'
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='delivery', model_code='orderDeliverySub', perm_code='create',
    )
    def post(self, request, *args, pk, **kwargs):  # pylint: disable=R0914
        SubPeriods.check_open(
            request.user.company_current_id,
            request.user.tenant_current_id,
            datetime.now()
        )

        cls_model = DisperseModel(app_model='saleorder.SaleOrder').get_model()
        cls_m2m_product_model = DisperseModel(app_model='saleorder.SaleOrderProduct').get_model()
        if cls_model and cls_m2m_product_model and TypeCheck.check_uuid(pk):
            try:
                obj = cls_model.objects.get_current(pk=pk, fill__company=True)
                is_not_picking = False
                prod_so = cls_m2m_product_model.objects.filter(sale_order=obj, product__isnull=False)
                if prod_so.count() > 0:
                    is_services = 0
                    for item in prod_so:
                        if 1 not in item.product.product_choice:
                            is_services += 1
                    if prod_so.count() == is_services:
                        is_not_picking = True

                else:
                    raise serializers.ValidationError(
                        {
                            'detail': 'Need at least once product for delivery process run'
                        }
                    )
                config = DeliveryConfig.objects.get(company_id=str(obj.company_id))
                if not self.check_config(config):
                    raise serializers.ValidationError(
                        {
                            'detail': DeliverMsg.ERROR_CONFIG
                        }
                    )

                body_data = request.data
                process_id = None
                if 'process' in body_data:
                    process_id = request.data['process']
                    stage_app_id = request.data.get('process_stage_app', None)
                    if not stage_app_id or not TypeCheck.check_uuid(stage_app_id):
                        raise serializers.ValidationError({
                            'process': ProcessMsg.PROCESS_STAGE_APP_NOT_FOUND
                        })

                    process_obj = ProcessRuntimeControl.get_process_obj(process_id=process_id)
                    process_stage_app_obj = ProcessRuntimeControl.get_process_stage_app(
                        stage_app_id=stage_app_id, app_id=OrderDeliverySub.get_app_id()
                    )
                    if process_obj:
                        process_cls = ProcessRuntimeControl(process_obj=process_obj)
                        process_cls.validate_process(process_stage_app_obj=process_stage_app_obj, opp_id=None)

                call_task_background(
                    my_task=task_active_delivery_from_sale_order,
                    **{'sale_order_id': str(obj.id), 'process_id': process_id}
                )

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


class LeaseOrderActiveDelivery(APIView):

    @classmethod
    def check_config(cls, config):
        if not config.lead_picking and config.is_picking or not config.lead_delivery:
            # case 1: có setup picking mà ko chọn leader
            # case 2: ko setup lead cho delivery
            return False
        return True

    @swagger_auto_schema(
        operation_summary='Call delivery at LeaseOrder Detail',
        operation_description='"id" is Lease Order ID - Start delivery process of this'
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='delivery', model_code='orderDeliverySub', perm_code='create',
    )
    def post(self, request, *args, pk, **kwargs):  # pylint: disable=R0914
        SubPeriods.check_open(
            request.user.company_current_id,
            request.user.tenant_current_id,
            datetime.now()
        )

        cls_model = DisperseModel(app_model='leaseorder.LeaseOrder').get_model()
        cls_m2m_product_model = DisperseModel(app_model='leaseorder.LeaseOrderProduct').get_model()
        if cls_model and cls_m2m_product_model and TypeCheck.check_uuid(pk):
            try:
                obj = cls_model.objects.get_current(pk=pk, fill__company=True)
                is_not_picking = False
                prod_lo = cls_m2m_product_model.objects.filter(sale_order=obj, product__isnull=False)
                if prod_lo.count() > 0:
                    is_services = 0
                    for item in prod_lo:
                        if 1 not in item.product.product_choice:
                            is_services += 1
                    if prod_lo.count() == is_services:
                        is_not_picking = True

                else:
                    raise serializers.ValidationError(
                        {
                            'detail': 'Need at least once product for delivery process run'
                        }
                    )
                config = DeliveryConfig.objects.get(company_id=str(obj.company_id))
                if not self.check_config(config):
                    raise serializers.ValidationError(
                        {
                            'detail': DeliverMsg.ERROR_CONFIG
                        }
                    )

                body_data = request.data
                process_id = None
                if 'process' in body_data:
                    process_id = request.data['process']
                    stage_app_id = request.data.get('process_stage_app', None)
                    if not stage_app_id or not TypeCheck.check_uuid(stage_app_id):
                        raise serializers.ValidationError({
                            'process': ProcessMsg.PROCESS_STAGE_APP_NOT_FOUND
                        })

                    process_obj = ProcessRuntimeControl.get_process_obj(process_id=process_id)
                    process_stage_app_obj = ProcessRuntimeControl.get_process_stage_app(
                        stage_app_id=stage_app_id, app_id=OrderDeliverySub.get_app_id()
                    )
                    if process_obj:
                        process_cls = ProcessRuntimeControl(process_obj=process_obj)
                        process_cls.validate_process(process_stage_app_obj=process_stage_app_obj, opp_id=None)

                call_task_background(
                    my_task=task_active_delivery_from_lease_order,
                    **{'lease_order_id': str(obj.id), 'process_id': process_id}
                )

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
