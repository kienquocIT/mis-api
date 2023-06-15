from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.masterdata.saledata.models import ProductWareHouse
from ..models import DeliveryConfig, OrderDelivery, OrderDeliverySub, OrderDeliveryProduct

__all__ = ['OrderDeliveryListSerializer', 'OrderDeliverySubListSerializer', 'OrderDeliverySubDetailSerializer',
           'OrderDeliverySubUpdateSerializer']


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
            'delivery_data',
            'picked_quantity'
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
            'state',
            'code',
            'sale_order_data',
            'date_created',
            'estimated_delivery_date',
            'actual_delivery_date',
        )


class OrderDeliveryListSerializer(serializers.ModelSerializer):
    sub_list = serializers.SerializerMethodField()

    @classmethod
    def get_sub_list(cls, obj):
        sub_list = []
        query_sub_list = OrderDeliverySub.objects.filter(
            tenant_id=obj.tenant_id, company_id=obj.company_id,
            order_delivery=obj
        )
        if query_sub_list:
            for query_sub in query_sub_list:
                serializer = OrderDeliverySubListSerializer(query_sub)
                sub_list.append(serializer.data)

        return sub_list

    class Meta:
        model = OrderDelivery
        fields = (
            'id',
            'title',
            'code',
            'sale_order_id',
            'sale_order_data',
            'state',
            'sub',
            'sub_list',
            'date_created', 'date_modified', 'is_active'
        )


class OrderDeliverySubDetailSerializer(serializers.ModelSerializer):
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
            'estimated_delivery_date',
            'actual_delivery_date',
            'customer_data',
            'contact_data'
        )


class ProductDeliveryUpdateSerializer(serializers.Serializer):  # noqa
    product_id = serializers.UUIDField()
    done = serializers.IntegerField(min_value=1)
    delivery_data = serializers.JSONField(allow_null=True)


class OrderDeliverySubUpdateSerializer(serializers.ModelSerializer):
    products = ProductDeliveryUpdateSerializer(many=True)

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
        )

    @classmethod
    def validate_state(cls, value):
        if value < 2:
            return value
        raise serializers.ValidationError(
            {
                'State': _('Can not update when status is Done!')
            }
        )

    @classmethod
    def update_self_info(cls, instance, validated_data):
        instance.estimated_delivery_date = validated_data['estimated_delivery_date']
        instance.actual_delivery_date = validated_data['actual_delivery_date']
        instance.remarks = validated_data['remarks']

    @classmethod
    def minus_product_warehouse_stock(cls, tenant_com_info, product_id, stock_info):
        save_list = []
        for data in stock_info:
            product_warehouse = ProductWareHouse.objects.filter(
                tenant_id=tenant_com_info['tenant_id'],
                company_id=tenant_com_info['company_id'],
                product_id=product_id,
                warehouse_id=data['warehouse'],
                uom_id=data['uom']
            )
            if product_warehouse.exists():
                selected = product_warehouse.first()
                selected.sold_amount += data['stock']
                save_list.append(selected)

        ProductWareHouse.objects.bulk_update(save_list, fields=['sold_amount'])

    @classmethod
    def update_prod(cls, sub, product_done):
        for obj in OrderDeliveryProduct.objects.filter_current(
                delivery_sub=sub
        ):
            if str(obj.product_id) in product_done:
                delivery_data = product_done[str(obj.product_id)]['delivery_data']  # list format
                obj.picked_quantity = product_done[str(obj.product_id)]['picked_num']
                obj.delivery_data = delivery_data
                # config case 1, 2, 3
                cls.minus_product_warehouse_stock(
                    {'tenant_id': sub.tenant_id, 'company_id': sub.company_id},
                    obj.product_id,
                    delivery_data
                )
                obj.save(update_fields=['picked_quantity', 'delivery_data'])

    @classmethod
    def create_prod(cls, new_sub, instance):
        # update to current product list of current sub
        prod_arr = []
        for obj in OrderDeliveryProduct.objects.filter_current(
                delivery_sub=instance
        ):
            new_prod = OrderDeliveryProduct(
                delivery_sub=new_sub,
                product=obj.product,
                uom=obj.uom,
                delivery_quantity=obj.delivery_quantity,
                delivered_quantity_before=obj.delivered_quantity_before + obj.picked_quantity,
                remaining_quantity=obj.delivery_quantity - (obj.delivered_quantity_before + obj.picked_quantity),
                ready_quantity=obj.delivery_quantity - (obj.delivered_quantity_before + obj.picked_quantity),
                picked_quantity=0
            )
            new_prod.before_save()
            prod_arr.append(new_prod)
        OrderDeliveryProduct.objects.bulk_create(prod_arr)

    @classmethod
    def create_new_code(cls):
        new_code = ''
        delivery = OrderDeliverySub.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        char = "D"
        temper = delivery + 1
        new_code = f"{char}{temper:03d}"
        return new_code

    @classmethod
    def create_new_sub(cls, instance, total_done, case=0):
        new_code = OrderDeliverySubUpdateSerializer.create_new_code()
        new_sub = OrderDeliverySub.objects.create(
            company_id=instance.company_id,
            tenant_id=instance.tenant_id,
            order_delivery=instance.order_delivery,
            date_done=None,
            code=new_code,
            previous_step=instance,
            times=instance.times + 1,
            delivery_quantity=instance.delivery_quantity,
            delivered_quantity_before=instance.delivered_quantity_before + total_done,
            remaining_quantity=instance.delivery_quantity - (instance.delivered_quantity_before + total_done),
            ready_quantity=instance.delivery_quantity - (instance.delivered_quantity_before + total_done),
            delivery_data=None,
            is_updated=False,
            state=0 if case == 4 else 1,
            sale_order_data=instance.sale_order_data,
            estimated_delivery_date=instance.estimated_delivery_date,
            actual_delivery_date=instance.actual_delivery_date,
            customer_data=instance.customer_data,
            contact_data=instance.contact_data
        )
        return new_sub

    @classmethod
    def config_one(cls, instance, total_done, product_done):
        try:
            with transaction.atomic():
                if instance.remaining_quantity == total_done:
                    # update product and sub date_done
                    cls.update_prod(instance, product_done)
                    instance.date_done = timezone.now()
                    instance.state = 2
                    instance.is_updated = True
                    instance.save(
                        update_fields=['date_done', 'state', 'is_updated', 'estimated_delivery_date',
                                       'actual_delivery_date', 'remarks']
                    )
                else:
                    raise serializers.ValidationError(
                        {
                            'products': _('Done quantity not equal remain quantity!')
                        }
                    )
        except Exception as err:
            print(err)

    @classmethod
    def config_two(cls, instance, total_done, product_done):
        try:
            with transaction.atomic():
                # cho phep giao nhieu lan and tạo sub mới
                cls.update_prod(instance, product_done)
                instance.date_done = timezone.now()
                instance.state = 2
                instance.is_updated = True
                instance.save(
                    update_fields=['date_done', 'state', 'is_updated', 'estimated_delivery_date',
                                   'actual_delivery_date', 'remarks']
                )
                if instance.remaining_quantity > total_done:
                    new_sub = cls.create_new_sub(instance, total_done, 2)
                    cls.create_prod(new_sub, instance)
                    delivery_obj = instance.order_delivery
                    delivery_obj.sub = new_sub
                    delivery_obj.save(update_fields=['sub'])
        except Exception as err:
            print(err)

    @classmethod
    def config_three(cls, instance, total_done, product_done):
        try:
            with transaction.atomic():
                order_delivery = instance.order_delivery
                if instance.remaining_quantity == total_done:
                    cls.update_prod(instance, product_done)
                    instance.date_done = timezone.now()
                    instance.state = 2
                    instance.is_updated = True
                    instance.save(
                        update_fields=['date_done', 'state', 'is_updated', 'estimated_delivery_date',
                                       'actual_delivery_date', 'remarks']
                    )
                    order_delivery.state = 2
                    order_delivery.save(update_fields=['state'])
                else:
                    raise serializers.ValidationError(
                        {
                            'products': _('Done quantity not equal remain quantity!')
                        }
                    )
        except Exception as err:
            print('err delivery config 3', err)

    @classmethod
    def config_four(cls, instance, total_done, product_done):
        try:
            with transaction.atomic():
                cls.update_prod(instance, product_done)
                order_delivery = instance.order_delivery
                if instance.remaining_quantity > total_done:
                    new_sub = cls.create_new_sub(instance, total_done, 4)
                    cls.create_prod(new_sub, instance)
                    order_delivery.sub = new_sub
                elif instance.remaining_quantity == total_done:
                    instance.date_done = timezone.now()
                    instance.is_updated = True
                    instance.state = 2
                    instance.ready_quantity += total_done
                    order_delivery.state = 2
                    instance.save(
                       update_fields=['date_done', 'ready_quantity', 'state', 'is_updated']
                    )
                order_delivery.save(update_fields=['sub', 'state'])
        except Exception as err:
            print(err)

    def update(self, instance, validated_data):
        # declare default object
        validated_product = validated_data['products']
        config = DeliveryConfig.objects.get(company_id=instance.company_id)
        is_picking = config.is_picking
        is_partial = config.is_partial_ship
        product_done = {}
        total_done = 0
        for item in validated_product:
            product_done[str(item['product_id'])] = {}
            total_done += item['done']
            product_done[str(item['product_id'])]['picked_num'] = item['done']
            product_done[str(item['product_id'])]['delivery_data'] = item['delivery_data']

        # update instance info
        self.update_self_info(instance, validated_data)
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
