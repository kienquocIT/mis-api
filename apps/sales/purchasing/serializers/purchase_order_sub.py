from rest_framework import serializers

from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.accounts import Account
from apps.masterdata.saledata.models.price import Tax
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure
from apps.sales.purchasing.models import PurchaseRequestProduct, PurchaseOrderProduct, PurchaseOrderRequest, \
    PurchaseRequest, PurchaseOrderRequestProduct, PurchaseQuotation, PurchaseOrderQuotation, PurchaseOrderPaymentStage
from apps.sales.saleorder.models import SaleOrderProduct
from apps.shared import AccountsMsg, ProductMsg, PurchaseRequestMsg, SaleMsg, PurchasingMsg


class PurchaseOrderCommonCreate:

    @classmethod
    def validate_product(cls, dict_data):
        product = {}
        uom_order_request = {}
        uom_order_actual = {}
        tax = {}
        purchase_request_products_data = []
        if 'purchase_request_products_data' in dict_data:
            purchase_request_products_data = dict_data['purchase_request_products_data']
            del dict_data['purchase_request_products_data']
        if 'product' in dict_data:
            product = dict_data['product']
            del dict_data['product']
        if 'uom_order_request' in dict_data:
            uom_order_request = dict_data['uom_order_request']
            del dict_data['uom_order_request']
        if 'uom_order_actual' in dict_data:
            uom_order_actual = dict_data['uom_order_actual']
            del dict_data['uom_order_actual']
        if 'tax' in dict_data:
            tax = dict_data['tax']
            del dict_data['tax']
        return {
            'purchase_request_products_data': purchase_request_products_data,
            'product': product,
            'uom_order_request': uom_order_request,
            'uom_order_actual': uom_order_actual,
            'tax': tax,
        }

    @classmethod
    def validate_payment_stage_data(cls, dict_data):
        if 'tax' in dict_data:
            tax_id = dict_data['tax'].get('id', None)
            del dict_data['tax']
            dict_data.update({'tax_id': tax_id})
        return dict_data

    @classmethod
    def create_m2m_order_purchase_request(cls, validated_data, instance):
        PurchaseOrderRequest.objects.bulk_create([PurchaseOrderRequest(
            purchase_order=instance,
            purchase_request_id=purchase_request.get('id', None),
        ) for purchase_request in validated_data['purchase_requests_data']])
        return True

    @classmethod
    def create_m2m_order_purchase_quotation(cls, validated_data, instance):
        PurchaseOrderQuotation.objects.bulk_create([PurchaseOrderQuotation(
            purchase_order=instance,
            purchase_quotation_id=purchase_quotation['purchase_quotation'].get('id', None),
            is_use=purchase_quotation['is_use'],
        ) for purchase_quotation in validated_data['purchase_quotations_data']])
        return True

    @classmethod
    def create_purchase_request_products_data(cls, validated_data, instance):
        PurchaseOrderRequestProduct.objects.bulk_create([
            PurchaseOrderRequestProduct(
                purchase_order=instance,
                purchase_request_product_id=purchase_request_product['purchase_request_product'],
                sale_order_product_id=purchase_request_product['sale_order_product'],
                quantity_order=purchase_request_product['quantity_order'],
                gr_remain_quantity=purchase_request_product['quantity_order'],
            ) for purchase_request_product in validated_data['purchase_request_products_data']
        ])

    @classmethod
    def create_product(cls, validated_data, instance):
        for purchase_order_product in validated_data['purchase_order_products_data']:
            data = cls.validate_product(dict_data=purchase_order_product)
            order_product = PurchaseOrderProduct.objects.create(
                purchase_order=instance,
                product_id=data['product'].get('id', None),
                uom_order_request_id=data['uom_order_request'].get('id', None),
                uom_order_actual_id=data['uom_order_actual'].get('id', None),
                tax_id=data['tax'].get('id', None),
                gr_remain_quantity=purchase_order_product.get('product_quantity_order_actual', 0),
                **purchase_order_product
            )
            if order_product:
                if data['purchase_request_products_data']:
                    PurchaseOrderRequestProduct.objects.bulk_create([
                        PurchaseOrderRequestProduct(
                            purchase_order=instance,
                            purchase_request_product_id=purchase_request_product.get('purchase_request_product', None),
                            purchase_order_product=order_product,
                            sale_order_product_id=purchase_request_product.get('sale_order_product', None),
                            quantity_order=purchase_request_product['quantity_order'],
                            gr_remain_quantity=purchase_request_product['quantity_order'],
                            uom_stock_id=purchase_request_product.get('uom_stock', {}).get('id', None),
                            is_stock=purchase_request_product.get('is_stock', False),
                        ) for purchase_request_product in data['purchase_request_products_data']
                    ])
        return True

    @classmethod
    def create_payment_stage(cls, validated_data, instance):
        bulk_info = []
        for purchase_order_payment_stage in validated_data['purchase_order_payment_stage']:
            valid_data = cls.validate_payment_stage_data(purchase_order_payment_stage)
            bulk_info.append(PurchaseOrderPaymentStage(
                purchase_order=instance,
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                **valid_data,
            ))
        PurchaseOrderPaymentStage.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def delete_old_m2m_purchase_order_request(cls, instance):
        old_purchase_order_request = PurchaseOrderRequest.objects.filter(purchase_order=instance)
        if old_purchase_order_request:
            old_purchase_order_request.delete()
        return True

    @classmethod
    def delete_old_m2m_purchase_order_quotation(cls, instance):
        old_purchase_order_quotation = PurchaseOrderQuotation.objects.filter(purchase_order=instance)
        if old_purchase_order_quotation:
            old_purchase_order_quotation.delete()
        return True

    @classmethod
    def delete_old_pr_product(cls, instance):
        old_pr_product = PurchaseOrderRequestProduct.objects.filter(
            purchase_order=instance,
            purchase_order_product__isnull=True
        )
        if old_pr_product:
            old_pr_product.delete()
        return True

    @classmethod
    def delete_old_product(cls, instance):
        old_product = PurchaseOrderProduct.objects.filter(purchase_order=instance)
        if old_product:
            pr_products = PurchaseOrderRequestProduct.objects.filter(purchase_order_product__in=old_product)
            if pr_products:
                pr_products.delete()
            old_product.delete()
        return True

    @classmethod
    def delete_old_payment_stage(cls, instance):
        old_payment_stage = PurchaseOrderPaymentStage.objects.filter(purchase_order=instance)
        if old_payment_stage:
            old_payment_stage.delete()
        return True

    @classmethod
    def create_purchase_order_sub_models(cls, validated_data, instance, is_update=False):
        if 'purchase_requests_data' in validated_data:
            if is_update is True:
                cls.delete_old_m2m_purchase_order_request(instance=instance)
            cls.create_m2m_order_purchase_request(
                validated_data=validated_data,
                instance=instance
            )
        if 'purchase_quotations_data' in validated_data:
            if is_update is True:
                cls.delete_old_m2m_purchase_order_quotation(instance=instance)
            cls.create_m2m_order_purchase_quotation(
                validated_data=validated_data,
                instance=instance
            )
        if 'purchase_request_products_data' in validated_data:
            if is_update is True:
                cls.delete_old_pr_product(instance=instance)
            cls.create_purchase_request_products_data(
                validated_data=validated_data,
                instance=instance
            )
        if 'purchase_order_products_data' in validated_data:
            if is_update is True:
                cls.delete_old_product(instance=instance)
            cls.create_product(
                validated_data=validated_data,
                instance=instance
            )
        if 'purchase_order_payment_stage' in validated_data:
            if is_update is True:
                cls.delete_old_payment_stage(instance=instance)
            cls.create_payment_stage(
                validated_data=validated_data,
                instance=instance
            )
        return True


class PurchasingCommonValidate:

    @classmethod
    def validate_purchase_requests_data(cls, value):
        if isinstance(value, list):
            purchase_request_list = PurchaseRequest.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id__in=value
            )
            if purchase_request_list.count() == len(value):
                return [
                    {'id': str(item.id), 'title': item.title, 'code': item.code}
                    for item in purchase_request_list
                ]
            raise serializers.ValidationError({'detail': PurchaseRequestMsg.PURCHASE_REQUEST_NOT_EXIST})
        raise serializers.ValidationError({'detail': PurchaseRequestMsg.PURCHASE_REQUEST_IS_ARRAY})

    @classmethod
    def validate_supplier(cls, value):
        try:
            return Account.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Account.DoesNotExist:
            raise serializers.ValidationError({'supplier': AccountsMsg.ACCOUNT_NOT_EXIST})

    @classmethod
    def validate_contact(cls, value):
        try:
            return Contact.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Contact.DoesNotExist:
            raise serializers.ValidationError({'contact': AccountsMsg.CONTACT_NOT_EXIST})

    @classmethod
    def validate_product(cls, value):
        try:
            if value is None:
                return {}
            product = Product.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(product.id),
                'title': product.title,
                'code': product.code,
                'product_choice': product.product_choice,
            }
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': ProductMsg.PRODUCT_DOES_NOT_EXIST})

    @classmethod
    def validate_purchase_request_product(cls, value):
        if PurchaseRequestProduct.objects.filter(id=value).exists():
            return str(value)
        raise serializers.ValidationError({
            'purchase_request_product': PurchaseRequestMsg.PURCHASE_REQUEST_NOT_EXIST
        })

    @classmethod
    def validate_purchase_quotation(cls, value):
        try:
            purchase_quotation = PurchaseQuotation.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(purchase_quotation.id),
                'title': purchase_quotation.title,
                'code': purchase_quotation.code,
            }
        except PurchaseQuotation.DoesNotExist:
            raise serializers.ValidationError({
                'purchase_quotation': PurchasingMsg.PURCHASE_QUOTATION_NOT_EXIST
            })

    @classmethod
    def validate_sale_order_product(cls, value):
        if value is None:
            return value
        if SaleOrderProduct.objects.filter(id=value).exists():
            return str(value)
        raise serializers.ValidationError({
            'sale_order_product': SaleMsg.SALE_ORDER_PRODUCT_NOT_EXIST
        })

    @classmethod
    def validate_unit_of_measure(cls, value):
        try:
            if value is None:
                return {}
            uom = UnitOfMeasure.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(uom.id),
                'title': uom.title,
                'code': uom.code
            }
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'unit_of_measure': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST})

    @classmethod
    def validate_tax(cls, value):
        try:
            tax = Tax.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(tax.id),
                'title': tax.title,
                'code': tax.code,
                'value': tax.rate
            }
        except Tax.DoesNotExist:
            raise serializers.ValidationError({'tax': ProductMsg.TAX_DOES_NOT_EXIST})

    @classmethod
    def validate_product_quantity_order_actual(cls, value):
        if value <= 0:
            raise serializers.ValidationError({'quantity_order': PurchasingMsg.PURCHASE_ORDER_QUANTITY})
        return value


class PurchaseOrderCommonGet:

    @classmethod
    def get_uom(cls, uom_obj, uom_id):
        return {
            'id': uom_id,
            'title': uom_obj.title,
            'code': uom_obj.code,
            'uom_group': {
                'id': uom_obj.group_id,
                'title': uom_obj.group.title,
                'code': uom_obj.group.code,
                'uom_reference': {
                    'id': uom_obj.group.uom_reference_id,
                    'title': uom_obj.group.uom_reference.title,
                    'code': uom_obj.group.uom_reference.code,
                    'ratio': uom_obj.group.uom_reference.ratio,
                    'rounding': uom_obj.group.uom_reference.rounding,
                } if uom_obj.group.uom_reference else {},
            } if uom_obj.group else {},
            'ratio': uom_obj.ratio,
            'rounding': uom_obj.rounding,
            'is_referenced_unit': uom_obj.is_referenced_unit,
        } if uom_obj else {}
