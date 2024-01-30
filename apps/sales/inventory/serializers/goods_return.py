from rest_framework import serializers

from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.inventory.models import GoodsReturn, GoodsReturnProductDetail
from apps.sales.saleorder.models import SaleOrder


class GoodsReturnListSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    delivery = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReturn
        fields = (
            'id',
            'title',
            'code',
            'sale_order',
            'note',
            'delivery',
            'product',
            'uom',
            'system_status',
            'date_created'
        )

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'code': obj.sale_order.code,
            'title': obj.sale_order.title,
            'sale_person': {
                'id': obj.sale_order.employee_inherit_id,
                'code': obj.sale_order.employee_inherit.code,
                'fullname': obj.sale_order.employee_inherit.get_full_name(2),
            } if obj.sale_order.employee_inherit else {}
        } if obj.sale_order else {}

    @classmethod
    def get_delivery(cls, obj):
        return {
            'id': obj.delivery_id,
            'code': obj.delivery.code
        } if obj.delivery_id else {}


def create_delivery_product_detail_mapped(goods_return, product_detail_list):
    bulk_info = []
    for item in product_detail_list:
        bulk_info.append(
            GoodsReturnProductDetail.objects.create(
                goods_return=goods_return,
                **item
            )
        )
    GoodsReturnProductDetail.objects.filter(goods_return=goods_return).delete()
    GoodsReturnProductDetail.objects.bulk_create(bulk_info)
    return True


class GoodsReturnCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsReturn
        fields = (
            'title',
            'code',
            'sale_order',
            'note',
            'delivery',
            'product',
            'uom',
            'system_status',
        )

    def create(self, validated_data):
        goods_return = GoodsReturn.objects.create(
            code=f'GRT00{GoodsReturn.objects.all().count() + 1}',
            **validated_data
        )
        create_delivery_product_detail_mapped(
            goods_return,
            self.initial_data.get('product_detail_list', []),
        )
        return goods_return


class GoodsReturnDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsReturn
        fields = (
            'id',
            'title',
            'code',
            'sale_order',
            'note',
            'delivery',
            'product',
            'uom',
            'system_status',
        )


class GoodsReturnUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsReturn
        fields = (
            'title',
            'code',
            'sale_order',
            'note',
            'delivery',
            'product',
            'uom',
            'system_status',
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        create_delivery_product_detail_mapped(
            instance,
            self.initial_data.get('product_detail_list', []),
        )
        return instance


class SaleOrderListSerializerForGoodsReturn(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'title',
            'code',
            'customer',
            'sale_person',
            'date_created',
            'system_status',
            'delivery_status',
        )

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'title': obj.customer.name,
            'code': obj.customer.code,
        } if obj.customer else {}

    @classmethod
    def get_sale_person(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'first_name': obj.employee_inherit.first_name,
            'last_name': obj.employee_inherit.last_name,
            'email': obj.employee_inherit.email,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'is_active': obj.employee_inherit.is_active,
        } if obj.employee_inherit else {}


class DeliveryListSerializerForGoodsReturn(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = OrderDeliverySub
        fields = (
            'id',
            'title',
            'code',
            'sale_order_data',
            'delivery_quantity',
            'state',
            'is_active',
            'times',
            'details',
            'date'
        )

    @classmethod
    def get_details(cls, obj):
        return [{
            'product_data': item.product_data,
            'uom_data': item.uom_data,
            'total_order': item.ready_quantity,
            'delivered_quantity': item.picked_quantity,
            'product_unit_price': item.product_unit_price,
            'product_subtotal_price': item.product_subtotal_price,
            'product_general_traceability_method': item.product.general_traceability_method,
        } for item in obj.delivery_product_delivery_sub.all()]

    @classmethod
    def get_date(cls, obj):
        return obj.order_delivery.date_created


class GetDeliveryProductsDeliveredSerializer(serializers.ModelSerializer):
    products_delivered_data_by_serial = serializers.SerializerMethodField()
    products_delivered_data_by_lot = serializers.SerializerMethodField()

    class Meta:
        model = OrderDeliverySub
        fields = (
            'id',
            'title',
            'code',
            'products_delivered_data_by_serial',
            'products_delivered_data_by_lot'
        )

    @classmethod
    def get_products_delivered_data_by_serial(cls, obj):
        return [{
            'product': serial.delivery_product.product_data,
            'uom': serial.delivery_product.uom_data,
            'product_unit_price': serial.delivery_product.product_unit_price,
            'product_subtotal_price': serial.delivery_product.product_subtotal_price,
            'serial_id': serial.product_warehouse_serial_id,
            'vendor_serial_number': serial.product_warehouse_serial.vendor_serial_number,
            'serial_number': serial.product_warehouse_serial.serial_number,
        } for serial in obj.delivery_serial_delivery_sub.all()]

    @classmethod
    def get_products_delivered_data_by_lot(cls, obj):
        return [{
            'product': lot.delivery_product.product_data,
            'uom': lot.delivery_product.uom_data,
            'product_unit_price': lot.delivery_product.product_unit_price,
            'lot_id': lot.product_warehouse_lot_id,
            'lot_number': lot.product_warehouse_lot.lot_number,
            'quantity_delivery': lot.quantity_delivery
        } for lot in obj.delivery_lot_delivery_sub.all()]
