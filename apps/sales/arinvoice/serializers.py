import hashlib
import uuid
import time
import json
import base64
from datetime import datetime
import requests

from rest_framework import serializers
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.arinvoice.models import ARInvoice, ARInvoiceDelivery, ARInvoiceItems, ARInvoiceAttachmentFile, \
    ARInvoiceSign
from apps.shared import SaleMsg

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


def create_item_mapped(ar_invoice, data_item_list):
    bulk_data = []
    for item in data_item_list:
        bulk_data.append(ARInvoiceItems(ar_invoice=ar_invoice, **item))
    ARInvoiceItems.objects.filter(ar_invoice=ar_invoice).delete()
    item_mapped = ARInvoiceItems.objects.bulk_create(bulk_data)
    return item_mapped


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


def read_money_vnd(num):
    text1 = ' mươi'
    text2 = ' trăm'

    xe0 = ['', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']
    xe1 = ['', 'mười'] + [f'{pre}{text1}' for pre in xe0[2:]]
    xe2 = [''] + [f'{pre}{text2}' for pre in xe0[1:]]

    result = ""
    str_n = str(num)
    len_n = len(str_n)

    if len_n == 1:
        result = xe0[num]
    elif len_n == 2:
        if num == 10:
            result = "mười"
        else:
            result = xe1[int(str_n[0])] + " " + xe0[int(str_n[1])]
    elif len_n == 3:
        result = xe2[int(str_n[0])] + " " + read_money_vnd(int(str_n[1:]))
    elif len_n <= 6:
        result = read_money_vnd(int(str_n[:-3])) + " nghìn, " + read_money_vnd(int(str_n[-3:]))
    elif len_n <= 9:
        result = read_money_vnd(int(str_n[:-6])) + " triệu, " + read_money_vnd(int(str_n[-6:]))
    elif len_n <= 12:
        result = read_money_vnd(int(str_n[:-9])) + " tỷ, " + read_money_vnd(int(str_n[-9:]))

    return result.strip().capitalize()


class ARInvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARInvoice
        fields = (
            'title',
            'customer_mapped',
            'sale_order_mapped',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'system_status',

            'customer_code',
            'customer_name',
            'buyer_name',
            'customer_tax_number',
            'customer_billing_address',
            'customer_bank_code',
            'customer_bank_number',
        )

    def validate(self, validate_data):
        if not validate_data.get('sale_order_mapped'):
            validate_data['is_free_input'] = True
        return validate_data

    # @decorator_run_workflow
    def create(self, validated_data):
        ar_invoice = ARInvoice.objects.create(**validated_data, code=f'AR-00{ARInvoice.objects.all().count()+1}')

        create_delivery_mapped(ar_invoice, self.initial_data.get('delivery_mapped_list', []))
        create_item_mapped(
            ar_invoice,
            self.initial_data.get('data_item_list', [])
        )
        attachment = self.initial_data.get('attachment', '')
        if attachment:
            create_files_mapped(ar_invoice, attachment.strip().split(','))

        return ar_invoice


class ARInvoiceDetailSerializer(serializers.ModelSerializer):
    delivery_mapped = serializers.SerializerMethodField()
    item_mapped = serializers.SerializerMethodField()
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
            'is_created_einvoice',
            'delivery_mapped',
            'item_mapped',
            'attachment',

            'is_free_input',
            'customer_code',
            'customer_name',
            'buyer_name',
            'customer_tax_number',
            'customer_billing_address',
            'customer_bank_code',
            'customer_bank_number',
        )

    @classmethod
    def get_delivery_mapped(cls, obj):
        return [{
            'id': item.delivery_mapped_id,
            'title': item.delivery_mapped.title,
        } if item.delivery_mapped else {} for item in obj.ar_invoice_deliveries.all()]

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
                'group_id': item.product_uom.group_id
            } if item.product_uom else {},
            'product_quantity': item.product_quantity,
            'product_unit_price': item.product_unit_price,
            'product_subtotal': item.product_subtotal,
            'product_discount_rate': item.product_discount_rate,
            'product_discount_value': item.product_discount_value,
            'product_tax': {
                'id': item.product_tax_id,
                'code': item.product_tax.code,
                'title': item.product_tax.title,
                'rate': item.product_tax.rate,
            } if item.product_tax else {},
            'product_tax_value': item.product_tax_value,
            'product_subtotal_final': item.product_subtotal_final
        } for item in obj.ar_invoice_items.all()]

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
            'system_status',

            'customer_code',
            'customer_name',
            'buyer_name',
            'customer_tax_number',
            'customer_billing_address',
            'customer_bank_code',
            'customer_bank_number',
        )

    @classmethod
    def process_value_xml(cls, instance, amount):
        billing_address = instance.customer_mapped.account_mapped_billing_address.filter(
            is_default=True
        ).first() if instance.customer_mapped else None
        cus_address = (
            f"{billing_address.account_name}, {billing_address.account_address}"
        ) if billing_address else instance.customer_billing_address
        bank_code = instance.customer_mapped.account_banks_mapped.filter(
            is_default=True
        ).first().bank_name if instance.customer_mapped else instance.customer_bank_code
        bank_number = instance.customer_mapped.account_banks_mapped.filter(
            is_default=True
        ).first().bank_account_number if instance.customer_mapped else instance.customer_bank_code
        money_text = read_money_vnd(int(amount))
        money_text = money_text[:-1] if money_text[-1] == ',' else money_text

        buyer_name = ''
        if instance.buyer_name:
            buyer_name = instance.buyer_name
        elif instance.customer_name:
            buyer_name = instance.customer_name
        elif instance.customer_mapped:
            buyer_name = instance.customer_mapped.name

        return [cus_address, bank_code, bank_number, money_text, buyer_name]

    @classmethod
    def create_xml(cls, instance, item_mapped, pattern):
        count = 1
        product_xml = ''
        total = 0
        vat = 0
        amount = 0
        discount = 0
        number_vat = []
        for item in item_mapped:
            if float(item.product_quantity) > 0:
                total += float(item.product_subtotal)
                vat += float(item.product_tax_value)
                amount += float(item.product_subtotal_final)
                if item.product_tax_id:
                    number_vat.append(item.product_tax.rate)
                product_xml += (
                    "<Product>"
                    f"<Code>{item.product.code}</Code>"
                    f"<No>{count}</No>"
                    f"<Feature>1</Feature>"
                    f"<ProdName>{item.product.title}</ProdName>"
                    f"<ProdUnit>{item.product_uom.title}</ProdUnit>"
                    f"<ProdQuantity>{item.product_quantity}</ProdQuantity>"
                    f"<ProdPrice>{item.product_unit_price}</ProdPrice>"
                    f"<Discount></Discount>"
                    f"<DiscountAmount></DiscountAmount>"
                    f"<Total>{item.product_subtotal}</Total>"
                    f"<VATRate>{int(item.product_tax.rate) if item.product_tax_id else 0}</VATRate>"
                    f"<VATAmount>{item.product_tax_value if item.product_tax_id else 0}</VATAmount>"
                    "<VATRateOther/>"
                    f"<Amount>{item.product_subtotal_final}</Amount>"
                    "<Extra></Extra>"
                    "</Product>"
                )
                if float(item.product_discount_rate) > 0:
                    discount += float(item.product_discount_value)
                    product_xml += (
                        "<Product>"
                        "<Code></Code>"
                        "<No></No>"
                        "<Feature>3</Feature>"
                        f"<ProdName>Chiết khấu {item.product_discount_rate}% "
                        f"(cho sản phẩm {item.product.title})</ProdName>"
                        "<ProdUnit></ProdUnit>"
                        "<ProdQuantity></ProdQuantity>"
                        "<ProdPrice></ProdPrice>"
                        "<Discount></Discount>"
                        "<DiscountAmount></DiscountAmount>"
                        f"<Total>{float(item.product_discount_value) * -1}</Total>"
                        "<VATRate>-1</VATRate>"
                        "<VATAmount>0</VATAmount>"
                        "<VATRateOther/>"
                        f"<Amount>{float(item.product_discount_value) * -1}</Amount>"
                        "<Extra></Extra>"
                        "</Product>"
                    )
                count += 1
        number_vat = list(set(number_vat))

        if len(number_vat) > 0 and instance.invoice_example == 2:
            raise serializers.ValidationError({'Error': "Product rows in sales invoice can not have VAT (API)."})

        value_xml = cls.process_value_xml(instance, amount)
        # [cus_address, bank_code, bank_number, money_text, buyer_name]

        return (
            "<Invoices>"
            "<Inv>"
            "<Invoice>"
            f"<Ikey>{instance.id}-{pattern}</Ikey>"
            f"<InvNo>{instance.invoice_number}</InvNo>"
            "<CusCode>"
            f"{instance.customer_mapped.code if instance.customer_mapped else instance.customer_code}"
            "</CusCode>"
            f"<Buyer>{value_xml[4]}</Buyer>"
            "<CusName>"
            f"{instance.customer_mapped.name if instance.customer_mapped else instance.customer_name}"
            "</CusName>"
            f"<Email>{instance.customer_mapped.email if instance.customer_mapped else ''}</Email>"
            "<EmailCC></EmailCC>"
            f"<CusAddress>{value_xml[0]}</CusAddress>"
            f"<CusBankName>{value_xml[1]}</CusBankName>"
            f"<CusBankNo>{value_xml[2]}</CusBankNo>"
            f"<CusPhone>{instance.customer_mapped.phone if instance.customer_mapped else ''}</CusPhone>"
            "<CusTaxCode>"
            f"{instance.customer_mapped.tax_code if instance.customer_mapped else instance.customer_tax_number}"
            "</CusTaxCode>"
            "<PaymentMethod>Tiền mặt/Chuyển khoản</PaymentMethod>"
            "<ArisingDate>"
            f"{datetime.strptime(str(instance.document_date), '%Y-%m-%d 00:00:00').strftime('%d/%m/%Y')}"
            "</ArisingDate>"
            "<ExchangeRate></ExchangeRate>"
            "<CurrencyUnit>"
            f"{instance.customer_mapped.currency.abbreviation if instance.customer_mapped else 'VND'}"
            "</CurrencyUnit>"
            "<Extra></Extra>"

            f"<Products>{product_xml}</Products>"

            f"<Total>{total - discount}</Total>"
            f"<VATRate>{int(vat * 100 / (total - discount)) if len(number_vat) == 1 else 0}</VATRate>"
            f"<VATAmount>{vat}</VATAmount>"
            "<VATRateOther/>"
            f"<Amount>{amount}</Amount>"
            f"<AmountInWords>{value_xml[3]} đồng</AmountInWords>"
            "</Invoice>"
            "</Inv>"
            "</Invoices>"
        )

    @classmethod
    def create_update_invoice(cls, instance, item_mapped):
        xml_data = cls.create_xml(instance, item_mapped, instance.invoice_sign)

        token = generate_token("POST", "API", "Api@0317493763")
        headers = {"Authentication": f"{token}", "Content-Type": "application/json"}

        response = requests.post(
            "http://0317493763.softdreams.vn/api/publish/importInvoice",
            headers=headers,
            json={
                "XmlData": xml_data,
                "Pattern": instance.invoice_sign,
                "Serial": ""
            },
            timeout=60
        )
        if response.status_code != 200:
            raise serializers.ValidationError(
                {'Error': f"Create/Update Invoice Failed. {json.loads(response.text).get('Message', '')}"}
            )

        instance.is_created_einvoice = True
        if not instance.buyer_name:
            instance.buyer_name = instance.customer_mapped.name
        instance.save(update_fields=['is_created_einvoice', 'buyer_name'])
        return response.status_code

    def validate(self, validate_data):
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        create_delivery_mapped(instance, self.initial_data.get('delivery_mapped_list', []))
        item_mapped = create_item_mapped(
            instance,
            self.initial_data.get('data_item_list', [])
        )
        attachment = self.initial_data.get('attachment', '')
        if attachment:
            create_files_mapped(instance, attachment.strip().split(','))

        if 'create_invoice' in self.initial_data:
            self.create_update_invoice(instance, item_mapped)

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
                'tax',
                'product_tax_title',
                'product_tax_value',
                'product_tax_amount',
            ))[0]
        } for item in obj.delivery_product_delivery_sub.all()]

    @classmethod
    def get_already(cls, obj):
        return ARInvoiceDelivery.objects.filter(delivery_mapped=obj).exists()


class ARInvoiceSignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARInvoiceSign
        fields = (
            'one_vat_sign',
            'many_vat_sign',
            'sale_invoice_sign'
        )

    def validate(self, validate_data):
        valid_lengths = (2, 0)
        valid_len_one_vat = len(validate_data.get('one_vat_sign')) not in valid_lengths
        valid_len_many_vat = len(validate_data.get('many_vat_sign')) not in valid_lengths
        valid_len_sale_invoice_sign = len(validate_data.get('sale_invoice_sign')) not in valid_lengths
        if valid_len_one_vat or valid_len_many_vat or valid_len_sale_invoice_sign:
            raise serializers.ValidationError({'Error': 'Sign must have only 2 letters.'})

        this_year = str(datetime.now().year)[2:]
        if len(validate_data.get('one_vat_sign')) == 2:
            validate_data['one_vat_sign'] = f'1C{this_year}T' + validate_data.get('one_vat_sign')
        if len(validate_data.get('many_vat_sign')) == 2:
            validate_data['many_vat_sign'] = f'1C{this_year}T' + validate_data.get('many_vat_sign')
        if len(validate_data.get('sale_invoice_sign')) == 2:
            validate_data['sale_invoice_sign'] = f'2C{this_year}T' + validate_data.get('sale_invoice_sign')
        return validate_data

    def create(self, validated_data):
        tenant_id = self.context.get('tenant_id', None)
        company_id = self.context.get('company_id', None)
        ARInvoiceSign.objects.filter(tenant_id=tenant_id, company_id=company_id).delete()
        sign = ARInvoiceSign.objects.create(**validated_data)

        return sign


class ARInvoiceSignListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARInvoiceSign
        fields = (
            'one_vat_sign',
            'many_vat_sign',
            'sale_invoice_sign',
            'tenant',
            'company'
        )


class ARInvoiceSignDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARInvoiceSign
        fields = (
            'one_vat_sign',
            'many_vat_sign',
            'sale_invoice_sign',
            'tenant',
            'company'
        )
