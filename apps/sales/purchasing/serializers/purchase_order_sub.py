from rest_framework import serializers

from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.accounts import Account
from apps.masterdata.saledata.models.price import Tax
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure
from apps.sales.purchasing.models import PurchaseRequestProduct, PurchaseOrderProduct, PurchaseOrderRequest, \
    PurchaseRequest, PurchaseOrderRequestProduct, PurchaseQuotation, PurchaseOrderQuotation
from apps.sales.saleorder.models import SaleOrderProduct
from apps.shared import AccountsMsg, ProductMsg, PurchaseRequestMsg, SaleMsg, PurchasingMsg


class PurchaseOrderCommonCreate:

    @classmethod
    def validate_product(cls, dict_data):
        product = {}
        uom_request = {}
        uom_order = {}
        tax = {}
        purchase_request_product_datas = []
        if 'purchase_request_product_datas' in dict_data:
            purchase_request_product_datas = dict_data['purchase_request_product_datas']
            del dict_data['purchase_request_product_datas']
        if 'product' in dict_data:
            product = dict_data['product']
            del dict_data['product']
        if 'uom_request' in dict_data:
            uom_request = dict_data['uom_request']
            del dict_data['uom_request']
        if 'uom_order' in dict_data:
            uom_order = dict_data['uom_order']
            del dict_data['uom_order']
        if 'tax' in dict_data:
            tax = dict_data['tax']
            del dict_data['tax']
        return {
            'purchase_request_product_datas': purchase_request_product_datas,
            'product': product,
            'uom_request': uom_request,
            'uom_order': uom_order,
            'tax': tax,
        }

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
            purchase_quotation_id=purchase_quotation.purchase_quotation.get('id', None),
            is_use=purchase_quotation.is_use,
        ) for purchase_quotation in validated_data['purchase_quotations_data']])
        return True

    @classmethod
    def create_product(cls, validated_data, instance):
        for purchase_order_product in validated_data['purchase_order_products_data']:
            data = cls.validate_product(dict_data=purchase_order_product)
            order_product = PurchaseOrderProduct.objects.create(
                purchase_order=instance,
                product_id=data['product'].get('id', None),
                uom_request_id=data['uom_request'].get('id', None),
                uom_order_id=data['uom_order'].get('id', None),
                tax_id=data['tax'].get('id', None),
                **purchase_order_product
            )
            if order_product:
                if data['purchase_request_product_datas']:
                    PurchaseOrderRequestProduct.objects.bulk_create([
                        PurchaseOrderRequestProduct(
                            **purchase_request_product,
                            purchase_order_product=order_product,
                        ) for purchase_request_product in data['purchase_request_product_datas']
                    ])
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
    def delete_old_product(cls, instance):
        old_product = PurchaseOrderProduct.objects.filter(purchase_order=instance)
        if old_product:
            old_product.delete()
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
        if 'purchase_order_products_data' in validated_data:
            if is_update is True:
                cls.delete_old_product(instance=instance)
            cls.create_product(
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
        try:
            if PurchaseRequestProduct.objects.get(id=value):
                return str(value)
        except PurchaseRequestProduct.DoesNotExist:
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
        try:
            if value is None:
                return value
            if SaleOrderProduct.objects.get(id=value):
                return str(value)
        except SaleOrderProduct.DoesNotExist:
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
