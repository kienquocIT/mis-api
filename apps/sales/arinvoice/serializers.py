from rest_framework import serializers
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.arinvoice.models import ARInvoice, ARInvoiceDelivery, ARInvoiceItems, ARInvoiceAttachmentFile

__all__ = [
    'DeliveryListSerializerForARInvoice',
    'ARInvoiceListSerializer',
    'ARInvoiceDetailSerializer',
    'ARInvoiceCreateSerializer',
    'ARInvoiceUpdateSerializer'
]

from apps.shared import SaleMsg


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


def create_files_mapped(ar_invoice, file_id_list):
    try:
        bulk_data_file = []
        for index, file_id in enumerate(file_id_list):
            bulk_data_file.append(ARInvoiceAttachmentFile(
                ar_invoice=ar_invoice,
                attachment_id=file_id,
                order=index
            ))
        ARInvoiceAttachmentFile.objects.filter(ar_invoice=ar_invoice).delete()
        ARInvoiceAttachmentFile.objects.bulk_create(bulk_data_file)
        return True
    except Exception as err:
        raise serializers.ValidationError({'files': SaleMsg.SAVE_FILES_ERROR + f' {err}'})


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
            ''
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
        attachment = self.initial_data.get('attachment', '')
        if attachment:
            create_files_mapped(ar_invoice, attachment.strip().split(','))

        return ar_invoice


class ARInvoiceDetailSerializer(serializers.ModelSerializer):
    delivery_mapped = serializers.SerializerMethodField()
    item_and_discount_mapped = serializers.SerializerMethodField()
    customer_mapped = serializers.SerializerMethodField()
    sale_order_mapped = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

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
            'item_and_discount_mapped',
            'attachment'
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
            'product': {
                'id': item.product_id,
                'code': item.product.code,
                'title': item.product.title,
            } if item.product else {},
            'product_uom': {
                'id': item.product_uom_id,
                'code': item.product_uom.code,
                'title': item.product_uom.title,
            } if item.product_uom else {},
            'product_quantity': item.product_quantity,
            'product_unit_price': item.product_unit_price,
            'product_tax_value': item.product_tax_value,
            'product_subtotal': item.product_subtotal,
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

    @classmethod
    def get_attachment(cls, obj):
        att_objs = ARInvoiceAttachmentFile.objects.select_related('attachment').filter(ar_invoice=obj)
        return [item.attachment.get_detail() for item in att_objs]


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
        attachment = self.initial_data.get('attachment', '')
        if attachment:
            create_files_mapped(instance, attachment.strip().split(','))

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
