import hashlib
import uuid
import time
import json
import base64
from datetime import datetime
import requests
from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.recurrence.models import Recurrence
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.arinvoice.models import (
    ARInvoice, ARInvoiceDelivery, ARInvoiceItems, ARInvoiceAttachmentFile, ARInvoiceSign
)
from apps.sales.leaseorder.models import LeaseOrder
from apps.sales.saleorder.models import SaleOrder
from apps.shared import SerializerCommonHandle


__all__ = [
    'ARInvoiceCommonFunc',
    'SaleOrderListSerializerForARInvoice',
    'LeaseOrderListSerializerForARInvoice',
    'DeliveryListSerializerForARInvoice',
    'ARInvoiceSignListSerializer',
    'ARInvoiceSignCreateSerializer',
    'ARInvoiceSignDetailSerializer',
    'ARInvoiceRecurrenceListSerializer'
]


class ARInvoiceCommonFunc:
    @staticmethod
    def create_delivery_mapped(ar_invoice_obj, delivery_mapped_list):
        bulk_data = []
        for item in delivery_mapped_list:
            bulk_data.append(ARInvoiceDelivery(ar_invoice=ar_invoice_obj, **item))
        ARInvoiceDelivery.objects.filter(ar_invoice=ar_invoice_obj).delete()
        ARInvoiceDelivery.objects.bulk_create(bulk_data)
        return True

    @staticmethod
    def create_items_mapped(ar_invoice_obj, data_item_list):
        bulk_data = []
        sum_pretax_value = 0
        sum_discount_value = 0
        sum_tax_value = 0
        sum_after_tax_value = 0
        for order, item in enumerate(data_item_list):
            bulk_data.append(ARInvoiceItems(ar_invoice=ar_invoice_obj, order=order, **item))
            sum_pretax_value += float(item.get('product_payment_value', 0))
            sum_discount_value += float(item.get('product_discount_value', 0))
            sum_tax_value += float(item.get('product_tax_value', 0))
            sum_after_tax_value += float(item.get('product_subtotal_final', 0))
        ARInvoiceItems.objects.filter(ar_invoice=ar_invoice_obj).delete()
        ARInvoiceItems.objects.bulk_create(bulk_data)
        ar_invoice_obj.sum_pretax_value = sum_pretax_value
        ar_invoice_obj.sum_discount_value = sum_discount_value
        ar_invoice_obj.sum_tax_value = sum_tax_value
        ar_invoice_obj.sum_after_tax_value = sum_after_tax_value
        ar_invoice_obj.save(
            update_fields=['sum_pretax_value', 'sum_discount_value', 'sum_tax_value', 'sum_after_tax_value']
        )
        return True

    @staticmethod
    def create_files_mapped(ar_invoice_obj, attachment_list):
        SerializerCommonHandle.handle_attach_file(
            relate_app=Application.objects.filter(id=ARInvoice.get_app_id()).first(),
            model_cls=ARInvoiceAttachmentFile,
            instance=ar_invoice_obj,
            attachment_result=attachment_list,
        )
        return True

    @staticmethod
    def generate_token(http_method, username, password):
        epoch_start = 0
        timestamp = str(int(time.time() - epoch_start))
        nonce = uuid.uuid4().hex
        signature_raw_data = http_method.upper() + timestamp + nonce

        md5 = hashlib.md5()
        md5.update(signature_raw_data.encode('utf-8'))
        signature = base64.b64encode(md5.digest()).decode('utf-8')

        return f"{signature}:{nonce}:{timestamp}:{username}:{password}"

    @classmethod
    def process_value_xml(cls, instance, amount):
        billing_address = instance.customer_mapped.account_mapped_billing_address.filter(
            is_default=True
        ).first() if instance.customer_mapped else None
        cus_address = (
            f"{billing_address.account_name}, {billing_address.account_address}"
        ) if billing_address else ''
        bank_df = instance.customer_mapped.account_banks_mapped.filter(
            is_default=True
        ).first() if instance.customer_mapped else None
        bank_code = bank_df.bank_code if bank_df else ''
        bank_number = bank_df.bank_account_number if bank_df else ''
        if not (bank_code and bank_number):
            raise serializers.ValidationError({'error': "Can not find bank information."})

        money_text = ARInvoiceCommonFunc.read_money_vnd(int(amount))
        money_text = money_text[:-1] if money_text[-1] == ',' else money_text

        buyer_information = ''
        if instance.buyer_information:
            buyer_information = instance.buyer_information
        elif instance.customer_mapped:
            buyer_information = instance.customer_mapped.name

        return [cus_address, bank_code, bank_number, money_text, buyer_information]

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
                    "<ProdPrice>"
                    f"{(float(item.product_subtotal)-float(item.product_discount_value))/float(item.product_quantity)}"
                    "</ProdPrice>"
                    f"<Discount></Discount>"
                    f"<DiscountAmount></DiscountAmount>"
                    f"<Total>{float(item.product_subtotal)-float(item.product_discount_value)}</Total>"
                    f"<VATRate>{int(item.product_tax.rate) if item.product_tax_id else 0}</VATRate>"
                    f"<VATAmount>{item.product_tax_value if item.product_tax_id else 0}</VATAmount>"
                    "<VATRateOther/>"
                    f"<Amount>{item.product_subtotal_final}</Amount>"
                    "<Extra></Extra>"
                    "</Product>"
                )
                if float(item.product_discount_value) > 0:
                    discount += float(item.product_discount_value)
                #     product_xml += (
                #         "<Product>"
                #         "<Code></Code>"
                #         "<No></No>"
                #         "<Feature>3</Feature>"
                #         "<ProdName>"
                #         f"Chiết khấu xxx% (cho sản phẩm {item.product.title})"
                #         "</ProdName>"
                #         "<ProdUnit></ProdUnit>"
                #         "<ProdQuantity></ProdQuantity>"
                #         "<ProdPrice></ProdPrice>"
                #         "<Discount></Discount>"
                #         "<DiscountAmount></DiscountAmount>"
                #         f"<Total>{float(item.product_discount_value) * -1}</Total>"
                #         "<VATRate>-1</VATRate>"
                #         "<VATAmount>0</VATAmount>"
                #         "<VATRateOther/>"
                #         f"<Amount>{float(item.product_discount_value) * -1}</Amount>"
                #         "<Extra></Extra>"
                #         "</Product>"
                #     )
                count += 1
        number_vat = list(set(number_vat))

        if len(number_vat) > 0 and instance.invoice_example == 2:
            raise serializers.ValidationError({'error': "Product rows in sales invoice can not have VAT (API)."})

        value_xml = cls.process_value_xml(instance, amount)
        # [cus_address, bank_code, bank_number, money_text, buyer_information]

        return (
            "<Invoices>"
            "<Inv>"
            "<Invoice>"
            f"<Ikey>{instance.id}-{pattern}</Ikey>"
            f"<InvNo>{instance.invoice_number}</InvNo>"
            "<CusCode>"
            f"{instance.customer_mapped.code if instance.customer_mapped else ''}"
            "</CusCode>"
            f"<Buyer>{value_xml[4]}</Buyer>"
            "<CusName>"
            f"{instance.customer_mapped.name if instance.customer_mapped else ''}"
            "</CusName>"
            f"<Email>{instance.customer_mapped.email if instance.customer_mapped else ''}</Email>"
            "<EmailCC></EmailCC>"
            f"<CusAddress>{value_xml[0]}</CusAddress>"
            f"<CusBankName>{value_xml[1]}</CusBankName>"
            f"<CusBankNo>{value_xml[2]}</CusBankNo>"
            f"<CusPhone>{instance.customer_mapped.phone if instance.customer_mapped else ''}</CusPhone>"
            "<CusTaxCode>"
            f"{instance.customer_mapped.tax_code if instance.customer_mapped else ''}"
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

        token = ARInvoiceCommonFunc.generate_token("POST", "API", "Api@0317493763")
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
                {'error': f"Create/Update Invoice Failed. {json.loads(response.text).get('Message', '')}"}
            )

        instance.is_created_einvoice = True
        instance.save(update_fields=['is_created_einvoice'])
        return response.status_code

    @staticmethod
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
            result = xe2[int(str_n[0])] + " " + ARInvoiceCommonFunc.read_money_vnd(int(str_n[1:]))
        elif len_n <= 6:
            result = (ARInvoiceCommonFunc.read_money_vnd(int(str_n[:-3])) +
                      " nghìn, " + ARInvoiceCommonFunc.read_money_vnd(int(str_n[-3:])))
        elif len_n <= 9:
            result = (ARInvoiceCommonFunc.read_money_vnd(int(str_n[:-6])) +
                      " triệu, " + ARInvoiceCommonFunc.read_money_vnd(int(str_n[-6:])))
        elif len_n <= 12:
            result = (ARInvoiceCommonFunc.read_money_vnd(int(str_n[:-9])) +
                      " tỷ, " + ARInvoiceCommonFunc.read_money_vnd(int(str_n[-9:])))

        return result


class SaleOrderListSerializerForARInvoice(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    has_not_ar_delivery = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'title',
            'code',
            'opportunity',
            'sale_order_payment_stage',
            'has_not_ar_delivery'
        )

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
        } if obj.opportunity else {}

    @classmethod
    def get_has_not_ar_delivery(cls, obj):
        return OrderDeliverySub.objects.filter(order_delivery__sale_order=obj, is_done_ar_invoice=False).exists()


class LeaseOrderListSerializerForARInvoice(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    has_not_ar_delivery = serializers.SerializerMethodField()

    class Meta:
        model = LeaseOrder
        fields = (
            'id',
            'title',
            'code',
            'opportunity',
            'lease_payment_stage',
            'has_not_ar_delivery'
        )

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
        } if obj.opportunity else {}

    @classmethod
    def get_has_not_ar_delivery(cls, obj):
        return OrderDeliverySub.objects.filter(order_delivery__lease_order=obj, is_done_ar_invoice=False).exists()


class DeliveryListSerializerForARInvoice(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()

    class Meta:
        model = OrderDeliverySub
        fields = (
            'id',
            'title',
            'code',
            'remarks',
            'sale_order_data',
            'lease_order_data',
            'service_order_data',
            'is_done_ar_invoice',
            'actual_delivery_date',
            'details',
        )

    @classmethod
    def get_details(cls, obj):
        details = []
        so_mapped = obj.sale_order
        lo_mapped = obj.lease_order
        # svo_mapped = obj.service_order
        if so_mapped:
            delivery_data = [{
                'order_id': str(obj.sale_order_id),
                'id': str(item.id),
                'product_data': item.product_data.get('product_data', {}),
                'uom_data': item.uom_data,
                'tax_data': item.tax_data,
                'delivery_quantity': item.delivery_quantity,
                'delivered_quantity_before': item.delivered_quantity_before,
                'picked_quantity': item.picked_quantity,
                'ar_value_done': item.ar_value_done
            } for item in obj.delivery_product_delivery_sub.filter(picked_quantity__gt=0)]

            so_data = [{
                'order_id': str(so_mapped.id),
                'id': str(item.id),
                'product_data': item.product_data.get('product_data', {}),
                'uom_data': item.uom_data,
                'product_quantity': item.product_quantity,
                'product_unit_price': item.product_unit_price,
                'product_subtotal_price': item.product_subtotal_price,
                'product_discount_value': item.product_discount_value,
                'tax_data': item.tax_data,
                'product_tax_value': item.product_tax_value
            } for item in so_mapped.sale_order_product_sale_order.all()]

            details = {
                'delivery_data': delivery_data,
                'order_data': so_data,
            }
        if lo_mapped:
            delivery_data = [{
                'order_id': str(obj.lease_order_id),
                'id': str(item.id),
                'product_data': item.product_data.get('product_data', {}),
                'uom_data': item.uom_data,
                'tax_data': item.tax_data,
                'delivery_quantity': item.delivery_quantity,
                'delivered_quantity_before': item.delivered_quantity_before,
                'picked_quantity': item.picked_quantity,
                'product_quantity_time': item.product_quantity_time,
                'ar_value_done': item.ar_value_done
            } for item in obj.delivery_product_delivery_sub.filter(picked_quantity__gt=0)]

            lo_data = [{
                'order_id': str(lo_mapped.id),
                'id': str(item.id),
                'product_data': item.product_data.get('product_data', {}),
                'uom_data': item.uom_data,
                'product_quantity': item.product_quantity,
                'product_quantity_time': item.product_quantity_time,
                'product_unit_price': item.product_unit_price,
                'product_subtotal_price': item.product_subtotal_price,
                'product_discount_value': item.product_discount_value,
                'tax_data': item.tax_data,
                'product_tax_value': item.product_tax_value
            } for item in lo_mapped.lease_order_product_lease_order.all()]

            details = {
                'delivery_data': delivery_data,
                'order_data': lo_data,
            }
        return details


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
            raise serializers.ValidationError({'error': 'Sign must have only 2 letters.'})

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


class ARInvoiceRecurrenceListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    recurrence_list = serializers.SerializerMethodField()

    class Meta:
        model = ARInvoice
        fields = (
            'id',
            'title',
            'code',
            'employee_inherit',
            'date_created',
            'status',
            'recurrence_list',
        )

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'first_name': obj.employee_inherit.first_name,
            'last_name': obj.employee_inherit.last_name,
            'email': obj.employee_inherit.email,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'phone': obj.employee_inherit.phone,
            'is_active': obj.employee_inherit.is_active,
        } if obj.employee_inherit else {}

    @classmethod
    def get_status(cls, obj):
        return Recurrence.objects.filter(doc_template_id=obj.id).exists()

    @classmethod
    def get_recurrence_list(cls, obj):
        return [{
            'id': recurrence.id,
            'title': recurrence.title,
        } for recurrence in Recurrence.objects.filter(doc_template_id=obj.id)]
