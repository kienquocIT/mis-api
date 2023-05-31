from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from ..models import DeliveryConfig, OrderDeliverySub
from apps.sales.delivery.models import OrderPicking, OrderPickingProduct, OrderPickingSub, OrderDelivery

__all__ = [
    'OrderPickingListSerializer',
    'OrderPickingDetailSerializer',
    'OrderPickingProductListSerializer',
    'OrderPickingSubListSerializer',
    'OrderPickingUpdateSerializer'
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
        xx = OrderPickingProductListSerializer(
            obj.orderpickingproduct_set.all(),
            many=True,
        ).data
        return xx

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
    delivery_option = serializers.IntegerField(min_value=1)

    # tạo delivery sub sau khi picking done
    @staticmethod
    def create_delivery_sub(picked_quantity_total, remain, picking_obj):
        delivery = OrderDelivery.objects.filter(sale_order_id=picking_obj.sale_order_id)
        # get delivery config
        config = DeliveryConfig.objects.get(company_id=picking_obj.company_id)
        is_picking = config.is_pikcing
        is_partial = config.is_partial_ship

        if is_partial and is_picking:
            # giao hàng nhiều lần
            pass
        elif picked_quantity_total == remain:
            # đợi full
            # tạo sub delivery
            sub_delivery = OrderDeliverySub.objects.create(
                order_delivery=delivery,
                date_done=None,
                previous_step=None,
                times=1,
                delivery_quantity=picking_obj.delivery_quantity,
                delivered_quantity_before=picking_obj.delivered_quantity_before,
                remaining_quantity=picking_obj.remaining_quantity,
                ready_quantity=picked_quantity_total,
                delivery_data=picking_obj.pickup_data
            )
            # create delivery prod
            for obj in OrderPickingProduct.objects.filter_current(
                    picking_sub=picking_obj.sub
            ):
                OrderPickingProduct.objects.create(
                    product=obj,
                    product_data=obj.product_data,
                    uom=obj.uom,
                    uom_data=obj.uom_data,
                    delivery_quantity=obj.pickup_quantity,
                    delivered_quantity_before=0,
                    remaining_quantity=obj.remaining_quantity,
                    ready_quantity=picked_quantity_total,
                    delivery_sub=sub_delivery,
                )
            # giao hàng 1 lần delivery = 1 giao nhiều lần delivery = 0
            # state = 0 (wait). state = 1 giao nhiều lần (Partial). state = 2 giao 1 lần (full)
            state_val = 0
            if is_picking == 0 and is_partial == 0:
                state_val = 2
            elif is_partial == 1:
                state_val = 1
            delivery.state = state_val
            delivery.save()

    @staticmethod
    def create_new_picking_sub(instance, sub):
        # create new sub follow by prev sub
        new_sub = OrderPickingSub.objects.create(
            tenant_id=sub.tenant_id,
            company_id=sub.company_id,
            order_picking=instance,
            date_done=None,
            previous_step=sub,
            times=sub.times + 1,
            pickup_quantity=sub.pickup_quantity,
            picked_quantity_before=sub.picked_quantity_before + sub.picked_quantity,
            remaining_quantity=sub.remaining_quantity - sub.picked_quantity,
            picked_quantity=0,
            pickup_data=sub.pickup_data,
        )
        instance.sub = new_sub
        instance.save(update_fields=['sub'])
        # create prod with new sub id
        for obj in OrderPickingProduct.objects.filter_current(
                picking_sub=sub
        ):
            OrderPickingProduct.objects.create(
                product_data=obj.product_data,
                uom_data=obj.uom_data,
                uom_id=obj.uom_id,
                pickup_quantity=obj.pickup_quantity,
                picked_quantity_before=obj.picked_quantity_before + obj.picked_quantity,
                remaining_quantity=obj.remaining_quantity - obj.picked_quantity,
                picked_quantity=0,
                picking_sub=new_sub,
                product_id=obj.product_id
            )
    '''
    STEP 1: update table OrderPicking
        + estimated_delivery_date
        + ware_house, ware_house_data
        + to_location, remarks

    STEP 2: update table OrderPickingProduct
        * điều kiện remain >= done
            + picked_quantity

    STEP 3: update current sub và tạo mới nếu chưa đủ cho table OrderPickingSub
        * nếu chưa update vào current và tạo mới nếu rồi update vào current
        => update vào currenct 
            + picked_quantity
            + pickup_data ex. {
                                product_id: { 
                                                remaining_quantity: '', 
                                                picked_quantity: validated_data['done'], 
                                                pickup_quantity: '', 
                                                picked_quantity_before: ''
                                            }
                              }
        => tạo mới
            + times = times cũ + 1
            + picked_quantity_before = tổng done trước đó
            + remaining_quantity = remaining - done
            + previous_step_id = sub_id_current

    STEP 4: update cho phiếu delivery nếu đã done
        + kiem tra giao hàng picking = true (đợi đủ), 
        + picking = true và giao nhieu lan = true hoặc chỉ có giao nhiểu lần => post prod mới update qua delivery
    '''
    def update(self, instance, validated_data):
        picking_obj = instance
        # convert prod to dict
        product_done = {
            str(item['product_id']): item['done'] for item in validated_data['products']
        }

        # update picking info step 1
        picking_obj.estimated_delivery_date = validated_data['estimated_delivery_date']
        picking_obj.ware_house = validated_data['ware_house']
        picking_obj.ware_house_data = {
            'id': str(validated_data['ware_house'].id),
            'title': validated_data['ware_house'].title,
            'code': validated_data['ware_house'].code
        }
        picking_obj.to_location = validated_data['to_location']
        picking_obj.remarks = validated_data['remarks']
        picking_obj.save(
            update_fields=['estimated_delivery_date', 'ware_house', 'ware_house_data', 'to_location',
                           'remarks']
        )
        # loop prod list get from picking prod step 2
        pickup_data = {}
        picked_quantity_total = 0
        for obj in OrderPickingProduct.objects.filter_current(
                picking_sub=self.instance.sub
        ):
            if str(obj.product_id) in product_done:
                # update and save picked quantity
                if obj.remaining_quantity >= product_done[str(obj.product_id)]:
                    obj.picked_quantity = product_done[str(obj.product_id)]
                    obj.save(update_fields=['picked_quantity'])
                    pickup_data[str(obj.product_id)] = {
                        'remaining_quantity': obj.remaining_quantity,
                        'picked_quantity': product_done[str(obj.product_id)],
                        'pickup_quantity': obj.pickup_quantity,
                        'picked_quantity_before': obj.picked_quantity_before
                    }
                    picked_quantity_total += product_done[str(obj.product_id)]
                else:
                    raise serializers.ValidationError(
                        {
                            'products': _('Picked quantity must be less more than pickup remain')
                        }
                    )
            continue  # Skip the current iteration if num is 3

        # update sub after update product step 3
        picking_sub = OrderPickingSub.objects.filter_current(order_picking=picking_obj.id).order_by('-times')
        remain = 0
        for sub in picking_sub:
            sub.pickup_data = pickup_data
            remain = sub.remaining_quantity
            sub.picked_quantity = picked_quantity_total
            sub.ware_house = picking_obj.ware_house
            sub.ware_house_data = picking_obj.ware_house_data
            sub.to_location = picking_obj.to_location
            sub.remarks = picking_obj.remarks
            sub.date_done = timezone.now
            sub.pickup_data = pickup_data
            sub.save(update_fields=['picked_quantity', 'pickup_data', 'ware_house', 'ware_house_data',
                                    'to_location', 'remarks', 'date_done'])
            if remain > picked_quantity_total:
                # chưa đủ => tạo mới sub
                self.create_new_picking_sub(instance, sub)
            if picked_quantity_total == remain:
                # change state from ready to Done if picked was enough.
                instance.state = 1
                instance.save(update_fields=['state'])

        # trigger delivery state step 4
        self.create_delivery_sub(picked_quantity_total, remain, picking_obj)
        return picking_obj

    class Meta:
        model = OrderPicking
        fields = ('products', 'sale_order_id', 'delivery_option', 'sub', 'estimated_delivery_date', 'ware_house',
                  'ware_house_data', 'to_location', 'remarks')
