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
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import (
    Account, Product, UnitOfMeasure, Tax, AccountBillingAddress, BankAccount
)
from apps.sales.delivery.models import OrderDeliverySub, OrderDeliveryProduct
from apps.sales.arinvoice.models import (
    ARInvoice, ARInvoiceDelivery, ARInvoiceItems, ARInvoiceAttachmentFile, ARInvoiceSign
)
from apps.sales.leaseorder.models import LeaseOrder, LeaseOrderProduct
from apps.sales.saleorder.models import SaleOrder, SaleOrderProduct
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel,
    SerializerCommonValidate, SerializerCommonHandle
)


__all__ = [
    'ARInvoiceListSerializer',
    'ARInvoiceDetailSerializer',
    'ARInvoiceCreateSerializer',
    'ARInvoiceUpdateSerializer',
    'SaleOrderListSerializerForARInvoice',
    'DeliveryListSerializerForARInvoice',
    'ARInvoiceSignListSerializer',
    'ARInvoiceSignCreateSerializer',
    'ARInvoiceSignDetailSerializer',
    'ARInvoiceRecurrenceListSerializer'
]


class ARInvoiceListSerializer(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = ARInvoice
        fields = (
            'id',
            'title',
            'code',
            'customer_mapped_data',
            'buyer_information',
            'sale_order_mapped_data',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'invoice_status',
            'date_created',
            'employee_created'
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}


class ARInvoiceCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer_mapped = serializers.UUIDField()
    billing_address_id = serializers.UUIDField(allow_null=True)
    company_bank_account = serializers.UUIDField(allow_null=True)
    sale_order_mapped = serializers.UUIDField(allow_null=True)
    lease_order_mapped = serializers.UUIDField(allow_null=True)
    delivery_mapped_list = serializers.JSONField(default=list)
    data_item_list = serializers.JSONField(default=list)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = ARInvoice
        fields = (
            'title',
            'customer_mapped',
            'billing_address_id',
            'company_bank_account',
            'buyer_information',
            'invoice_method',
            'sale_order_mapped',
            'lease_order_mapped',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'note',
            'delivery_mapped_list',
            'data_item_list',
            'attachment',
            # recurrence
            'is_recurrence_template',
            'is_recurring',
            'recurrence_task_id',
        )

    @classmethod
    def validate_customer_mapped(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'customer_mapped': "Customer does not exist."})

    @classmethod
    def validate_sale_order_mapped(cls, value):
        if value:
            try:
                return SaleOrder.objects.get(id=value)
            except SaleOrder.DoesNotExist:
                raise serializers.ValidationError({'sale_order_mapped': "Sale order does not exist."})
        return None

    @classmethod
    def validate_lease_order_mapped(cls, value):
        if value:
            try:
                return LeaseOrder.objects.get(id=value)
            except LeaseOrder.DoesNotExist:
                raise serializers.ValidationError({'lease_order_mapped': "Lease order does not exist."})
        return None

    @classmethod
    def validate_company_bank_account(cls, value):
        if value:
            try:
                return BankAccount.objects.get(id=value)
            except BankAccount.DoesNotExist:
                raise serializers.ValidationError({'company_bank_account': "Company bank account does not exist."})
        return None

    @classmethod
    def validate_delivery_mapped_list(cls, delivery_mapped_list):
        try:
            parse_data_delivery_mapped_list = []
            for delivery_id in delivery_mapped_list:
                delivery_obj = OrderDeliverySub.objects.get(id=delivery_id)
                parse_data_delivery_mapped_list.append({
                    'delivery_mapped': delivery_obj,
                    'delivery_mapped_data': {
                        'id': str(delivery_obj.id),
                        'code': delivery_obj.code
                    }
                })
            return parse_data_delivery_mapped_list
        except OrderDeliverySub.DoesNotExist:
            raise serializers.ValidationError({'delivery_mapped': "Delivery does not exist."})

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(user=user, model_cls=ARInvoiceAttachmentFile, value=value)

    def validate(self, validate_data):
        billing_address_id = validate_data.pop('billing_address_id')
        # parse data customer_mapped
        customer_mapped = validate_data.get('customer_mapped')
        if customer_mapped:
            if not AccountBillingAddress.objects.filter(id=billing_address_id).exists():
                if customer_mapped.account_type_selection == 1:
                    raise serializers.ValidationError({
                        'billing_address': "Billing address is required for organization customer."
                    })
            validate_data['customer_mapped_data'] = {
                'id': str(customer_mapped.id),
                'code': customer_mapped.code,
                'name': customer_mapped.name,
                'tax_code': customer_mapped.tax_code,
                'billing_address_id': str(billing_address_id),
            }
        # parse data sale_order_mapped
        sale_order_mapped = validate_data.get('sale_order_mapped')
        if sale_order_mapped:
            validate_data['sale_order_mapped_data'] = {
                'id': str(sale_order_mapped.id),
                'code': sale_order_mapped.code,
                'title': sale_order_mapped.title,
                'sale_order_payment_stage': sale_order_mapped.sale_order_payment_stage
            }
        # parse data lease_order_mapped
        lease_order_mapped = validate_data.get('lease_order_mapped')
        if lease_order_mapped:
            validate_data['lease_order_mapped_data'] = {
                'id': str(lease_order_mapped.id),
                'code': lease_order_mapped.code,
                'title': lease_order_mapped.title,
                'lease_payment_stage': lease_order_mapped.lease_payment_stage
            }
        # parse data bank_account
        bank_account = validate_data.get('company_bank_account')
        if bank_account:
            validate_data['company_bank_account_data'] = {
                'id': str(bank_account.id),
                'title': (f"{bank_account.bank_account_number} ({bank_account.bank_account_owner}) - "
                          f"{bank_account.bank_mapped.bank_name} ({bank_account.bank_mapped.bank_abbreviation})")
            }
        # check valid data bank number
        if validate_data.get('invoice_method') == 2 and not validate_data.get('company_bank_account'):
            raise serializers.ValidationError({'company_bank_account': "Company bank account is not null."})
        # check valid data data_item_list
        valid_data_item_list = []
        if not sale_order_mapped and not lease_order_mapped:
            for item in validate_data.get('data_item_list', []):
                product_obj = Product.objects.filter(id=item.get('product_id')).first()
                uom_obj = UnitOfMeasure.objects.filter(id=item.get('product_uom_id')).first()
                tax_obj = Tax.objects.filter(id=item.get('product_tax_id')).first()

                if not all([product_obj, uom_obj]):
                    raise serializers.ValidationError({'data_item_list': "Missing delivery item info."})

                # Lấy giá trị gốc
                product_quantity = float(item.get('product_quantity', 0))
                product_unit_price = float(item.get('product_unit_price', 0))
                product_subtotal = product_quantity * product_unit_price

                # Lấy input từ client
                product_payment_percent = item.get('product_payment_percent')
                product_payment_value = float(item.get('product_payment_value', 0))
                product_discount_percent = item.get('product_discount_percent')
                product_discount_value = float(item.get('product_discount_value', 0))

                # Tính giá trị hàng hóa đợt này (Trước khi trừ KM)
                if product_payment_percent:
                    product_payment_percent = float(product_payment_percent)
                    if not (0 <= product_payment_percent <= 100):
                        raise serializers.ValidationError(
                            {'product_payment_percent': "Payment percent must be 0-100."})
                    product_payment_value = product_subtotal * product_payment_percent / 100
                    if product_payment_value > product_subtotal:
                        raise serializers.ValidationError(
                            {'product_payment_value': "Payment value can not be greater than Total value."})

                # Tính giảm giá (Discount)
                if product_discount_percent:
                    product_discount_percent = float(product_discount_percent)
                    if not (0 <= product_discount_percent <= 100):
                        raise serializers.ValidationError(
                            {'product_discount_percent': "Discount percent must be 0-100."})
                    product_discount_value = product_subtotal * product_discount_percent / 100
                    if product_discount_value > product_subtotal:
                        raise serializers.ValidationError(
                            {'product_discount_value': "Discount value can not be greater than Total value."})

                # Tính thuế cho đợt này
                tax_rate = tax_obj.rate if tax_obj else 0
                product_tax_value = (product_payment_value - product_discount_value) * tax_rate / 100

                valid_data_item_list.append({
                    'delivery_item_mapped': None,
                    'product': product_obj,
                    'product_data': {
                        'id': str(product_obj.id),
                        'code': product_obj.code,
                        'title': product_obj.title,
                        'description': product_obj.description,
                    } if product_obj else {},
                    'product_uom': uom_obj,
                    'product_uom_data': {
                        'id': str(uom_obj.id),
                        'code': uom_obj.code,
                        'title': uom_obj.title,
                        'group_id': str(uom_obj.group_id)
                    } if uom_obj else {},
                    'product_quantity': product_quantity,
                    'product_unit_price': product_unit_price,
                    'product_subtotal': product_subtotal,
                    # Các số liệu tính toán cho Hóa đơn này
                    'product_payment_percent': product_payment_percent,
                    'product_payment_value': product_payment_value,
                    'product_discount_percent': product_discount_percent,
                    'product_discount_value': product_discount_value,
                    'product_tax': tax_obj,
                    'product_tax_data': {
                        'id': str(tax_obj.id),
                        'code': tax_obj.code,
                        'title': tax_obj.title,
                        'rate': tax_obj.rate,
                    } if tax_obj else {},
                    'product_tax_value': product_tax_value,
                    'product_subtotal_final': product_payment_value - product_discount_value + product_tax_value,
                    'note': item.get('note', '')
                })
        else:
            for item in validate_data.get('data_item_list', []):
                delivery_item_obj = OrderDeliveryProduct.objects.filter(
                    id=item.get('delivery_item_mapped_id')
                ).first()
                product_obj = Product.objects.filter(id=item.get('product_id')).first()
                uom_obj = UnitOfMeasure.objects.filter(id=item.get('product_uom_id')).first()
                tax_obj = Tax.objects.filter(id=item.get('product_tax_id')).first()

                if not all([product_obj, uom_obj, delivery_item_obj]):
                    raise serializers.ValidationError({'data_item_list': "Missing delivery item info."})

                # Lấy giá trị gốc
                product_quantity = delivery_item_obj.picked_quantity
                product_unit_price = delivery_item_obj.product_cost
                product_subtotal = product_quantity * product_unit_price  # Tổng (Net)

                # Lấy input từ client
                product_payment_percent = item.get('product_payment_percent')
                product_payment_value = float(item.get('product_payment_value', 0))
                product_discount_percent = item.get('product_discount_percent')
                product_discount_value = float(item.get('product_discount_value', 0))

                # Tính giá trị hàng hóa đợt này (Trước khi trừ KM)
                if product_payment_percent:
                    product_payment_percent = float(product_payment_percent)
                    if not (0 <= product_payment_percent <= 100):
                        raise serializers.ValidationError(
                            {'product_payment_percent': "Payment percent must be 0-100."})
                    product_payment_value = product_subtotal * product_payment_percent / 100
                    if product_payment_value > product_subtotal - delivery_item_obj.ar_value_done:
                        raise serializers.ValidationError(
                            {'product_payment_value': "Payment value can not be greater than Total value."})

                # Tính giảm giá (Discount)
                if product_discount_percent:
                    product_discount_percent = float(product_discount_percent)
                    if not (0 <= product_discount_percent <= 100):
                        raise serializers.ValidationError(
                            {'product_discount_percent': "Discount percent must be 0-100."})
                    product_discount_value = product_subtotal * product_discount_percent / 100
                    if product_discount_value > product_subtotal - delivery_item_obj.ar_value_done:
                        raise serializers.ValidationError(
                            {'product_discount_value': "Discount value can not be greater than Total value."})

                # Tính thuế cho đợt này
                tax_rate = tax_obj.rate if tax_obj else 0
                product_tax_value = (product_payment_value - product_discount_value) * tax_rate / 100

                valid_data_item_list.append({
                    'delivery_item_mapped': delivery_item_obj,
                    'product': product_obj,
                    'product_data': {
                        'id': str(product_obj.id),
                        'code': product_obj.code,
                        'title': product_obj.title,
                        'description': product_obj.description,
                    } if product_obj else {},
                    'product_uom': uom_obj,
                    'product_uom_data': {
                        'id': str(uom_obj.id),
                        'code': uom_obj.code,
                        'title': uom_obj.title,
                        'group_id': str(uom_obj.group_id)
                    } if uom_obj else {},
                    'product_quantity': product_quantity,
                    'product_unit_price': product_unit_price,
                    'product_subtotal': product_subtotal,
                    # Các số liệu tính toán cho Hóa đơn này
                    'product_payment_percent': product_payment_percent,
                    'product_payment_value': product_payment_value,
                    'product_discount_percent': product_discount_percent,
                    'product_discount_value': product_discount_value,
                    'product_tax': tax_obj,
                    'product_tax_data': {
                        'id': str(tax_obj.id),
                        'code': tax_obj.code,
                        'title': tax_obj.title,
                        'rate': tax_obj.rate,
                    } if tax_obj else {},
                    'product_tax_value': product_tax_value,
                    'product_subtotal_final': product_payment_value - product_discount_value + product_tax_value,
                    'note': item.get('note', '')
                })

        validate_data['data_item_list'] = valid_data_item_list
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        delivery_mapped_list = validated_data.pop('delivery_mapped_list', [])
        data_item_list = validated_data.pop('data_item_list', [])
        attachment_list = validated_data.pop('attachment', [])

        ar_invoice_obj = ARInvoice.objects.create(**validated_data)

        ARInvoiceCommonFunc.create_delivery_mapped(ar_invoice_obj, delivery_mapped_list)
        ARInvoiceCommonFunc.create_items_mapped(ar_invoice_obj, data_item_list)
        ARInvoiceCommonFunc.create_files_mapped(ar_invoice_obj, attachment_list)

        return ar_invoice_obj


class ARInvoiceDetailSerializer(AbstractDetailSerializerModel):
    customer_mapped_data = serializers.SerializerMethodField()
    delivery_mapped = serializers.SerializerMethodField()
    item_mapped = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    invoice_info = serializers.SerializerMethodField()

    class Meta:
        model = ARInvoice
        fields = (
            'id',
            'code',
            'title',
            'customer_mapped_data',
            'buyer_information',
            'invoice_method',
            'sale_order_mapped_data',
            'lease_order_mapped_data',
            'company_bank_account_data',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_info',
            'invoice_example',
            'is_created_einvoice',
            'delivery_mapped',
            'item_mapped',
            'attachment',
            'invoice_status',
            'note',
        )

    @classmethod
    def get_customer_mapped_data(cls, obj):
        if obj.customer_mapped:
            obj.customer_mapped_data['bank_account_list'] = [{
                'id': str(item.id),
                'bank_country_id': str(item.country_id),
                'bank_name': item.bank_name,
                'bank_code': item.bank_code,
                'bank_account_name': item.bank_account_name,
                'bank_account_number': item.bank_account_number,
                'bic_swift_code': item.bic_swift_code,
                'is_default': item.is_default
            } for item in obj.customer_mapped.account_banks_mapped.all()]
            obj.customer_mapped_data['billing_address_list'] = [{
                'id': str(item.id),
                'account_name': item.account_name,
                'email': item.email,
                'tax_code': item.tax_code,
                'account_address': item.account_address,
                'full_address': item.full_address,
                'is_default': item.is_default
            } for item in obj.customer_mapped.account_mapped_billing_address.all()]
        return obj.customer_mapped_data

    @classmethod
    def get_delivery_mapped(cls, obj):
        return [item.delivery_mapped_data for item in obj.ar_invoice_deliveries.all()]

    @classmethod
    def get_item_mapped(cls, obj):
        return [{
            'id': item.id,
            'order': item.order,
            'delivery_item_mapped_id': str(item.delivery_item_mapped_id),
            'product_data': item.product_data,
            'product_uom_data': item.product_uom_data,
            'product_quantity': item.product_quantity,
            'product_unit_price': item.product_unit_price,
            'product_subtotal': item.product_subtotal,
            'product_payment_percent': item.product_payment_percent,
            'product_payment_value': item.product_payment_value,
            'product_discount_percent': item.product_discount_percent,
            'product_discount_value': item.product_discount_value,
            'product_tax_data': item.product_tax_data,
            'product_tax_value': item.product_tax_value,
            'product_subtotal_final': item.product_subtotal_final,
            'note': item.note,
        } for item in obj.ar_invoice_items.all()]

    @classmethod
    def get_attachment(cls, obj):
        return [item.attachment.get_detail() for item in obj.ar_invoice_attachments.all()]

    @classmethod
    def get_invoice_info(cls, obj):
        if obj.is_created_einvoice:
            ikey = str(obj.id) + '-' + obj.invoice_sign
            http_method = "POST"
            username = "API"
            password = "Api@0317493763"
            token = ARInvoiceCommonFunc.generate_token(http_method, username, password)
            headers = {"Authentication": f"{token}", "Content-Type": "application/json"}
            response = requests.post(
                "http://0317493763.softdreams.vn/api/publish/getInvoicesByIkeys",
                headers=headers,
                json={
                    'Ikeys': [ikey]
                },
                timeout=30
            )
            if response.status_code == 200:
                invoice_info = json.loads(response.text).get('Data', {})['Invoices']
                return invoice_info[0] if invoice_info else {}
        return {}


class ARInvoiceUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer_mapped = serializers.UUIDField()
    billing_address_id = serializers.UUIDField(allow_null=True)
    company_bank_account = serializers.UUIDField(allow_null=True)
    sale_order_mapped = serializers.UUIDField(allow_null=True)
    lease_order_mapped = serializers.UUIDField(allow_null=True)
    delivery_mapped_list = serializers.JSONField(default=list)
    data_item_list = serializers.JSONField(default=list)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = ARInvoice
        fields = (
            'title',
            'customer_mapped',
            'billing_address_id',
            'company_bank_account',
            'buyer_information',
            'invoice_method',
            'sale_order_mapped',
            'lease_order_mapped',
            'posting_date',
            'document_date',
            'invoice_date',
            'invoice_sign',
            'invoice_number',
            'invoice_example',
            'note',
            'delivery_mapped_list',
            'data_item_list',
            'attachment'
        )

    @classmethod
    def validate_customer_mapped(cls, value):
        return ARInvoiceCreateSerializer.validate_customer_mapped(value)

    @classmethod
    def validate_sale_order_mapped(cls, value):
        return ARInvoiceCreateSerializer.validate_sale_order_mapped(value)

    @classmethod
    def validate_lease_order_mapped(cls, value):
        return ARInvoiceCreateSerializer.validate_lease_order_mapped(value)

    @classmethod
    def validate_company_bank_account(cls, value):
        return ARInvoiceCreateSerializer.validate_company_bank_account(value)

    @classmethod
    def validate_delivery_mapped_list(cls, delivery_mapped_list):
        return ARInvoiceCreateSerializer.validate_delivery_mapped_list(delivery_mapped_list)

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=ARInvoiceAttachmentFile, value=value, doc_id=self.instance.id
        )

    def validate(self, validate_data):
        return ARInvoiceCreateSerializer().validate(validate_data)

    @decorator_run_workflow
    def update(self, instance, validated_data):
        delivery_mapped_list = validated_data.pop('delivery_mapped_list', [])
        data_item_list = validated_data.pop('data_item_list', [])
        attachment_list = validated_data.pop('attachment', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        ARInvoiceCommonFunc.create_delivery_mapped(instance, delivery_mapped_list)
        ARInvoiceCommonFunc.create_items_mapped(instance, data_item_list)
        ARInvoiceCommonFunc.create_files_mapped(instance, attachment_list)

        return instance


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
            sum_pretax_value += float(item.get('product_subtotal', 0))
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

# related serializers
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
            'already',
            'details',
            'actual_delivery_date'
        )

    @classmethod
    def get_details(cls, obj):
        so_mapped = obj.order_delivery.sale_order if obj.order_delivery else None
        so_product_data = {
            str(item.product_id): {
                'product_id': str(item.product_id),
                'product_data': item.product_data,
                'product_unit_price': item.product_unit_price,
                'product_discount_value': item.product_discount_value,
                'product_tax_data': item.tax_data
            }
            for item in so_mapped.sale_order_product_sale_order.all()
        } if so_mapped else {}

        details = []
        for item in obj.delivery_product_delivery_sub.all():
            so_product_data_get = so_product_data.get(str(item.product_id), {})
            if so_product_data_get:
                product_subtotal = so_product_data_get.get('product_unit_price', 0) * item.picked_quantity
                product_discount_amount = product_subtotal * so_product_data_get.get('product_discount_value', 0) / 100
                so_product_data_get['product_subtotal'] = product_subtotal
                so_product_data_get['product_discount_value'] = product_discount_amount
                so_product_data_get['product_tax_value'] = (
                    product_subtotal - product_discount_amount
                ) * so_product_data_get.get('product_tax_data', {}).get('rate', 0) / 100
                so_product_data_get['product_subtotal_final'] = (
                    product_subtotal - product_discount_amount
                ) + so_product_data_get.get('product_tax_value', 0)
            details.append({
                'id': str(item.id),
                'delivery_id': str(obj.id),
                'product_uom_data': item.uom_data,
                'delivery_quantity': item.delivery_quantity,
                'product_quantity': item.picked_quantity,
                **so_product_data_get
            })
        return details

    @classmethod
    def get_already(cls, obj):
        return obj.is_done_ar_invoice


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
