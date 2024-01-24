from rest_framework import serializers
from apps.sales.inventory.models import GoodsReceipt
from apps.sales.apinvoice.models import APInvoice, APInvoiceItems, APInvoiceGoodsReceipt, APInvoiceAttachmentFile
from apps.shared import SaleMsg

__all__ = [
    'GoodsReceiptListSerializerForAPInvoice',
    'APInvoiceListSerializer',
    'APInvoiceCreateSerializer',
    'APInvoiceDetailSerializer',
    'APInvoiceUpdateSerializer'
]


class APInvoiceListSerializer(serializers.ModelSerializer):
    supplier_mapped = serializers.SerializerMethodField()
    po_mapped = serializers.SerializerMethodField()

    class Meta:
        model = APInvoice
        fields = (
            'id',
            'title',
            'code',
            'supplier_mapped',
            'supplier_name',
            'po_mapped',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'system_status'
        )

    @classmethod
    def get_supplier_mapped(cls, obj):
        return {
            'id': obj.supplier_mapped_id,
            'code': obj.supplier_mapped.code,
            'name': obj.supplier_mapped.name
        } if obj.supplier_mapped else {}

    @classmethod
    def get_po_mapped(cls, obj):
        return {
            'id': obj.po_mapped_id,
            'code': obj.po_mapped.code,
            'title': obj.po_mapped.title
        } if obj.po_mapped else {}


def create_goods_receipt_mapped(ap_invoice, gr_mapped_list):
    bulk_data = []
    for item in gr_mapped_list:
        bulk_data.append(APInvoiceGoodsReceipt(ap_invoice=ap_invoice, goods_receipt_mapped_id=item))
    APInvoiceGoodsReceipt.objects.filter(ap_invoice=ap_invoice).delete()
    APInvoiceGoodsReceipt.objects.bulk_create(bulk_data)
    return True


def create_item_mapped(ap_invoice, data_item_list):
    bulk_data = []
    for item in data_item_list:
        bulk_data.append(APInvoiceItems(ap_invoice=ap_invoice, **item))
    APInvoiceItems.objects.filter(ap_invoice=ap_invoice).delete()
    APInvoiceItems.objects.bulk_create(bulk_data)
    return True


def create_files_mapped(ap_invoice, file_id_list):
    try:
        bulk_data_file = []
        for index, file_id in enumerate(file_id_list):
            bulk_data_file.append(APInvoiceAttachmentFile(
                ap_invoice=ap_invoice,
                attachment_id=file_id,
                order=index
            ))
        APInvoiceAttachmentFile.objects.filter(ap_invoice=ap_invoice).delete()
        APInvoiceAttachmentFile.objects.bulk_create(bulk_data_file)
        return True
    except Exception as err:
        raise serializers.ValidationError({'files': SaleMsg.SAVE_FILES_ERROR + f' {err}'})


class APInvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = APInvoice
        fields = (
            'title',
            'supplier_mapped',
            'supplier_name',
            'po_mapped',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'system_status'
        )

    def validate(self, validate_data):
        if validate_data.get('supplier_mapped'):
            if validate_data['supplier_mapped'].name == validate_data['supplier_name']:
                validate_data['supplier_name'] = None
            else:
                validate_data['supplier_mapped'] = None
        return validate_data

    # @decorator_run_workflow
    def create(self, validated_data):
        ap_invoice = APInvoice.objects.create(**validated_data, code=f'AP-00{APInvoice.objects.all().count()+1}')

        create_goods_receipt_mapped(ap_invoice, self.initial_data.get('goods_receipt_mapped_list', []))
        create_item_mapped(
            ap_invoice,
            self.initial_data.get('data_item_list', []),
        )
        attachment = self.initial_data.get('attachment', '')
        if attachment:
            create_files_mapped(ap_invoice, attachment.strip().split(','))

        return ap_invoice


class APInvoiceDetailSerializer(serializers.ModelSerializer):
    goods_receipt_mapped = serializers.SerializerMethodField()
    item_mapped = serializers.SerializerMethodField()
    supplier_mapped = serializers.SerializerMethodField()
    po_mapped = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = APInvoice
        fields = (
            'id',
            'title',
            'code',
            'supplier_mapped',
            'supplier_name',
            'po_mapped',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'system_status',
            'goods_receipt_mapped',
            'item_mapped',
            'attachment'
        )

    @classmethod
    def get_goods_receipt_mapped(cls, obj):
        return [{
            'id': item.goods_receipt_mapped_id,
            'title': item.goods_receipt_mapped.title,
        } for item in obj.ap_invoice_goods_receipts.all()]

    @classmethod
    def get_item_mapped(cls, obj):
        return [{
            'item_index': item.item_index,
            'product_data': {
                'id': item.product_id,
                'code': item.product.code,
                'title': item.product.title,
            } if item.product else {},
            'uom_data': {
                'id': item.product_uom_id,
                'code': item.product_uom.code,
                'title': item.product_uom.title,
            } if item.product_uom else {},
            'quantity_import': item.product_quantity,
            'product_unit_price': item.product_unit_price,
            'product_tax_value': item.product_tax_value,
            'product_subtotal_price': item.product_subtotal,
        } for item in obj.ap_invoice_items.all()]

    @classmethod
    def get_supplier_mapped(cls, obj):
        return {
            'id': obj.supplier_mapped_id,
            'code': obj.supplier_mapped.code,
            'name': obj.supplier_mapped.name,
        } if obj.supplier_mapped else {}

    @classmethod
    def get_po_mapped(cls, obj):
        return {
            'id': obj.po_mapped_id,
            'code': obj.po_mapped.code,
            'title': obj.po_mapped.title,
        } if obj.po_mapped else {}

    @classmethod
    def get_attachment(cls, obj):
        att_objs = APInvoiceAttachmentFile.objects.select_related('attachment').filter(ap_invoice=obj)
        return [item.attachment.get_detail() for item in att_objs]


class APInvoiceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = APInvoice
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

        create_goods_receipt_mapped(instance, self.initial_data.get('goods_receipt_mapped_list', []))
        create_item_mapped(
            instance,
            self.initial_data.get('data_item_list', [])
        )
        attachment = self.initial_data.get('attachment', '')
        if attachment:
            create_files_mapped(instance, attachment.strip().split(','))

        return instance


class GoodsReceiptListSerializerForAPInvoice(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    purchase_order = serializers.SerializerMethodField()
    already = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'id',
            'title',
            'code',
            'goods_receipt_type',
            'purchase_order',
            'date_received',
            'system_status',
            'details',
            'already'
        )

    @classmethod
    def get_purchase_order(cls, obj):
        return {
            'id': obj.purchase_order_id,
            'title': obj.purchase_order.title,
            'code': obj.purchase_order.code,
            'detail': [{
                'product_id': item.product_id,
                'product_quantity_order_actual': item.product_quantity_order_actual
            } for item in obj.purchase_order.purchase_order_product_order.all()]
        } if obj.purchase_order else {}

    @classmethod
    def get_details(cls, obj):
        return [{
            'product_data': {
                'id': item.product_id,
                'code': item.product.code,
                'title': item.product.title
            },
            'uom_data': {
                'id': item.uom_id,
                'code': item.uom.code,
                'title': item.uom.title
            },
            'quantity_import': item.quantity_import,
            'product_unit_price': item.product_unit_price,
            'product_subtotal_price': item.product_subtotal_price,
            'product_subtotal_price_after_tax': item.product_subtotal_price_after_tax,
            'order': item.order
        } for item in obj.goods_receipt_product_goods_receipt.all()]

    @classmethod
    def get_already(cls, obj):
        return APInvoiceGoodsReceipt.objects.filter(goods_receipt_mapped=obj).count()
