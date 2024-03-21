import hashlib
import uuid
import time
import base64
import requests
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

from apps.sales.saleorder.models import SaleOrderProduct

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


def create_item_mapped(ar_invoice, data_item_list, data_discount_list):
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


def generate_token(http_method, username, password):
    epoch_start = 0
    timestamp = str(int(time.time() - epoch_start))
    nonce = uuid.uuid4().hex
    signature_raw_data = http_method.upper() + timestamp + nonce

    md5 = hashlib.md5()
    md5.update(signature_raw_data.encode('utf-8'))
    signature = base64.b64encode(md5.digest()).decode('utf-8')

    return f"{signature}:{nonce}:{timestamp}:{username}:{password}"


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
        create_item_mapped(
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
    item_mapped = serializers.SerializerMethodField()
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
            'item_mapped',
            'attachment'
        )

    @classmethod
    def get_delivery_mapped(cls, obj):
        return [{
            'id': item.delivery_mapped_id,
            'title': item.delivery_mapped.title,
        } for item in obj.ar_invoice_deliveries.all()]

    @classmethod
    def get_item_mapped(cls, obj):
        return [{
            'item_index': item.item_index,
            'product': {
                'id': item.product_id,
                'code': item.product.code,
                'title': item.product.title,
                'des': item.product.description,
            } if item.product else {},
            'product_uom': {
                'id': item.product_uom_id,
                'code': item.product_uom.code,
                'title': item.product_uom.title,
            } if item.product_uom else {},
            'product_quantity': item.product_quantity,
            'product_unit_price': item.product_unit_price,
            'product_subtotal': item.product_subtotal,
            'product_discount_rate': item.product_discount_rate,
            'product_discount_value': item.product_discount_value,
            'product_tax_rate': item.product_tax_rate,
            'product_tax_title': item.product_tax_title,
            'product_tax_value': item.product_tax_value,
            'product_subtotal_final': item.product_subtotal_final
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
        create_item_mapped(
            instance,
            self.initial_data.get('data_item_list', []),
            self.initial_data.get('data_discount_list', [])
        )
        attachment = self.initial_data.get('attachment', '')
        if attachment:
            create_files_mapped(instance, attachment.strip().split(','))

        if 'publish_invoice' in self.initial_data:
            http_method = "POST"
            username = "API"
            password = "Api@0317493763"
            token = generate_token(http_method, username, password)
            response = requests.post(
                "http://0317493763.softdreams.vn/api/publish/importInvoice",
                data={
                    "XmlData": "<Invoices>"
                               "<Inv>"
                               "<Invoice>"
                               "<Ikey>7a61aaf7-a766-4d4a-b710-2fa6e1aa4a1f</Ikey>"
                               "<CusCode>TEST1</CusCode>"
                               "<Buyer>System Admin</Buyer>"
                               "<CusName>Công ty Test 1</CusName>"
                               "<Email>nguyenduonghai07@gmail.com</Email>"
                               "<EmailCC></EmailCC>"
                               "<CusAddress>TPHCM, số 20 đường 22, xã Bình Chánh</CusAddress>"
                               "<CusBankName>MB Bank</CusBankName>"
                               "<CusBankNo>8608603112001</CusBankNo>"
                               "<CusPhone>0359610773</CusPhone>"
                               "<CusTaxCode>8807436399</CusTaxCode>"
                               "<PaymentMethod>Chuyển khoản</PaymentMethod>"
                               "<ArisingDate></ArisingDate>"
                               "<ExchangeRate></ExchangeRate>"
                               "<CurrencyUnit>VND</CurrencyUnit>"
                               "<Extra></Extra>"
                               "<Products>"
                               "<Product>"
                               "<Code>CANON EF 24-70MM</Code>"
                               "<No>1</No>"
                               "<Feature>1</Feature>"
                               "<ProdName>Ống kính Canon EF 24-70mm f/2.8L II USM</ProdName>"
                               "<ProdUnit>Cái</ProdUnit>"
                               "<ProdQuantity>3</ProdQuantity>"
                               "<ProdPrice>32000000</ProdPrice>"
                               "<Discount></Discount>"
                               "<DiscountAmount></DiscountAmount>"
                               "<Total>96000000</Total>"
                               "<VATRate>10</VATRate>"
                               "<VATRateOther/>"
                               "<VATAmount>9600000</VATAmount>"
                               "<Amount>105600000</Amount>"
                               "<Extra></Extra>"
                               "</Product>"
                               "</Products>"
                               "<Total>96000000</Total>"
                               "<VATRate>10</VATRate>"
                               "<VATRateOther/>"
                               "<VATAmount>9600000</VATAmount>"
                               "<Amount>105600000</Amount>"
                               "<AmountInWords>Một trăm lẻ năm triệu sáu trăm ngàn đồng</AmountInWords>"
                               "</Invoice>"
                               "</Inv>"
                               "</Invoices>",
                    "Pattern": "1C24TMT",
                    "Serial": ""
                },
                timeout=60
            )

        return instance


class DeliveryListSerializerForARInvoice(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    already = serializers.SerializerMethodField()
    sum_tax = serializers.SerializerMethodField()
    sum_discount = serializers.SerializerMethodField()
    sum_discount_rate = serializers.SerializerMethodField()

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
            'details',
            'sum_tax',
            'sum_discount',
            'sum_discount_rate'
        )

    @classmethod
    def get_sum_tax(cls, obj):
        return obj.order_delivery.sale_order.total_product_tax

    @classmethod
    def get_sum_discount(cls, obj):
        return obj.order_delivery.sale_order.total_product_discount

    @classmethod
    def get_sum_discount_rate(cls, obj):
        return obj.order_delivery.sale_order.total_product_discount_rate

    @classmethod
    def get_details(cls, obj):
        return [{
            'product_data': item.product_data,
            'uom_data': item.uom_data,
            'delivery_quantity': item.delivery_quantity,
            'delivered_quantity_before': item.delivered_quantity_before,
            'picked_quantity': item.picked_quantity,
            'data_from_so': list(obj.order_delivery.sale_order.sale_order_product_sale_order.filter(
                order=item.order
            ).values(
                'product_description',
                'product_unit_price',
                'product_discount_value',
                'product_discount_amount',
                'product_tax_title',
                'product_tax_value',
                'product_tax_amount',
            ))[0]
        } for item in obj.delivery_product_delivery_sub.all()]

    @classmethod
    def get_already(cls, obj):
        return ARInvoiceDelivery.objects.filter(delivery_mapped=obj).exists()
