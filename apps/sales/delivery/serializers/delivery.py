from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from ..models import DeliveryConfig, OrderDelivery, OrderDeliverySub, OrderDeliveryProduct

__all__ = ['OrderDeliveryListSerializer', 'OrderDeliveryDetailSerializer', 'OrderDeliveryUpdateSerializer']


class OrderDeliveryProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDeliveryProduct
        fields = (
            'id',
            'product_data',
            'uom_data',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'delivery_data'
        )


class OrderDeliverySubListSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    @classmethod
    def get_products(cls, obj):
        prod = OrderDeliveryProductListSerializer(
            obj.orderdeliveryproduct_set.all(),
            many=True,
        ).data
        return prod

    class Meta:
        model = OrderDeliverySub
        fields = (
            'id',
            'date_done',
            'previous_step',
            'times',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'delivery_data',
            'products',
        )


class OrderDeliveryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDelivery
        fields = (
            'id',
            'title',
            'code',
            'sale_order_id',
            'sale_order_data',
            'from_picking_area',
            'customer_id',
            'customer_data',
            'contact_id',
            'contact_data',
            'estimated_delivery_date',
            'actual_delivery_date',
            'kind_pickup',
            'state',
            'remarks',
            'sub',
            'delivery_option',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'delivery_data',
            'date_created', 'date_modified', 'is_active'
        )


class OrderDeliveryDetailSerializer(serializers.ModelSerializer):
    sub = OrderDeliverySubListSerializer()

    class Meta:
        model = OrderDelivery
        fields = (
            'id',
            'title',
            'code',
            'sale_order_id',
            'sale_order_data',
            'from_picking_area',
            'customer_id',
            'customer_data',
            'contact_id',
            'contact_data',
            'estimated_delivery_date',
            'actual_delivery_date',
            'kind_pickup',
            'state',
            'remarks',
            'delivery_option',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'delivery_data',
            'sub',
            'date_created', 'date_modified', 'is_active'
        )


class ProductDeliveryUpdateSerializer(serializers.Serializer):  # noqa
    product_id = serializers.UUIDField()
    done = serializers.IntegerField(min_value=1)
    delivery_data = serializers.JSONField(allow_null=True)


class OrderDeliveryUpdateSerializer(serializers.ModelSerializer):
    products = ProductDeliveryUpdateSerializer(many=True)
    sale_order_id = serializers.UUIDField()
    delivery_option = serializers.IntegerField(min_value=0)

    class Meta:
        model = OrderDelivery
        fields = (
            'sale_order_id',
            'estimated_delivery_date',
            'actual_delivery_date',
            'remarks',
            'delivery_option',
            'kind_pickup',
            'sub',
            'products',
            'date_created', 'date_modified', 'is_active'
        )

    @classmethod
    def update_self_info(cls, instance, validated_data, is_partial):
        instance.estimated_delivery_date = validated_data['estimated_delivery_date']
        instance.actual_delivery_date = validated_data['actual_delivery_date']
        instance.remarks = validated_data['remarks']
        instance.delivery_option = validated_data['delivery_option']
        instance.kind_pickup = 1 if is_partial else 0
        instance.save(
            update_fields=['estimated_delivery_date', 'actual_delivery_date', 'remarks', 'delivery_option',
                           'kind_pickup']
        )

    @classmethod
    def update_prod(cls, sub, product_done):
        # update to current product list of current sub
        for obj in OrderDeliveryProduct.objects.filter_current(
                delivery_sub=sub
        ):
            if str(obj.product_id) in product_done:
                obj.picked_quantity = product_done[str(obj.product_id)]['picked_num']
                obj.delivery_data = product_done[str(obj.product_id)]['delivery_data']
                obj.save()

    @classmethod
    def create_prod(cls, new_sub, instance):
        # update to current product list of current sub
        prod_arr = []
        for obj in OrderDeliveryProduct.objects.filter_current(
                delivery_sub=instance.sub
        ):
            new_prod = OrderDeliveryProduct(
                delivery_sub=new_sub,
                product=obj.product,
                uom=obj.uom,
                delivery_quantity=obj.delivery_quantity,
                delivered_quantity_before=obj.picked_quantity,
                remaining_quantity=obj.delivery_quantity - obj.picked_quantity,
                ready_quantity=obj.delivery_quantity,
                picked_quantity=0
            )
            new_prod.before_save()
            prod_arr.append(new_prod)
        OrderDeliveryProduct.objects.bulk_create(prod_arr)

    @classmethod
    def create_new_sub(cls, instance, total_done):
        sub = instance.sub
        new_sub = OrderDeliverySub.objects.create(
            company_id=instance.company_id,
            tenant_id=instance.tenant_id,
            order_delivery=instance,
            date_done=None,
            previous_step=sub,
            times=sub.times + 1,
            delivery_quantity=sub.delivery_quantity,
            delivered_quantity_before=total_done,
            remaining_quantity=sub.delivery_quantity - total_done,
            ready_quantity=sub.ready_quantity,
            delivery_data=None
        )
        return new_sub

    @classmethod
    def config_one(cls, instance, total_done, product_done):
        sub = instance.sub
        if sub.remaining_quantity == total_done:
            # update product and sub date_done
            cls.update_prod(sub, product_done)
            sub.date_done = timezone.now()
            sub.save(update_fields=['date_done'])
            instance.state = 3
            instance.save()
        else:
            raise serializers.ValidationError(
                {
                    'products': _('Done quantity not equal remain quantity!')
                }
            )

    @classmethod
    def config_two(cls, instance, total_done, product_done):
        try:
            with transaction.atomic():
                sub = instance.sub
                # cho phep giao nhieu lan and tạo sub mới
                cls.update_prod(sub, product_done)
                sub.date_done = timezone.now()
                sub.save()
                if sub.remaining_quantity > total_done:
                    new_sub = cls.create_new_sub(instance, total_done)
                    cls.create_prod(new_sub, instance)
                    instance.sub = new_sub
                    instance.save(update_fields=['sub'])
                elif sub.remaining_quantity == total_done:
                    instance.state = 3
                    instance.save(update_fields=['state'])
        except Exception as err:
            print(err)

    @classmethod
    def config_three(cls, instance, total_done, product_done):
        if hasattr(instance, 'sub'):
            sub = instance.sub
            if sub:
                if sub.remaining_quantity == total_done:
                    cls.update_prod(sub, product_done)
                    sub.date_done = timezone.now()
                    instance.state = 3
                    instance.save()
                else:
                    raise serializers.ValidationError(
                        {
                            'products': _('Done quantity not equal remain quantity!')
                        }
                    )
            raise serializers.ValidationError(
                {
                    'products': _('Picking still in progress!')
                }
            )

    @classmethod
    def config_four(cls, instance, total_done, product_done):
        try:
            with transaction.atomic():
                sub = instance.sub
                cls.update_prod(sub, product_done)
                if sub.remaining_quantity > total_done:
                    new_sub = cls.create_new_sub(instance, total_done)
                    cls.create_prod(new_sub, instance)
                    instance.state = 1
                    instance.sub = new_sub
                    instance.save(update_fields=['state', 'sub'])
                elif sub.remaining_quantity == total_done:
                    sub.date_done = timezone.now()
                    sub.delivered_quantity_before += total_done
                    sub.remaining_quantity = sub.delivery_quantity - sub.delivered_quantity_before
                    sub.save(
                        update_fields=['date_done', 'ready_quantity', 'delivery_quantity_before', 'remaining_quantity']
                    )
                    instance.state = 3
                    instance.save(update_fields=['state'])
        except Exception as err:
            print(err)

    def update(self, instance, validated_data):
        # declare default object
        prod = validated_data['products']
        config = DeliveryConfig.objects.get(company_id=instance.company_id)
        is_picking = config.is_picking
        is_partial = config.is_partial_ship
        product_done = {}
        total_done = 0
        for item in prod:
            product_done[str(item['product_id'])] = {}
            total_done += item['done']
            product_done[str(item['product_id'])]['picked_num'] = item['done']
            product_done[str(item['product_id'])]['delivery_data'] = item['delivery_data']

        # update instance info
        self.update_self_info(instance, validated_data, is_partial)
        if not is_partial and not is_picking:
            # config 1
            self.config_one(instance, total_done, product_done)
        elif is_partial and not is_picking:
            # config 2
            self.config_two(instance, total_done, product_done)
        elif is_picking and not is_partial:
            # config 3
            self.config_three(instance, total_done, product_done)
        else:
            # config 4
            self.config_four(instance, total_done, product_done)

        return instance
