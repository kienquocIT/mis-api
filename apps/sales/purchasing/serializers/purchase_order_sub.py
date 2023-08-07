from rest_framework import serializers

from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.accounts import Account
from apps.masterdata.saledata.models.price import Tax
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure
from apps.sales.purchasing.models import PurchaseRequestProduct, PurchaseOrderProductRequest, PurchaseOrderRequest
from apps.shared import AccountsMsg, ProductMsg
from apps.shared.translations.sales import PurchaseRequestMsg


class PurchaseOrderCommonCreate:

    @classmethod
    def create_m2m_order_purchase_request(cls, validated_data, instance):
        PurchaseOrderRequest.objects.bulk_create([PurchaseOrderRequest(
            purchase_order=instance,
            purchase_request_id=purchase_request.get('id', None),
        ) for purchase_request in validated_data['purchase_requests_data']])
        return True

    @classmethod
    def create_product(cls, validated_data, instance):
        for purchase_order_product in validated_data['purchase_order_products_data']:
            PurchaseOrderProductRequest.objects.create(
                purchase_order=instance,
                product_id=purchase_order_product['product'].get('id', None),
                uom_request_id=purchase_order_product['uom_request'].get('id', None),
                uom_order_id=purchase_order_product['uom_order'].get('id', None),
                tax_id=purchase_order_product['tax'].get('id', None),
                **purchase_order_product
            )
        return True

    @classmethod
    def delete_old_m2m_purchase_order_request(cls, instance):
        old_purchase_order_request = PurchaseOrderRequest.objects.filter(purchase_order=instance)
        if old_purchase_order_request:
            old_purchase_order_request.delete()
        return True

    @classmethod
    def delete_old_product(cls, instance):
        old_product = PurchaseOrderProductRequest.objects.filter(purchase_order=instance)
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
    def validate_purchase_request_product(cls, value):
        try:
            purchase_request_product = PurchaseRequestProduct.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(purchase_request_product.id),
                'title': purchase_request_product.title,
                'code': purchase_request_product.code,
                'sale_order_product_id': purchase_request_product.sale_order_product_id,
            }
        except PurchaseRequestProduct.DoesNotExist:
            raise serializers.ValidationError({
                'purchase_request_product': PurchaseRequestMsg.PURCHASE_REQUEST_NOT_EXIST
            })

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
