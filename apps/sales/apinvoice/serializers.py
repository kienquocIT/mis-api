from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, Product, UnitOfMeasure, Tax
from apps.sales.inventory.models import GoodsReceipt
from apps.sales.apinvoice.models import APInvoice, APInvoiceItems, APInvoiceGoodsReceipt, APInvoiceAttachmentFile
from apps.sales.purchasing.models import PurchaseOrder
from apps.shared import (
    SaleMsg, AbstractCreateSerializerModel, AbstractListSerializerModel, AbstractDetailSerializerModel
)

__all__ = [
    'APInvoiceListSerializer',
    'APInvoiceCreateSerializer',
    'APInvoiceDetailSerializer',
    'APInvoiceUpdateSerializer',
    'PurchaseOrderListSerializerForAPInvoice',
    'GoodsReceiptListSerializerForAPInvoice',
]


class APInvoiceListSerializer(AbstractListSerializerModel):
    class Meta:
        model = APInvoice
        fields = (
            'id',
            'title',
            'code',
            'supplier_mapped_data',
            'purchase_order_mapped_data',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'date_created'
        )


class APInvoiceCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    supplier_mapped = serializers.UUIDField()
    purchase_order_mapped = serializers.UUIDField(allow_null=True)
    goods_receipt_mapped_list = serializers.JSONField(default=list)
    data_item_list = serializers.JSONField(default=list)

    class Meta:
        model = APInvoice
        fields = (
            'title',
            'supplier_mapped',
            'purchase_order_mapped',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'note',
            'goods_receipt_mapped_list',
            'data_item_list',
        )

    @classmethod
    def validate_supplier_mapped(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'supplier_mapped': "Supplier does not exist."})

    @classmethod
    def validate_purchase_order_mapped(cls, value):
        if value:
            try:
                return PurchaseOrder.objects.get(id=value)
            except PurchaseOrder.DoesNotExist:
                raise serializers.ValidationError({'purchase_order_mapped': "Purchase order does not exist."})
        return None

    @classmethod
    def validate_goods_receipt_mapped_list(cls, goods_receipt_mapped_list):
        try:
            parse_data_goods_receipt_mapped_list = []
            for delivery_id in goods_receipt_mapped_list:
                gr_obj = GoodsReceipt.objects.get(id=delivery_id)
                parse_data_goods_receipt_mapped_list.append({
                    'goods_receipt_mapped': gr_obj,
                    'goods_receipt_mapped_data': {
                        'id': str(gr_obj.id),
                        'code': gr_obj.code,
                        'title': gr_obj.title,
                    }
                })
            return parse_data_goods_receipt_mapped_list
        except GoodsReceipt.DoesNotExist:
            raise serializers.ValidationError({'goods_receipt_mapped_list': "Goods receipt does not exist."})

    def validate(self, validate_data):
        # parse data supplier_mapped
        supplier_mapped = validate_data.get('supplier_mapped')
        if supplier_mapped:
            validate_data['supplier_mapped_data'] = {
                'id': str(supplier_mapped.id),
                'code': supplier_mapped.code,
                'name': supplier_mapped.name,
                'tax_code': supplier_mapped.tax_code,
            }
        # parse data purchase_order_mapped
        purchase_order_mapped = validate_data.get('purchase_order_mapped')
        if purchase_order_mapped:
            validate_data['purchase_order_mapped_data'] = {
                'id': str(purchase_order_mapped.id),
                'code': purchase_order_mapped.code,
                'title': purchase_order_mapped.title,
                'purchase_order_payment_stage': []
            }
        # check valid data data_item_list
        for item in validate_data.get('data_item_list', []):
            product_obj = Product.objects.filter(id=item.get('product_id')).first()
            uom_obj = UnitOfMeasure.objects.filter(id=item.get('product_uom_id')).first()
            tax_obj = Tax.objects.filter(id=item.get('product_tax_id')).first()
            if any([
                product_obj is None,
                uom_obj is None,
                float(item.get('product_quantity', 0)) <= 0,
                float(item.get('product_unit_price', 0)) <= 0,
                float(item.get('product_subtotal', 0)) <= 0,
            ]):
                raise serializers.ValidationError({'data_item_list': "Data items are not valid."})
            item['product_data'] = {
                'id': str(product_obj.id),
                'code': product_obj.code,
                'title': product_obj.title,
                'description': product_obj.description,
            } if product_obj else {}
            item['product_uom_data'] = {
                'id': str(uom_obj.id),
                'code': uom_obj.code,
                'title': uom_obj.title,
                'group_id': str(uom_obj.group_id)
            } if uom_obj else {}
            item['product_tax_data'] = {
                'id': str(tax_obj.id),
                'code': tax_obj.code,
                'title': tax_obj.title,
                'rate': tax_obj.rate,
            } if tax_obj else {}
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        goods_receipt_mapped_list = validated_data.pop('goods_receipt_mapped_list', [])
        data_item_list = validated_data.pop('data_item_list', [])

        ap_invoice = APInvoice.objects.create(**validated_data)

        APInvoiceCommonFunc.create_goods_receipt_mapped(ap_invoice, goods_receipt_mapped_list)
        APInvoiceCommonFunc.create_item_mapped(ap_invoice, data_item_list)

        attachment = self.initial_data.get('attachment', '')
        if attachment:
            APInvoiceCommonFunc.create_files_mapped(ap_invoice, attachment.strip().split(','))

        return ap_invoice


class APInvoiceDetailSerializer(AbstractDetailSerializerModel):
    goods_receipt_mapped = serializers.SerializerMethodField()
    item_mapped = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = APInvoice
        fields = (
            'id',
            'title',
            'code',
            'supplier_mapped_data',
            'purchase_order_mapped_data',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'goods_receipt_mapped',
            'item_mapped',
            'attachment',
            'note',
        )

    @classmethod
    def get_goods_receipt_mapped(cls, obj):
        return [{
            'id': item.goods_receipt_mapped_id,
            'code': item.goods_receipt_mapped.code,
            'title': item.goods_receipt_mapped.title,
        } for item in obj.ap_invoice_goods_receipts.all()]

    @classmethod
    def get_item_mapped(cls, obj):
        return [{
            'id': item.id,
            'item_index': item.item_index,
            'product_data': item.product_data,
            'product_uom_data': item.product_uom_data,
            'product_quantity': item.product_quantity,
            'product_unit_price': item.product_unit_price,
            'product_subtotal': item.product_subtotal,
            'product_tax_data': item.product_tax_data,
            'product_tax_value': item.product_tax_value,
            'product_subtotal_final': item.product_subtotal_final,
            'note': item.note,
            'increased_FA_value': item.increased_FA_value,
        } for item in obj.ap_invoice_items.all()]

    @classmethod
    def get_attachment(cls, obj):
        att_objs = APInvoiceAttachmentFile.objects.select_related('attachment').filter(ap_invoice=obj)
        return [item.attachment.get_detail() for item in att_objs]


class APInvoiceUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    supplier_mapped = serializers.UUIDField()
    purchase_order_mapped = serializers.UUIDField(allow_null=True)
    goods_receipt_mapped_list = serializers.JSONField(default=list)
    data_item_list = serializers.JSONField(default=list)

    class Meta:
        model = APInvoice
        fields = (
            'title',
            'supplier_mapped',
            'purchase_order_mapped',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'note',
            'goods_receipt_mapped_list',
            'data_item_list',
        )

    @classmethod
    def validate_supplier_mapped(cls, value):
        return APInvoiceCreateSerializer.validate_supplier_mapped(value)

    @classmethod
    def validate_purchase_order_mapped(cls, value):
        return APInvoiceCreateSerializer.validate_purchase_order_mapped(value)

    @classmethod
    def validate_goods_receipt_mapped_list(cls, goods_receipt_mapped_list):
        return APInvoiceCreateSerializer.validate_goods_receipt_mapped_list(goods_receipt_mapped_list)

    def validate(self, validate_data):
        return APInvoiceCreateSerializer().validate(validate_data)

    @decorator_run_workflow
    def update(self, instance, validated_data):
        goods_receipt_mapped_list = validated_data.pop('goods_receipt_mapped_list', [])
        data_item_list = validated_data.pop('data_item_list', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        APInvoiceCommonFunc.create_goods_receipt_mapped(instance, goods_receipt_mapped_list)
        APInvoiceCommonFunc.create_item_mapped(instance, data_item_list)

        attachment = self.initial_data.get('attachment', '')
        if attachment:
            APInvoiceCommonFunc.create_files_mapped(instance, attachment.strip().split(','))

        return instance


class APInvoiceCommonFunc:
    @staticmethod
    def create_goods_receipt_mapped(ap_invoice, gr_mapped_list):
        bulk_data = []
        for item in gr_mapped_list:
            bulk_data.append(APInvoiceGoodsReceipt(ap_invoice=ap_invoice, **item))
        APInvoiceGoodsReceipt.objects.filter(ap_invoice=ap_invoice).delete()
        APInvoiceGoodsReceipt.objects.bulk_create(bulk_data)
        return True

    @staticmethod
    def create_item_mapped(ap_invoice, data_item_list):
        bulk_data = []
        sum_pretax_value = 0
        sum_tax_value = 0
        sum_after_tax_value = 0
        for item in data_item_list:
            bulk_data.append(APInvoiceItems(ap_invoice=ap_invoice, **item))
            sum_pretax_value += float(item.get('product_subtotal', 0))
            sum_tax_value += float(item.get('product_tax_value', 0))
            sum_after_tax_value += float(item.get('product_subtotal_final', 0))
        APInvoiceItems.objects.filter(ap_invoice=ap_invoice).delete()
        items_mapped = APInvoiceItems.objects.bulk_create(bulk_data)
        ap_invoice.sum_pretax_value = sum_pretax_value
        ap_invoice.sum_tax_value = sum_tax_value
        ap_invoice.sum_after_tax_value = sum_after_tax_value
        ap_invoice.save(
            update_fields=['sum_pretax_value', 'sum_tax_value', 'sum_after_tax_value']
        )
        return items_mapped

    @staticmethod
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


# related serializers
class PurchaseOrderListSerializerForAPInvoice(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrder
        fields = (
            'id',
            'title',
            'code',
        )


class GoodsReceiptListSerializerForAPInvoice(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    already = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'id',
            'title',
            'code',
            'goods_receipt_type',
            'purchase_order_data',
            'date_received',
            'system_status',
            'details',
            'already'
        )

    @classmethod
    def get_details(cls, obj):
        return [{
            'product_id': str(item.product_id),
            'product_data': item.product_data,
            'product_unit_price': item.product_unit_price,
            'product_tax_data': item.tax_data,
            'product_uom_data': item.uom_data,
            'gr_quantity': item.product_quantity_order_actual,
            'product_quantity': item.quantity_import,
            'product_subtotal': item.quantity_import * item.product_unit_price,
            'product_tax_value': item.quantity_import * item.product_unit_price * (
                item.tax.rate / 100 if item.tax else 0
            ),
            'product_subtotal_final': item.quantity_import * item.product_unit_price * (
                    1 + (item.tax.rate / 100 if item.tax else 0)
            )
        } for item in obj.goods_receipt_product_goods_receipt.all()]

    @classmethod
    def get_already(cls, obj):
        return obj.has_ap_invoice_already
