from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.shared import AbstractDetailSerializerModel, AbstractCreateSerializerModel, AbstractListSerializerModel, HRMsg
from apps.shared.translations.base import AttachmentMsg
from ..models import DeliveryConfig, OrderDelivery, OrderDeliverySub, OrderDeliveryProduct, OrderDeliveryAttachment, \
    OrderDeliveryProductLeased
from ..utils import DeliHandler

__all__ = ['OrderDeliveryListSerializer', 'OrderDeliverySubListSerializer', 'OrderDeliverySubDetailSerializer',
           'OrderDeliverySubUpdateSerializer']


def handle_attach_file(instance, attachment_result):
    if attachment_result and isinstance(attachment_result, dict):
        relate_app = Application.objects.filter(id="1373e903-909c-4b77-9957-8bcf97e8d6d3").first()
        if relate_app:
            state = OrderDeliveryAttachment.resolve_change(
                result=attachment_result, doc_id=instance.id, doc_app=relate_app,
            )
            if state:
                return True
        raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
    return True


class OrderDeliveryProductListSerializer(serializers.ModelSerializer):
    is_not_inventory = serializers.SerializerMethodField()

    @classmethod
    def get_is_not_inventory(cls, obj):
        if obj.product.product_choice:
            if 1 in obj.product.product_choice:
                return bool(True)
        if isinstance(obj.offset_data, dict):
            if obj.offset_data:
                return bool(True)
        return bool(False)

    class Meta:
        model = OrderDeliveryProduct
        fields = (
            'id',
            'order',
            'is_promotion',
            'product_data',
            'offset_data',
            'product_quantity',
            'product_quantity_new',
            'remaining_quantity_new',
            'product_quantity_leased',
            'product_quantity_leased_data',
            'uom_data',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'delivery_data',
            'picked_quantity',
            'is_not_inventory'
        )


class OrderDeliverySubListSerializer(AbstractListSerializerModel):
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            "id": obj.employee_inherit_id,
            "full_name": f'{obj.employee_inherit.last_name} {obj.employee_inherit.first_name}'
        } if obj.employee_inherit else {}

    class Meta:
        model = OrderDeliverySub
        fields = (
            'id',
            'code',
            'sale_order_data',
            'lease_order_data',
            'date_created',
            'estimated_delivery_date',
            'actual_delivery_date',
            'employee_inherit',
            'state',
        )


class OrderDeliverySubMinimalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDeliverySub
        fields = (
            'id',
            'code',
            'date_created',
        )


class OrderDeliveryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDelivery
        fields = (
            'id',
            'title',
            'code',
            'sale_order_data',
            'state',
            'is_active',
        )


class OrderDeliverySubDetailSerializer(AbstractDetailSerializerModel):
    products = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_products(cls, obj):
        prod = OrderDeliveryProductListSerializer(
            obj.delivery_product_delivery_sub.all(),
            many=True,
        ).data
        return prod

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                "id": str(obj.employee_inherit_id),
                "full_name": f'{obj.employee_inherit.last_name} {obj.employee_inherit.first_name}'
            }
        return {}

    @classmethod
    def get_attachments(cls, obj):
        return [file_obj.get_detail() for file_obj in obj.attachment_m2m.all()]

    class Meta:
        model = OrderDeliverySub
        fields = (
            'order_delivery',
            'id',
            'remarks',
            'times',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'is_updated',
            'products',
            'state',
            'code',
            'sale_order_data',
            'lease_order_data',
            'estimated_delivery_date',
            'actual_delivery_date',
            'customer_data',
            'contact_data',
            'config_at_that_point',
            'attachments',
            'delivery_logistic',
            'workflow_runtime_id',
            'employee_inherit',
        )


class ProductDeliveryUpdateSerializer(serializers.Serializer):  # noqa
    product_id = serializers.UUIDField()
    done = serializers.IntegerField(min_value=1)
    delivery_data = serializers.JSONField(allow_null=True)
    product_quantity_leased_data = serializers.JSONField(allow_null=True, required=False)
    order = serializers.IntegerField(min_value=1)


class OrderDeliverySubUpdateSerializer(AbstractCreateSerializerModel):
    products = ProductDeliveryUpdateSerializer(many=True)
    employee_inherit_id = serializers.UUIDField()
    estimated_delivery_date = serializers.DateTimeField()
    actual_delivery_date = serializers.DateTimeField()

    class Meta:
        model = OrderDeliverySub
        fields = (
            'order_delivery',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'is_updated',
            'state',
            'estimated_delivery_date',
            'actual_delivery_date',
            'remarks',
            'products',
            'attachments',
            'delivery_logistic',
            'employee_inherit_id'
        )

    @classmethod
    def validate_state(cls, value):
        if value < 2:
            return value
        raise serializers.ValidationError({'State': _('Can not update when status is Done!')})

    def validate_attachments(self, attrs):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = OrderDeliveryAttachment.valid_change(
                current_ids=attrs, employee_id=user.employee_current_id, doc_id=self.instance.id
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    def validate(self, validate_data):
        product_data = validate_data.get('products', [])
        for product in product_data:
            deli_product = OrderDeliveryProduct.objects.filter_current(
                delivery_sub=self.instance, product_id=product.get('product_id', None)
            ).first()
            if deli_product:
                deli_quantity = product.get('done', 0)
                if deli_quantity > deli_product.remaining_quantity:
                    raise serializers.ValidationError({
                        'detail': _('Products must have picked quantity equal to or less than remaining quantity')
                    })
        return validate_data

    @classmethod
    def update_self_info(cls, instance, validated_data):
        if 'estimated_delivery_date' in validated_data:
            instance.estimated_delivery_date = validated_data['estimated_delivery_date']
        if 'actual_delivery_date' in validated_data:
            instance.actual_delivery_date = validated_data['actual_delivery_date']
        if 'remarks' in validated_data:
            instance.remarks = validated_data['remarks']
        if 'delivery_logistic' in validated_data and validated_data['delivery_logistic']:
            instance.delivery_logistic = validated_data['delivery_logistic']
        if 'system_status' in validated_data:
            instance.system_status = validated_data['system_status']

    @classmethod
    def update_prod(cls, sub, product_done, config):
        for obj in OrderDeliveryProduct.objects.filter_current(
                delivery_sub=sub
        ):
            obj_key = str(obj.product_id) + "___" + str(obj.order)
            if obj_key in product_done:
                if 1 in obj.product.product_choice or sub.lease_order_data:
                    # kiểm tra product id và order trùng với product update ko
                    delivery_data = product_done[obj_key]['delivery_data']  # list format
                    obj.picked_quantity = product_done[obj_key]['picked_num']
                    obj.delivery_data = delivery_data
                    obj.product_quantity_leased_data = product_done[obj_key]['product_quantity_leased_data']

                    if (config['is_picking'] and config['is_partial_ship'] and
                            obj.picked_quantity > obj.remaining_quantity):
                        raise serializers.ValidationError(
                            {'detail': _('Products must have picked quantity equal to or less than remaining quantity')}
                        )
                else:
                    obj.picked_quantity = product_done[obj_key]['picked_num']
                # sau khi update sẽ chạy các func trong save()
                obj.save(update_fields=['picked_quantity', 'delivery_data', 'product_quantity_leased_data'])

                # update OrderDeliveryProductLeased
                # sau khi update sẽ chạy các func trong save()
                # obj.delivery_product_leased_delivery_product.all().delete()
                # OrderDeliveryProductLeased.objects.bulk_create([OrderDeliveryProductLeased(
                #     delivery_product_id=obj.id, tenant_id=obj.tenant_id,
                #     company_id=obj.company_id, **product_leased,
                # ) for product_leased in obj.product_quantity_leased_data])
        return True

    # none_picking_many_delivery
    @classmethod
    def config_two_four(cls, instance, product_done, next_association_id, next_node_collab_id, config):
        # cho phep giao nhieu lan and tạo sub mới
        cls.update_prod(instance, product_done, config)
        instance.date_done = timezone.now()
        # instance.state = 2
        instance.is_updated = True
        instance.next_association_id = next_association_id
        instance.next_node_collab_id = next_node_collab_id
        instance.save(
            update_fields=[
                'date_done', 'state', 'is_updated', 'estimated_delivery_date',
                'actual_delivery_date', 'remarks', 'attachments', 'delivery_logistic',
                'system_status', 'next_association_id', 'next_node_collab_id',
            ]
        )
        return True

    @classmethod
    def update_instance_and_product(cls, instance, validated_data, product_done, config):
        next_association_id = validated_data.get('next_association_id', None)
        next_node_collab_id = validated_data.get('next_node_collab_id', None)
        if len(product_done) > 0:
            # update instance info
            cls.update_self_info(instance, validated_data)
            # if product_done
            # to do check if not submit product so update common info only
            try:
                with transaction.atomic():
                    cls.config_two_four(
                        instance=instance,
                        product_done=product_done,
                        next_association_id=next_association_id,
                        next_node_collab_id=next_node_collab_id,
                        config=config
                    )
            except Exception as err:
                print(err)
                raise err
        else:
            if 'products' in validated_data:
                del validated_data['products']
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()
            instance.order_delivery.employee_inherit = instance.employee_inherit
            instance.order_delivery.save()
        return True

    @decorator_run_workflow
    def update(self, instance, validated_data):
        DeliHandler.check_update_prod_and_emp(instance, validated_data)
        validated_product = validated_data.get('products', [])
        attachments = validated_data.pop('attachments', None)
        config = instance.config_at_that_point
        if not config:
            get_config = DeliveryConfig.objects.get(company_id=instance.company_id)
            config = {
                "is_picking": get_config.is_picking,
                "is_partial_ship": get_config.is_partial_ship
            }
        product_done = {}
        total_done = 0
        for item in validated_product:
            prod_key = str(item['product_id']) + "___" + str(item['order'])
            total_done += item['done']
            product_done[prod_key] = {}
            product_done[prod_key]['picked_num'] = item.get('done', 0)
            product_done[prod_key]['delivery_data'] = item.get('delivery_data', [])
            product_done[prod_key]['product_quantity_leased_data'] = item.get('product_quantity_leased_data', [])
        instance.save()

        # update instance and product
        self.update_instance_and_product(
            instance=instance,
            validated_data=validated_data,
            product_done=product_done,
            config=config,
        )

        if attachments is not None:
            handle_attach_file(instance, attachments)

        return instance


class OrderDeliverySubRecoveryListSerializer(serializers.ModelSerializer):
    delivery_id = serializers.SerializerMethodField()
    delivery_data = serializers.SerializerMethodField()
    delivery_product_data = serializers.SerializerMethodField()

    class Meta:
        model = OrderDeliverySub
        fields = (
            'delivery_id',
            'delivery_data',
            'delivery_product_data',
        )

    @classmethod
    def get_delivery_id(cls, obj):
        return obj.id

    @classmethod
    def get_delivery_data(cls, obj):
        return {
            'id': obj.id,
            'code': obj.code,
            'actual_delivery_date': obj.actual_delivery_date.date(),
        }

    @classmethod
    def get_delivery_product_data(cls, obj):
        return [
            {
                'product_id': deli_product.product_id,
                'product_data': deli_product.product_data,
                'asset_type': deli_product.asset_type,
                'offset_id': deli_product.offset_id,
                'offset_data': deli_product.offset_data,
                'uom_id': deli_product.uom_id,
                'uom_data': deli_product.uom_data,
                'product_quantity': deli_product.product_quantity,
                'product_quantity_time': deli_product.product_quantity_time,
                'product_unit_price': deli_product.product_unit_price,
                'product_subtotal_price': 0,
                'quantity_ordered': deli_product.delivery_quantity,
                'quantity_delivered': deli_product.picked_quantity,
                'quantity_recovered': 0,
                'quantity_recovery': 0,
                'delivery_data': deli_product.delivery_data,

                'product_depreciation_subtotal': deli_product.product_depreciation_subtotal,
                'product_depreciation_price': deli_product.product_depreciation_price,
                'product_depreciation_method': deli_product.product_depreciation_method,
                'product_depreciation_adjustment': deli_product.product_depreciation_adjustment,
                'product_depreciation_time': deli_product.product_depreciation_time,
                'product_depreciation_start_date': obj.actual_delivery_date.date(),
                'product_depreciation_end_date': deli_product.product_depreciation_end_date,

                'product_lease_start_date': obj.actual_delivery_date.date(),
            }
            for deli_product in obj.delivery_product_delivery_sub.all()
        ]
