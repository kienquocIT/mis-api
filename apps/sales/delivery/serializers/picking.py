from django.utils import timezone
from django.db import transaction
from rest_framework import serializers

from apps.masterdata.saledata.models import ProductWareHouse, UnitOfMeasure
from apps.sales.delivery.models import (
    OrderDeliveryProduct, OrderPickingProduct, OrderPickingSub, OrderDelivery
)
from apps.shared.translations.sales import DeliverMsg
from ..models.delivery import OrderDeliveryProductWarehouse
from ..utils import CommonFunc

__all__ = [
    'OrderPickingListSerializer',
    'OrderPickingSubDetailSerializer',
    'OrderPickingProductListSerializer',
    'OrderPickingSubListSerializer',
    'OrderPickingSubUpdateSerializer',
]


class OrderPickingProductListSerializer(serializers.ModelSerializer):
    uom_data = serializers.SerializerMethodField()

    class Meta:
        model = OrderPickingProduct
        fields = (
            'id',
            'order',
            'is_promotion',
            'product_data',
            'uom_data',
            'pickup_quantity',
            'picked_quantity_before',
            'remaining_quantity',
            'picked_quantity',
        )

    @classmethod
    def get_uom_data(cls, obj):
        return {
            'id': obj.uom_id,
            'title': obj.uom.title,
            'code': obj.uom.code,
            'ratio': obj.uom.ratio
        } if obj.uom else {}


class OrderPickingSubListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                "id": obj.employee_inherit_id,
                "full_name": f'{obj.employee_inherit.last_name} {obj.employee_inherit.first_name}'
            }
        return {}

    class Meta:
        model = OrderPickingSub
        fields = (
            'id',
            'code',
            'sale_order_data',
            'date_created',
            'state',
            'estimated_delivery_date',
            'employee_inherit'
        )


class OrderPickingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderPickingSub
        fields = (
            'code',
            'sale_order_data',
            'date_created',
            'estimated_delivery_date',
            'employee_inherit',
            'state',
        )


class OrderPickingSubDetailSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_products(cls, obj):
        return OrderPickingProductListSerializer(
            obj.picking_product_picking_sub.all(),
            many=True,
        ).data

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                "id": str(obj.employee_inherit_id),
                "full_name": f'{obj.employee_inherit.last_name} {obj.employee_inherit.first_name}'
            }
        return {}

    class Meta:
        model = OrderPickingSub
        fields = (
            'id',
            'code',
            'order_picking',
            'sale_order_data',
            'ware_house_data',
            'estimated_delivery_date',
            'state',
            'remarks',
            'to_location',
            'products',
            'pickup_quantity',
            'picked_quantity_before',
            'remaining_quantity',
            'picked_quantity',
            'delivery_option',
            'employee_inherit'
        )


class ProductPickingUpdateSerializer(serializers.Serializer):  # noqa
    product_id = serializers.UUIDField()
    done = serializers.IntegerField(min_value=1)
    delivery_data = serializers.JSONField()
    order = serializers.IntegerField(min_value=1)


class OrderPickingSubUpdateSerializer(serializers.ModelSerializer):
    products = ProductPickingUpdateSerializer(many=True)
    sale_order_id = serializers.UUIDField()
    employee_inherit_id = serializers.UUIDField()
    delivery_option = serializers.IntegerField(min_value=0)

    @classmethod
    def validate_state(cls, value):
        if value == 1:
            raise serializers.ValidationError(
                {
                    'state': DeliverMsg.ERROR_STATE
                }
            )
        return value

    @classmethod
    def plus_product_warehouse_picked(cls, instance, product_update):
        prod_id_temp = {}
        prod_update = []
        for key, value in product_update.items():
            delivery_data = value['delivery_data'][0]
            key_prod = key.split('___')[0]
            if key_prod not in prod_id_temp:
                prod_id_temp[key_prod] = value['stock']
            else:
                prod_id_temp[key_prod] += value['stock']
            picked_uom = UnitOfMeasure.objects.get(id=delivery_data['uom'])
            picked_unit = prod_id_temp[key_prod] * picked_uom.ratio
            product_warehouse = ProductWareHouse.objects.filter(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                product_id=key_prod,
                warehouse_id=delivery_data['warehouse']
            )
            if product_warehouse.exists():
                prod_warehouse = product_warehouse.first()
                in_stock = prod_warehouse.stock_amount
                in_stock = (in_stock - prod_warehouse.picked_ready)*prod_warehouse.uom.ratio
                if in_stock > 0 and in_stock >= picked_unit:
                    prod_warehouse.picked_ready += picked_unit / prod_warehouse.uom.ratio
                    prod_update.append(prod_warehouse)
                else:
                    raise serializers.ValidationError(
                        {
                            'products': DeliverMsg.ERROR_OUT_STOCK
                        }
                    )
        ProductWareHouse.objects.bulk_update(prod_update, fields=['picked_ready'])

    @classmethod
    def update_picking_to_delivery_prod(cls, instance, total, product_update):
        delivery = OrderDelivery.objects.filter(
            sale_order_id=instance.sale_order_data['id']
        ).first()
        delivery_sub = delivery.sub
        # update stock cho delivery prod
        obj_update = []
        # loop trong picking product
        for key, value in product_update.items():
            delivery_data = value['delivery_data'][0]
            key_prod = key.split('___')[0]
            delivery_prod = OrderDeliveryProduct.objects.filter(
                delivery_sub=delivery_sub,
                product_id=key_prod,
                uom_id=delivery_data['uom'],
                order=key.split('___')[1]
            )
            if delivery_prod.exists():
                delivery_prod = delivery_prod.first()
                # cộng vào stock cho delivery prod
                delivery_prod.ready_quantity += value['stock']
                delivery_prod.delivery_data.append(delivery_data)
                obj_update.append(delivery_prod)

                # create delivery product warehouse
                product_warehouse = ProductWareHouse.objects.filter(
                    tenant_id=instance.tenant_id,
                    company_id=instance.company_id,
                    product_id=key_prod,
                    warehouse_id=delivery_data['warehouse']
                ).first()
                if delivery and delivery_prod and product_warehouse:
                    delivery_product_warehouse = OrderDeliveryProductWarehouse.objects.filter(
                        tenant_id=instance.tenant_id,
                        company_id=instance.company_id,
                        delivery=delivery,
                        delivery_product=delivery_prod,
                        product_warehouse=product_warehouse,
                    ).first()
                    if delivery_product_warehouse:
                        delivery_product_warehouse.total_picking += total
                    else:
                        OrderDeliveryProductWarehouse.objects.create(
                            tenant_id=instance.tenant_id,
                            company_id=instance.company_id,
                            delivery=delivery,
                            delivery_product=delivery_prod,
                            product_warehouse=product_warehouse,
                            total_picking=total
                        )
        cls.plus_product_warehouse_picked(instance, product_update)
        OrderDeliveryProduct.objects.bulk_update(obj_update, fields=['ready_quantity', 'delivery_data'])
        # update ready stock cho delivery sub
        delivery_sub.ready_quantity += total
        if instance.delivery_option == 1 or instance.remaining_quantity == total:
            delivery_sub.state = 1

        delivery_sub.estimated_delivery_date = instance.estimated_delivery_date
        delivery_sub.save(update_fields=['state', 'estimated_delivery_date', 'ready_quantity'])

    @classmethod
    def update_prod_current(cls, instance, prod_update, total_picked):
        pickup_data_temp = {}
        for key, item in prod_update.items():
            delivery_data = item['delivery_data'][0]
            key_prod = key.split('___')[0]
            # mỗi phiếu picking chỉ có 1 product match với warehouse nên có thể lấy value 0 của list delivery_data
            get_prod = OrderPickingProduct.objects.filter(
                picking_sub=instance,
                product_id=key_prod,
                uom_id=delivery_data['uom'],
                order=key.split('___')[1]
            )
            if get_prod.exists():
                this_prod = get_prod.first()
                this_prod.picked_quantity = item['stock']

                pickup_data_temp[key] = {
                    'remaining_quantity': this_prod.remaining_quantity,
                    'picked_quantity': item['stock'],
                    'pickup_quantity': this_prod.pickup_quantity,
                    'picked_quantity_before': this_prod.picked_quantity_before
                }
                this_prod.save(update_fields=['picked_quantity'])

        # cls.update_picking_to_delivery_prod(instance, total_picked, prod_update)

        if total_picked > instance.remaining_quantity:
            raise serializers.ValidationError(
                {'products': DeliverMsg.ERROR_QUANTITY}
            )
        return pickup_data_temp

    @classmethod
    def create_new_picking_sub(cls, instance):
        picking = instance.order_picking
        # create new sub follow by prev sub
        new_sub = OrderPickingSub.objects.create(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            order_picking=picking,
            date_done=None,
            previous_step=instance,
            times=instance.times + 1,
            pickup_quantity=instance.pickup_quantity,
            picked_quantity_before=instance.picked_quantity_before + instance.picked_quantity,
            remaining_quantity=instance.pickup_quantity - (instance.picked_quantity_before + instance.picked_quantity),
            picked_quantity=0,
            pickup_data=instance.pickup_data,
            sale_order_data=picking.sale_order_data,
            delivery_option=instance.delivery_option,
            config_at_that_point=instance.config_at_that_point,
            employee_inherit=instance.employee_inherit
        )

        picking.sub = new_sub
        picking.save(update_fields=['sub'])
        # create prod with new sub id
        obj_new_prod = []
        for obj in OrderPickingProduct.objects.filter(
                picking_sub=instance
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
                product_id=obj.product_id,
                order=obj.order
            )
            new_item.before_save()
            obj_new_prod.append(new_item)
        OrderPickingProduct.objects.bulk_create(obj_new_prod)

    @classmethod
    def update_current_sub(cls, instance, pickup_data, total):
        # update sub after update product
        instance.date_done = timezone.now()
        instance.pickup_data = pickup_data
        instance.picked_quantity = total
        instance.state = 1
        instance.save(
            update_fields=['picked_quantity', 'pickup_data', 'ware_house', 'ware_house_data', 'to_location', 'remarks',
                           'date_done', 'state', 'estimated_delivery_date']
        )

        if total < instance.remaining_quantity:
            # giao hàng nhiều lần
            # update current sub
            # tạo mới sub and tạo mới prod, gán sub cho prod picking
            cls.create_new_picking_sub(instance)
        if total == instance.remaining_quantity:
            picking = instance.order_picking
            picking.state = 1
            picking.save(update_fields=['state'])

    def validate(self, validate_data):
        if len(validate_data['products']) > 0 and 'estimated_delivery_date' not in validate_data:
            raise serializers.ValidationError(
                {
                    'detail': DeliverMsg.ERROR_ESTIMATED_DATE
                }
            )
        return validate_data

    def update(self, instance, validated_data):
        # convert prod to dict
        product_done = {}
        picked_quantity_total = 0
        CommonFunc.check_update_prod_and_emp(instance, validated_data)
        print('check update pass')

        if 'products' in validated_data and len(validated_data['products']) > 0:
            for item in validated_data['products']:
                item_key = str(item['product_id']) + "___" + str(item['order'])
                picked_quantity_total += item['done']
                product_done[item_key] = {
                    'stock': item['done'],
                    'delivery_data': item['delivery_data']
                }
            instance.estimated_delivery_date = validated_data['estimated_delivery_date']
            instance.remarks = validated_data['remarks']
            instance.to_location = validated_data['to_location']
            instance.ware_house = validated_data['ware_house']
            try:
                with transaction.atomic():
                    # update picking prod và delivery prod trừ vào warehouse stock
                    pickup_data = self.update_prod_current(instance, product_done, picked_quantity_total)
                    self.update_current_sub(instance, pickup_data, picked_quantity_total)
            except Exception as err:
                print(err)
                raise err
        else:
            del validated_data['products']
            del validated_data['state']
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()
            instance.order_picking.employee_inherit = instance.employee_inherit
            instance.order_picking.save()
        return instance

    class Meta:
        model = OrderPickingSub
        fields = ('products', 'sale_order_id', 'order_picking', 'state', 'estimated_delivery_date', 'ware_house',
                  'to_location', 'remarks', 'delivery_option', 'employee_inherit_id')
