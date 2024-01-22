from rest_framework import serializers

from apps.masterdata.saledata.models import Account
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.arinvoice.models import ARInvoice, ARInvoiceDelivery, ARInvoiceItems

__all__ = [
    'DeliveryListSerializerForARInvoice',
    'ARInvoiceListSerializer',
    'ARInvoiceDetailSerializer',
    'ARInvoiceCreateSerializer',
    'ARInvoiceUpdateSerializer'
]


class ARInvoiceListSerializer(serializers.ModelSerializer):
    customer_mapped = serializers.SerializerMethodField()
    sale_order_mapped = serializers.SerializerMethodField()

    class Meta:
        model = ARInvoice
        fields = (
            'id',
            'title',
            'code',
            'customer_mapped',
            'customer_name',
            'sale_order_mapped',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'system_status'
        )

    @classmethod
    def get_customer_mapped(cls, obj):
        return {
            'id': obj.customer_mapped_id,
            'code': obj.customer_mapped.code,
            'name': obj.customer_mapped.name
        } if obj.customer_mapped else {}

    @classmethod
    def get_sale_order_mapped(cls, obj):
        return {
            'id': obj.sale_order_mapped_id,
            'code': obj.sale_order_mapped.code,
            'title': obj.sale_order_mapped.title
        } if obj.sale_order_mapped else {}


def create_delivery_mapped(ar_invoice, delivery_mapped_list):
    bulk_data = []
    for item in delivery_mapped_list:
        bulk_data.append(ARInvoiceDelivery(ar_invoice=ar_invoice, delivery_mapped_id=item))
    ARInvoiceDelivery.objects.filter(ar_invoice=ar_invoice).delete()
    ARInvoiceDelivery.objects.bulk_create(bulk_data)
    return True


def create_item_and_discount_mapped(ar_invoice, data_item_list, data_discount_list):
    bulk_data = []
    for item in data_item_list:
        bulk_data.append(ARInvoiceItems(ar_invoice=ar_invoice, **item))
    for item in data_discount_list:
        bulk_data.append(ARInvoiceItems(ar_invoice=ar_invoice, **item))
    ARInvoiceItems.objects.filter(ar_invoice=ar_invoice).delete()
    ARInvoiceItems.objects.bulk_create(bulk_data)
    return True


class ARInvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARInvoice
        fields = (
            'title',
            'customer_mapped',
            'customer_name',
            'sale_order_mapped',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'system_status'
        )

    def validate(self, validate_data):
        if validate_data.get('customer_mapped'):
            if validate_data['customer_mapped'].name == validate_data['customer_name']:
                validate_data['customer_name'] = None
            else:
                validate_data['customer_mapped'] = None
        return validate_data

    # @decorator_run_workflow
    def create(self, validated_data):
        ar_invoice = ARInvoice.objects.create(**validated_data, code=f'AR-00{ARInvoice.objects.all().count()+1}')

        create_delivery_mapped(ar_invoice, self.initial_data.get('delivery_mapped_list', []))
        create_item_and_discount_mapped(
            ar_invoice,
            self.initial_data.get('data_item_list', []),
            self.initial_data.get('data_discount_list', [])
        )

        return ar_invoice


class ARInvoiceDetailSerializer(serializers.ModelSerializer):
    delivery_mapped = serializers.SerializerMethodField()
    item_and_discount_mapped = serializers.SerializerMethodField()
    customer_mapped = serializers.SerializerMethodField()
    sale_order_mapped = serializers.SerializerMethodField()

    class Meta:
        model = ARInvoice
        fields = (
            'id',
            'title',
            'code',
            'customer_mapped',
            'customer_name',
            'sale_order_mapped',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'system_status',
            'delivery_mapped',
            'item_and_discount_mapped'
        )

    @classmethod
    def get_delivery_mapped(cls, obj):
        return [{
            'id': item.delivery_mapped_id,
            'title': item.delivery_mapped.title,
        } for item in obj.ar_invoice_deliveries.all()]

    @classmethod
    def get_item_and_discount_mapped(cls, obj):
        return [{
            'item_index': item.item_index,
            'product_mapped': {
                'id': item.product_mapped_id,
                'code': item.product_mapped.code,
                'title': item.product_mapped.title,
            } if item.product_mapped else {},
            'product_mapped_uom': {
                'id': item.product_mapped_uom_id,
                'code': item.product_mapped_uom.code,
                'title': item.product_mapped_uom.title,
            } if item.product_mapped_uom else {},
            'product_mapped_quantity': item.product_mapped_quantity,
            'product_mapped_unit_price': item.product_mapped_unit_price,
            'product_mapped_tax_value': item.product_mapped_tax_value,
            'product_mapped_subtotal': item.product_mapped_subtotal,
            'discount_name': item.discount_name,
            'discount_uom': item.discount_uom,
            'discount_quantity': item.discount_quantity,
            'discount_unit_price': item.discount_unit_price,
            'discount_subtotal': item.discount_subtotal
        } for item in obj.ar_invoice_items.all()]

    @classmethod
    def get_customer_mapped(cls, obj):
        return {
            'id': obj.customer_mapped_id,
            'code': obj.customer_mapped.code,
            'name': obj.customer_mapped.name,
        } if obj.customer_mapped else {}

    @classmethod
    def get_sale_order_mapped(cls, obj):
        return {
            'id': obj.sale_order_mapped_id,
            'code': obj.sale_order_mapped.code,
            'title': obj.sale_order_mapped.title,
        } if obj.sale_order_mapped else {}


class ARInvoiceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARInvoice
        fields = (
            'title',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'system_status'
        )

    def validate(self, validate_data):
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        create_delivery_mapped(instance, self.initial_data.get('delivery_mapped_list', []))
        create_item_and_discount_mapped(
            instance,
            self.initial_data.get('data_item_list', []),
            self.initial_data.get('data_discount_list', [])
        )

        return instance


class DeliveryListSerializerForARInvoice(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    already = serializers.SerializerMethodField()

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
            'already',
            'details'
        )

    @classmethod
    def get_details(cls, obj):
        return [{
            'product_data': item.product_data,
            'uom_data': item.uom_data,
            'delivery_quantity': item.delivery_quantity,
            'delivered_quantity_before': item.delivered_quantity_before,
            'picked_quantity': item.picked_quantity,
            'product_unit_price': item.product_unit_price,
            'product_tax_value': item.product_tax_value,
        } for item in obj.delivery_product_delivery_sub.all()]

    @classmethod
    def get_already(cls, obj):
        return ARInvoiceDelivery.objects.filter(delivery_mapped=obj).count()
