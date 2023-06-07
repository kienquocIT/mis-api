from django.db import transaction
from rest_framework import serializers
import django.utils
from django.utils.translation import gettext_lazy as _

from ..models import (
    OrderDeliverySub, OrderDeliveryProduct, OrderPicking, OrderPickingProduct, OrderPickingSub, OrderDelivery
)


__all__ = [
    'OrderPickingListSerializer',
    'OrderPickingDetailSerializer',
    'OrderPickingProductListSerializer',
    'OrderPickingSubListSerializer',
    'OrderPickingUpdateSerializer',
]


class OrderPickingProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPickingProduct
        fields = (
            'id',
            'product_data',
            'uom_data',
            'pickup_quantity',
            'picked_quantity_before',
            'remaining_quantity',
            'picked_quantity',
        )


class OrderPickingSubListSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    @classmethod
    def get_products(cls, obj):
        return OrderPickingProductListSerializer(
            obj.orderpickingproduct_set.all(),
            many=True,
        ).data

    class Meta:
        model = OrderPickingSub
        fields = (
            'id',
            'date_done',
            'previous_step',
            'times',
            'pickup_quantity',
            'picked_quantity_before',
            'remaining_quantity',
            'picked_quantity',
            'pickup_data',
            'products',
        )


class OrderPickingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPicking
        fields = (
            'id',
            'title',
            'code',
            'sale_order_id',
            'sale_order_data',
            'ware_house_id',
            'ware_house_data',
            'estimated_delivery_date',
            'state',
            'remarks',
            'delivery_option',
            'pickup_quantity',
            'picked_quantity_before',
            'remaining_quantity',
            'picked_quantity',
            'pickup_data',
            'sub',
            'date_created', 'date_modified', 'is_active'
        )


class OrderPickingDetailSerializer(serializers.ModelSerializer):
    sub = OrderPickingSubListSerializer()

    class Meta:
        model = OrderPicking
        fields = (
            'id',
            'code',
            'sale_order_id',
            'sale_order_data',
            'ware_house_id',
            'ware_house_data',
            'estimated_delivery_date',
            'state',
            'remarks',
            'to_location',
            'delivery_option',
            'pickup_quantity',
            'picked_quantity_before',
            'remaining_quantity',
            'picked_quantity',
            'pickup_data',
            'sub',
            'date_created', 'date_modified', 'is_active'
        )


class ProductPickingUpdateSerializer(serializers.Serializer):  # noqa
    product_id = serializers.UUIDField()
    done = serializers.IntegerField(min_value=1)


class OrderPickingUpdateSerializer(serializers.ModelSerializer):
    products = ProductPickingUpdateSerializer(many=True)
    sale_order_id = serializers.UUIDField()
    delivery_option = serializers.IntegerField(min_value=0)

    @staticmethod
    def update_delivery_sub(instance, total, product_update):
        delivery = OrderDelivery.objects.filter(sale_order_id=instance.sale_order_id).first()
        delivery_sub = delivery.sub
        if not delivery_sub:
            delivery_sub = OrderDeliverySub.objects.create(
                order_delivery=delivery,
                date_done=django.utils.timezone.now(),
                previous_step=None,
                times=1,
                delivery_quantity=instance.pickup_quantity,
                delivered_quantity_before=0,
                remaining_quantity=instance.pickup_quantity,
                ready_quantity=0,
                delivery_data=None
            )
            delivery.sub = delivery_sub
        obj_list_id = []
        obj_update = []
        for key, value in product_update.items():
            delivery_prod = OrderDeliveryProduct.objects.filter(
                delivery_sub=delivery_sub,
                product_id=key
            )
            if delivery_prod.exists():
                delivery_prod.ready_quantity += value
                obj_update.append(delivery_prod)
            else:
                obj_list_id.append(key)
        OrderDeliveryProduct.objects.bulk_update(obj_update, fields=['ready_quantity'])
        create_new_prod = []
        for item in OrderPickingProduct.objects.filter(
                product_id__in=obj_list_id,
                picking_sub=instance.sub
        ):
            val_new = OrderDeliveryProduct(
                delivery_sub=delivery_sub,
                product=item.product,
                uom=item.uom,
                delivery_quantity=item.pickup_quantity,
                delivered_quantity_before=0,
                remaining_quantity=item.remaining_quantity,
                ready_quantity=product_update[str(item.product_id)],
                picked_quantity=0,
                delivery_data={}
            )
            val_new.before_save()
            create_new_prod.append(val_new)

        OrderDeliveryProduct.objects.bulk_create(create_new_prod)

        if instance.delivery_option == 1:
            delivery.state = 1
        elif total == instance.sub.remaining_quantity:
            delivery.state = 2
        delivery.estimated_delivery_date = instance.estimated_delivery_date
        delivery.save(update_fields=['state', 'estimated_delivery_date', 'sub'])

    @staticmethod
    def create_new_picking_sub(instance):
        sub = instance.sub
        # create new sub follow by prev sub
        new_sub = OrderPickingSub.objects.create(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            order_picking=instance,
            date_done=None,
            previous_step=sub,
            times=sub.times + 1,
            pickup_quantity=sub.pickup_quantity,
            picked_quantity_before=sub.picked_quantity_before + sub.picked_quantity,
            remaining_quantity=sub.pickup_quantity - (sub.picked_quantity_before + sub.picked_quantity),
            picked_quantity=0,
            pickup_data=sub.pickup_data,
        )
        instance.sub = new_sub
        instance.save(update_fields=['sub'])
        # create prod with new sub id
        obj_new_prod = []
        for obj in OrderPickingProduct.objects.filter_current(
                picking_sub=sub
        ):
            new_item = OrderPickingProduct(
                product_data=obj.product_data,
                uom_data=obj.uom_data,
                uom_id=obj.uom_id,
                pickup_quantity=obj.pickup_quantity,
                picked_quantity_before=obj.picked_quantity_before + obj.picked_quantity,
                remaining_quantity=obj.pickup_quantity - (obj.picked_quantity_before + obj.picked_quantity),
                picked_quantity=0,
                picking_sub=new_sub,
                product_id=obj.product_id
            )
            new_item.before_save()
            obj_new_prod.append(new_item)
        OrderPickingProduct.objects.bulk_create(obj_new_prod)

    @staticmethod
    def isupdate_picking_info(instance, validated_data):
        # update picking info
        picking_obj = instance
        picking_obj.estimated_delivery_date = validated_data['estimated_delivery_date']
        picking_obj.ware_house = validated_data['ware_house']
        picking_obj.to_location = validated_data['to_location']
        picking_obj.remarks = validated_data['remarks']
        picking_obj.save(
            update_fields=['estimated_delivery_date', 'ware_house', 'ware_house_data', 'to_location',
                           'remarks']
        )

    @classmethod
    def update_prod_current_by_sub(cls, instance, prod_update, total_picked):
        pickup_data_temp = {}
        prod_list_by_sub = OrderPickingProduct.objects.filter_current(
            picking_sub=instance.sub
        )
        if instance.delivery_option == 1 or total_picked == instance.sub.remaining_quantity:
            # cho phép delivery nhiều lần or phiếu đã pick đủ
            # update current prod and update delivery prod
            for obj in prod_list_by_sub:
                if str(obj.product_id) in prod_update:
                    # nếu obj có trong list update
                    pickup_data_temp[str(obj.product_id)] = {
                        'remaining_quantity': obj.remaining_quantity,
                        'picked_quantity': prod_update[str(obj.product_id)],
                        'pickup_quantity': obj.pickup_quantity,
                        'picked_quantity_before': obj.picked_quantity_before
                    }
                    obj.picked_quantity = prod_update[str(obj.product_id)]
                    obj.save(update_fields=['picked_quantity'])

            cls.update_delivery_sub(instance, total_picked, prod_update)

        elif instance.delivery_option == 0 and total_picked < instance.sub.remaining_quantity:
            raise serializers.ValidationError(
                {
                    'products': _('Done quantity not equal remain quantity!')
                }
            )
        return pickup_data_temp

    @classmethod
    def update_current_sub(cls, instance, pickup_data, total):
        # update sub after update product
        picking_sub = instance.sub
        picking_sub.date_done = django.utils.timezone.now()
        picking_sub.pickup_data = pickup_data
        picking_sub.picked_quantity = total
        picking_sub.to_location = instance.to_location
        picking_sub.remarks = instance.remarks
        picking_sub.ware_house = instance.ware_house
        picking_sub.save(
            update_fields=['picked_quantity', 'pickup_data', 'ware_house', 'to_location', 'remarks',
                           'date_done']
        )
        if instance.delivery_option == 1 and not total == picking_sub.remaining_quantity:
            # giao hàng nhiều lần
            # update current sub
            # tạo mới sub and tạo mới prod, gán sub cho phiếu picking
            cls.create_new_picking_sub(instance)

        if total == picking_sub.remaining_quantity:
            instance.state = 1
            instance.save(update_fields=['state'])

    def update(self, instance, validated_data):
        picking_obj = instance
        # convert prod to dict
        product_done = {}
        picked_quantity_total = 0
        for item in validated_data['products']:
            picked_quantity_total += item['done']
            product_done[str(item['product_id'])] = item['done']
        try:
            with transaction.atomic():
                # update picking info step 1
                self.isupdate_picking_info(instance, validated_data)

                # update product by sub if partial status true or picked equal remain
                pickup_data = self.update_prod_current_by_sub(instance, product_done, picked_quantity_total)

                # update and tracking current sub
                self.update_current_sub(instance, pickup_data, picked_quantity_total)
        except Exception as err:
            print(err)
        return picking_obj

    class Meta:
        model = OrderPicking
        fields = ('products', 'sale_order_id', 'delivery_option', 'sub', 'estimated_delivery_date', 'ware_house',
                  'ware_house_data', 'to_location', 'remarks')
