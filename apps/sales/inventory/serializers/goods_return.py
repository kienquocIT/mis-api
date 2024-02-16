from rest_framework import serializers
from apps.sales.delivery.models import OrderDeliverySub, DeliveryConfig
from apps.sales.inventory.models import GoodsReturn
from apps.sales.inventory.serializers.goods_return_sub import GoodsReturnSubSerializerForNonPicking
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
            } if obj.sale_order.employee_inherit else {},
            'customer': {
                'id': obj.sale_order.customer_id,
                'code': obj.sale_order.customer.code,
                'name': obj.sale_order.customer.name,
            } if obj.sale_order.employee_inherit else {}
        } if obj.sale_order else {}

    @classmethod
    def get_delivery(cls, obj):
        return {
            'id': obj.delivery_id,
            'code': obj.delivery.code
        } if obj.delivery_id else {}


class GoodsReturnCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150, required=True)

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

        GoodsReturnSubSerializerForNonPicking.create_delivery_product_detail_mapped(
            goods_return,
            self.initial_data.get('product_detail_list', []),
        )

        config = DeliveryConfig.objects.filter_current(fill__tenant=True, fill__company=True).first()
        if config.is_picking is True:
            pass
        else:
            GoodsReturnSubSerializerForNonPicking.update_delivery(
                goods_return,
                self.initial_data.get('product_detail_list', [])
            )
        return goods_return


class GoodsReturnDetailSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    delivery = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    data_detail = serializers.SerializerMethodField()

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
            'date_created',
            'data_detail'
        )

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'code': obj.sale_order.code,
            'title': obj.sale_order.title,
            'customer_name': obj.sale_order.customer.name if obj.sale_order.customer else ''
        } if obj.sale_order else {}

    @classmethod
    def get_delivery(cls, obj):
        return {
            'id': obj.delivery_id,
            'code': obj.delivery.code
        } if obj.delivery_id else {}

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'code': obj.product.code,
            'title': obj.product.title,
        } if obj.product else {}

    @classmethod
    def get_uom(cls, obj):
        return {
            'id': obj.uom_id,
            'code': obj.uom.code,
            'title': obj.uom.title,
        } if obj.uom else {}

    @classmethod
    def get_data_detail(cls, obj):
        return [{
            'id': item.id,
            'type': item.type,
            'default_return_number': item.default_return_number,
            'default_redelivery_number': item.default_redelivery_number,
            'lot_no': {
                'id': item.lot_no_id,
                'lot_number': item.lot_no.lot_number
            } if item.lot_no else {},
            'lot_return_number': item.lot_return_number,
            'lot_redelivery_number': item.lot_redelivery_number,
            'serial_no': {
                'id': item.serial_no_id,
                'vendor_serial_number': item.serial_no.vendor_serial_number,
                'serial_number': item.serial_no.serial_number,
            } if item.serial_no else {},
            'is_return': item.is_return,
            'is_redelivery': item.is_redelivery
        } for item in obj.goods_return_product_detail.all()]


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
        GoodsReturnSubSerializerForNonPicking.create_delivery_product_detail_mapped(
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
            'total_order': item.delivery_quantity,
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
            'is_returned': serial.is_returned
        } for serial in obj.delivery_serial_delivery_sub.all()]

    @classmethod
    def get_products_delivered_data_by_lot(cls, obj):
        return [{
            'product': lot.delivery_product.product_data,
            'uom': lot.delivery_product.uom_data,
            'product_unit_price': lot.delivery_product.product_unit_price,
            'lot_id': lot.product_warehouse_lot_id,
            'lot_number': lot.product_warehouse_lot.lot_number,
            'quantity_delivery': lot.quantity_delivery,
            'returned_quantity': lot.returned_quantity
        } for lot in obj.delivery_lot_delivery_sub.all()]
