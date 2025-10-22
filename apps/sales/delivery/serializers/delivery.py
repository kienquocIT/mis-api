from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.company.utils import CompanyHandler
from apps.core.workflow.tasks import decorator_run_workflow
from apps.shared import AbstractDetailSerializerModel, AbstractCreateSerializerModel, AbstractListSerializerModel, \
    HRMsg, FORMATTING
from apps.shared.translations.base import AttachmentMsg
from ..models import DeliveryConfig, OrderDelivery, OrderDeliverySub, OrderDeliveryProduct, OrderDeliveryAttachment
from ..utils import DeliHandler

__all__ = [
    'OrderDeliveryListSerializer',
    'OrderDeliverySubListSerializer',
    'OrderDeliverySubDetailSerializer',
    'OrderDeliverySubUpdateSerializer',
    'OrderDeliverySubMinimalListSerializer',
    'OrderDeliverySubRecoveryListSerializer',
]


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
        if obj.asset_type:
            if obj.asset_type >= 1:
                return bool(True)
        return bool(False)

    class Meta:
        model = OrderDeliveryProduct
        fields = (
            'id',
            'order',
            'is_promotion',
            'product_data',
            'asset_type',
            'offset_data',
            'tool_data',
            'asset_data',
            'product_quantity',
            'uom_data',
            'tax_data',
            'product_description',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'delivery_data',
            'picked_quantity',
            'is_not_inventory',

            'product_cost',
            'product_depreciation_subtotal',
            'product_depreciation_price',
            'product_depreciation_method',
            'product_depreciation_adjustment',
            'product_depreciation_time',
            'product_depreciation_start_date',
            'product_depreciation_end_date',

            'product_lease_start_date',
            'product_lease_end_date',

            'depreciation_data',
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
    sale_order = serializers.SerializerMethodField()

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

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'title': obj.sale_order.title,
            'code': obj.sale_order.code,
            'customer_data': obj.sale_order.customer_data,
            'contact_data': obj.sale_order.contact_data,
            'date_approved': obj.sale_order.date_approved.date().strftime("%d/%m/%Y")
            if obj.sale_order.date_approved else None,
        } if obj.sale_order else {}

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
            'sale_order',
        )


# PRINT SERIALIZER
class OrderDeliveryProductListPrintSerializer(serializers.ModelSerializer):
    product_data = serializers.SerializerMethodField()
    product_description = serializers.SerializerMethodField()
    is_not_inventory = serializers.SerializerMethodField()
    product_subtotal = serializers.SerializerMethodField()
    product_subtotal_after_tax = serializers.SerializerMethodField()

    @classmethod
    def get_product_data(cls, obj):
        return {
            'id': str(obj.product_id),
            'title': obj.product.title,
            'code': obj.product.code,
            'avatar_img': obj.product.avatar_img.url if obj.product.avatar_img else None
        } if obj.product else {}

    @classmethod
    def get_product_description(cls, obj):
        return obj.product_description if obj.product_description else (obj.product.description if obj.product else '')

    @classmethod
    def get_is_not_inventory(cls, obj):
        if obj.product.product_choice:
            if 1 in obj.product.product_choice:
                return bool(True)
        if obj.asset_type:
            if obj.asset_type >= 1:
                return bool(True)
        return bool(False)

    @classmethod
    def get_product_subtotal(cls, obj):
        value = obj.product_cost * obj.picked_quantity
        return CompanyHandler.parse_currency(obj=obj, value=value)

    @classmethod
    def get_product_subtotal_after_tax(cls, obj):
        subtotal = obj.product_cost * obj.picked_quantity
        tax = subtotal * obj.tax_data.get('rate', 0) / 100
        value = subtotal + tax
        return CompanyHandler.parse_currency(obj=obj, value=value)

    class Meta:
        model = OrderDeliveryProduct
        fields = (
            'id',
            'order',
            'is_promotion',
            'product_data',
            'asset_type',
            'offset_data',
            'tool_data',
            'asset_data',
            'product_quantity',
            'uom_data',
            'tax_data',
            'product_description',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'delivery_data',
            'picked_quantity',
            'is_not_inventory',

            'product_cost',
            'product_subtotal',
            'product_subtotal_after_tax',

            'product_depreciation_subtotal',
            'product_depreciation_price',
            'product_depreciation_method',
            'product_depreciation_adjustment',
            'product_depreciation_time',
            'product_depreciation_start_date',
            'product_depreciation_end_date',

            'product_lease_start_date',
            'product_lease_end_date',

            'depreciation_data',
        )


class OrderDeliverySubPrintSerializer(AbstractDetailSerializerModel):
    products = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    sale_order = serializers.SerializerMethodField()
    estimated_delivery_date_print = serializers.SerializerMethodField()
    actual_delivery_date_print = serializers.SerializerMethodField()
    pretax_amount = serializers.SerializerMethodField()
    pretax_amount_word = serializers.SerializerMethodField()
    tax_amount = serializers.SerializerMethodField()
    tax_amount_word = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    total_amount_word = serializers.SerializerMethodField()

    @classmethod
    def get_products(cls, obj):
        prod = OrderDeliveryProductListPrintSerializer(
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

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'title': obj.sale_order.title,
            'code': obj.sale_order.code,
            'customer_data': obj.sale_order.customer_data,
            'contact_data': obj.sale_order.contact_data,
            'date_approved': obj.sale_order.date_approved.date().strftime("%d/%m/%Y")
            if obj.sale_order.date_approved else None,
        } if obj.sale_order else {}

    @classmethod
    def get_estimated_delivery_date_print(cls, obj):
        return obj.estimated_delivery_date.date().strftime("%d/%m/%Y") if obj.estimated_delivery_date else None

    @classmethod
    def get_actual_delivery_date_print(cls, obj):
        return obj.actual_delivery_date.date().strftime("%d/%m/%Y") if obj.actual_delivery_date else None

    @classmethod
    def get_pretax_amount(cls, obj):
        pretax = 0
        for delivery_product in obj.delivery_product_delivery_sub.all():
            subtotal = delivery_product.product_cost * delivery_product.picked_quantity
            pretax += subtotal
        return CompanyHandler.parse_currency(obj=obj, value=pretax)

    @classmethod
    def get_pretax_amount_word(cls, obj):
        return FORMATTING.number_to_vietnamese(
            number=OrderDeliverySubPrintSerializer.get_pretax_amount(obj=obj)
        ).capitalize()

    @classmethod
    def get_tax_amount(cls, obj):
        tax = 0
        for delivery_product in obj.delivery_product_delivery_sub.all():
            subtotal = delivery_product.product_cost * delivery_product.picked_quantity
            tax += subtotal * delivery_product.tax_data.get('rate', 0) / 100
        return CompanyHandler.parse_currency(obj=obj, value=tax)

    @classmethod
    def get_tax_amount_word(cls, obj):
        return FORMATTING.number_to_vietnamese(
            number=OrderDeliverySubPrintSerializer.get_tax_amount(obj=obj)
        ).capitalize()

    @classmethod
    def get_total_amount(cls, obj):
        pretax = 0
        tax = 0
        for delivery_product in obj.delivery_product_delivery_sub.all():
            subtotal = delivery_product.product_cost * delivery_product.picked_quantity
            pretax += subtotal
            tax += subtotal * delivery_product.tax_data.get('rate', 0) / 100
        value = pretax + tax
        return CompanyHandler.parse_currency(obj=obj, value=value)

    @classmethod
    def get_total_amount_word(cls, obj):
        return FORMATTING.number_to_vietnamese(
            number=OrderDeliverySubPrintSerializer.get_total_amount(obj=obj)
        ).capitalize()

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
            'estimated_delivery_date_print',
            'actual_delivery_date_print',
            'customer_data',
            'contact_data',
            'config_at_that_point',
            'attachments',
            'delivery_logistic',
            'workflow_runtime_id',
            'employee_inherit',
            'sale_order',
            'pretax_amount',
            'pretax_amount_word',
            'tax_amount',
            'tax_amount_word',
            'total_amount',
            'total_amount_word',
        )


class ProductDeliveryUpdateSerializer(serializers.Serializer):  # noqa
    product_id = serializers.UUIDField()
    done = serializers.IntegerField(min_value=1)
    delivery_data = serializers.JSONField(default=list)
    tool_data = serializers.JSONField(default=list)
    asset_data = serializers.JSONField(default=list)
    product_depreciation_start_date = serializers.CharField(required=False, allow_null=True)
    product_lease_start_date = serializers.CharField(required=False, allow_null=True)
    depreciation_data = serializers.JSONField(default=list)
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
                target = product_done[obj_key]
                if 1 in obj.product.product_choice or sub.lease_order_data:
                    # Kiểm tra product id và order trùng với product update ko
                    obj.picked_quantity = target.get('picked_num', 0)
                    obj.delivery_data = target.get('delivery_data', [])
                    obj.tool_data = target.get('tool_data', [])
                    obj.asset_data = target.get('asset_data', [])
                    obj.product_depreciation_start_date = target.get('product_depreciation_start_date', None)
                    obj.product_lease_start_date = target.get('product_lease_start_date', None)
                    obj.depreciation_data = target.get('depreciation_data', [])
                    obj.quantity_remain_recovery = target.get('picked_num', 0)

                    if 'is_picking' in config and 'is_partial_ship' in config:
                        if (config['is_picking'] and config['is_partial_ship'] and
                                obj.picked_quantity > obj.remaining_quantity):
                            raise serializers.ValidationError(
                                {'detail': _(
                                    'Products must have picked quantity equal to or less than remaining quantity'
                                )}
                            )
                else:
                    obj.picked_quantity = target.get('picked_num', 0)
                # Sau khi update sẽ chạy các func trong save()
                obj.save(update_fields=[
                    'picked_quantity', 'delivery_data',
                    'tool_data', 'asset_data',
                    'product_depreciation_start_date', 'product_lease_start_date',
                    'depreciation_data', 'quantity_remain_recovery',
                ])
        return True

    # none_picking_many_delivery
    @classmethod
    def config_two_four(cls, instance, product_done, next_association_id, next_node_collab_id, config):
        # cho phep giao nhieu lan and tạo sub mới
        cls.update_prod(instance, product_done, config)
        instance.date_done = timezone.now()
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
            product_done[prod_key]['tool_data'] = item.get('tool_data', [])
            product_done[prod_key]['asset_data'] = item.get('asset_data', [])
            product_done[prod_key]['product_depreciation_start_date'] = item.get(
                'product_depreciation_start_date', None
            )
            product_done[prod_key]['product_lease_start_date'] = item.get('product_lease_start_date', None)
            product_done[prod_key]['depreciation_data'] = item.get('depreciation_data', [])
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
                'tool_data': [{
                    "product_id": delivery_tool.product_id,
                    "product_data": delivery_tool.product_data,
                    "tool_id": delivery_tool.tool_id,
                    "tool_data": delivery_tool.tool_data,
                    "uom_time_id": delivery_tool.uom_time_id,
                    "uom_time_data": delivery_tool.uom_time_data,
                    "product_quantity": delivery_tool.product_quantity,
                    "product_quantity_time": delivery_tool.product_quantity_time,
                    "product_depreciation_subtotal": delivery_tool.product_depreciation_subtotal,
                    "product_depreciation_price": delivery_tool.product_depreciation_price,
                    "product_depreciation_method": delivery_tool.product_depreciation_method,
                    "product_depreciation_adjustment": delivery_tool.product_depreciation_adjustment,
                    "product_depreciation_time": delivery_tool.product_depreciation_time,
                    "product_depreciation_start_date": delivery_tool.product_depreciation_start_date,
                    "product_depreciation_end_date": delivery_tool.product_depreciation_end_date,
                    "product_lease_start_date": delivery_tool.product_lease_start_date,
                    "product_lease_end_date": delivery_tool.product_lease_end_date,
                    "depreciation_data": delivery_tool.depreciation_data,
                    "quantity_remain_recovery": delivery_tool.quantity_remain_recovery,
                } for delivery_tool in deli_product.delivery_pt_delivery_product.filter(
                    quantity_remain_recovery__gt=0
                )],
                'asset_data': [{
                    "product_id": delivery_asset.product_id,
                    "product_data": delivery_asset.product_data,
                    "asset_id": delivery_asset.asset_id,
                    "asset_data": delivery_asset.asset_data,
                    "uom_time_id": delivery_asset.uom_time_id,
                    "uom_time_data": delivery_asset.uom_time_data,
                    "product_quantity": delivery_asset.product_quantity,
                    "product_quantity_time": delivery_asset.product_quantity_time,
                    "product_depreciation_subtotal": delivery_asset.product_depreciation_subtotal,
                    "product_depreciation_price": delivery_asset.product_depreciation_price,
                    "product_depreciation_method": delivery_asset.product_depreciation_method,
                    "product_depreciation_adjustment": delivery_asset.product_depreciation_adjustment,
                    "product_depreciation_time": delivery_asset.product_depreciation_time,
                    "product_depreciation_start_date": delivery_asset.product_depreciation_start_date,
                    "product_depreciation_end_date": delivery_asset.product_depreciation_end_date,
                    "product_lease_start_date": delivery_asset.product_lease_start_date,
                    "product_lease_end_date": delivery_asset.product_lease_end_date,
                    "depreciation_data": delivery_asset.depreciation_data,
                    "quantity_remain_recovery": delivery_asset.quantity_remain_recovery,
                } for delivery_asset in deli_product.delivery_pa_delivery_product.filter(
                    quantity_remain_recovery__gt=0
                )],
                'uom_id': deli_product.uom_id,
                'uom_data': deli_product.uom_data,
                'product_quantity': deli_product.product_quantity,
                'product_quantity_time': deli_product.product_quantity_time,
                'product_cost': deli_product.product_cost,
                'product_subtotal_cost': 0,
                'quantity_delivered': deli_product.picked_quantity,
                'quantity_remain_recovery': deli_product.quantity_remain_recovery,
                'quantity_recovery': 0,
                'delivery_data': deli_product.delivery_data,
            }
            for deli_product in obj.delivery_product_delivery_sub.filter(quantity_remain_recovery__gt=0)
        ]


class DeliveryProductLeaseListSerializer(serializers.ModelSerializer):
    tool_asset_data = serializers.SerializerMethodField()

    class Meta:
        model = OrderDeliveryProduct
        fields = (
            'id',
            'tool_asset_data',
        )

    @classmethod
    def get_tool_asset_data(cls, obj):
        result = []
        delivery_tools = obj.delivery_pt_delivery_product.all()
        if delivery_tools:
            for delivery_tool in delivery_tools:
                if delivery_tool.tool:
                    data_custom = delivery_tool.tool_data
                    data_custom.update({
                        'id': delivery_tool.tool_id,
                        'asset_type': 2,
                        'offset_data': obj.offset_data,
                        'tool_data': {
                            'id': delivery_tool.tool_id, 'title': delivery_tool.tool.title
                        },
                        'product_cost': delivery_tool.tool.unit_price,
                        'product_lease_start_date': delivery_tool.product_lease_start_date,
                        'product_lease_end_date': delivery_tool.product_lease_end_date,
                        'product_depreciation_time': delivery_tool.product_depreciation_time,
                        'status': delivery_tool.tool.status,
                        'quantity': delivery_tool.tool.quantity,
                        'quantity_leased': delivery_tool.tool.quantity_leased,
                    })
                    result.append(data_custom)

        delivery_assets = obj.delivery_pa_delivery_product.all()
        if delivery_assets:
            for delivery_asset in delivery_assets:
                if delivery_asset.asset:
                    data_custom = delivery_asset.asset_data
                    data_custom.update({
                        'id': delivery_asset.asset_id,
                        'asset_type': 3,
                        'offset_data': obj.offset_data,
                        'asset_data': {
                            'id': delivery_asset.asset_id, 'title': delivery_asset.asset.title
                        },
                        'product_cost': delivery_asset.asset.original_cost,
                        'product_lease_start_date': delivery_asset.product_lease_start_date,
                        'product_lease_end_date': delivery_asset.product_lease_end_date,
                        'product_depreciation_time': delivery_asset.product_depreciation_time,
                        'status': delivery_asset.asset.status,
                        'quantity': 1,
                        'quantity_leased': 1 if delivery_asset.asset.status == 2 else 0,
                    })
                    result.append(data_custom)

        return result
